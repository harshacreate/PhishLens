# Changelog

All notable changes to PhishLens are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

## [1.1.0] - Unreleased (prepared; tag after review and merge)

### Security
- Fixed an SSRF gap in the TLS enrichment check: a public-looking name that resolved to a loopback, private or metadata address was previously contacted. Names are now resolved once, non-global answers are refused, and OpenSSL connects to the vetted IP (`tools.resolve_public`, test `test_tls_check_refuses_names_that_resolve_to_internal_addresses`).

### Added / changed
- Out-of-template probe sets (`phishlens/probes.py`, `make probes`) and hybrid scoring: typosquat and combosquat signals plus a risk floor for high-severity rule signals; hold-out recall rose from 1/10 (model only) to 9/10 with 0/12 false positives.
- `/api/metrics` result cached after load testing showed 240 ms per call (now ~4 ms).
- Model comparison study (`phishlens/compare.py`, `GET /api/compare`, `make compare`, UI section *Model study*): logistic regression vs decision tree vs random forest vs Gaussian naive Bayes with confusion matrices and 5-fold cross-validation.
- HTTP hardening layer (`web_security.py`): CSP and OWASP security headers, request IDs, structured access logs without bodies, audit log line for every authorized enrichment, JSON errors, rate limits.
- Security test suite (`tests/test_security.py`) and comparison test.
- Fixed navbar spacing next to the logo; 44 px touch targets on small screens.
- Academic report, presentation, synopsis, diagrams, demo script and viva notes under `report/`; showcase page under `docs/`.
- Registered-domain features now use the bundled Public Suffix List data through pinned `tldextract` with network suffix updates disabled.
- Added a reproducible public-data evaluation using PhiLegit-100K v1 and Tranco 947N2, with domain-level deduplication, exclusions, checksums, and stratified bootstrap confidence intervals.
- Added confidence intervals to the synthetic out-of-template probe metrics; the hybrid's small-probe recall remains explicitly separate from real-data recall.

## [1.0.0] - 2026-11-10

### Added
- First complete release: Flask API, interactive dashboard, external tool integrations,
  Docker image and Compose file, unit tests and GitHub Actions CI.
