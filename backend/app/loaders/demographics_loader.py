import os
import json
from typing import List, Dict, Any

DEFAULT_DEMOGRAPHICS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../data/raw/demographics_pilot.json")
)

def load_demographics(file_path: str = DEFAULT_DEMOGRAPHICS_PATH) -> List[Dict[str, Any]]:
    """
    Loads district demographic data from Census 2011 + NFHS-5 projections.
    Normalizes into the demographics schema.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Demographics file not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    normalized = []
    for item in data:
        record = {
            "region_id": item["region_id"],
            "admin_hierarchy": item["admin_hierarchy"],
            "population_total": item["population_total"],
            "population_rural": item.get("population_rural", 0),
            "population_urban": item.get("population_urban", 0),
            "vulnerability_index": item.get("vulnerability_index", 0.5),
            "census_year": item.get("census_year", 2011),
            "projection_source": item.get("projection_source", "NFHS-5 (2019-21)"),
            "source": item.get("source", "Census 2011 & NFHS-5"),
            "source_url": item.get("source_url", "https://censusindia.gov.in"),
            "retrieved_at": item.get("retrieved_at"),
            "data_quality": item.get("data_quality", "real")
        }
        normalized.append(record)

    return normalized
