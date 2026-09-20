from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class AdminHierarchy(BaseModel):
    country_code: str = "IND"
    admin1: str
    admin2: str
    admin3: Optional[str] = None
    locality: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CitizenRequestInput(BaseModel):
    raw_text: str
    source_channel: str = "voice_web_speech"
    language_hint: Optional[str] = None
    admin_hierarchy: AdminHierarchy
    photo_evidence_url: Optional[str] = None

class CitizenRequestRecord(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    raw_text: str
    translated_text: str
    source_channel: str
    detected_language: str
    category: str
    sub_category: Optional[str] = None
    urgency_level: str = "medium"
    admin_hierarchy: AdminHierarchy
    cluster_id: Optional[str] = None
    data_quality: str = "synthetic"  # 'real' | 'synthetic'

class PriorityScoreComponents(BaseModel):
    demand_count: int
    population_affected: int
    facilities_count: int
    infra_deficit_score: float
    existing_investment_inr_cr: float

class PriorityRecommendation(BaseModel):
    region_id: str
    district_name: str
    state_name: str
    sector: str
    priority_score: float
    rank: int
    components: PriorityScoreComponents
    silent_need_flag: bool
    mismatch_status: str
    grounded_explanation: str
    data_quality: str = "synthetic"

class ProjectImpactResult(BaseModel):
    project_id: str
    project_name: str
    sector: str
    district: str
    state: str
    completion_date: str
    pre_complaints_count: int
    post_complaints_count: int
    impact_percentage: float
    verification_status: str
    data_disclaimer: str = "Based on available post-commissioning reporting data; not a guaranteed forecast."
