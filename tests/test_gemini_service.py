"""
tests/test_gemini_service.py  —  STEP 7 Unit Tests
===================================================
All tests run offline (USE_MOCK_GEMINI=true forced via env patch).
No Gemini API key required; no network calls made.
"""

import os
import pytest

# Force mock mode for ALL tests in this module
os.environ["USE_MOCK_GEMINI"] = "true"
os.environ["GEMINI_API_KEY"] = ""

# Re-import after setting env so module-level flags are correct
from backend.services.gemini_service import (
    _stage1_detect_language,
    _stage2_classify,
    _stage3_extract_location,
    _stage4_cluster,
    understand_citizen_request,
    generate_grounded_explanation,
    parse_natural_language_query,
)


# ---------------------------------------------------------------------------
# Stage 1 — Language Detection
# ---------------------------------------------------------------------------

class TestStage1LanguageDetection:

    def test_english_text_detected(self):
        assert _stage1_detect_language("The hospital is too far from our village.") == "en"

    def test_hindi_text_detected(self):
        assert _stage1_detect_language("हमारे गाँव में अस्पताल नहीं है।") == "hi"

    def test_marathi_text_detected(self):
        assert _stage1_detect_language("आमच्या गावात रस्ता नाही आहे.") == "mr"

    def test_empty_string_defaults_to_english(self):
        assert _stage1_detect_language("") == "en"

    def test_mixed_devanagari_defaults_hindi_without_marathi_markers(self):
        # Generic Devanagari without Marathi-specific markers → hindi
        result = _stage1_detect_language("यह समस्या बहुत बड़ी है")
        assert result == "hi"


# ---------------------------------------------------------------------------
# Stage 2 — Classification
# ---------------------------------------------------------------------------

class TestStage2Classification:

    def test_healthcare_english(self):
        cat, sub, urgency = _stage2_classify("The PHC is 20km away and needs more doctors.")
        assert cat == "healthcare"
        assert urgency in ("high", "critical")

    def test_water_english(self):
        cat, sub, urgency = _stage2_classify("No clean drinking water supply in our area.")
        assert cat == "water_sanitation"

    def test_roads_english(self):
        cat, sub, urgency = _stage2_classify("The road to our village is broken with potholes.")
        assert cat == "roads_transport"

    def test_education_english(self):
        cat, sub, urgency = _stage2_classify("No teachers in the school for 3 months.")
        assert cat == "education"

    def test_emergency_bumps_urgency_to_critical(self):
        _, _, urgency = _stage2_classify("Emergency! Someone died because hospital was far.")
        assert urgency == "critical"

    def test_hindi_healthcare(self):
        cat, _, _ = _stage2_classify("हमारे गाँव में दवाखाना बहुत दूर है।")
        assert cat == "healthcare"

    def test_marathi_water(self):
        cat, _, _ = _stage2_classify("आमच्या वस्तीत पाणी येत नाही.")
        assert cat == "water_sanitation"

    def test_unknown_text_defaults_healthcare(self):
        cat, _, _ = _stage2_classify("Something completely unrelated xyz 123")
        assert cat == "healthcare"


# ---------------------------------------------------------------------------
# Stage 3 — Location Extraction
# ---------------------------------------------------------------------------

class TestStage3LocationExtraction:

    def test_pune_extracted(self):
        loc = _stage3_extract_location("The PHC in Pune is overcrowded.")
        assert loc["admin2"] == "Pune"
        assert loc["admin1"] == "Maharashtra"
        assert loc["country_code"] == "IND"

    def test_thane_extracted(self):
        loc = _stage3_extract_location("Thane district hospital beds are full.")
        assert loc["admin2"] == "Thane"
        assert loc["admin1"] == "Maharashtra"

    def test_varanasi_extracted(self):
        loc = _stage3_extract_location("Health centres in Varanasi need doctors.")
        assert loc["admin2"] == "Varanasi"
        assert loc["admin1"] == "Uttar Pradesh"

    def test_devanagari_pune_extracted(self):
        loc = _stage3_extract_location("पुणे येथे रुग्णालय नाही.")
        assert loc["admin2"] == "Pune"

    def test_devanagari_varanasi_extracted(self):
        loc = _stage3_extract_location("वाराणसी में पानी नहीं आता।")
        assert loc["admin2"] == "Varanasi"

    def test_unknown_location_defaults_pune(self):
        loc = _stage3_extract_location("No location mentioned in this request.")
        assert loc["admin2"] == "Pune"


# ---------------------------------------------------------------------------
# Stage 4 — Semantic Clustering
# ---------------------------------------------------------------------------

class TestStage4Clustering:

    def test_cluster_id_format(self):
        cluster = _stage4_cluster("healthcare", {"admin2": "Pune"})
        assert cluster == "CLUSTER-HEA-PUN"

    def test_cluster_id_water_varanasi(self):
        cluster = _stage4_cluster("water_sanitation", {"admin2": "Varanasi"})
        assert cluster == "CLUSTER-WAT-VAR"

    def test_cluster_id_roads_thane(self):
        cluster = _stage4_cluster("roads_transport", {"admin2": "Thane"})
        assert cluster == "CLUSTER-ROA-THA"


# ---------------------------------------------------------------------------
# Full Pipeline — understand_citizen_request
# ---------------------------------------------------------------------------

