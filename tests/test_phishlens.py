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


def test_registered_domain_uses_public_suffix_list_and_handles_bad_hosts():
    uk = extract("https://login.example.co.uk/")
    assert uk["registered_domain"] == "example.co.uk"
    assert uk["vector"]["num_subdomains"] == 1
    assert extract("https://mail.shop.example.com.au/")["registered_domain"] == "example.com.au"
    assert extract("https://a.b.example.com/")["registered_domain"] == "example.com"
    assert extract("https://account.blogspot.com/")["registered_domain"] == "account.blogspot.com"
    assert extract("https://paypal.co.uk/")["signals"] == []
    assert extract("http://192.0.2.10/login")["registered_domain"] == "192.0.2.10"
    ipv6 = extract("http://[2001:db8::1]/")
    assert ipv6["registered_domain"] == "2001:db8::1"
    assert ipv6["vector"]["has_ip_host"] == 1
    malformed = extract("http://[2001:db8::1")
    assert malformed["registered_domain"] == ""
    assert malformed["vector"]["has_ip_host"] == 0


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


def test_model_comparison_reports_every_candidate():
    from phishlens.compare import CANDIDATES, compare
    report = compare()
    assert [r["model"] for r in report["results"]] == list(CANDIDATES)
    for row in report["results"]:
        c = row["confusion"]
        assert c["tn"] + c["fp"] + c["fn"] + c["tp"] == report["n_test"]
        assert row["roc_auc"] >= 0.9


def test_squatting_signals():
    from phishlens.features import squatting
    assert squatting("paypa1-secure-login.com")["typosquat"] == ["paypal"]
    assert squatting("linkedln.com")["typosquat"] == ["linkedin"]
    assert "hdfc" in squatting("hdfc-netbanking-kyc-update.in")["combosquat"]
    for own in ("paypal.com", "linkedin.com", "hdfcbank.com", "microsoftonline.com"):
        assert squatting(own) == {"typosquat": [], "combosquat": []}


def test_hybrid_floor_catches_punycode_but_not_path_mentions():
    m = PhishModel.train()
    homograph = m.score_url("http://xn--pypal-4ve.com/signin")
    assert homograph["model_risk"] < 40 and homograph["risk"] >= 70 and homograph["floor_applied"]
    article = m.score_url("https://en.wikipedia.org/wiki/PayPal")
    assert article["risk"] < 40 and not article["floor_applied"]


def test_holdout_probes_hybrid_beats_model_only():
    from phishlens.probes import evaluate
    report = evaluate()["holdout"]
    assert report["hybrid"]["recall"] > report["model_only"]["recall"]
    assert report["hybrid"]["fp"] == 0
    assert report["hybrid"]["recall_ci95"] is not None
    assert report["hybrid"]["fpr_ci95"][0] == 0.0
    assert report["hybrid"]["fpr_ci95"][1] > 0.0


def test_wilson_intervals_handle_small_samples_and_zero_false_positives():
    from phishlens.probes import _wilson_interval
    assert _wilson_interval(1, 10) == [0.018, 0.404]
    assert _wilson_interval(0, 12) == [0.0, 0.242]
    assert _wilson_interval(0, 0) is None


def test_tls_check_refuses_names_that_resolve_to_internal_addresses(monkeypatch):
    import socket
    def fake_getaddrinfo(host, *args, **kwargs):
        table = {"rebind.example": "127.0.0.1", "metadata.example": "169.254.169.254",
                 "intranet.example": "10.1.2.3", "public.example": "93.184.216.34"}
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (table[host], 0))]
    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
    for host in ("rebind.example", "metadata.example", "intranet.example"):
        assert tools.resolve_public(host) is None
        if tools.available("openssl"):
            result = tools.tls_cert(host)
            assert result["reachable"] is False and "refused" in result["error"]
    assert tools.resolve_public("public.example") == "93.184.216.34"
