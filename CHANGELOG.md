# Change log

This page lists the main changes to PhishLens.

## [1.1.0] - Not released yet

This version is ready for review. Add its release tag after review and merge.

### Security

- Fixed a server side request forgery (SSRF) bug in the TLS check. Before, a domain that looked public could point to a private or system address, and the app might connect to it. The app now looks up the address once, refuses any address that is not public, and makes the TLS connection to the checked address. Code: tools.resolve_public. Test: test_tls_check_refuses_names_that_resolve_to_internal_addresses.

### Added and changed

- Added test links with patterns that were not in the training data in phishlens/probes.py and make probes. The added checks look for misspelled brand names, extra words added to brand names, and strong warning signs. In the saved test, the model alone found 1 of 10 phishing links. The model with the extra checks found 9 of 10 and marked none of 12 safe test links as phishing.
- Saved the /api/metrics result. A load test showed that each call took 240 ms. It now takes about 4 ms.
- Added a model comparison in phishlens/compare.py, at GET /api/compare, from make compare and in the Model Study screen. It compares logistic regression, decision tree, random forest, and Gaussian naive Bayes. It shows result tables and tests each model on five parts of the data.
- Added web_security.py for CSP and OWASP security headers, request IDs, access logs without request bodies, a record for each allowed data check, JSON error replies, and request limits.
- Added security tests in tests/test_security.py and a test for the model comparison.
- Fixed the space around the logo in the menu and made phone tap areas 44 pixels high.
- Added the report, slides, short report, diagrams, demo steps, interview questions, and project page.
- Changed domain checks to use saved Public Suffix List data from the fixed tldextract package. The app does not download updates while it runs.
- Added a repeatable test with public data from PhiLegit-100K v1 and Tranco 947N2. It removes repeated domains, lists removed rows, checks file hashes, and shows result ranges from grouped samples.
- Added result ranges for the made-up link tests. These results stay separate from the public data results.

## [1.0.0] - 2026-11-10

### Added

- First full release. It includes a Flask API, a dashboard, links to outside tools, a Docker image and Compose file, tests, and GitHub Actions checks.
