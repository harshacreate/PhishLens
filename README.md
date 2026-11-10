# PhishLens

**Explainable hybrid phishing-URL detection, with an honest out-of-template evaluation.**

Design Project II · Semester IV (2024–25) · B.Tech, specialisation in Cyber Security, DISC, Hindustan Institute of Technology and Science, Chennai · by **Malepati Sree Harsha**

![tests](https://img.shields.io/badge/tests-18%20passing-2ea44f) ![python](https://img.shields.io/badge/python-3.12-3776AB) ![docker](https://img.shields.io/badge/docker-compose-2496ED) ![license](https://img.shields.io/badge/license-MIT-blue) ![focus](https://img.shields.io/badge/focus-explainable%20ML-0f8f8a)

![PhishLens verdict](docs/screenshots/02-phishing-verdict.png)

PhishLens scores a URL, a pasted e-mail or a batch of links, and shows exactly which signals and features drove the score. It never opens the links it analyses. The project also asks the harder question: **does it work on attack styles it was never trained on?** On a pre-registered hold-out set, the model alone caught 1 in 10. A transparent hybrid caught 9 in 10 with no false alarms.

## Key results (measured)

| Result | Value |
|---|---|
| In-distribution F1, four models (synthetic, 2,400 URLs) | **0.962 – 0.970** (tie at the 3% label-noise ceiling) |
| Hold-out recall on out-of-template phishing, **model only** | **1 / 10** (shortcut learning) |
| Hold-out recall, **hybrid** (typosquat + combosquat signals, risk floor) | **9 / 10**, false positives **0 / 12** |
| Security fix | SSRF in TLS enrichment found and fixed (resolve once, refuse non-global IPs, connect to the vetted IP) |
| Automated tests | **18 / 18 passing** |
| Single-URL analysis under load | p50 5.3 ms · 1,391 req/s; `/api/metrics` cut from 240 ms to 3.8 ms by caching |

| Model | F1 | ROC-AUC | 5-fold AUC |
|---|---|---|---|
| Logistic Regression | 0.970 | 0.968 | 0.970 ± 0.007 |
| Decision Tree | 0.969 | 0.966 | 0.963 ± 0.008 |
| Random Forest | 0.962 | 0.964 | 0.973 ± 0.008 |
| Gaussian Naive Bayes | 0.970 | 0.969 | 0.970 ± 0.005 |

![Out-of-template recall](docs/diagrams/chart-probes.png)

The hold-out probe set (10 phishing, 12 benign) was written *before* the hybrid was designed and never used for tuning. It is small, so treat the result as indicative. All data are synthetic or illustrative; no claim is made about real-world detection rates.

## Features

- **16 interpretable URL features** and human-readable rule signals (IP host, punycode, `@` trick, suspicious TLD, shortener, redirect, brand look-alike, keywords …).
- **Exact explanations:** logistic regression; each feature's contribution = coefficient × standardised value.
- **Typosquat and combosquat detection** (`paypa1`, `linkedln`, `hdfc-netbanking-kyc-update`).
- **Hybrid scoring:** a high-severity signal sets a risk floor of 75; the model's own score is always shown alongside.
- **E-mail cues:** urgency, credential/payment requests, generic greetings.
- **Batch mode** (≤ 25 URLs), JSON export, print view.
- **Model study:** logistic regression vs decision tree vs random forest vs naive Bayes, confusion matrices, 5-fold CV.
- **Opt-in passive enrichment:** WHOIS, A/MX/SPF/DMARC and TLS certificate, only for domains you confirm you are authorized to check.

## Architecture

![Architecture](docs/diagrams/architecture.png)

## Quick start

```bash
docker compose up --build -d
open http://localhost:8102
```

```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
make test       # 18 tests
make evaluate   # held-out metrics
make compare    # four-model study
make probes     # out-of-template evaluation (dev + hold-out)
make run        # http://127.0.0.1:8000
```

## Security

The analysed URL is never fetched. Enrichment requires an explicit authorization flag, accepts only public DNS names, and refuses names that resolve to loopback, private or metadata addresses (SSRF). It also has an audit log and a rate limit. Strict CSP, OWASP headers, no-store API responses and body-free logs apply throughout. See [SECURITY.md](SECURITY.md).

## Documentation

| Document | |
|---|---|
| [Project report (PDF)](report/PhishLens_Project_Report.pdf) · [Word](report/PhishLens_Project_Report.docx) | IEEE-style report: literature survey, SRS, UML/DFD, implementation, testing, results, references |
| [Presentation (PowerPoint)](report/PhishLens_Presentation.pptx) · [PDF](report/PhishLens_Presentation.pdf) | Review / viva slides with speaker notes |
| [Synopsis](report/PhishLens_Synopsis.pdf) | Two-page project synopsis |
| [Demo script](report/Demo_Script.md) | Timed live-demonstration walkthrough |
| [Viva questions](report/Viva_Questions.md) | Likely examiner / interviewer questions with answers |
| [Portfolio copy](report/Portfolio_Copy.md) | GitHub description, LinkedIn and resume text |
| [Showcase page](docs/index.html) | Landing page for GitHub Pages (Settings → Pages → `main` / `docs`) |
| [Security policy](SECURITY.md) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) | Threat model, disclosure process, workflow, history |

## Limitations and roadmap

- Synthetic training data; small probe sets. Next: a licensed corpus with a time-based split and confidence intervals.
- The registered domain is approximated by the last two labels. Next: the Public Suffix List.
- Brandless lures on free web hosting are still missed (1 hold-out miss).
- Fixed brand list (20). Next: learn brands from certificate-transparency logs.

## Repository layout

```
├── .dockerignore
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── Makefile
├── PROJECT_OVERVIEW.md
├── README.md
├── SECURITY.md
├── Start.command
├── docker-compose.yml
├── docs/
│   ├── README.md
│   ├── diagrams/  (12 images)
│   ├── index.html
│   └── screenshots/  (7 images)
├── phishlens/
│   ├── __init__.py
│   ├── app.py
│   ├── compare.py
│   ├── data/
│   ├── dataset.py
│   ├── evaluate.py
│   ├── features.py
│   ├── model.py
│   ├── probes.py
│   ├── static/
│   │   └── index.html
│   ├── tools.py
│   └── web_security.py
├── requirements.txt
├── scripts/
│   └── loadtest.py
└── tests/
    ├── test_phishlens.py
    └── test_security.py
```

## License

MIT, see [LICENSE](LICENSE).
