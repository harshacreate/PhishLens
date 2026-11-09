"""Explainable phishing classifier (standardised logistic regression).

Logistic regression is chosen for transparency: each feature's standardised
coefficient times its value is that feature's contribution to the risk score, so
the UI can show WHY a URL was flagged. The model trains in milliseconds and is
built once at app startup.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from phishlens.dataset import make_dataset
from phishlens.features import FEATURE_NAMES, extract, vector_list


@dataclass
class PhishModel:
    scaler: StandardScaler
    clf: LogisticRegression

    @classmethod
    def train(cls, seed: int = 0) -> "PhishModel":
        X, y, _ = make_dataset(seed=seed)
        scaler = StandardScaler().fit(X)
        clf = LogisticRegression(max_iter=1000, C=1.0).fit(scaler.transform(X), y)
        return cls(scaler, clf)

    def score_url(self, url: str) -> Dict:
        feat = extract(url)
        x = np.array(vector_list(feat), dtype=float).reshape(1, -1)
        xs = self.scaler.transform(x)
        proba = float(self.clf.predict_proba(xs)[0, 1])
        # Per-feature contribution to the log-odds (coef * standardised value).
        contrib = (self.clf.coef_[0] * xs[0])
        order = np.argsort(-np.abs(contrib))
        drivers = [{
            "feature": FEATURE_NAMES[i],
            "value": feat["vector"][FEATURE_NAMES[i]],
            "contribution": round(float(contrib[i]), 3),
            "direction": "raises" if contrib[i] > 0 else "lowers",
        } for i in order[:6] if abs(contrib[i]) > 0.01]
        verdict = "Phishing" if proba >= 0.7 else ("Suspicious" if proba >= 0.4 else "Likely safe")
        return {
            "url": url, "host": feat["host"], "registered_domain": feat["registered_domain"],
            "risk": round(proba * 100, 1), "verdict": verdict,
            "signals": [{"text": t, "severity": s} for t, s in feat["signals"]],
            "drivers": drivers,
            "features": feat["vector"],
        }

    def evaluate(self, seed: int = 1) -> Dict:
        from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score
        X, y, _ = make_dataset(seed=seed + 50)
        proba = self.clf.predict_proba(self.scaler.transform(X))[:, 1]
        pred = (proba >= 0.5).astype(int)
        return {
            "roc_auc": round(float(roc_auc_score(y, proba)), 3),
            "precision": round(float(precision_score(y, pred)), 3),
            "recall": round(float(recall_score(y, pred)), 3),
            "f1": round(float(f1_score(y, pred)), 3),
            "n": int(len(y)),
        }