class TestUnderstandCitizenRequest:

    def test_returns_required_keys(self):
        result = understand_citizen_request("No hospital in our village.", "text")
        required = {
            "raw_text", "translated_text", "source_channel",
            "detected_language", "category", "sub_category",
            "urgency_level", "admin_hierarchy", "cluster_id",
            "confidence_score", "mode",
        }
        assert required.issubset(result.keys())

    def test_mode_is_mock_in_mock_mode(self):
        result = understand_citizen_request("Road broken in Thane.", "text")
        assert result["mode"] == "mock_gemini"

    def test_confidence_score_in_mock_mode(self):
        result = understand_citizen_request("Water shortage in Pune.", "text")
        assert result["confidence_score"] == 0.92

    def test_source_channel_preserved(self):
        result = understand_citizen_request("Healthcare needed.", "voice")
        assert result["source_channel"] == "voice"

    def test_admin_hierarchy_caller_override(self):
        caller_h = {"country_code": "IND", "admin1": "Uttar Pradesh", "admin2": "Varanasi", "locality": "Godowlia"}
        result = understand_citizen_request("Need more doctors.", "text", admin_hierarchy=caller_h)
        assert result["admin_hierarchy"]["admin2"] == "Varanasi"
        assert result["admin_hierarchy"]["locality"] == "Godowlia"

    def test_multilingual_hindi_pipeline(self):
        result = understand_citizen_request("हमारे गाँव में अस्पताल नहीं है।", "text")
        assert result["detected_language"] == "hi"
        assert result["category"] == "healthcare"

    def test_multilingual_marathi_pipeline(self):
        result = understand_citizen_request("आमच्या गावात पाणी येत नाही आहे.", "messaging_app")
        assert result["detected_language"] == "mr"
        assert result["category"] == "water_sanitation"
        assert result["source_channel"] == "messaging_app"

    def test_cluster_id_present_and_non_empty(self):
        result = understand_citizen_request("School has no teachers in Thane.")
        assert result["cluster_id"].startswith("CLUSTER-")

    def test_raw_text_preserved(self):
        text = "The PHC in Kalyan is 20km away."
        result = understand_citizen_request(text)
        assert result["raw_text"] == text


# ---------------------------------------------------------------------------
# Explanation Layer
# ---------------------------------------------------------------------------

class TestGenerateGroundedExplanation:

    def _make_district_info(self) -> dict:
        return {
            "population": 3_115_000,
            "facilities_count": 12,
            "citizen_demand_count": 45,
            "existing_investment_cr": 6.2,
            "admin1": "Maharashtra",
            "sector": "healthcare",
        }

    def test_returns_required_keys(self):
        result = generate_grounded_explanation("Thane", self._make_district_info(), {"priority_score": 72.5})
        assert "district" in result
        assert "priority_score" in result
        assert "explanation" in result
        assert "grounded_inputs" in result
        assert "footnote" in result

    def test_district_name_in_result(self):
        result = generate_grounded_explanation("Thane", self._make_district_info(), {"priority_score": 72.5})
        assert result["district"] == "Thane"

    def test_priority_score_preserved(self):
        result = generate_grounded_explanation("Pune", self._make_district_info(), {"priority_score": 85.0})
        assert result["priority_score"] == 85.0

    def test_explanation_contains_district_name(self):
        result = generate_grounded_explanation("Varanasi", self._make_district_info(), {"priority_score": 91.0})
        assert "Varanasi" in result["explanation"]

    def test_footnote_mentions_census(self):
        result = generate_grounded_explanation("Pune", self._make_district_info(), {"priority_score": 80.0})
        assert "Census 2011" in result["footnote"]

    def test_grounded_inputs_match_district_info(self):
        info = self._make_district_info()
        result = generate_grounded_explanation("Thane", info, {"priority_score": 72.5})
        gi = result["grounded_inputs"]
        assert gi["population"] == info["population"]
        assert gi["facilities_count"] == info["facilities_count"]
        assert gi["citizen_demand_count"] == info["citizen_demand_count"]


# ---------------------------------------------------------------------------
# NL Query Parser
# ---------------------------------------------------------------------------

class TestParseNaturalLanguageQuery:

    def test_returns_required_keys(self):
        result = parse_natural_language_query("show high demand healthcare in Maharashtra")
        assert "query" in result
        assert "structured_filter" in result
        assert "interpretation" in result

    def test_state_maharashtra_extracted(self):
        result = parse_natural_language_query("districts with healthcare gaps in Maharashtra")
        assert result["structured_filter"]["state"] == "Maharashtra"

    def test_state_uttar_pradesh_extracted(self):
        result = parse_natural_language_query("water sanitation issues in Uttar Pradesh")
        assert result["structured_filter"]["state"] == "Uttar Pradesh"

    def test_district_pune_extracted(self):
        result = parse_natural_language_query("show Pune education data")
        assert result["structured_filter"]["district"] == "Pune"

    def test_sector_healthcare_extracted(self):
        result = parse_natural_language_query("show under-funded hospital districts")
        assert result["structured_filter"]["sector"] == "healthcare"

    def test_sector_water_extracted(self):
        result = parse_natural_language_query("regions with low water sanitation")
        assert result["structured_filter"]["sector"] == "water_sanitation"

    def test_sort_investment_asc_for_underfunded(self):
        result = parse_natural_language_query("show under-funded regions")
        assert result["structured_filter"]["sort"] == "investment_asc"

    def test_sort_demand_desc_for_high_demand(self):
        result = parse_natural_language_query("show districts with most requests")
        assert result["structured_filter"]["sort"] == "demand_desc"

    def test_query_preserved(self):
        q = "healthcare gaps in Maharashtra"
        result = parse_natural_language_query(q)
        assert result["query"] == q

    def test_all_null_for_generic_query(self):
        result = parse_natural_language_query("show all districts")
        filt = result["structured_filter"]
        assert filt["state"] is None
        assert filt["district"] is None
        assert filt["sector"] is None
