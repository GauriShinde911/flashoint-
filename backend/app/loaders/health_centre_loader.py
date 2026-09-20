import os
import json
from typing import List, Dict, Any

DEFAULT_HEALTH_CENTRES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../data/raw/health_centres_pilot.json")
)

def load_health_centres(file_path: str = DEFAULT_HEALTH_CENTRES_PATH) -> List[Dict[str, Any]]:
    """
    Loads geo-coded PHCs/CHCs from the All India Health Centres Directory.
    Normalizes into the infrastructure_facility schema.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Health centres file not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    normalized = []
    for item in data:
        record = {
            "facility_id": item["facility_id"],
            "name": item["name"],
            "category": "healthcare",
            "facility_type": item.get("facility_type", "Health Centre"),
            "admin_hierarchy": item["admin_hierarchy"],
            "status": item.get("status", "operational"),
            "source": item.get("source", "All India Health Centres Directory (data.gov.in)"),
            "source_url": item.get("source_url", "https://data.gov.in"),
            "retrieved_at": item.get("retrieved_at"),
            "data_quality": item.get("data_quality", "real")
        }
        normalized.append(record)

    return normalized
