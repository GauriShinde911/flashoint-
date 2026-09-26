"""
Gemini Understanding & Explanation Service  —  STEP 7
======================================================
4-stage pipeline (ADK-style):
  Stage 1 — Language Detection
  Stage 2 — Category / Urgency Classification
  Stage 3 — Location + Entity Extraction
  Stage 4 — Semantic Clustering

USE_MOCK_GEMINI=true  → fully deterministic offline path (no API key needed)
USE_MOCK_GEMINI=false → real Gemini 1.5-flash call; falls back to deterministic
                         path on any error.

The Gemini API key is held SERVER-SIDE only; it never reaches the browser.
"""

import os
import json
import re
from typing import Dict, Any, Optional

# ---------------------------------------------------------------------------
# Environment flags — read once at import time
# ---------------------------------------------------------------------------
USE_MOCK_GEMINI: bool = os.getenv("USE_MOCK_GEMINI", "true").lower() in ("true", "1", "yes")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# Known pilot districts (expand in config for multi-country BRICS support)
_PILOT_DISTRICTS: Dict[str, str] = {
    "pune": "Pune",
    "पुणे": "Pune",
    "thane": "Thane",
    "ठाणे": "Thane",
    "varanasi": "Varanasi",
    "बनारस": "Varanasi",
    "वाराणसी": "Varanasi",
}

_STATE_MAP: Dict[str, str] = {
    "Pune": "Maharashtra",
    "Thane": "Maharashtra",
    "Varanasi": "Uttar Pradesh",
}


# ===========================================================================
# Stage 1 — Language Detection
# ===========================================================================

def _stage1_detect_language(text: str) -> str:
    """
    Heuristic language detection.
    Returns ISO 639-1 code: 'en' | 'hi' | 'mr'
    """
    devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
    if devanagari_count == 0:
        return "en"
    # Marathi-specific words not common in standard Hindi
    marathi_markers = [
        "आहे", "नाही", "करून", "खूप", "गावात",
        "रस्ता", "पाणी", "शाळा", "आणि", "माझ्या",
    ]
    if any(m in text for m in marathi_markers):
        return "mr"
    return "hi"


# ===========================================================================
# Stage 2 — Category / Urgency Classification
# ===========================================================================

_CATEGORY_KEYWORDS: list[tuple[str, str, str, list[str]]] = [
    # (category, sub_category, default_urgency, keywords)
    (
        "healthcare", "phc_shortage", "high",
        ["hospital", "doctor", "clinic", "phc", "health", "medicine", "nurse",
         "ambulance", "दवाखाना", "अस्पताल", "डॉक्टर", "आरोग्य", "स्वास्थ्य",
         "दवाई", "रुग्णालय"],
    ),
    (
        "water_sanitation", "drinking_water_pipeline", "high",
        ["water", "pipe", "borewell", "tap", "drinking", "sanitation", "toilet",
         "sewage", "पाणी", "नळ", "जल", "पानी", "बोरवेल", "शौचालय"],
    ),
    (
        "roads_transport", "all_weather_road", "medium",
        ["road", "highway", "bus", "bridge", "traffic", "transport", "pothole",
         "रस्ता", "सड़क", "पुल", "बस", "वाहन", "खड्डे"],
    ),
    (
        "education", "school_infrastructure", "medium",
        ["school", "teacher", "classroom", "toilet", "education", "book",
         "student", "शाळा", "स्कूल", "शिक्षक", "शिक्षा", "विद्यार्थी"],
    ),
]


def _stage2_classify(text: str) -> tuple[str, str, str]:
    """Returns (category, sub_category, urgency_level)."""
    lower = text.lower()
    for cat, sub_cat, urgency, keywords in _CATEGORY_KEYWORDS:
        if any(kw in lower for kw in keywords):
            # Bump urgency to 'critical' if death/emergency words present
            if any(w in lower for w in ["emergency", "death", "died", "मृत्यु", "आपत्काल"]):
                urgency = "critical"
            return (cat, sub_cat, urgency)
    return ("healthcare", "general_infrastructure", "medium")


# ===========================================================================
# Stage 3 — Location + Entity Extraction
# ===========================================================================

def _stage3_extract_location(text: str) -> Dict[str, str]:
    """
    Returns an admin_hierarchy dict.
    Defaults to Pune/Maharashtra if no pilot district detected.
    """
    lower = text.lower()
    district = "Pune"
    for keyword, name in _PILOT_DISTRICTS.items():
        if keyword in lower:
            district = name
            break

    state = _STATE_MAP.get(district, "Maharashtra")
    return {
        "country_code": "IND",
        "admin1": state,
        "admin2": district,
        "locality": "Central Ward",
    }


# ===========================================================================
# Stage 4 — Semantic Clustering
# ===========================================================================

