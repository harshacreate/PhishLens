"""Out-of-template probe sets: does the model generalise beyond its generator?

The classifier is trained and tested on URLs produced by ``dataset.py``. Scoring
well there only proves it learned the generator's templates. These probes are
hand-written URLs built with tricks the generator never produces (typosquats,
combosquats on ordinary TLDs, punycode on .com, real login pages of the brands).

* ``DEV_PROBES`` were written first and used for error analysis; the typosquat /
  combosquat signals and the hybrid floor were designed after looking at them,
  so results on this set are optimistic by construction.
* ``HOLDOUT_PROBES`` were written *before* that design work and never used for
  tuning. They are the honest generalisation estimate.

All URLs are illustrative strings for offline scoring; PhishLens never visits them.
The phishing examples use made-up domains and documentation IP ranges.

Usage: ``python -m phishlens.probes`` (prints JSON).
"""

from __future__ import annotations

import json
import warnings
from typing import Dict, List, Tuple

warnings.filterwarnings("ignore")

Probe = Tuple[str, int]          # (url, label) with 1 = phishing

DEV_PROBES: List[Probe] = [(u, 1) for u in [
    "http://xn--pypal-4ve.com/signin",
    "http://paypa1-secure-login.com/verify",
    "https://secure-login.microsoftonline-support.com/auth",
    "http://appleid.apple.com.verify-session.net/login",
    "http://198.51.100.23/owa/login",
    "http://accounts-google.com.account-recovery.info/",
    "https://hdfc-netbanking-kyc-update.in/",
    "http://www.amaz0n-orders.co/track",
    "http://login.wellsfargo.secure-alerts.online/",
    "https://dhl-parcel-redelivery.com/pay",
]] + [(u, 0) for u in [
    "https://accounts.google.com/signin",
    "https://www.paypal.com/signin",
    "https://login.microsoftonline.com/",
    "https://appleid.apple.com/",
    "https://netbanking.hdfcbank.com/netbanking/",
    "https://www.linkedin.com/login",
    "https://github.com/login",
    "https://en.wikipedia.org/wiki/Phishing",
    "https://www.irctc.co.in/nget/train-search",
    "https://mail.google.com/mail/u/0/",
]]

HOLDOUT_PROBES: List[Probe] = [(u, 1) for u in [
    "http://instagram-copyright-appeal.com/form",
    "https://faceb00k-security.net/checkpoint",
    "http://www.linkedln.com/uas/login",
    "https://coinbase.wallet-sync.io/connect",
    "http://203.0.113.77/icici/login.php",
    "https://sbi-yono-rewards.in/claim",
    "http://secure-account-update.weebly.com/",
    "https://netflix-billing-help.com/update",
    "http://xn--fcebook-8va.com/login",
    "https://microsoft-365-login.web.app/",
]] + [(u, 0) for u in [
    "https://www.instagram.com/accounts/login/",
    "https://www.facebook.com/login.php",
    "https://www.linkedin.com/feed/",
    "https://www.coinbase.com/signin",
    "https://www.icicibank.com/personal-banking",
    "https://www.onlinesbi.sbi/",
    "https://www.netflix.com/browse",
    "https://outlook.office.com/mail/",
    "https://www.python.org/downloads/",
    "https://stackoverflow.com/questions/tagged/security",
    "https://en.wikipedia.org/wiki/PayPal",
    "https://github.com/paypal",
]]


def _confusion(model, probes: List[Probe], key: str) -> Dict:
    tp = fp = tn = fn = 0
    misses: List[Dict] = []
    for url, label in probes:
        result = model.score_url(url)
        flagged = 1 if result[key] >= 40 else 0          # Suspicious or Phishing
        if flagged and label:
            tp += 1
        elif flagged and not label:
            fp += 1
            misses.append({"url": url, "expected": "benign", key: result[key]})
        elif label:
            fn += 1
            misses.append({"url": url, "expected": "phishing", key: result[key]})
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "precision": round(precision, 3),
            "recall": round(recall, 3), "fpr": round(fpr, 3), "f1": round(f1, 3),
            "precision_ci95": _wilson_interval(tp, tp + fp),
            "recall_ci95": _wilson_interval(tp, tp + fn),
            "fpr_ci95": _wilson_interval(fp, fp + tn), "errors": misses}


def _wilson_interval(successes: int, trials: int, z: float = 1.959963984540054):
    """Return a two-sided 95% Wilson score interval, including zero successes."""
    if trials <= 0:
        return None
    proportion = successes / trials
    z_squared = z * z
    denominator = 1 + z_squared / trials
    center = (proportion + z_squared / (2 * trials)) / denominator
    margin = (
        z
        * ((proportion * (1 - proportion) / trials + z_squared / (4 * trials * trials)) ** 0.5)
        / denominator
    )
    return [round(max(0.0, center - margin), 3), round(min(1.0, center + margin), 3)]


def evaluate(model=None) -> Dict:
    from phishlens.model import PhishModel
    model = model or PhishModel.train(seed=0)
    out = {
        "threshold": "flagged when score >= 40 (Suspicious or Phishing)",
        "interval_method": "two-sided 95% Wilson score intervals; descriptive for these small probe sets",
    }
    for name, probes in (("dev", DEV_PROBES), ("holdout", HOLDOUT_PROBES)):
        out[name] = {"n": len(probes),
                     "model_only": _confusion(model, probes, "model_risk"),
                     "hybrid": _confusion(model, probes, "risk")}
    return out


def main():
    print(json.dumps(evaluate(), indent=2))


if __name__ == "__main__":
    main()
