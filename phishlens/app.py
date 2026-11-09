"""PhishLens — Phishing URL & Email Analyzer (Flask backend)."""

from __future__ import annotations

import os

from flask import Flask, jsonify, request, send_from_directory

from phishlens import tools
from phishlens.features import extract_urls
from phishlens.model import PhishModel

HERE = os.path.dirname(__file__)
STATIC = os.path.join(HERE, "static")

app = Flask(__name__, static_folder=STATIC, static_url_path="/static")
MODEL = PhishModel.train(seed=0)     # trained once at startup (synthetic feature data)


@app.route("/")
def index():
    return send_from_directory(STATIC, "index.html")


@app.route("/health")
def health():
    return "ok"


@app.route("/api/analyze", methods=["POST"])
def analyze():
    text = (request.get_json(force=True, silent=True) or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "paste a URL or an email body"}), 400
    urls = extract_urls(text)
    if not urls:
        return jsonify({"error": "no URL found in the input"}), 400
    primary = MODEL.score_url(urls[0])
    primary["other_urls"] = urls[1:6]
    # simple email text signals
    low = text.lower()
    primary["email_signals"] = [s for s in [
        "urgency language ('immediately', 'suspended', 'verify now')" if any(
            k in low for k in ("immediately", "suspended", "verify now", "within 24", "urgent", "act now")) else None,
        "asks for credentials / payment info" if any(
            k in low for k in ("password", "card number", "ssn", "otp", "pin", "cvv")) else None,
        "generic greeting ('dear customer')" if "dear customer" in low or "dear user" in low else None,
    ] if s]
    return jsonify(primary)


@app.route("/api/enrich", methods=["POST"])
def enrich():
    d = request.get_json(force=True, silent=True) or {}
    domain = (d.get("domain") or "").strip().lower()
    if not domain:
        return jsonify({"error": "domain required"}), 400
    return jsonify({
        "domain": domain,
        "whois": tools.whois_lookup(domain),
        "dns": tools.dns_records(domain),
        "tls": tools.tls_cert(domain),
    })


@app.route("/api/metrics")
def metrics():
    return jsonify(MODEL.evaluate())


@app.route("/api/examples")
def examples():
    return jsonify({
        "safe": ["https://www.google.com/", "https://github.com/explore",
                 "https://www.amazon.in/orders"],
        "phishing": ["http://paypal-verify.tk/login",
                     "http://apple.com.secure99.ml/confirm",
                     "https://netflix.com@account-update.xyz/billing"],
    })


@app.route("/api/tools")
def tool_status():
    import importlib.util
    return jsonify({
        "whois": tools.tool_available("whois"),
        "dnspython": importlib.util.find_spec("dns") is not None,
        "tls": True,
    })


def main():
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8000")))


if __name__ == "__main__":
    main()
