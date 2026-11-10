# PhishLens — project overview

**Course:** Design Project II · Semester IV · 2024–25 · **Author:** Malepati Sree Harsha · **Focus:** phishing signals and explainable triage

## Goal

Inspect pasted links and email text offline, display the features behind a synthetic-data risk estimate, and let a user request passive domain enrichment only after confirming authorization.

## Components

- `phishlens/features.py` — URL parser, signal rules, and numeric feature vector.
- `phishlens/dataset.py` — fixed-seed generator for synthetic benign/phishing-shaped URL features.
- `phishlens/model.py` — standardized logistic regression, feature drivers, and held-out metrics.
- `phishlens/tools.py` — time-bounded WHOIS, DNS, and OpenSSL adapters with public-domain validation.
- `phishlens/app.py` — Flask endpoints for single, batch, metrics, and authorized enrichment.
- `phishlens/static/index.html` — interactive dashboard with risk gauge, model card, batch results, and report export.

## Data and scope

Training and evaluation samples are generated locally from deterministic templates; they are not an external phishing corpus. Offline analysis does not fetch URLs. Enrichment is optional, passive, and requires an authorization confirmation.

## Run and verify

```bash
docker compose up --build -d
make test
make evaluate
```

Open `http://localhost:8102`. See the main README for assumptions and limitations.