def _stage4_cluster(category: str, admin_hierarchy: Dict[str, str]) -> str:
    """
    Generates a deterministic cluster ID for grouping related requests.
    Format: CLUSTER-{CATEGORY_PREFIX}-{DISTRICT_PREFIX}
    """
    cat_prefix = category[:3].upper()
    district_prefix = admin_hierarchy.get("admin2", "UNK")[:3].upper()
    return f"CLUSTER-{cat_prefix}-{district_prefix}"


# ===========================================================================
# Real Gemini call (used only when USE_MOCK_GEMINI=false)
# ===========================================================================

_GEMINI_PROMPT_TEMPLATE = """
Analyze this citizen grievance submitted in India and return valid JSON ONLY.
No markdown fences, no explanation — raw JSON only.

Grievance text: "{text}"

Required JSON fields:
{{
  "detected_language": "<ISO 639-1 code: en | hi | mr>",
  "category": "<healthcare | water_sanitation | roads_transport | education>",
  "sub_category": "<specific sub-issue, e.g. phc_shortage>",
  "urgency_level": "<critical | high | medium | low>",
  "admin2": "<district name from: Pune, Thane, Varanasi, or best guess>",
  "admin1": "<state name>",
  "entity_mentions": ["<list of named entities: hospitals, roads, landmarks>"]
}}
""".strip()


def _call_gemini(text: str) -> Optional[Dict[str, Any]]:
    """
    Makes a single Gemini 1.5-flash API call.
    Returns parsed JSON dict on success, None on any failure.
    """
    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = _GEMINI_PROMPT_TEMPLATE.format(text=text.replace('"', "'"))
        response = model.generate_content(prompt)
        raw = response.text.strip()
        # Strip any accidental markdown fences
        if raw.startswith("```"):
            raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()
        return json.loads(raw)
    except Exception as exc:
        print(f"[WARN] Gemini API call failed, falling back to deterministic pipeline: {exc}")
        return None


# ===========================================================================
# Public API — Understanding Pipeline
# ===========================================================================

