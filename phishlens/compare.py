"""Compare candidate classifiers on the same synthetic URL features.

Usage: ``python -m phishlens.compare`` (prints JSON). The production model stays
logistic regression because each prediction can be decomposed into per-feature
contributions; this script records what that transparency costs (or doesn't)
against less interpretable models trained on identical data.
"""

from __future__ import annotations

import json
import time
import warnings
from typing import Dict

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from phishlens.dataset import make_dataset

warnings.filterwarnings("ignore")

CANDIDATES = {
    "Logistic Regression": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "Decision Tree": lambda: DecisionTreeClassifier(max_depth=6, random_state=0),
    "Random Forest": lambda: RandomForestClassifier(n_estimators=150, random_state=0),
    "Gaussian Naive Bayes": lambda: GaussianNB(),
}
INTERPRETABLE = {"Logistic Regression": "per-feature contributions",
                 "Decision Tree": "readable rule path",
                 "Random Forest": "global importances only",
                 "Gaussian Naive Bayes": "per-feature likelihoods"}


def compare(train_seed: int = 5, test_seed: int = 51) -> Dict:
    X_train, y_train, _ = make_dataset(seed=train_seed)
    X_test, y_test, _ = make_dataset(seed=test_seed)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    rows = []
    for name, factory in CANDIDATES.items():
        start = time.perf_counter()
        model = factory().fit(X_train, y_train)
        train_ms = (time.perf_counter() - start) * 1000
        proba = model.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
        cv_scores = cross_val_score(factory(), X_train, y_train, cv=cv, scoring="roc_auc")
        rows.append({
            "model": name,
            "accuracy": round(float(accuracy_score(y_test, pred)), 3),
            "precision": round(float(precision_score(y_test, pred)), 3),
            "recall": round(float(recall_score(y_test, pred)), 3),
            "f1": round(float(f1_score(y_test, pred)), 3),
            "roc_auc": round(float(roc_auc_score(y_test, proba)), 3),
            "cv_auc_mean": round(float(np.mean(cv_scores)), 3),
            "cv_auc_std": round(float(np.std(cv_scores)), 3),
            "confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
            "train_ms": round(train_ms, 1),
            "explainability": INTERPRETABLE[name],
        })
    return {"dataset": "synthetic generated URL features (3% label noise)",
            "train_seed": train_seed, "test_seed": test_seed,
            "n_train": int(len(y_train)), "n_test": int(len(y_test)), "results": rows}


def main():
    print(json.dumps(compare(), indent=2))


if __name__ == "__main__":
    main()
