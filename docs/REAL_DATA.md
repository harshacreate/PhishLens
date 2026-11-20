# PhishLens test with public links

## Results

The model was trained only on made-up links, using seed 0. The two public data sets below were saved for this test only. They were not used to train or adjust the model. A score of 70 or more counted as phishing. PhishLens did not look up or open any test link.

| Check | Phishing links found | Safe links marked as phishing | Safe links left alone | Phishing links missed | Precision (95% range) | Recall (95% range) | F1 (95% range) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Model only | 13,300 | 194 | 32,948 | 19,842 | 0.986 (0.984 to 0.988) | 0.401 (0.396 to 0.407) | 0.570 (0.565 to 0.576) |
| Model and extra rules | 13,786 | 257 | 32,885 | 19,356 | 0.982 (0.980 to 0.984) | 0.416 (0.411 to 0.421) | 0.584 (0.579 to 0.590) |

Precision shows how often a phishing result was right. Recall shows how many phishing links were found. F1 is one score that combines both. The test used the same number of phishing and safe examples. This makes it possible to compare the two checks, but it does not match real use. Phishing links are much less common in real life, so the precision here does not show what it would be in real use.

The extra rules found 486 more phishing domains and raised recall by 1.5 points. They also gave 63 more wrong alerts on the Tranco popular-site list. This test does not show how the checker will work on every link.

## Data sources and licenses

- Phishing links: [PhiLegit-100K, version 1](https://data.mendeley.com/datasets/726pyz4j53/1), DOI [10.17632/726pyz4j53.1](https://doi.org/10.17632/726pyz4j53.1). It uses CC BY 4.0 and combines PhiUSIIL and LegitPhish. Its README asks users to credit both sources. The saved archive SHA-256 is d95a1419f4b2d1cb98c3ce31fedf7cdabd148f70f42e6ed3de6244366b525558.
- Popular sites: [Tranco list 947N2](https://tranco-list.eu/download/947N2/50000). It is a list of the top 50,000 domains, made at 2026-11-09 22:00:01 UTC. It covers 2026-10-11 to 2026-11-09 and uses CrUX, Farsight, Majestic, Cloudflare Radar, and Cisco Umbrella. Tranco says the list is for research. The source terms include CC BY 3.0, CC BY-SA 4.0, and CC BY-NC 4.0. Cisco Umbrella is free to use. This test is non-commercial research. The saved CSV SHA-256 is 664b9c716992204d48f87c27a12dd08c9f77b4c468249dbdc57f10c3b52f70e2.

Tranco ranks popular domains. It does not prove that a site is safe; a popular site may be hacked. For this test, each chosen domain's HTTPS home page was treated as safe. The test did not check whether the site worked or what it showed.

## How the test data was made

- In PhiLegit, label 0 means phishing. I used its 50,000 phishing links and did not use its safe links.
- I used the Public Suffix List, a list of domain endings, to find the main registered name for each link. I kept one link for each phishing domain: the link that came first in letter order. This cut 50,000 links down to 33,461 domains.
- I removed 319 phishing domains that were also in Tranco. Then I picked the top-ranked 33,142 Tranco domains left. The final test has 33,142 phishing domains and 33,142 popular domains, or 66,284 links. No phishing links were repeated or broken.
- The test data was not used to train the model, choose link details, or choose the score limit. The model was fit only on made-up links with seed 0.
- Scores of 70 or more counted as phishing. Scores from 40 to 69 counted as not phishing for this test.
- I made two-sided 95% ranges from 2,000 repeat samples, using seed 20261111. Each sample kept the two groups separate and picked by class and main domain name. These ranges show changes within this saved test. They do not include mistakes in the source labels or in treating popular sites as safe.
- The Public Suffix List code uses tldextract 5.4.0 and its saved domain list. It does not download updates while the app runs. To update the list, change the pinned package on purpose, then run the suffix tests and this test again.

## Run the test again

Use Python 3.12 and install bsdtar to read the PhiLegit RAR file. From the project folder, run:

    python -m pip install -r requirements-real-data.txt
    python -m phishlens.real_data --download --data-dir data/real-data

The download checks both saved SHA-256 values before scoring the links. The archive and Tranco file stay in the ignored data/real-data/ folder and are not saved in Git.

The saved run used Python 3.12.16, NumPy 2.0.2, SciPy 1.13.1, scikit-learn 1.6.1, and tldextract 5.4.0. The tool prints the software versions, source details, removed rows, result tables, scores, and ranges as JSON.

## Credit

Mia, S., Bushra, J. J., & Tasnim, M. (2026). PhiLegit-100K, version 1. Mendeley Data. DOI: 10.17632/726pyz4j53.1. The data README credits Prasad & Chandra (2024), PhiUSIIL Phishing URL (Website), UCI Machine Learning Repository, and Potpelwar, Kulkarni, & Waghmare (2025), LegitPhish, Data in Brief 63, 111972.

Tranco list 947N2 was made on 2026-11-09. Use its list ID when citing it.
