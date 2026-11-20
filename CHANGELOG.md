# Change log

This page lists the main PhishLens changes. It uses the [Keep a Changelog format](https://keepachangelog.com/en/1.1.0/). Version numbers use [SemVer](https://semver.org/).

## [1.1.0] - Not released yet

This version is ready for review. Add its release tag after the review and merge.

### Security

- Fixed a server-side request forgery (SSRF) problem in the TLS check. Before the fix, a domain that looked public could point to a private or system address, and the app would connect to it. The app now looks up the address once, rejects addresses that are not public, and makes the TLS connection to the checked address. Code: tools.resolve_public. Test: test_tls_check_refuses_names_that_resolve_to_internal_addresses.

### Added and changed

- Added test URLs with patterns outside the training data in phishlens/probes.py and make probes. Added a combined score for misspelled brand names, brand names joined to extra words, and serious rule signals. On the saved test set, recall rose from 1 out of 10 to 9 out of 10, with no false alerts on 12 safe test URLs.
- Saved the /api/metrics result after a load test showed that each call took 240 ms. It now takes about 4 ms.
- Added a model comparison in phishlens/compare.py, at GET /api/compare, from make compare and in the Model Study screen. It compares logistic regression, decision tree, random forest and Gaussian naive Bayes. It shows result tables and tests each model over five parts of the data.
- Added web_security.py for CSP and OWASP security headers, request IDs, access logs with no request bodies, a record for each allowed data check, JSON errors and request limits.
- Added security tests in tests/test_security.py and a test for the model comparison.
- Fixed the space around the logo in the menu and made small-screen tap areas 44 pixels tall.
- Added the report, slides, short report, diagrams, demo script and interview notes under report/. Added the project page under docs/.
- Changed domain checks to use the saved Public Suffix List data from the fixed tldextract package. The app does not download list updates while it runs.
- Added a repeatable test with public data from PhiLegit-100K v1 and Tranco 947N2. It removes repeated domains, lists removed rows, checks file hashes and shows confidence ranges from grouped samples.
- Added confidence ranges for the made-up URL tests. The results from those small tests are kept separate from the real-data results.

## [1.0.0] - 2026-11-10

### Added

- First full release. It has a Flask API, a working dashboard, links to outside tools, a Docker image and Compose file, unit tests and GitHub Actions checks.
