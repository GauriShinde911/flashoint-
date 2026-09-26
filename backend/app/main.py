import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Literal
from fastapi import FastAPI, HTTPException, Query, Body, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.config import settings
from backend.app.storage import get_storage
from backend.engine.scoring import calculate_priority_score
from backend.engine.silent_need_detector import detect_silent_needs
from backend.engine.mismatch_detector import detect_investment_mismatches
from backend.engine.project_check import check_existing_projects
from backend.engine.impact_engine import measure_project_impact
from backend.services.gemini_service import (
    understand_citizen_request,
    generate_grounded_explanation,
    parse_natural_language_query,
    analyze_infrastructure_photo
)

app = FastAPI(
    title="Development Priority Intelligence API",
    description="Multilingual AI & Deterministic Analytics Platform for Digital Public Infrastructure (Track 1 / BRICS)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models with Strict Pydantic Validation
class SubmitRequestModel(BaseModel):
    raw_text: str = Field(..., min_length=1, max_length=2000, description="Raw text of citizen request")
    source_channel: Optional[Literal["voice", "text", "messaging_app"]] = Field(
        default="text", description="Channel through which request was submitted"
    )
    detected_language: Optional[str] = Field(default=None, max_length=10)
    district: Optional[str] = Field(default="Pune", max_length=100)

class QueryModel(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural language search query")

class AnalyzePhotoModel(BaseModel):
    image_base64: str = Field(..., min_length=10, description="Base64 encoded photo")
    mime_type: Optional[str] = Field(default="image/jpeg", max_length=50)
    text_context: Optional[str] = Field(default=None, max_length=1000)
    district: Optional[str] = Field(default="Pune", max_length=100)

# Helper to aggregate district metrics from storage
def get_district_aggregates():
    store = get_storage()
    demos_list = [store.get_demographics("Pune"), store.get_demographics("Thane"), store.get_demographics("Varanasi")]
    all_demographics = {}
    for d in demos_list:
        if d:
            admin2_name = d.get("admin_hierarchy", {}).get("admin2") or d.get("admin2") or d.get("region_id")
            if admin2_name:
                all_demographics[admin2_name] = d

    all_facilities = store.get_infrastructure_facilities()
    all_requests = store.get_citizen_requests(limit=1000)
    all_projects = store.get_government_projects()

    pilot_districts = [
        {"district_name": "Pune", "state_name": "Maharashtra", "lat": 18.5204, "lon": 73.8567, "investment_cr": 14.5},
        {"district_name": "Thane", "state_name": "Maharashtra", "lat": 19.2403, "lon": 73.1305, "investment_cr": 6.2},
        {"district_name": "Varanasi", "state_name": "Uttar Pradesh", "lat": 25.3176, "lon": 82.9739, "investment_cr": 22.0},
    ]

    aggregated = []
    for pd in pilot_districts:
        dname = pd["district_name"]
        demo = all_demographics.get(dname, {})
        pop = demo.get("population_total") or demo.get("total_population") or 5000000

        fac_count = len([f for f in all_facilities if f.get("admin_hierarchy", {}).get("admin2") == dname])
        req_count = len([r for r in all_requests if r.get("admin_hierarchy", {}).get("admin2") == dname])
        inv = pd["investment_cr"]

        # Priority scoring
        score_res = calculate_priority_score(
            population=pop,
            facilities_count=fac_count,
            citizen_demand_count=req_count,
            existing_investment_cr=inv
        )

        # Existing project check
        proj_res = check_existing_projects(admin2=dname, category="healthcare", projects_list=all_projects)

        aggregated.append({
            "district_id": f"IND-{pd['state_name'][:2].upper()}-{dname[:3].upper()}",
            "district_name": dname,
            "admin2": dname,
            "admin1": pd["state_name"],
            "sector": "healthcare",
            "population": pop,
            "facilities_count": fac_count,
            "citizen_demand_count": req_count,
            "existing_investment_cr": inv,
            "priority_score": score_res["priority_score"],
            "score_breakdown": score_res["breakdown"],
            "weights_used": score_res["weights_used"],
            "existing_project_status": proj_res["status"],
            "matching_projects": proj_res["projects"],
            "lat": pd["lat"],
            "lon": pd["lon"],
            "data_quality": "real" if fac_count > 0 else "synthetic"
        })

    # Sort deterministically by priority score descending
    aggregated.sort(key=lambda x: x["priority_score"], reverse=True)
    for idx, item in enumerate(aggregated, 1):
        item["rank"] = idx

    return aggregated

# Modular API Router
api_router = APIRouter()

@api_router.get("/health")
@api_router.get("/api/health")
def health_check():
    return {
        "status": "online",
        "platform": settings.project_name,
        "version": "1.0.0",
        "dpg_status": "open_digital_public_good",
        "country": settings.default_country
    }

@api_router.get("/districts")
def get_ranked_districts(sector: Optional[str] = None, data_quality: Optional[str] = None):
    districts = get_district_aggregates()
    if data_quality and data_quality != "all":
        districts = [d for d in districts if d.get("data_quality") == data_quality]
    return districts

@api_router.get("/districts/{district_id}")
def get_district_detail(district_id: str):
    districts = get_district_aggregates()
    for d in districts:
        if d["district_name"].lower() == district_id.lower() or d["district_id"].lower() == district_id.lower():
            return d
    raise HTTPException(status_code=404, detail="District not found")

@api_router.get("/explain/{district_name}")
def explain_district(district_name: str):
    districts = get_district_aggregates()
    for d in districts:
        if d["district_name"].lower() == district_name.lower():
            score_info = {"priority_score": d["priority_score"]}
            return generate_grounded_explanation(d["district_name"], d, score_info)
    raise HTTPException(status_code=404, detail="District not found for explanation")

@api_router.post("/requests")
def submit_citizen_request(req_data: SubmitRequestModel):
    store = get_storage()
    understanding = understand_citizen_request(
        raw_text=req_data.raw_text,
        source_channel=req_data.source_channel or "text"
    )

    district_name = req_data.district or understanding["admin_hierarchy"]["admin2"]
    state_name = "Maharashtra" if district_name in ["Pune", "Thane"] else "Uttar Pradesh"

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record = {
        "id": f"REQ-SYNTH-{str(uuid.uuid4())[:8].upper()}",
        "timestamp": now_iso,
        "raw_text": req_data.raw_text,
        "translated_text": understanding.get("translated_text", req_data.raw_text),
        "source_channel": req_data.source_channel or "text",
        "detected_language": req_data.detected_language or understanding["detected_language"],
        "category": understanding["category"],
        "sub_category": understanding["sub_category"],
        "urgency_level": understanding["urgency_level"],
        "admin_hierarchy": {
            "country_code": "IND",
            "admin1": state_name,
            "admin2": district_name,
            "locality": "Central Ward"
        },
        "cluster_id": understanding["cluster_id"],
        "data_quality": "synthetic",
        "source": "citizen_input",
        "source_url": None,
        "retrieved_at": now_iso
    }

    store.save_citizen_request(record)
    return {
        "status": "success",
        "message": "Citizen request processed and stored.",
        "analysis": understanding,
        "record": record
    }

@api_router.get("/requests")
def list_citizen_requests(limit: int = 100, category: Optional[str] = None, admin2: Optional[str] = None):
    store = get_storage()
    return store.get_citizen_requests(limit=limit, category=category, admin2=admin2)

@api_router.post("/query")
def natural_language_query(query_data: QueryModel):
    parsed = parse_natural_language_query(query_data.query)
    districts = get_district_aggregates()
    filt = parsed["structured_filter"]

    results = districts

    # State filter
    if filt.get("state"):
        results = [r for r in results if r["admin1"].lower() == filt["state"].lower()]

    # District filter (single or compound districts list)
    if filt.get("districts"):
        allowed = [d.lower() for d in filt["districts"]]
        results = [r for r in results if r["district_name"].lower() in allowed]
    elif filt.get("district"):
        results = [r for r in results if r["district_name"].lower() == filt["district"].lower()]

    # Sector filter (single or compound sectors list)
    if filt.get("sectors"):
        allowed_s = [s.lower() for s in filt["sectors"]]
        results = [r for r in results if r.get("sector", "").lower() in allowed_s]
    elif filt.get("sector"):
        results = [r for r in results if r.get("sector", "").lower() == filt["sector"].lower()]

    # Min score filter
    if filt.get("min_score") is not None:
        results = [r for r in results if r["priority_score"] >= filt["min_score"]]

    # Sort
    sort_key = filt.get("sort", "priority_score_desc")
    if sort_key == "demand_desc":
        results = sorted(results, key=lambda x: x.get("citizen_demand_count", 0), reverse=True)
    elif sort_key == "investment_asc":
        results = sorted(results, key=lambda x: x.get("existing_investment_cr", 0))
    else:  # priority_score_desc (default)
        results = sorted(results, key=lambda x: x["priority_score"], reverse=True)

    return {
        "query": query_data.query,
        "structured_filter": filt,
        "interpretation": parsed["interpretation"],
        "result_count": len(results),
        "results": results
    }

@api_router.get("/silent-needs")
def get_silent_needs():
    districts = get_district_aggregates()
    return detect_silent_needs(districts)

@api_router.get("/mismatches")
def get_mismatches():
    districts = get_district_aggregates()
    return detect_investment_mismatches(districts)

@api_router.get("/impact")
def get_impact():
    store = get_storage()
    projects = store.get_government_projects()
    requests = store.get_citizen_requests(limit=1000)

    results = []
    for proj in projects:
        imp = measure_project_impact(proj, requests, window_days=180)
        results.append(imp)
    return results

@api_router.get("/datasets")
def get_dataset_metadata():
    store = get_storage()
    versions = store.get_dataset_versions()
    return {
        "datasets": versions,
        "census_honesty_note": "Population figures sourced from Census 2011 (last published) and NFHS-5 district estimates; India's next census is in progress as of 2026 and not yet released."
    }

@api_router.post("/analyze-photo")
def analyze_photo_endpoint(payload: AnalyzePhotoModel):
    """
    Evaluates citizen photo evidence using Gemini 1.5 Flash multimodal vision.
    Returns damage detection, category tag, severity score, and visual evidence summary.
    """
    result = analyze_infrastructure_photo(
        image_base64=payload.image_base64,
        mime_type=payload.mime_type or "image/jpeg",
        text_context=payload.text_context,
        district=payload.district or "Pune"
    )
    return result

# Include router for both /api/v1 prefix and legacy root prefix
app.include_router(api_router, prefix="/api/v1", tags=["v1"])
app.include_router(api_router, prefix="", tags=["legacy"])

