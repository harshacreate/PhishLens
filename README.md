# PhishLens — Phishing URL & Email Analyzer

**Year:** 2 · **Stack:** Python (Flask) + HTML/CSS/JS + scikit-learn · **Tools:** whois · dig/dnspython · TLS (OpenSSL/ssl)

Paste a URL or a whole email and PhishLens extracts the phishing signals, scores
the risk with an **explainable** machine-learning model, and (on request) runs
live domain lookups. The model is trained on a bundled synthetic feature dataset.

## Features
- **Explainable risk score** — a logistic-regression model over 16 interpretable
  URL features; the UI shows *which* features drove the score.
- **Signal detection** — IP hosts, brand lookalikes, suspicious TLDs, `@`/redirect
  tricks, punycode homographs, shorteners, credential/urgency keywords.
- **Email mode** — paste an email; it pulls out URLs and flags urgency / credential
  requests / generic greetings.
- **Opt-in live enrichment** — whois (domain age), DNS incl. SPF/DMARC, and the
  TLS certificate. Passive lookups, off by default.
- **Risk gauge, indicator list, feature-contribution table, examples.**

## Tools used
| Tool | Where |
|------|-------|
| whois | domain age & registrar (young domains are a phishing signal) |
| dig / dnspython | DNS records + SPF/DMARC presence |
| TLS (OpenSSL / Python ssl) | certificate issuer, validity, TLS version |

## Run with Docker
```bash
docker compose up --build -d      # then open http://localhost:8102
docker compose down
```
Or double-click **Start.command** (macOS). Local: `make setup && make run`.

## Model quality (synthetic benchmark)
ROC-AUC ≈ 0.97 on a held-out split of the synthetic feature dataset — a measure of
the method on generated data, not of real-world phishing detection.

## Scope & safety
Offline analysis works on your pasted input only. Live lookups are **opt-in** and
**passive** (the same queries a browser/resolver makes); nothing is attacked.
