"""
tests/test_step8_explanation_query.py  —  STEP 8 Unit + Integration Tests
==========================================================================
Covers:
  - Upgraded generate_grounded_explanation (evidence_summary, data_quality, rank)
  - Upgraded _parse_nl_query_deterministic (compound sectors, min_score, districts)
  - /explain endpoint returning new fields
  - /query endpoint with sector filter, min_score, sort validation
All run offline (USE_MOCK_GEMINI=true forced).
"""

import os
import pytest

os.environ["USE_MOCK_GEMINI"] = "true"
os.environ["GEMINI_API_KEY"] = ""

from backend.services.gemini_service import (
    generate_grounded_explanation,
    _build_explanation_text,
    _parse_nl_query_deterministic,
    parse_natural_language_query,
)
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# _build_explanation_text (helper)
# ---------------------------------------------------------------------------

class TestBuildExplanationText:

    def test_contains_district_and_state(self):
        text = _build_explanation_text("Varanasi", "Uttar Pradesh", 91.0, "31.1 lakh", 5, 62, 22.0)
        assert "Varanasi" in text
        assert "Uttar Pradesh" in text

    def test_contains_score(self):
        text = _build_explanation_text("Pune", "Maharashtra", 78.5, "31.1 lakh", 12, 40, 14.5)
        assert "78.5" in text

    def test_rank_included_when_provided(self):
        text = _build_explanation_text("Thane", "Maharashtra", 72.0, "25.0 lakh", 8, 35, 6.2, rank=2)
        assert "Rank #2" in text

    def test_rank_omitted_when_none(self):
        text = _build_explanation_text("Pune", "Maharashtra", 78.5, "31.1 lakh", 12, 40, 14.5, rank=None)
        assert "Rank" not in text

    def test_contains_investment(self):
        text = _build_explanation_text("Pune", "Maharashtra", 78.5, "31.1 lakh", 12, 40, 14.5)
        assert "14.5" in text

    def test_contains_demand_count(self):
        text = _build_explanation_text("Pune", "Maharashtra", 78.5, "31.1 lakh", 12, 40, 14.5)
        assert "40" in text


# ---------------------------------------------------------------------------
# generate_grounded_explanation (STEP 8 upgraded)
# ---------------------------------------------------------------------------

def _sample_district_info(district="Thane", rank=2):
    return {
        "population": 2_500_000,
        "facilities_count": 8,
        "citizen_demand_count": 35,
        "existing_investment_cr": 6.2,
        "admin1": "Maharashtra",
        "sector": "healthcare",
        "data_quality": "real",
        "rank": rank,
    }


class TestGenerateGroundedExplanationStep8:

    def test_new_fields_present(self):
        result = generate_grounded_explanation("Thane", _sample_district_info(), {"priority_score": 72.0})
        assert "evidence_summary" in result
        assert "explanation_mode" in result
        assert "data_quality" in result
        assert "state" in result
        assert "rank" in result

    def test_evidence_summary_keys(self):
        result = generate_grounded_explanation("Thane", _sample_district_info(), {"priority_score": 72.0})
        es = result["evidence_summary"]
        assert "population" in es
        assert "population_readable" in es
        assert "facilities_count" in es
        assert "citizen_demand_count" in es
        assert "existing_investment_cr" in es

    def test_evidence_summary_values_match(self):
        info = _sample_district_info()
        result = generate_grounded_explanation("Thane", info, {"priority_score": 72.0})
        es = result["evidence_summary"]
        assert es["population"] == info["population"]
        assert es["facilities_count"] == info["facilities_count"]
        assert es["citizen_demand_count"] == info["citizen_demand_count"]

    def test_data_quality_passed_through(self):
        info = _sample_district_info()
        info["data_quality"] = "synthetic"
        result = generate_grounded_explanation("Thane", info, {"priority_score": 72.0})
        assert result["data_quality"] == "synthetic"

    def test_rank_in_result(self):
        result = generate_grounded_explanation("Thane", _sample_district_info(rank=2), {"priority_score": 72.0})
        assert result["rank"] == 2

    def test_explanation_mode_deterministic_in_mock(self):
        result = generate_grounded_explanation("Pune", _sample_district_info(), {"priority_score": 80.0})
        assert result["explanation_mode"] == "deterministic"

    def test_backward_compat_grounded_inputs_still_present(self):
        result = generate_grounded_explanation("Varanasi", _sample_district_info(), {"priority_score": 91.0})
        assert "grounded_inputs" in result
        assert "population" in result["grounded_inputs"]

    def test_footnote_still_mentions_census(self):
        result = generate_grounded_explanation("Pune", _sample_district_info(), {"priority_score": 80.0})
        assert "Census 2011" in result["footnote"]

    def test_explanation_contains_rank_clause(self):
        result = generate_grounded_explanation("Thane", _sample_district_info(rank=2), {"priority_score": 72.0})
        assert "Rank #2" in result["explanation"]

    def test_explanation_contains_score(self):
        result = generate_grounded_explanation("Pune", _sample_district_info(), {"priority_score": 78.5})
        assert "78.5" in result["explanation"]


# ---------------------------------------------------------------------------
# _parse_nl_query_deterministic (STEP 8 compound support)
# ---------------------------------------------------------------------------

