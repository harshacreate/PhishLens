"""URL / email feature extraction for phishing detection.

The SAME extractor is used to build the training set and to score live input, so
there is no train/serve skew. Features are interpretable, which lets the model
explain *why* something looks like phishing.
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Tuple
from urllib.parse import urlparse

FEATURE_NAMES: List[str] = [
    "url_length", "host_length", "num_dots", "num_hyphens", "num_subdomains",
    "has_ip_host", "has_at_symbol", "is_punycode", "uses_https", "suspicious_tld",
    "is_shortener", "has_redirect", "digit_ratio_host", "host_entropy",
    "brand_lookalike", "suspicious_keywords",
]

SUSPICIOUS_TLDS = {"zip", "xyz", "top", "tk", "ml", "ga", "cf", "gq", "country",
                   "kim", "work", "click", "link", "review", "fit", "mom", "loan"}
SHORTENERS = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly", "cutt.ly"}
KEYWORDS = {"login", "log-in", "signin", "verify", "verification", "account", "secure",
            "update", "confirm", "bank", "password", "webscr", "ebayisapi", "wallet",
            "billing", "invoice", "unlock", "suspend", "security"}
BRANDS = {"paypal", "apple", "microsoft", "google", "amazon", "facebook", "netflix",
          "instagram", "bankofamerica", "chase", "wellsfargo", "hdfc", "sbi", "icici",
          "whatsapp", "linkedin", "dhl", "fedex", "coinbase", "binance"}

_IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def _entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _registered_domain(host: str) -> str:
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def extract(url: str) -> Dict:
    """Return a dict with the numeric feature vector plus human-readable signals."""
    url = url.strip()
    if "://" not in url:
        url = "http://" + url
    p = urlparse(url)
    host = (p.hostname or "").lower()
    path_q = (p.path or "") + ("?" + p.query if p.query else "")
    reg = _registered_domain(host)
    tld = host.rsplit(".", 1)[-1] if "." in host else ""

    has_ip = 1 if _IP_RE.match(host) else 0
    punycode = 1 if "xn--" in host else 0
    sub = max(0, host.count(".") - 1) if host else 0
    digits = sum(c.isdigit() for c in host)
    digit_ratio = round(digits / len(host), 3) if host else 0.0
    shortener = 1 if reg in SHORTENERS else 0
    redirect = 1 if ("//" in path_q or "url=" in path_q.lower() or "redirect" in path_q.lower()) else 0
    tld_bad = 1 if tld in SUSPICIOUS_TLDS else 0
    kw_hits = [k for k in KEYWORDS if k in url.lower()]
    # Brand lookalike: a known brand appears somewhere but is NOT the registered domain.
    brand_hits = [b for b in BRANDS if b in host or b in path_q.lower()]
    lookalike = 1 if any(b not in reg for b in brand_hits) and brand_hits else 0

    vec = {
        "url_length": len(url),
        "host_length": len(host),
        "num_dots": host.count("."),
        "num_hyphens": host.count("-"),
        "num_subdomains": sub,
        "has_ip_host": has_ip,
        "has_at_symbol": 1 if "@" in url else 0,
        "is_punycode": punycode,
        "uses_https": 1 if p.scheme == "https" else 0,
        "suspicious_tld": tld_bad,
        "is_shortener": shortener,
        "has_redirect": redirect,
        "digit_ratio_host": digit_ratio,
        "host_entropy": round(_entropy(host), 3),
        "brand_lookalike": lookalike,
        "suspicious_keywords": min(len(kw_hits), 5),
    }

    signals = []
    if has_ip:
        signals.append(("IP address used as hostname", "high"))
    if lookalike:
        signals.append(("brand name on a non-matching domain (%s)" % ", ".join(brand_hits), "high"))
    if tld_bad:
        signals.append(("suspicious TLD .%s" % tld, "medium"))
    if "@" in url:
        signals.append(("'@' in URL (redirect trick)", "high"))
    if punycode:
        signals.append(("punycode host (possible homograph)", "high"))
    if p.scheme != "https":
        signals.append(("no HTTPS", "low"))
    if shortener:
        signals.append(("URL shortener hides the destination", "medium"))
    if redirect:
        signals.append(("open-redirect style parameter", "medium"))
    if kw_hits:
        signals.append(("credential/urgency keywords: %s" % ", ".join(kw_hits[:5]), "medium"))
    if sub >= 3:
        signals.append(("many subdomains (%d)" % sub, "low"))

    return {"vector": vec, "signals": signals, "host": host, "registered_domain": reg, "tld": tld}


def vector_list(feat: Dict) -> List[float]:
    return [float(feat["vector"][name]) for name in FEATURE_NAMES]


def extract_urls(text: str) -> List[str]:
    """Pull URLs out of a pasted email/body; fall back to the whole string."""
    urls = re.findall(r"https?://[^\s\"'<>)]+", text)
    if not urls:
        m = re.search(r"\b([a-z0-9.-]+\.[a-z]{2,})(/[^\s]*)?", text.lower())
        if m:
            urls = [m.group(0)]
    return urls
