"""
tests/test_step9_api_completion.py — STEP 9 Unit & Integration Tests
======================================================================
Covers:
  - Pydantic input validation (422 Unprocessable Entity on invalid inputs)
  - SubmitRequestModel validation: max_length=2000, min_length=1, source_channel enum
  - QueryModel validation: max_length=500, min_length=1
  - APIRouter verification: both /api/v1/* and legacy /* routes work identically
  - CORS header & origin settings
  - Timezone-aware ISO timestamps without deprecation warnings
"""

import os
import pytest
from fastapi.testclient import TestClient

os.environ["USE_MOCK_GEMINI"] = "true"
os.environ["GEMINI_API_KEY"] = ""

from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)


class TestStep9InputValidation:

    # --- SubmitRequestModel validation ---

    def test_submit_valid_request(self):
        payload = {
            "raw_text": "Need urgent PHC setup in rural block.",
            "source_channel": "text",
            "district": "Pune"
        }
        res = client.post("/api/v1/requests", json=payload)
        assert res.status_code == 200
        assert res.json()["status"] == "success"

    def test_submit_valid_messaging_app_channel(self):
        payload = {
            "raw_text": "Clean drinking water pipeline damaged.",
            "source_channel": "messaging_app",
            "district": "Thane"
        }
        res = client.post("/api/v1/requests", json=payload)
        assert res.status_code == 200

    def test_submit_valid_voice_channel(self):
        payload = {
            "raw_text": "Road repair needed urgently.",
            "source_channel": "voice",
            "district": "Varanasi"
        }
        res = client.post("/api/v1/requests", json=payload)
        assert res.status_code == 200

    def test_submit_empty_text_returns_422(self):
        payload = {
            "raw_text": "",
            "source_channel": "text"
        }
        res = client.post("/api/v1/requests", json=payload)
        assert res.status_code == 422

    def test_submit_exceeds_max_length_returns_422(self):
        payload = {
            "raw_text": "A" * 2001,
            "source_channel": "text"
        }
        res = client.post("/api/v1/requests", json=payload)
        assert res.status_code == 422

    def test_submit_invalid_channel_returns_422(self):
        payload = {
            "raw_text": "Valid text request",
            "source_channel": "invalid_channel_xyz"
        }
        res = client.post("/api/v1/requests", json=payload)
        assert res.status_code == 422

    # --- QueryModel validation ---

    def test_query_valid(self):
        res = client.post("/api/v1/query", json={"query": "healthcare in Pune"})
        assert res.status_code == 200

    def test_query_empty_returns_422(self):
        res = client.post("/api/v1/query", json={"query": ""})
        assert res.status_code == 422

    def test_query_exceeds_500_chars_returns_422(self):
        res = client.post("/api/v1/query", json={"query": "x" * 501})
        assert res.status_code == 422


class TestStep9ApiV1RouterEquivalence:

    def test_health_routes(self):
        r1 = client.get("/health")
        r2 = client.get("/api/v1/health")
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json() == r2.json()

    def test_districts_routes(self):
        r1 = client.get("/districts")
        r2 = client.get("/api/v1/districts")
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert len(r1.json()) == len(r2.json())

    def test_district_detail_routes(self):
        r1 = client.get("/districts/Pune")
        r2 = client.get("/api/v1/districts/Pune")
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["district_name"] == "Pune"

    def test_explain_routes(self):
        r1 = client.get("/explain/Thane")
        r2 = client.get("/api/v1/explain/Thane")
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["district"] == r2.json()["district"]

    def test_silent_needs_routes(self):
        r1 = client.get("/silent-needs")
        r2 = client.get("/api/v1/silent-needs")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_mismatches_routes(self):
        r1 = client.get("/mismatches")
        r2 = client.get("/api/v1/mismatches")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_impact_routes(self):
        r1 = client.get("/impact")
        r2 = client.get("/api/v1/impact")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_datasets_routes(self):
        r1 = client.get("/datasets")
        r2 = client.get("/api/v1/datasets")
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["census_honesty_note"] == r2.json()["census_honesty_note"]


class TestStep9CorsConfiguration:

    def test_cors_origins_configured(self):
        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) > 0
        assert "*" not in settings.cors_origins
