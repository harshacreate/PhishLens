"""Opt-in live enrichment tools: whois, DNS/SPF/DMARC, TLS certificate.

These make PASSIVE lookups about the domain the user pasted (the same queries a
browser/resolver makes). They are OFF by default in the UI; the analyzer works
fully offline without them. Each degrades gracefully when the tool is missing.
"""

from __future__ import annotations

import re
import shutil
import socket
import ssl
import subprocess
from datetime import datetime, timezone
from typing import Dict


def tool_available(name: str) -> bool:
    return shutil.which(name) is not None


def whois_lookup(domain: str) -> Dict:
    if not tool_available("whois"):
        return {"available": False}
    try:
        r = subprocess.run(["whois", domain], capture_output=True, text=True, timeout=12)
    except (subprocess.TimeoutExpired, OSError):
        return {"available": True, "error": "lookup failed"}
    out = r.stdout
    created = registrar = None
    m = re.search(r"(?:Creation Date|created|Registered on)\D*(\d{4}-\d{2}-\d{2})", out, re.I)
    if m:
        created = m.group(1)
    m2 = re.search(r"Registrar:\s*(.+)", out, re.I)
    if m2:
        registrar = m2.group(1).strip()
    age_days = None
    if created:
        try:
            age_days = (datetime.now(timezone.utc) - datetime.strptime(created, "%Y-%m-%d").replace(tzinfo=timezone.utc)).days
        except ValueError:
            pass
    return {"available": True, "created": created, "registrar": registrar,
            "age_days": age_days,
            "young_domain": (age_days is not None and age_days < 90)}


def dns_records(domain: str) -> Dict:
    try:
        import dns.resolver
    except ImportError:
        return {"available": False}
    out = {"available": True, "a": [], "mx": [], "spf": None, "dmarc": None}
    res = dns.resolver.Resolver()
    res.lifetime = res.timeout = 5
    try:
        out["a"] = [r.address for r in res.resolve(domain, "A")][:5]
    except Exception:
        pass
    try:
        out["mx"] = [str(r.exchange).rstrip(".") for r in res.resolve(domain, "MX")][:5]
    except Exception:
        pass
    try:
        for r in res.resolve(domain, "TXT"):
            txt = b"".join(r.strings).decode("utf-8", "ignore")
            if "v=spf1" in txt.lower():
                out["spf"] = txt
    except Exception:
        pass
    try:
        for r in res.resolve("_dmarc." + domain, "TXT"):
            txt = b"".join(r.strings).decode("utf-8", "ignore")
            if "v=dmarc1" in txt.lower():
                out["dmarc"] = txt
    except Exception:
        pass
    out["has_spf"] = out["spf"] is not None
    out["has_dmarc"] = out["dmarc"] is not None
    return out


def tls_cert(host: str, port: int = 443) -> Dict:
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=6) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
    except Exception:
        return {"available": True, "reachable": False}
    subj = dict(x[0] for x in cert.get("subject", []))
    issuer = dict(x[0] for x in cert.get("issuer", []))
    return {
        "available": True, "reachable": True,
        "subject_cn": subj.get("commonName"),
        "issuer": issuer.get("organizationName") or issuer.get("commonName"),
        "valid_from": cert.get("notBefore"),
        "valid_to": cert.get("notAfter"),
        "tls_version": cipher[1] if cipher else None,
        "cipher": cipher[0] if cipher else None,
    }
