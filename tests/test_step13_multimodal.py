import base64
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.services.gemini_service import analyze_infrastructure_photo

client = TestClient(app)

# 1x1 transparent PNG in base64
SAMPLE_BASE64_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

def test_analyze_photo_direct_mock():
    # Test direct service function call with road context
    res = analyze_infrastructure_photo(
        image_base64=SAMPLE_BASE64_IMAGE,
        mime_type="image/png",
        text_context="Major pothole on highway causing accidents",
        district="Pune"
    )
    assert res["detected_damage"] is True
    assert res["category"] == "roads_transport"
    assert res["severity"] in ["high", "medium", "low", "critical"]
    assert 0.0 <= res["severity_score"] <= 1.0
    assert "visual_evidence_summary" in res
    assert "actionable_recommendation" in res
    assert res["district"] == "Pune"

def test_analyze_photo_direct_water_context():
    res = analyze_infrastructure_photo(
        image_base64=f"data:image/png;base64,{SAMPLE_BASE64_IMAGE}",
        mime_type="image/png",
        text_context="Drinking water pipeline broken and leaking into sewage",
        district="Thane"
    )
    assert res["category"] == "water_sanitation"
    assert res["district"] == "Thane"

def test_analyze_photo_direct_health_context():
    res = analyze_infrastructure_photo(
        image_base64=SAMPLE_BASE64_IMAGE,
        mime_type="image/png",
        text_context="PHC primary health centre building wall cracked and unstaffed",
        district="Varanasi"
    )
    assert res["category"] == "healthcare"
    assert res["district"] == "Varanasi"

def test_analyze_photo_endpoint_v1():
    payload = {
        "image_base64": SAMPLE_BASE64_IMAGE,
        "mime_type": "image/png",
        "text_context": "School classroom roof leaking",
        "district": "Pune"
    }
    res = client.post("/api/v1/analyze-photo", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["detected_damage"] is True
    assert data["category"] == "education"
    assert "visual_evidence_summary" in data

def test_analyze_photo_endpoint_legacy():
    payload = {
        "image_base64": SAMPLE_BASE64_IMAGE,
        "mime_type": "image/png",
        "text_context": "Pothole on station road",
        "district": "Pune"
    }
    res = client.post("/analyze-photo", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["category"] == "roads_transport"

def test_analyze_photo_validation_error():
    # Base64 too short (< 10 chars)
    payload = {
        "image_base64": "abc",
        "district": "Pune"
    }
    res = client.post("/api/v1/analyze-photo", json=payload)
    assert res.status_code == 422
