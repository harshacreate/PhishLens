import warnings
warnings.filterwarnings("ignore")
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
