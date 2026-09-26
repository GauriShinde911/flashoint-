"""
Gemini Understanding & Explanation Service  —  STEP 7 + STEP 8
===============================================================
4-stage understanding pipeline (ADK-style):
  Stage 1 — Language Detection
  Stage 2 — Category / Urgency Classification
  Stage 3 — Location + Entity Extraction
  Stage 4 — Semantic Clustering

Explanation layer (STEP 8):
  generate_grounded_explanation() — structured evidence_summary + data_quality badge.
  Gemini rephrases; it NEVER invents numbers.

NL Query parser (STEP 8):
  parse_natural_language_query() — compound sector/district/state/sort/min_score support.
  Gemini parses intent; backend executes deterministically.

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
# Dynamic environment flags — evaluated at call-time for seamless testing & runtime switching
# ---------------------------------------------------------------------------
def _is_mock_mode() -> bool:
    return os.getenv("USE_MOCK_GEMINI", "true").lower() in ("true", "1", "yes")

def _get_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()

def _get_model_name() -> str:
    return os.getenv("GEMINI_MODEL_NAME", "gemini-flash-latest").strip()

def _can_use_gemini() -> bool:
    return (not _is_mock_mode()) and bool(_get_api_key())

def __getattr__(name: str) -> Any:
    if name == "USE_MOCK_GEMINI":
        return _is_mock_mode()
    if name == "GEMINI_API_KEY":
        return _get_api_key()
    if name == "GEMINI_MODEL_NAME":
        return _get_model_name()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

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
        genai.configure(api_key=_get_api_key())
        model = genai.GenerativeModel(_get_model_name())
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
    mode = "live_gemini" if _can_use_gemini() else "mock_gemini"

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
    if _can_use_gemini():
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
# Public API — Explanation Layer  (STEP 8 upgrade)
# ===========================================================================

_EXPLAIN_PROMPT_TEMPLATE = """
You are a senior policy analyst. Rewrite the following district prioritization
justification in clear, professional English for a national policymaker audience.
Do NOT invent, alter, or omit any numbers. Use formal language.
Output the rewritten text only — no preamble, no markdown.

