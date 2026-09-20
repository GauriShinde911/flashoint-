import os
import json
from typing import List, Dict, Any

DEFAULT_HOSPITALS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../data/raw/hospitals_pilot.json")
)

def load_hospitals(file_path: str = DEFAULT_HOSPITALS_PATH) -> List[Dict[str, Any]]:
    """
    Loads geo-coded hospitals from the National Hospital Directory.
    Normalizes into the infrastructure_facility schema.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Hospitals file not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    normalized = []
    for item in data:
        record = {
            "facility_id": item["facility_id"],
            "name": item["name"],
            "category": "healthcare",
            "facility_type": item.get("facility_type", "Hospital"),
            "admin_hierarchy": item["admin_hierarchy"],
            "status": item.get("status", "operational"),
            "source": item.get("source", "National Hospital Directory (data.gov.in)"),
            "source_url": item.get("source_url", "https://data.gov.in"),
            "retrieved_at": item.get("retrieved_at"),
            "data_quality": item.get("data_quality", "real")
        }
        normalized.append(record)

    return normalized