class TestNLQueryDeterministicStep8:

    def test_single_sector_healthcare(self):
        result = _parse_nl_query_deterministic("healthcare gaps in Maharashtra")
        assert result["sector"] == "healthcare"
        assert result["sectors"] == ["healthcare"]

    def test_compound_sectors(self):
        result = _parse_nl_query_deterministic("districts with healthcare and water issues")
        assert set(result["sectors"]) == {"healthcare", "water_sanitation"}
        assert result["sector"] is None  # compound → no single sector

    def test_single_district_sets_district_field(self):
        result = _parse_nl_query_deterministic("Pune education needs")
        assert result["district"] == "Pune"
        assert result["districts"] == ["Pune"]

    def test_min_score_extracted(self):
        result = _parse_nl_query_deterministic("show districts with priority score above 70")
        assert result["min_score"] == 70

    def test_min_score_with_greater_than(self):
        result = _parse_nl_query_deterministic("priority > 60 regions")
        assert result["min_score"] == 60

    def test_no_min_score_returns_none(self):
        result = _parse_nl_query_deterministic("all healthcare districts")
        assert result["min_score"] is None

    def test_sort_investment_asc(self):
        result = _parse_nl_query_deterministic("show under-funded water districts")
        assert result["sort"] == "investment_asc"

    def test_sort_demand_desc(self):
        result = _parse_nl_query_deterministic("districts with most requests")
        assert result["sort"] == "demand_desc"

    def test_sort_default_priority(self):
        result = _parse_nl_query_deterministic("show all districts")
        assert result["sort"] == "priority_score_desc"

    def test_has_required_keys(self):
        result = _parse_nl_query_deterministic("healthcare in Maharashtra")
        for key in ["state", "district", "districts", "sector", "sectors", "sort", "min_score"]:
            assert key in result


# ---------------------------------------------------------------------------
# parse_natural_language_query (public function)
# ---------------------------------------------------------------------------

class TestParseNaturalLanguageQueryStep8:

    def test_interpretation_updated_for_sector(self):
        result = parse_natural_language_query("healthcare gaps in Maharashtra")
        assert "healthcare" in result["interpretation"]

    def test_interpretation_mentions_all_for_no_filter(self):
        result = parse_natural_language_query("show all districts")
        assert "All" in result["interpretation"]

    def test_min_score_in_interpretation(self):
        result = parse_natural_language_query("districts with score above 70")
        assert "70" in result["interpretation"]


# ---------------------------------------------------------------------------
# /explain endpoint (integration tests)
# ---------------------------------------------------------------------------

class TestExplainEndpointStep8:

    def test_explain_pune_returns_200(self):
        res = client.get("/explain/Pune")
        assert res.status_code == 200

    def test_explain_returns_evidence_summary(self):
        res = client.get("/explain/Pune")
        data = res.json()
        assert "evidence_summary" in data

    def test_explain_returns_explanation_mode(self):
        res = client.get("/explain/Thane")
        data = res.json()
        assert "explanation_mode" in data
        assert data["explanation_mode"] == "deterministic"

    def test_explain_returns_data_quality(self):
        res = client.get("/explain/Varanasi")
        data = res.json()
        assert "data_quality" in data

    def test_explain_returns_state_field(self):
        res = client.get("/explain/Varanasi")
        data = res.json()
        assert data["state"] == "Uttar Pradesh"

    def test_explain_returns_rank(self):
        res = client.get("/explain/Pune")
        data = res.json()
        # rank is an integer (1, 2, or 3)
        assert isinstance(data["rank"], int)
        assert 1 <= data["rank"] <= 3

    def test_explain_backward_compat_footnote(self):
        res = client.get("/explain/Pune")
        data = res.json()
        assert "footnote" in data
        assert "Grounded strictly" in data["footnote"]

    def test_explain_unknown_district_returns_404(self):
        res = client.get("/explain/UnknownCity")
        assert res.status_code == 404

    def test_explain_case_insensitive(self):
        res = client.get("/explain/pune")
        assert res.status_code == 200


# ---------------------------------------------------------------------------
# /query endpoint (integration — sector, sort, min_score filters)
# ---------------------------------------------------------------------------

class TestQueryEndpointStep8:

    def test_query_state_filter(self):
        res = client.post("/query", json={"query": "healthcare districts in Maharashtra"})
        assert res.status_code == 200
        data = res.json()
        # All results must be Maharashtra
        for r in data["results"]:
            assert r["admin1"] == "Maharashtra"

    def test_query_returns_structured_filter(self):
        res = client.post("/query", json={"query": "all districts"})
        data = res.json()
        assert "structured_filter" in data
        assert "interpretation" in data
        assert "result_count" in data

    def test_query_sort_priority_desc_is_ordered(self):
        res = client.post("/query", json={"query": "show all districts"})
        data = res.json()
        scores = [r["priority_score"] for r in data["results"]]
        assert scores == sorted(scores, reverse=True)

    def test_query_sort_investment_asc(self):
        res = client.post("/query", json={"query": "show under-funded districts"})
        data = res.json()
        investments = [r["existing_investment_cr"] for r in data["results"]]
        assert investments == sorted(investments)

    def test_query_interpretation_present(self):
        res = client.post("/query", json={"query": "healthcare in Maharashtra"})
        data = res.json()
        assert len(data["interpretation"]) > 10

    def test_query_result_count_matches_results_list(self):
        res = client.post("/query", json={"query": "all districts"})
        data = res.json()
        assert data["result_count"] == len(data["results"])
