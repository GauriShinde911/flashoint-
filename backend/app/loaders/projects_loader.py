import os
import json
from typing import List, Dict, Any

DEFAULT_PROJECTS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../data/synthetic/completed_projects.json")
)

def load_government_projects(file_path: str = DEFAULT_PROJECTS_PATH) -> List[Dict[str, Any]]:
    """
    Loads completed and ongoing public government projects.
    Normalizes into the government_project schema.
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    normalized = []
    for item in data:
        record = {
            "project_id": item["project_id"],
            "name": item["name"],
            "sector": item["sector"],
            "admin_hierarchy": item["admin_hierarchy"],
            "status": item["status"],
            "budget_inr_cr": item.get("budget_inr_cr", 0.0),
            "completion_date": item.get("completion_date"),
            "data_quality": item.get("data_quality", "synthetic"),
            "source": item.get("source", "government_project_portal"),
            "source_url": item.get("source_url"),
            "retrieved_at": item.get("retrieved_at", "2026-09-01T00:00:00Z")
        }
        normalized.append(record)

    return normalized
