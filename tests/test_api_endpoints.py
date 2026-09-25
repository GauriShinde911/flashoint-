import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoints():
    res1 = client.get("/health")
    assert res1.status_code == 200
    assert res1.json()["status"] == "online"

    res2 = client.get("/api/health")
    assert res2.status_code == 200
    assert res2.json()["status"] == "online"

def test_districts_endpoint():
    res = client.get("/districts")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3
    # Check deterministic ordering by priority score descending
    scores = [d["priority_score"] for d in data]
    assert scores == sorted(scores, reverse=True)

def test_explain_endpoint():
    res = client.get("/explain/Pune")
    assert res.status_code == 200
    data = res.json()
    assert data["district"] == "Pune"
    assert "footnote" in data
    assert "Grounded strictly" in data["footnote"]

def test_post_requests_endpoint():
    payload = {
        "raw_text": "Primary Health Centre in Kalyan is 20km away, emergency care needed.",
        "source_channel": "text",
        "district": "Thane"
    }
    res = client.post("/requests", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["analysis"]["category"] == "healthcare"

def test_post_query_endpoint():
    payload = {"query": "show under-funded healthcare in Maharashtra"}
    res = client.post("/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "structured_filter" in data
    assert data["structured_filter"]["state"] == "Maharashtra"

def test_datasets_endpoint():
    res = client.get("/datasets")
    assert res.status_code == 200
    data = res.json()
    assert "datasets" in data
    assert "census_honesty_note" in data
