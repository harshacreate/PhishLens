"""Offline evaluation against the pinned PhiLegit and Tranco snapshots.

The evaluator never visits a URL. It scores URL strings with the frozen model
trained on the repository's synthetic data, and reports a domain-disjoint,
balanced case-control set. Raw downloads stay in the ignored data/real-data
directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import scipy
import sklearn
import tldextract

from phishlens.features import extract
from phishlens.model import PhishModel


PHILEGIT_VERSION = "1"
PHILEGIT_DOI = "10.17632/726pyz4j53.1"
PHILEGIT_URL = (
    "https://data.mendeley.com/public-files/datasets/726pyz4j53/files/"
    "6b117911-d901-4ea4-9cc4-af55b763c10f/file_downloaded"
)
PHILEGIT_SHA256 = "d95a1419f4b2d1cb98c3ce31fedf7cdabd148f70f42e6ed3de6244366b525558"
TRANCO_LIST_ID = "947N2"
TRANCO_CREATED = "2026-11-09T22:00:01.753741"
TRANCO_URL = "https://tranco-list.eu/download/947N2/50000"
TRANCO_SHA256 = "664b9c716992204d48f87c27a12dd08c9f77b4c468249dbdc57f10c3b52f70e2"
BOOTSTRAP_SEED = 20261111
BOOTSTRAP_REPLICATES = 2000
PHISHING_THRESHOLD = 70.0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, destination: Path, expected_sha256: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url, headers={"User-Agent": "PhishLens-real-data-evaluation/1.0"}
    )
    temporary = destination.with_suffix(destination.suffix + ".part")
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            with temporary.open("wb") as output:
                shutil.copyfileobj(response, output)
        actual = _sha256(temporary)
        if actual != expected_sha256:
            raise ValueError(
                "SHA-256 mismatch for {}: expected {}, received {}".format(
                    destination.name, expected_sha256, actual
                )
            )
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def _ensure_dataset(data_dir: Path, download: bool) -> Tuple[Path, Path]:
    data_dir.mkdir(parents=True, exist_ok=True)
    tranco_path = data_dir / "tranco-947N2-top-50000.csv"
    if not tranco_path.exists():
        if not download:
            raise FileNotFoundError(
                "Tranco snapshot is missing; rerun with --download."
            )
        _download(TRANCO_URL, tranco_path, TRANCO_SHA256)
    elif _sha256(tranco_path) != TRANCO_SHA256:
        raise ValueError("Tranco snapshot checksum does not match list 947N2.")

    philegit_dir = data_dir / "philegit-v1"
    candidates = list(philegit_dir.rglob("PhiLegit-100K.csv")) if philegit_dir.exists() else []
    if not candidates:
        archive = data_dir / "PhiLegit-100K-v1.rar"
        if not archive.exists():
            if not download:
                raise FileNotFoundError(
                    "PhiLegit v1 is missing; rerun with --download."
                )
            _download(PHILEGIT_URL, archive, PHILEGIT_SHA256)
        elif _sha256(archive) != PHILEGIT_SHA256:
            raise ValueError("PhiLegit archive checksum does not match version 1.")
        extractor = shutil.which("bsdtar")
        if extractor is None:
            raise RuntimeError(
                "PhiLegit v1 is a RAR archive; install bsdtar and rerun."
            )
        philegit_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [extractor, "-xf", str(archive), "-C", str(philegit_dir)],
            check=True,
        )
        candidates = list(philegit_dir.rglob("PhiLegit-100K.csv"))
    if len(candidates) != 1:
        raise RuntimeError(
            "Expected one PhiLegit-100K.csv in {}; found {}.".format(
                philegit_dir, len(candidates)
            )
        )
    return candidates[0], tranco_path


def _read_rows(philegit_csv: Path, tranco_csv: Path) -> Tuple[List[Dict], List[Tuple[int, str]]]:
    with philegit_csv.open("r", encoding="utf-8-sig", newline="") as source:
        phish_rows = [
            row for row in csv.DictReader(source)
            if row.get("label_legit_1_phish_0") == "0"
        ]

    tranco_rows: List[Tuple[int, str]] = []
    with tranco_csv.open("r", encoding="utf-8-sig", newline="") as source:
        for row in csv.reader(source):
            if len(row) >= 2:
                try:
                    tranco_rows.append((int(row[0]), row[1].strip().lower()))
                except ValueError:
                    continue
    return phish_rows, tranco_rows


def _build_domain_disjoint_sample(
    phish_rows: List[Dict], tranco_rows: List[Tuple[int, str]]
) -> Tuple[List[Tuple[str, int]], Dict[str, int]]:
    phish_by_domain: Dict[str, str] = {}
    malformed = 0
    exact_duplicates = 0
    seen_urls = set()
    for row in phish_rows:
        url = (row.get("URL") or "").strip()
        if not url:
            malformed += 1
            continue
        if url in seen_urls:
            exact_duplicates += 1
            continue
        seen_urls.add(url)
        domain = extract(url)["registered_domain"]
        if not domain:
            malformed += 1
            continue
        current = phish_by_domain.get(domain)
        if current is None or url < current:
            phish_by_domain[domain] = url

    tranco_domains: List[Tuple[int, str]] = []
    seen_tranco = set()
    for rank, host in tranco_rows:
        domain = extract("https://" + host + "/")["registered_domain"]
        if domain and domain not in seen_tranco:
            tranco_domains.append((rank, domain))
            seen_tranco.add(domain)

    overlapping = set(phish_by_domain).intersection(seen_tranco)
    positives = [
        (url, 1) for domain, url in sorted(phish_by_domain.items())
        if domain not in overlapping
    ]
    positive_domains = {
        extract(url)["registered_domain"] for url, _ in positives
    }

    negatives: List[Tuple[str, int]] = []
    negative_domains = set()
    for _, domain in tranco_domains:
        if domain in positive_domains:
            continue
        negative_domains.add(domain)
        negatives.append(("https://" + domain + "/", 0))
        if len(negatives) == len(positives):
            break
    if not positives or len(negatives) != len(positives):
        raise RuntimeError(
            "Could not create a nonempty balanced sample from the pinned sources."
        )

    return positives + negatives, {
        "phishing_source_rows": len(phish_rows),
        "malformed_or_hostless_phishing_urls": malformed,
        "duplicate_phishing_urls_excluded": exact_duplicates,
        "phishing_rows_reduced_to_one_url_per_registered_domain": (
            len(phish_rows) - malformed - exact_duplicates - len(phish_by_domain)
        ),
        "phishing_domains_overlapping_tranco_excluded": len(overlapping),
        "phishing_unique_registered_domains": len(positives),
        "tranco_rows_in_snapshot": len(tranco_rows),
        "tranco_unique_registered_domains": len(tranco_domains),
        "benign_domains_selected_by_rank": len(negatives),
    }


def _confusion(rows: List[Tuple[int, int]]) -> Dict[str, int]:
    tp = sum(label == 1 and prediction == 1 for label, prediction in rows)
    fp = sum(label == 0 and prediction == 1 for label, prediction in rows)
    tn = sum(label == 0 and prediction == 0 for label, prediction in rows)
    fn = sum(label == 1 and prediction == 0 for label, prediction in rows)
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}


def _metric_values(counts: Dict[str, int]) -> Dict[str, float]:
    tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def _bootstrap_ci(
    labels: np.ndarray,
    predictions: np.ndarray,
    seed: int = BOOTSTRAP_SEED,
    replicates: int = BOOTSTRAP_REPLICATES,
) -> Dict[str, List[float]]:
    positive_predictions = predictions[labels == 1]
    negative_predictions = predictions[labels == 0]
    if not len(positive_predictions) or not len(negative_predictions):
        raise ValueError("Both classes are required for the bootstrap interval.")

    rng = np.random.default_rng(seed)
    samples: Dict[str, List[float]] = {"precision": [], "recall": [], "f1": []}
    batch_size = max(1, min(100, replicates))
    remaining = replicates
    while remaining:
        size = min(batch_size, remaining)
        pos = positive_predictions[
            rng.integers(0, len(positive_predictions), size=(size, len(positive_predictions)))
        ].sum(axis=1)
        neg = negative_predictions[
            rng.integers(0, len(negative_predictions), size=(size, len(negative_predictions)))
        ].sum(axis=1)
        recall = pos / len(positive_predictions)
        precision = pos / np.maximum(pos + neg, 1)
        f1 = 2 * precision * recall / np.maximum(precision + recall, 1e-12)
        samples["precision"].extend(precision.tolist())
        samples["recall"].extend(recall.tolist())
        samples["f1"].extend(f1.tolist())
        remaining -= size

    return {
        name: [
            round(float(np.quantile(values, 0.025)), 3),
            round(float(np.quantile(values, 0.975)), 3),
        ]
        for name, values in samples.items()
    }


def evaluate(
    philegit_csv: Path,
    tranco_csv: Path,
    bootstrap_replicates: int = BOOTSTRAP_REPLICATES,
) -> Dict:
    phish_rows, tranco_rows = _read_rows(philegit_csv, tranco_csv)
    sample, counts = _build_domain_disjoint_sample(phish_rows, tranco_rows)
    model = PhishModel.train(seed=0)

    labels = np.array([label for _, label in sample], dtype=np.int8)
    model_only = []
    hybrid = []
    for url, label in sample:
        result = model.score_url(url)
        model_only.append((label, int(result["model_risk"] >= PHISHING_THRESHOLD)))
        hybrid.append((label, int(result["risk"] >= PHISHING_THRESHOLD)))

    def report(predictions: List[Tuple[int, int]]) -> Dict:
        confusion = _confusion(predictions)
        values = _metric_values(confusion)
        predicted = np.array([prediction for _, prediction in predictions], dtype=np.int8)
        intervals = _bootstrap_ci(
            labels, predicted, replicates=bootstrap_replicates
        )
        return {
            **confusion,
            "precision": round(values["precision"], 3),
            "recall": round(values["recall"], 3),
            "f1": round(values["f1"], 3),
            "ci95": intervals,
        }

    return {
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "scipy": scipy.__version__,
            "tldextract": tldextract.__version__,
        },
        "datasets": {
            "phishing": {
                "name": "PhiLegit-100K",
                "version": PHILEGIT_VERSION,
                "doi": PHILEGIT_DOI,
                "license": "CC BY 4.0",
                "archive_sha256": PHILEGIT_SHA256,
            },
            "benign": {
                "name": "Tranco top 50,000",
                "list_id": TRANCO_LIST_ID,
                "created_on": TRANCO_CREATED,
                "license": (
                    "Research-oriented composite list; its source-provider terms "
                    "include CC BY 3.0, CC BY-SA 4.0, and CC BY-NC 4.0. "
                    "This evaluation is non-commercial research."
                ),
                "csv_sha256": TRANCO_SHA256,
            },
        },
        "split": (
            "Held-out evaluation only; no corpus row used for training or threshold "
            "selection. One deterministically selected phishing URL per PSL-aware "
            "registered domain; exclude all phishing domains present in Tranco; "
            "select the highest-ranked non-overlapping Tranco domains to match the "
            "phishing-domain count. Balanced case-control sample."
        ),
        "preprocessing": counts,
        "threshold": "Phishing when score >= 70; Suspicious (40-69) is not positive.",
        "confidence_intervals": {
            "method": "stratified percentile bootstrap over unique registered domains",
            "level": 0.95,
            "replicates": bootstrap_replicates,
            "seed": BOOTSTRAP_SEED,
        },
        "n": int(len(labels)),
        "model_only": report(model_only),
        "hybrid": report(hybrid),
        "url_visits": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir", type=Path, default=Path("data/real-data"),
        help="ignored directory for pinned raw data (default: data/real-data)",
    )
    parser.add_argument(
        "--download", action="store_true",
        help="download and verify the pinned public datasets before evaluation",
    )
    parser.add_argument(
        "--bootstrap-replicates", type=int, default=BOOTSTRAP_REPLICATES,
        help="number of deterministic bootstrap replicates (default: 2000)",
    )
    args = parser.parse_args()
    try:
        philegit_csv, tranco_csv = _ensure_dataset(args.data_dir, args.download)
        print(json.dumps(
            evaluate(philegit_csv, tranco_csv, args.bootstrap_replicates),
            indent=2,
        ))
    except (FileNotFoundError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print("real-data evaluation failed: {}".format(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