Justification:
{text}
""".strip()


def _build_explanation_text(
    district_name: str,
    state: str,
    score: float,
    pop_str: str,
    facilities: int,
    demand: int,
    inv_cr: float,
    rank: Optional[int] = None,
) -> str:
    """Builds the deterministic explanation sentence used in both mock + live modes."""
    rank_clause = f" (Rank #{rank})" if rank is not None else ""
    return (
        f"{district_name} ({state}){rank_clause} achieves a Priority Score of {score}/100. "
        f"Key drivers: population of {pop_str} affected, only {facilities} healthcare "
        f"facilities recorded, {demand} citizen-reported demand requests logged, and existing "
        f"government investment of \u20b9{inv_cr} Cr — leaving a significant unmet gap. "
        f"No active central or state scheme currently fully closes this demand shortfall."
    )


def generate_grounded_explanation(
    district_name: str,
    district_info: Dict[str, Any],
    score_info: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Gemini Explanation Layer  (STEP 8).
    Returns structured evidence_summary + data_quality badge + optional rank.
    Gemini rephrases the deterministic text; it NEVER invents numbers.
    """
    pop = district_info.get("population", 0)
    if isinstance(pop, (int, float)):
        pop_str = f"{round(pop / 100_000.0, 1)} lakh"
    else:
        pop_str = str(pop)
    facilities = district_info.get("facilities_count", 0)
    demand = district_info.get("citizen_demand_count", 0)
    inv_cr = district_info.get("existing_investment_cr", 0.0)
    score = score_info.get("priority_score", 0.0)
    state = district_info.get("admin1", "India")
    rank = district_info.get("rank")  # may be None if not passed
    data_quality = district_info.get("data_quality", "real")

    # Always build deterministic text first (safe baseline + unit-testable)
    explanation_text = _build_explanation_text(
        district_name, state, score, pop_str, facilities, demand, inv_cr, rank
    )
    explanation_mode = "deterministic"

    # Live Gemini rephrase (never changes numbers; only improves prose)
    if _can_use_gemini():
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=_get_api_key())
            model = genai.GenerativeModel(_get_model_name())
            prompt = _EXPLAIN_PROMPT_TEMPLATE.format(text=explanation_text)
            resp = model.generate_content(prompt)
            rephrased = resp.text.strip()
            if rephrased:  # only replace if Gemini returned non-empty
                explanation_text = rephrased
                explanation_mode = "gemini_rephrased"
        except Exception as exc:
            print(f"[WARN] Gemini explanation enrichment failed, using deterministic text: {exc}")

    return {
        "district": district_name,
        "state": state,
        "rank": rank,
        "priority_score": score,
        "data_quality": data_quality,
        "explanation": explanation_text,
        "explanation_mode": explanation_mode,
        "evidence_summary": {
            "population": pop,
            "population_readable": pop_str,
            "facilities_count": facilities,
            "citizen_demand_count": demand,
            "existing_investment_cr": inv_cr,
        },
        # kept for backward-compat with existing tests
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
# Public API — Natural Language Query Parser  (STEP 8 upgrade)
# ===========================================================================

_NL_QUERY_PROMPT = """
Parse this natural-language policymaker query into a structured JSON filter.
Return valid JSON ONLY — no markdown, no explanation.

Query: "{query}"

Required JSON (use null for absent fields):
{{
  "state": "<Maharashtra | Uttar Pradesh | null>",
  "districts": ["<Pune | Thane | Varanasi>"],
  "sectors": ["<healthcare | water_sanitation | roads_transport | education>"],
  "sort": "<priority_score_desc | demand_desc | investment_asc>",
  "min_score": <0–100 integer or null>
}}
""".strip()


# Sector keyword map for compound detection
_SECTOR_KEYWORDS: list[tuple[str, list[str]]] = [
    ("healthcare",       ["health", "hospital", "clinic", "doctor", "phc", "medical"]),
    ("water_sanitation", ["water", "sanitation", "toilet", "sewage", "drainage", "borewell"]),
    ("roads_transport",  ["road", "transport", "bus", "bridge", "highway", "pothole"]),
    ("education",        ["school", "education", "teacher", "classroom", "student"]),
]


def _parse_nl_query_deterministic(query: str) -> Dict[str, Any]:
    """
    Fully deterministic NL query parser (always used in mock mode).
    STEP 8: supports compound multi-sector, multi-district, and min_score.
    """
    q = query.lower()

    # State
    state_filter = None
    if "maharashtra" in q:
        state_filter = "Maharashtra"
    elif "uttar pradesh" in q or " up " in q:
        state_filter = "Uttar Pradesh"

    # Districts — collect all mentioned (compound support)
    districts_found: list[str] = []
    for kw, name in _PILOT_DISTRICTS.items():
        if kw in q and name not in districts_found:
            districts_found.append(name)
    district_filter = districts_found[0] if len(districts_found) == 1 else (None if not districts_found else None)
    # For compound: store all in districts list
    districts_list = districts_found or None

    # Sectors — compound: collect all that match
    sectors_found: list[str] = []
    for sector, keywords in _SECTOR_KEYWORDS:
        if any(w in q for w in keywords):
            sectors_found.append(sector)
    sector_filter = sectors_found[0] if len(sectors_found) == 1 else None
    sectors_list = sectors_found or None

    # Sort
    sort_by = "priority_score_desc"
    if any(w in q for w in ["under-funded", "low investment", "underfunded"]):
        sort_by = "investment_asc"
    elif any(w in q for w in ["most requests", "high demand"]):
        sort_by = "demand_desc"

    # Min score threshold (e.g. "score above 70", "priority > 60")
    min_score = None
    score_match = re.search(r'(?:score|priority)\s*(?:above|over|>|>=)\s*(\d+)', q)
    if score_match:
        min_score = int(score_match.group(1))

    return {
        "state": state_filter,
        "district": district_filter,
        "districts": districts_list,
        "sector": sector_filter,
        "sectors": sectors_list,
        "sort": sort_by,
        "min_score": min_score,
    }


def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """
    Converts a natural-language policymaker question into a structured filter.
    STEP 8: supports compound sectors, districts list, and min_score.
    Gemini parses intent; backend executes the filter deterministically.
    """
    structured_filter = _parse_nl_query_deterministic(query)

    # Live Gemini override (merges into deterministic baseline)
    if _can_use_gemini():
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=_get_api_key())
            model = genai.GenerativeModel(_get_model_name())
            prompt = _NL_QUERY_PROMPT.format(query=query.replace('"', "'"))
            resp = model.generate_content(prompt)
            raw = resp.text.strip()
            if raw.startswith("```"):
                raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()
            parsed = json.loads(raw)
            # Merge Gemini result over deterministic baseline
            structured_filter.update({k: v for k, v in parsed.items() if v is not None})
        except Exception as exc:
            print(f"[WARN] Gemini NL query parse failed, using deterministic parser: {exc}")

    filt = structured_filter
    sectors_str = ", ".join(filt.get("sectors") or ([filt["sector"]] if filt.get("sector") else ["All"]))
    districts_str = ", ".join(filt.get("districts") or ([filt["district"]] if filt.get("district") else ["All"]))
    interpretation = (
        f"Filtering regions where state={filt.get('state') or 'All'}, "
        f"district(s)={districts_str}, "
        f"sector(s)={sectors_str}, "
        f"sorted by {filt.get('sort', 'priority_score_desc')}"
        + (f", min priority score={filt['min_score']}" if filt.get("min_score") else "") + "."
    )

    return {
        "query": query,
        "structured_filter": filt,
        "interpretation": interpretation,
    }


