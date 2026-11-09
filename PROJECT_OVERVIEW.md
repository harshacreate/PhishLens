# PhishLens — Project Overview

**Sector:** Email/web security + applied ML · **Year 2 project**

## Summary
An explainable phishing analyzer: it turns a URL or email into interpretable
features, scores the phishing risk with a logistic-regression model, and explains
the verdict feature-by-feature. Optional, passive whois/DNS/TLS lookups add live
context on request.

## Real tools
- **whois** — domain age and registrar.
- **dig / dnspython** — DNS records and SPF/DMARC presence.
- **TLS (OpenSSL / ssl)** — certificate issuer, validity and TLS version.

## How it works
- `phishlens/features.py` — 16 interpretable URL features (shared train/serve).
- `phishlens/dataset.py` — synthetic URL generator -> labelled features (with noise).
- `phishlens/model.py` — standardised logistic regression + per-feature explanation.
- `phishlens/tools.py` — opt-in passive enrichment. `app.py` + `static/` — the UI.

## Run
```bash
docker compose up --build -d   # http://localhost:8102
```

## Scope
Offline on your input; live lookups opt-in and passive. ROC-AUC ~0.97 is a
synthetic benchmark, not real-world performance.
