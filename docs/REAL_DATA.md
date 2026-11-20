# PhishLens real-data test

## Results

The model was trained on generated data with seed 0. The two data sets below were saved for testing only. They were not used to train or tune the model. The test used the app's phishing score limit of 70. PhishLens did not open or look up any test URL.

| Scorer | TP | FP | TN | FN | Precision (95% CI) | Recall (95% CI) | F1 (95% CI) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Model only | 13,300 | 194 | 32,948 | 19,842 | 0.986 (0.984–0.988) | 0.401 (0.396–0.407) | 0.570 (0.565–0.576) |
| Hybrid | 13,786 | 257 | 32,885 | 19,356 | 0.982 (0.980–0.984) | 0.416 (0.411–0.421) | 0.584 (0.579–0.590) |

The test has the same number of phishing and safe examples. This lets us compare the two scorers, but it does not match how often phishing appears in real use. The precision values here are not real-world precision. The hybrid found 486 more phishing domains and raised recall by 1.5 percentage points. It also gave 63 more false alerts on the Tranco safe-site list.

## Data sources and licenses

- Phishing URLs: [PhiLegit-100K, version 1](https://data.mendeley.com/datasets/726pyz4j53/1), DOI [10.17632/726pyz4j53.1](https://doi.org/10.17632/726pyz4j53.1). It uses CC BY 4.0. It combines PhiUSIIL and LegitPhish. Its README asks users to credit both sources. The saved archive SHA-256 is d95a1419f4b2d1cb98c3ce31fedf7cdabd148f70f42e6ed3de6244366b525558.
- Safe-site list: [Tranco list 947N2](https://tranco-list.eu/download/947N2/50000). This is the top 50,000 domains in the list made at 2026-11-09 22:00:01 UTC. It covers 2026-10-11 through 2026-11-09 and uses CrUX, Farsight, Majestic, Cloudflare Radar and Cisco Umbrella. Tranco says the list is for research. The source terms include CC BY 3.0, CC BY-SA 4.0 and CC BY-NC 4.0. Cisco Umbrella is free to use. This test is non-commercial research. The saved CSV SHA-256 is 664b9c716992204d48f87c27a12dd08c9f77b4c468249dbdc57f10c3b52f70e2.

Tranco ranks popular domains. It does not prove that a site is safe; a popular site may be hacked. For this test, each chosen domain's HTTPS home page is treated as a safe URL. The test does not check if the site works, is known to be safe, or what it shows.

## How the test set was made

- In PhiLegit, label 0 means phishing. It has 50,000 phishing URLs. No legitimate PhiLegit rows were used as safe examples.
- The Public Suffix List, including private suffixes, was used to find registered domains. One URL was kept for each phishing domain: the URL that comes first in letter order. This reduced 50,000 URLs to 33,461 domains.
- We removed 319 phishing domains that also appeared in Tranco. We then chose the 33,142 highest-ranked Tranco domains left. The final set has 33,142 phishing domains and 33,142 safe domains, or 66,284 URLs. There were no repeated or broken phishing URLs.
- The whole test set was kept out of model training and tuning. The logistic regression model was fit only on the generated data with seed 0. The test data was not used to train the model, pick features, or choose a score limit.
- A score of 70 or more means positive for both scorers. Scores from 40 to 69 mean “Suspicious” and count as negative here.
- We made two-sided 95% confidence intervals with 2,000 bootstrap samples. We sampled each group by class and registered domain, using seed 20261111. These ranges show variation within this test set. They do not cover mistakes in the source labels or the safe-site list.
- The test only downloads the saved source files. PhishLens does not look up or visit any URL in either data set.

The Public Suffix List code uses tldextract 5.4.0 and its saved suffix list. Network updates are turned off. To update this list, upgrade the pinned package on purpose, then run the suffix tests and this evaluation again. The app does not update it while running.

## Run the test again

From the project folder, use Python 3.12 and install bsdtar to read the PhiLegit RAR archive. Then run:

    python -m pip install -r requirements-real-data.txt
    python -m phishlens.real_data --download --data-dir data/real-data

The download step checks both saved SHA-256 values before scoring the data. The archive and Tranco file stay in the ignored data/real-data/ folder and are not saved in Git.

The saved run used Python 3.12.16, NumPy 2.0.2, SciPy 1.13.1, scikit-learn 1.6.1 and tldextract 5.4.0. The tool prints the software versions, source details, removed rows, result tables, scores and confidence ranges as JSON.

## Credit

Mia, S., Bushra, J. J., & Tasnim, M. (2026). PhiLegit-100K, version 1. Mendeley Data. DOI: 10.17632/726pyz4j53.1. The data README credits Prasad & Chandra (2024), PhiUSIIL Phishing URL (Website), UCI Machine Learning Repository, and Potpelwar, Kulkarni, & Waghmare (2025), LegitPhish, Data in Brief 63, 111972.

Tranco list 947N2 was made on 2026-11-09. Use its list ID when citing it.