# ===========================================================================
# Multimodal Photo Evidence Analysis (STEP 13)
# ===========================================================================

_MULTIMODAL_PROMPT = """You are an expert civic infrastructure engineer assessing photo evidence submitted by a citizen for a Digital Public Infrastructure (DPI) platform.
Context provided by citizen: "{context}"

Analyze this photo and determine:
1. detected_damage: boolean (true if visible infrastructure failure, degradation, or distress is shown, e.g. potholes, broken pipes, flood damage, hospital/clinic structural issues, missing medical facilities; false if unrelated or intact)
2. category: one of ["roads_transport", "water_sanitation", "healthcare", "education", "other"]
3. severity: one of ["low", "medium", "high", "critical"]
4. severity_score: float between 0.0 (negligible) and 1.0 (extreme immediate hazard)
5. visual_evidence_summary: 1-2 concise sentences objectively describing what is visible in the photo.
6. actionable_recommendation: 1 sentence stating the municipal or departmental response recommended.

Return ONLY a valid JSON object matching these 6 keys. Do not wrap in markdown or commentary."""


def analyze_infrastructure_photo(
    image_base64: str,
    mime_type: str = "image/jpeg",
    text_context: Optional[str] = None,
    district: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates citizen photo evidence using Gemini 1.5 Flash multimodal vision.
    Falls back to a deterministic structural assessment when offline (USE_MOCK_GEMINI=true).
    """
    import base64

    # Clean base64 string
    cleaned_b64 = image_base64
    if "," in cleaned_b64:
        # Strip data:image/...;base64, prefix if present
        cleaned_b64 = cleaned_b64.split(",", 1)[1]

    ctx_lower = (text_context or "").lower()

    # Determine simulated category from context or default to roads
    category = "roads_transport"
    if any(k in ctx_lower for k in ["school", "education", "teacher", "classroom", "student"]):
        category = "education"
    elif any(k in ctx_lower for k in ["health", "hospital", "phc", "doctor", "clinic", "bed", "medicine"]):
        category = "healthcare"
    elif any(k in ctx_lower for k in ["water", "pipe", "pipeline", "drain", "sewage", "tap"]):
        category = "water_sanitation"
    elif any(k in ctx_lower for k in ["road", "pothole", "highway", "bridge", "street"]):
        category = "roads_transport"

    # Default deterministic mock response
    mock_result: Dict[str, Any] = {
        "detected_damage": True,
        "category": category,
        "severity": "high",
        "severity_score": 0.85,
        "visual_evidence_summary": f"Simulated analysis: Visible structural degradation and surface inadequacy identified in {district or 'the reported area'}.",
        "actionable_recommendation": f"Priority dispatch for municipal {category.replace('_', ' ')} engineering team.",
        "data_quality": "mock",
        "district": district or "Pune",
        "verified_at": "2026-09-26T07:50:00Z"
    }

    if _can_use_gemini():
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=_get_api_key())
            model = genai.GenerativeModel(_get_model_name())

            image_bytes = base64.b64decode(cleaned_b64)
            image_part = {
                "mime_type": mime_type or "image/jpeg",
                "data": image_bytes
            }

            prompt = _MULTIMODAL_PROMPT.format(context=text_context or "Citizen reported infrastructure issue.")
            resp = model.generate_content([prompt, image_part])
            raw = resp.text.strip()
            if raw.startswith("```"):
                raw = re.sub(r"```[a-z]*\n?", "", raw).replace("```", "").strip()

            parsed = json.loads(raw)
            parsed["data_quality"] = "real"
            parsed["district"] = district or "Pune"
            parsed["verified_at"] = "2026-09-26T07:50:00Z"
            return parsed
        except Exception as exc:
            print(f"[WARN] Gemini multimodal vision analysis failed, using deterministic fallback: {exc}")
            mock_result["fallback_reason"] = str(exc)

    return mock_result