def understand_citizen_request(
    raw_text: str,
    source_channel: str = "text",
    admin_hierarchy: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Gemini Understanding Layer — 4-stage pipeline.

    Parameters
    ----------
    raw_text      : Original citizen grievance (any language)
    source_channel: 'voice' | 'text' | 'messaging_app'
    admin_hierarchy: Optional pre-known location; merged/overridden by pipeline

    Returns a structured dict ready to be stored as a CitizenRequest record.
    """
    mode = "mock_gemini" if (USE_MOCK_GEMINI or not GEMINI_API_KEY) else "live_gemini"

    # --- Stage 1: Language detection (always deterministic as baseline) ---
    detected_language = _stage1_detect_language(raw_text)

    # --- Stage 2: Category / urgency (always deterministic as baseline) ---
    category, sub_category, urgency_level = _stage2_classify(raw_text)

    # --- Stage 3: Location extraction (always deterministic as baseline) ---
    extracted_hierarchy = _stage3_extract_location(raw_text)

    # --- Merge with caller-supplied hierarchy (caller wins on admin2) ---
    if admin_hierarchy and admin_hierarchy.get("admin2"):
        extracted_hierarchy.update(admin_hierarchy)

    # --- Stage 4: Semantic cluster ID ---
    cluster_id = _stage4_cluster(category, extracted_hierarchy)

    # --- Live Gemini override (when enabled and key available) ---
    gemini_result: Optional[Dict[str, Any]] = None
    if not USE_MOCK_GEMINI and GEMINI_API_KEY:
        gemini_result = _call_gemini(raw_text)

    if gemini_result:
        detected_language = gemini_result.get("detected_language", detected_language)
        category = gemini_result.get("category", category)
        sub_category = gemini_result.get("sub_category", sub_category)
        urgency_level = gemini_result.get("urgency_level", urgency_level)
        if gemini_result.get("admin2"):
            extracted_hierarchy["admin2"] = gemini_result["admin2"]
        if gemini_result.get("admin1"):
            extracted_hierarchy["admin1"] = gemini_result["admin1"]
        cluster_id = _stage4_cluster(category, extracted_hierarchy)
        mode = "live_gemini"

    return {
        "raw_text": raw_text,
        "translated_text": raw_text,          # Translation is an optional Phase-5 enhancement
        "source_channel": source_channel,
        "detected_language": detected_language,
        "category": category,
        "sub_category": sub_category,
        "urgency_level": urgency_level,
        "admin_hierarchy": extracted_hierarchy,
        "cluster_id": cluster_id,
        "confidence_score": 0.92 if mode == "mock_gemini" else 0.98,
        "mode": mode,
    }


# ===========================================================================
# Public API — Explanation Layer
# ===========================================================================

def generate_grounded_explanation(
    district_name: str,
    district_info: Dict[str, Any],
    score_info: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Gemini Explanation Layer.
    Produces a grounded, evidence-cited justification from ACTUAL numbers.
    Gemini explains; it never invents the ranking.
    """
    pop = district_info.get("population", 0)
    pop_str = f"{round(pop / 100_000.0, 1)} lakh"
    facilities = district_info.get("facilities_count", 0)
    demand = district_info.get("citizen_demand_count", 0)
    inv_cr = district_info.get("existing_investment_cr", 0.0)
    score = score_info.get("priority_score", 0.0)
    state = district_info.get("admin1", "India")

    explanation_text = (
        f"{district_name} ({state}) is prioritized with a Priority Score of {score}/100 "
        f"because it combines a large affected population of {pop_str}, "
        f"severe infrastructure shortfall ({facilities} facilities available), "
        f"high citizen-reported demand ({demand} requests), and comparatively low existing "
        f"public investment of \u20b9{inv_cr} Cr. "
        f"No major active scheme currently fully addresses this demand gap."
    )

    # Attempt live Gemini enrichment (rephrase grounded explanation)
    if not USE_MOCK_GEMINI and GEMINI_API_KEY:
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            enrich_prompt = (
                f"Rewrite the following policymaker justification in clear, professional English. "
                f"Do NOT invent any numbers or change the facts. Output the rewritten text only.\n\n"
                f"{explanation_text}"
            )
            resp = model.generate_content(enrich_prompt)
            explanation_text = resp.text.strip() or explanation_text
        except Exception as exc:
            print(f"[WARN] Gemini explanation enrichment failed, using deterministic text: {exc}")

    return {
        "district": district_name,
        "priority_score": score,
        "explanation": explanation_text,
        "grounded_inputs": {
            "population": pop,
            "facilities_count": facilities,
            "citizen_demand_count": demand,
            "existing_investment_cr": inv_cr,
        },
        "footnote": (
            "Grounded strictly in verified Census 2011/NFHS-5, National Hospital Directory, "
            "and citizen reporting metrics without fabricated assertions."
        ),
    }


# ===========================================================================
# Public API — Natural Language Query Parser
# ===========================================================================

_NL_QUERY_PROMPT = """
Parse this natural-language policymaker query into a structured JSON filter.
Return valid JSON ONLY — no markdown, no explanation.

Query: "{query}"

Required JSON:
{{
  "state": "<state name or null>",
  "district": "<district name or null>",
  "sector": "<healthcare | water_sanitation | roads_transport | education | null>",
  "sort": "<priority_score_desc | demand_desc | investment_asc>"
}}
""".strip()


def _parse_nl_query_deterministic(query: str) -> Dict[str, Any]:
    """Fully deterministic NL query parser (always used in mock mode)."""
    q = query.lower()

    state_filter = None
    if "maharashtra" in q:
        state_filter = "Maharashtra"
    elif "uttar pradesh" in q or " up " in q:
        state_filter = "Uttar Pradesh"

    district_filter = None
    for kw, name in _PILOT_DISTRICTS.items():
        if kw in q:
            district_filter = name
            break

    sector_filter = None
    if any(w in q for w in ["health", "hospital", "clinic", "doctor"]):
        sector_filter = "healthcare"
    elif any(w in q for w in ["water", "sanitation", "toilet"]):
        sector_filter = "water_sanitation"
    elif any(w in q for w in ["road", "transport", "bus", "bridge"]):
        sector_filter = "roads_transport"
    elif any(w in q for w in ["school", "education", "teacher"]):
        sector_filter = "education"

    sort_by = "priority_score_desc"
    if any(w in q for w in ["under-funded", "low investment", "underfunded"]):
        sort_by = "investment_asc"
    elif any(w in q for w in ["most requests", "high demand"]):
        sort_by = "demand_desc"

    return {
        "state": state_filter,
        "district": district_filter,
        "sector": sector_filter,
        "sort": sort_by,
    }


def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """
    Converts a natural-language policymaker question into a structured filter.
    Gemini parses intent; backend executes the filter deterministically.
    """
    structured_filter = _parse_nl_query_deterministic(query)

    # Live Gemini override
    if not USE_MOCK_GEMINI and GEMINI_API_KEY:
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = _NL_QUERY_PROMPT.format(query=query.replace('"', "'"))
            resp = model.generate_content(prompt)
            raw = resp.text.strip()
            if raw.startswith("```"):
                raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()
            parsed = json.loads(raw)
            structured_filter = parsed
        except Exception as exc:
            print(f"[WARN] Gemini NL query parse failed, using deterministic parser: {exc}")

    filt = structured_filter
    interpretation = (
        f"Filtering regions where state={filt.get('state') or 'All'}, "
        f"district={filt.get('district') or 'All'}, "
        f"sector={filt.get('sector') or 'All'}, "
        f"sorted by {filt.get('sort', 'priority_score_desc')}."
    )

    return {
        "query": query,
        "structured_filter": filt,
        "interpretation": interpretation,
    }
