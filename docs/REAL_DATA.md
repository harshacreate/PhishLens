# Real-data evaluation

## Result

The frozen PhishLens model was trained on its existing synthetic generator with seed 0. It was not trained or tuned on either evaluation source. The evaluation used the product's existing phishing threshold of 70 and never fetched a URL.

| Scorer | TP | FP | TN | FN | Precision (95% CI) | Recall (95% CI) | F1 (95% CI) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Model only | 13,300 | 194 | 32,948 | 19,842 | 0.986 (0.984–0.988) | 0.401 (0.396–0.407) | 0.570 (0.565–0.576) |
| Hybrid | 13,786 | 257 | 32,885 | 19,356 | 0.982 (0.980–0.984) | 0.416 (0.411–0.421) | 0.584 (0.579–0.590) |

These are case-control results, not operational rates. The balanced sample makes precision comparable between the two scorers but does not represent phishing prevalence, so its precision is not a production positive predictive value. The hybrid caught 486 more phishing domains and raised recall by 1.5 percentage points, while it also produced 63 more false alerts against the Tranco benign proxy.

## Sources and licenses

- Phishing URLs: [PhiLegit-100K, version 1](https://data.mendeley.com/datasets/726pyz4j53/1), DOI [10.17632/726pyz4j53.1](https://doi.org/10.17632/726pyz4j53.1), released under CC BY 4.0. The corpus combines PhiUSIIL and LegitPhish; its included README requires attribution to both source datasets. The pinned archive SHA-256 is d95a1419f4b2d1cb98c3ce31fedf7cdabd148f70f42e6ed3de6244366b525558.
- Benign-domain proxy: [Tranco list 947N2](https://tranco-list.eu/download/947N2/50000), the top 50,000 ranks from the list generated 2026-11-09 22:00:01 UTC. Its metadata records the 30-day period 2026-10-11 through 2026-11-09 and the providers CrUX, Farsight, Majestic, Cloudflare Radar, and Cisco Umbrella. Tranco describes the list as research-oriented; the provider terms include CC BY 3.0, CC BY-SA 4.0, and CC BY-NC 4.0, and Cisco Umbrella is available free of charge. This run is non-commercial research. The pinned CSV SHA-256 is 664b9c716992204d48f87c27a12dd08c9f77b4c468249dbdc57f10c3b52f70e2.

The Tranco list is a popularity ranking, not a clean benign label source. A popular domain can still host compromised content. The evaluation treats each selected Tranco domain's HTTPS homepage as a benign URL proxy without checking reachability, reputation, or page contents.

## Split and preprocessing

- Source labels: PhiLegit label 0 is phishing. The source contains 50,000 phishing URLs; no legitimate PhiLegit rows are used as benign examples.
- Domain grouping: use the Public Suffix List, including private suffixes, to derive registered domains. Keep one URL per phishing registered domain, chosen by lexicographically smallest URL. This reduces 50,000 source rows to 33,461 domains.
- Leakage control: remove 319 phishing domains present in Tranco. Select the highest-ranked 33,142 remaining unique Tranco registered domains as benign examples. Final evaluation: 33,142 phishing and 33,142 benign domains; 66,284 URLs total. There were no exact duplicate or malformed phishing URLs.
- Training and tuning: the complete corpus is held out for evaluation only. The logistic-regression model is fit only on the existing generated dataset with seed 0; neither dataset is used for training, validation, feature selection, or threshold selection.
- Labels and threshold: score 70 or above is positive for both scorers. Scores from 40 through 69 (“Suspicious”) count as negative.
- Uncertainty: two-sided percentile bootstrap, stratified by class over unique registered domains, 2,000 replicates, seed 20261111. These intervals describe resampling uncertainty within this corpus and do not account for source-label or benign-proxy errors.
- Network: evaluation downloads only the pinned source files. PhishLens does not resolve or visit any URL in either corpus.

The Public Suffix List implementation is pinned to tldextract 5.4.0. It uses the bundled suffix snapshot with network refresh disabled and includes private suffixes. To update the suffix data, deliberately upgrade the pinned package and rerun the PSL fixtures and real-data evaluation; updates do not happen at application runtime.

## Reproduction

From the repository root, with Python 3.12 and bsdtar available for the PhiLegit RAR archive:

    python -m pip install -r requirements-real-data.txt
    python -m phishlens.real_data --download --data-dir data/real-data

The downloader checks both pinned SHA-256 digests before scoring. The raw archive and Tranco CSV remain in the ignored data/real-data/ directory and are not committed.

The recorded run used Python 3.12.16, NumPy 2.0.2, SciPy 1.13.1, scikit-learn 1.6.1, and tldextract 5.4.0. The evaluator prints the environment, dataset provenance, exclusions, confusion matrices, metrics, and confidence intervals as JSON.

## Attribution

Mia, S., Bushra, J. J., & Tasnim, M. (2026). PhiLegit-100K, version 1. Mendeley Data. DOI: 10.17632/726pyz4j53.1. The corpus README cites Prasad & Chandra (2024), PhiUSIIL Phishing URL (Website), UCI Machine Learning Repository, and Potpelwar, Kulkarni, & Waghmare (2025), LegitPhish, Data in Brief 63, 111972.

Tranco list 947N2 was created 2026-11-09 and is cited by its permanent list ID.
