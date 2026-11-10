"""Opt-in live enrichment tools: whois, DNS/SPF/DMARC, TLS certificate.

These make PASSIVE lookups about the domain the user pasted (the same queries a
browser/resolver makes). They are OFF by default in the UI; the analyzer works
fully offline without them. Each degrades gracefully when the tool is missing.
"""

from __future__ import annotations

import re
import ipaddress
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Dict


def available(name: str) -> bool:
    return shutil.which(name) is not None


# Backward-compatible alias used elsewhere in the app.
tool_available = available


def valid_public_domain(domain: str) -> bool:
    """Accept a public DNS name only; live lookups still require explicit user opt-in."""
    domain = (domain or "").strip().rstrip(".").lower()
    if len(domain) > 253 or "." not in domain or not re.fullmatch(r"[a-z0-9.-]+", domain):
        return False
    try:
        ipaddress.ip_address(domain)
        return False
    except ValueError:
        pass
    labels = domain.split(".")
    if any(not label or len(label) > 63 or label.startswith("-") or label.endswith("-") for label in labels):
        return False
    return labels[-1].isalpha() and len(labels[-1]) >= 2 and domain not in {"localhost.localdomain"}


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
    """Use OpenSSL's client and x509 commands for a user-opted-in TLS check."""
    if not valid_public_domain(host) or not available("openssl"):
        return {"available": False, "reachable": False}
    try:
        session = subprocess.run(
            ["openssl", "s_client", "-connect", f"{host}:{port}", "-servername", host,
             "-showcerts", "-verify_quiet"],
            input="\n", capture_output=True, text=True, timeout=8,
        )
    except (subprocess.TimeoutExpired, OSError):
        return {"available": True, "reachable": False}
    cert_match = re.search(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
                           session.stdout, flags=re.S)
    if not cert_match:
        return {"available": True, "reachable": False}
    try:
        cert = subprocess.run(
            ["openssl", "x509", "-noout", "-subject", "-issuer", "-dates", "-fingerprint", "-sha256"],
            input=cert_match.group(0), capture_output=True, text=True, timeout=5,
        )
    except (subprocess.TimeoutExpired, OSError):
        return {"available": True, "reachable": True, "error": "certificate parsing failed"}
    lines = dict(line.split("=", 1) for line in cert.stdout.splitlines() if "=" in line)
    protocol = re.search(r"Protocol\s*:\s*(TLSv[\d.]+)", session.stdout + session.stderr)
    cipher = re.search(r"Ciphersuite\s*:\s*([^\s]+)", session.stdout + session.stderr)
    return {
        "available": True, "reachable": bool(cert.stdout),
        "subject": lines.get("subject"), "issuer": lines.get("issuer"),
        "valid_from": lines.get("notBefore"), "valid_to": lines.get("notAfter"),
        "fingerprint_sha256": lines.get("sha256 Fingerprint"),
        "tls_version": protocol.group(1) if protocol else None,
        "cipher": cipher.group(1) if cipher else None,
    }
