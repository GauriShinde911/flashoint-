import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.models.schemas import (
    CitizenRequestInput,
    CitizenRequestRecord,
    PriorityRecommendation,
    ProjectImpactResult
)
from backend.app.services.analytics import (
    compute_priority_score,
    detect_silent_need,
    detect_investment_mismatch,
    compute_impact_measurement
)

app = FastAPI(
    title="Development Priority Intelligence API",
    description="Multilingual AI & Deterministic Analytics Platform for Digital Public Infrastructure (Track 1 / BRICS)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
SYNTHETIC_REQUESTS_PATH = os.path.join(DATA_DIR, "synthetic/citizen_requests.json")

# Sample Pilot Datasets (Fusion of Census 2011, NFHS-5, Hospital Directory, Scheme Outlays)
PILOT_DISTRICT_DATA = [
    {
        "region_id": "IND-MH-PUN",
        "district_name": "Pune",
        "state_name": "Maharashtra",
        "sector": "healthcare",
        "population": 9_429_408,  # Census 2011 baseline with NFHS-5 projection
        "facilities_count": 86,
        "infra_gap_level": "High",
        "existing_investment_cr": 14.5,
        "demand_count": 210,
        "lat": 18.5204,
        "lon": 73.8567
    },
    {
        "region_id": "IND-MH-THA",
        "district_name": "Thane",
        "state_name": "Maharashtra",
        "sector": "water_sanitation",
        "population": 11_060_148,
        "facilities_count": 110,
        "infra_gap_level": "High",
        "existing_investment_cr": 6.2,
        "demand_count": 245,
        "lat": 19.2183,
        "lon": 72.9781
    },
    {
        "region_id": "IND-UP-VAR",
        "district_name": "Varanasi",
        "state_name": "Uttar Pradesh",
        "sector": "healthcare",
        "population": 3_676_841,
        "facilities_count": 42,
        "infra_gap_level": "Medium",
        "existing_investment_cr": 22.0,
        "demand_count": 95,
        "lat": 25.3176,
        "lon": 82.9739
    },
    {
        "region_id": "IND-UP-GOR",
        "district_name": "Gorakhpur",
        "state_name": "Uttar Pradesh",
        "sector": "healthcare",
        "population": 4_440_895,
        "facilities_count": 31,
        "infra_gap_level": "High",
        "existing_investment_cr": 5.0,
        "demand_count": 260,
        "lat": 26.7606,
        "lon": 83.3732
    }
]

# Completed Government Infrastructure Projects for Impact Measurement
COMPLETED_PROJECTS = [
    {
        "project_id": "PRJ-NHM-MH-001",
        "project_name": "100-Bed Sub-District Hospital Upgradation",
        "sector": "healthcare",
        "district": "Pune",
        "state": "Maharashtra",
        "completion_date": "2025-06-15",
        "pre_complaints_count": 184,
        "post_complaints_count": 38
    },
    {
        "project_id": "PRJ-JJM-MH-004",
        "project_name": "Rural Piped Drinking Water Network (Phase II)",
        "sector": "water_sanitation",
        "district": "Thane",
        "state": "Maharashtra",
        "completion_date": "2025-03-10",
        "pre_complaints_count": 210,
        "post_complaints_count": 45
    },
    {
        "project_id": "PRJ-PMGSY-UP-009",
        "project_name": "All-Weather Rural Connectivity Arterial Road",
        "sector": "roads_transport",
        "district": "Gorakhpur",
        "state": "Uttar Pradesh",
        "completion_date": "2025-01-20",
        "pre_complaints_count": 142,
        "post_complaints_count": 98
    }
]

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "platform": settings.project_name,
        "version": "1.0.0",
        "dpg_status": "open_digital_public_good",
        "country": settings.default_country
    }

@app.get("/api/v1/requests")
def get_citizen_requests(limit: int = 50, sector: Optional[str] = None):
    if not os.path.exists(SYNTHETIC_REQUESTS_PATH):
        return []
    with open(SYNTHETIC_REQUESTS_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)
    if sector:
        records = [r for r in records if r.get("category") == sector]
    return records[:limit]

@app.get("/api/v1/priorities", response_model=List[PriorityRecommendation])
def get_priority_recommendations():
    recommendations = []
    
    for dist in PILOT_DISTRICT_DATA:
        scoring = compute_priority_score(
            population=dist["population"],
            facilities_count=dist["facilities_count"],
            demand_count=dist["demand_count"],
            existing_investment_cr=dist["existing_investment_cr"],
            infra_gap_level=dist["infra_gap_level"]
        )
        
        score = scoring["priority_score"]
        silent_need = detect_silent_need(
            infra_gap_level=dist["infra_gap_level"],
            demand_count=dist["demand_count"]
        )
        mismatch = detect_investment_mismatch(
            priority_score=score,
            existing_investment_cr=dist["existing_investment_cr"],
            demand_count=dist["demand_count"]
        )
        
        # Grounded explanation formula (Gemini grounded template representation)
        pop_str = f"{round(dist['population'] / 100_000.0, 1)} lakh"
        explanation = (
            f"{dist['district_name']} ({dist['state_name']}) is ranked with priority score {score} for {dist['sector']} "
            f"due to an affected population of {pop_str}, {dist['facilities_count']} facilities against an estimated target, "
            f"{dist['demand_count']} citizen grievance reports, and comparatively low existing investment of ₹{dist['existing_investment_cr']} Cr."
        )
        
        recommendations.append(
            PriorityRecommendation(
                region_id=dist["region_id"],
                district_name=dist["district_name"],
                state_name=dist["state_name"],
                sector=dist["sector"],
                priority_score=score,
                rank=0,
                components={
                    "demand_count": dist["demand_count"],
                    "population_affected": dist["population"],
                    "facilities_count": dist["facilities_count"],
                    "infra_deficit_score": scoring["components"]["infra_deficit_score"],
                    "existing_investment_inr_cr": dist["existing_investment_cr"]
                },
                silent_need_flag=silent_need,
                mismatch_status=mismatch,
                grounded_explanation=explanation,
                data_quality="synthetic"
            )
        )
    
    # Sort deterministically by priority score descending
    recommendations.sort(key=lambda r: r.priority_score, reverse=True)
    for idx, rec in enumerate(recommendations, 1):
        rec.rank = idx
        
    return recommendations

@app.get("/api/v1/impact", response_model=List[ProjectImpactResult])
def get_impact_audit():
    """
    Returns verified Before-vs-After impact audits for completed public infrastructure projects.
    """
    results = []
    for proj in COMPLETED_PROJECTS:
        impact_metrics = compute_impact_measurement(
            pre_complaints=proj["pre_complaints_count"],
            post_complaints=proj["post_complaints_count"]
        )
        results.append(
            ProjectImpactResult(
                project_id=proj["project_id"],
                project_name=proj["project_name"],
                sector=proj["sector"],
                district=proj["district"],
                state=proj["state"],
                completion_date=proj["completion_date"],
                pre_complaints_count=impact_metrics["pre_complaints"],
                post_complaints_count=impact_metrics["post_complaints"],
                impact_percentage=impact_metrics["impact_percentage"],
                verification_status=impact_metrics["verification_status"]
            )
        )
    return results
