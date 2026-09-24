import pytest
from backend.app.loaders.synthetic_requests_loader import load_synthetic_requests
from backend.app.storage import get_storage

def test_load_synthetic_requests():
    requests = load_synthetic_requests()
    assert 150 <= len(requests) <= 300, f"Expected 150-300 synthetic requests, got {len(requests)}"

    languages = set(r["detected_language"] for r in requests)
    assert {"en", "hi", "mr"}.issubset(languages), f"Missing expected languages, got {languages}"

    channels = set(r["source_channel"] for r in requests)
    assert {"voice", "text", "messaging_app"}.issubset(channels), f"Unexpected channels, got {channels}"

    districts = set(r["admin_hierarchy"]["admin2"] for r in requests)
    allowed_districts = {"Pune", "Thane", "Varanasi"}
    assert districts.issubset(allowed_districts), f"Found non-pilot districts: {districts - allowed_districts}"

    for req in requests:
        assert req["data_quality"] == "synthetic", f"Expected synthetic tag, got {req.get('data_quality')}"
        assert req["id"].startswith("REQ-SYNTH-")
        assert req["timestamp"].endswith("Z")
        assert req["admin_hierarchy"]["country_code"] == "IND"

def test_storage_synthetic_requests():
    store = get_storage()
    db_requests = store.get_citizen_requests(limit=500)
    assert len(db_requests) >= 200, f"Expected at least 200 requests in store, found {len(db_requests)}"

    synthetic_reqs = [r for r in db_requests if r.get("data_quality") == "synthetic"]
    assert len(synthetic_reqs) >= 200, f"Expected at least 200 synthetic requests in DB"
