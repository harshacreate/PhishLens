# PhishLens — portfolio copy

## GitHub
**Description:** Explainable phishing-URL analyser with an honest generalisation study: logistic regression with exact per-feature contributions, 4-model comparison, pre-registered out-of-template probes, typosquat/combosquat signals and a hybrid risk floor (hold-out recall 1/10 → 9/10, 0 FP). SSRF-safe opt-in WHOIS/DNS/TLS. Flask · Docker.

**Topics:** `cybersecurity` `phishing-detection` `machine-learning` `explainable-ai` `scikit-learn` `typosquatting` `ssrf` `flask` `docker` `python`

## LinkedIn — Projects section
**PhishLens — Explainable Phishing Detection with Out-of-Template Evaluation**
Built a local phishing-URL/e-mail analyser whose every verdict shows its signals and exact feature contributions. Four classifiers tied at ~97% F1 in-distribution — but on a pre-registered hold-out set of unseen attack styles the model alone caught only 1/10. Adding typosquat/combosquat detection and a hybrid risk floor raised recall to 9/10 with 0 false positives. Security review also found and fixed an SSRF in the TLS enrichment path. 18 automated tests, Docker, CI.
*Skills:* Python · Machine Learning · scikit-learn · Threat Modelling · Secure Coding · Flask · Docker

## Resume bullets
- Built **PhishLens**, an explainable phishing analyser (16 URL features, logistic regression with per-feature attributions) in Flask/Docker; benchmarked against 3 other models with 5-fold CV.
- Designed a pre-registered out-of-template evaluation exposing shortcut learning (hold-out recall **1/10**); a hybrid of typosquat/combosquat rules and a risk floor raised it to **9/10 with 0 false positives**.
- Found and fixed an **SSRF** in TLS enrichment (resolve-once, refuse non-global IPs, connect to vetted IP); covered by tests among 18 pytest cases; cut a hot endpoint from 240 ms to 4 ms after load testing.
