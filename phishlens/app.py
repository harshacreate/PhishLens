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
app.config["MAX_CONTENT_LENGTH"] = 128 * 1024
MODEL = PhishModel.train(seed=0)     # trained once at startup (synthetic feature data)


def _body():
    value = request.get_json(silent=True)
    return value if isinstance(value, dict) else None


@app.route("/")
def index():
    return send_from_directory(STATIC, "index.html")


@app.route("/health")
def health():
    return "ok"


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = _body()
    if data is None:
        return jsonify({"error": "expected a JSON object"}), 400
    text = data.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "paste a URL or an email body"}), 400
    if len(text) > 20_000:
        return jsonify({"error": "input is limited to 20,000 characters"}), 413
    urls = extract_urls(text)
    if not urls:
        return jsonify({"error": "no URL found in the input"}), 400
    primary = _score_email(text, urls[0])
    primary["other_urls"] = urls[1:6]
    return jsonify(primary)


def _score_email(text, url):
    result = MODEL.score_url(url)
    low = text.lower()
    result["email_signals"] = [s for s in [
        "Urgency language" if any(k in low for k in ("immediately", "suspended", "verify now", "within 24", "urgent", "act now")) else None,
        "Credential or payment request" if any(k in low for k in ("password", "card number", "ssn", "otp", "pin", "cvv")) else None,
        "Generic greeting" if "dear customer" in low or "dear user" in low else None,
    ] if s]
    return result


@app.route("/api/analyze/batch", methods=["POST"])
def analyze_batch():
    data = _body()
    if data is None:
        return jsonify({"error": "expected a JSON object"}), 400
    items = data.get("items", [])
    if not isinstance(items, list) or not items or len(items) > 25:
        return jsonify({"error": "provide between 1 and 25 URLs"}), 400
    results = []
    for item in items:
        if not isinstance(item, str) or len(item) > 2048:
            continue
        urls = extract_urls(item)
        if urls:
            results.append(_score_email(item, urls[0]))
    if not results:
        return jsonify({"error": "no valid URLs found"}), 400
    return jsonify({
        "results": results,
        "count": len(results),
        "average_risk": round(sum(x["risk"] for x in results) / len(results), 1),
        "high_risk": sum(x["risk"] >= 70 for x in results),
        "synthetic_model": True,
    })


@app.route("/api/enrich", methods=["POST"])
def enrich():
    d = _body()
    if d is None:
        return jsonify({"error": "expected a JSON object"}), 400
    domain = (d.get("domain") or "").strip().lower()
    if not d.get("confirm_own_domain"):
        return jsonify({"error": "confirm that you own or are authorized to check this domain"}), 400
    if not tools.valid_public_domain(domain):
        return jsonify({"error": "enter a valid public DNS name; IPs and local hosts are not accepted"}), 400
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
        "dig": tools.tool_available("dig"),
        "dnspython": importlib.util.find_spec("dns") is not None,
        "openssl": tools.tool_available("openssl"),
    })


def main():
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))


if __name__ == "__main__":
    main()
