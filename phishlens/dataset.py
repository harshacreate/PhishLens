"""Synthetic URL generator -> labelled feature dataset for training.

Benign and phishing URLs are generated from templates that mirror real-world
patterns, then run through the SAME feature extractor used at serve time. This is
synthetic training data for demonstrating the method, not a real phishing corpus.
"""

from __future__ import annotations

import random
from typing import List, Tuple

import numpy as np

from phishlens.features import BRANDS, FEATURE_NAMES, SUSPICIOUS_TLDS, extract, vector_list

_GOOD_TLDS = ["com", "org", "net", "io", "co", "in", "edu", "gov"]
_GOOD_PATHS = ["", "/", "/home", "/products", "/about", "/blog/post", "/help", "/pricing", "/account/settings"]
_WORDS = ["cloud", "shop", "news", "store", "studio", "labs", "market", "hub", "works", "mail"]


def _benign(rng: random.Random) -> str:
    base = rng.choice(sorted(BRANDS) + _WORDS)
    tld = rng.choice(_GOOD_TLDS)
    host = rng.choice(["www.", "", "shop.", "blog."]) + base + "." + tld
    scheme = "https://" if rng.random() > 0.08 else "http://"     # a few benign on http
    path = rng.choice(_GOOD_PATHS)
    if rng.random() < 0.18:                                       # mild overlap: a benign keyword path
        path = rng.choice(["/account/settings", "/login", "/secure/profile"])
    return scheme + host + path


def _phish(rng: random.Random) -> str:
    brand = rng.choice(sorted(BRANDS))
    style = rng.randint(0, 6)
    kw = rng.choice(["login", "verify", "account", "secure-update", "confirm", "billing"])
    if style == 0:                                   # brand lookalike on bad TLD
        return "http://%s-%s.%s/%s" % (brand, kw, rng.choice(sorted(SUSPICIOUS_TLDS)), kw)
    if style == 1:                                   # brand as subdomain of junk
        return "http://%s.com.%s%d.%s/%s" % (brand, rng.choice(_WORDS), rng.randint(1, 99),
                                             rng.choice(sorted(SUSPICIOUS_TLDS)), kw)
    if style == 2:                                   # IP host
        ip = ".".join(str(rng.randint(1, 254)) for _ in range(4))
        return "http://%s/%s/%s" % (ip, "secure", kw)
    if style == 3:                                   # @ redirect trick
        return "https://%s.com@%s.%s/%s" % (brand, rng.choice(_WORDS), rng.choice(sorted(SUSPICIOUS_TLDS)), kw)
    if style == 4:                                   # punycode homograph
        return "http://xn--%s-9ca.%s/%s" % (brand, rng.choice(sorted(SUSPICIOUS_TLDS)), kw)
    if style == 5:                                   # long hyphenated keyword host
        return "http://%s-%s-%s-%s.%s/%s" % (brand, "account", "security", "update",
                                             rng.choice(sorted(SUSPICIOUS_TLDS)), kw)
    return "http://bit.ly/%s%d" % (brand, rng.randint(100, 999))   # shortener


def make_dataset(n: int = 2400, seed: int = 5) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    rng = random.Random(seed)
    urls, labels = [], []
    for _ in range(n // 2):
        urls.append(_benign(rng)); labels.append(0)
        urls.append(_phish(rng)); labels.append(1)
    X = np.array([vector_list(extract(u)) for u in urls], dtype=float)
    y = np.array(labels, dtype=int)
    # ~3% label noise so the task is realistically hard (no leaky perfect scores).
    flip = rng.sample(range(len(y)), max(1, int(0.03 * len(y))))
    for i in flip:
        y[i] = 1 - y[i]
    return X, y, urls
