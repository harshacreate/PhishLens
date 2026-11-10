import warnings
warnings.filterwarnings("ignore")
from types import SimpleNamespace
from phishlens import tools
from phishlens.features import extract, extract_urls, FEATURE_NAMES, vector_list
from phishlens.model import PhishModel
from phishlens.app import app


def test_feature_extraction():
    f = extract("https://netflix.com@account-update.xyz/billing")
    assert f["vector"]["has_at_symbol"] == 1
    assert len(vector_list(f)) == len(FEATURE_NAMES)


def test_extract_urls_from_email():
    urls = extract_urls("Dear user, verify at http://paypal-verify.tk/login now")
    assert urls and "paypal-verify.tk" in urls[0]


def test_model_quality_and_scoring():
    m = PhishModel.train()
    met = m.evaluate()
    assert met["roc_auc"] >= 0.9
    assert m.score_url("https://www.google.com/")["risk"] < 25
    assert m.score_url("http://paypal-verify.tk/login")["risk"] > 70


def test_api():
    c = app.test_client()
    assert c.get("/health").data == b"ok"
    r = c.post("/api/analyze", json={"text": "http://apple.com.secure99.ml/confirm"}).get_json()
    assert r["verdict"] in ("Phishing", "Suspicious")
    assert len(r["drivers"]) >= 1


def test_batch_endpoint_and_input_limits():
    c = app.test_client()
    r = c.post("/api/analyze/batch", json={"items": [
        "https://www.example.com/", "http://paypal-verify.tk/login"
    ]})
    assert r.status_code == 200
    body = r.get_json()
    assert body["count"] == 2 and body["high_risk"] >= 1
    assert body["synthetic_model"] is True
    assert c.post("/api/analyze/batch", json={"items": ["https://x.test"] * 26}).status_code == 400
    assert c.post("/api/analyze", json={"text": "x" * 20_001}).status_code == 413


def test_live_enrichment_requires_owner_confirmation_and_public_domain(monkeypatch):
    c = app.test_client()
    assert c.post("/api/enrich", json={"domain": "example.com"}).status_code == 400
    assert c.post("/api/enrich", json={"domain": "127.0.0.1", "confirm_own_domain": True}).status_code == 400
    monkeypatch.setattr(tools, "whois_lookup", lambda _: {"available": True})
    monkeypatch.setattr(tools, "dns_records", lambda _: {"available": True})
    monkeypatch.setattr(tools, "tls_cert", lambda _: {"available": True})
    result = c.post("/api/enrich", json={
        "domain": "example.com", "confirm_own_domain": True
    })
    assert result.status_code == 200


def test_openssl_certificate_output_parser(monkeypatch):
    pem = "-----BEGIN CERTIFICATE-----\nQUJD\n-----END CERTIFICATE-----"
    calls = []
    def fake_run(command, **kwargs):
        calls.append(command)
        if command[1] == "s_client":
            return SimpleNamespace(stdout=f"{pem}\nProtocol : TLSv1.3\nCiphersuite : TLS_AES_128_GCM_SHA256", stderr="", returncode=0)
        return SimpleNamespace(stdout=(
            "subject=CN=fixture.example\nissuer=CN=Fixture CA\n"
            "notBefore=Jan  1 00:00:00 2026 GMT\nnotAfter=Jan  1 00:00:00 2027 GMT\n"
            "sha256 Fingerprint=AA:BB:CC"
        ), stderr="", returncode=0)
    monkeypatch.setattr(tools, "available", lambda _: True)
    monkeypatch.setattr(tools.subprocess, "run", fake_run)
    result = tools.tls_cert("example.com")
    assert result["reachable"] is True
    assert result["issuer"] == "CN=Fixture CA"
    assert result["tls_version"] == "TLSv1.3"
    assert calls[0][0:2] == ["openssl", "s_client"]


def test_domain_guard_rejects_local_and_ip_targets():
    assert tools.valid_public_domain("sub.example.com")
    assert not tools.valid_public_domain("localhost")
    assert not tools.valid_public_domain("127.0.0.1")
    assert not tools.valid_public_domain("-bad.example.com")
