import os
import json
from typing import List, Dict, Any

DEFAULT_SYNTHETIC_REQUESTS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../data/synthetic/citizen_requests.json")
)

def load_synthetic_requests(file_path: str = DEFAULT_SYNTHETIC_REQUESTS_PATH) -> List[Dict[str, Any]]:
    """
    Loads synthetic citizen requests from data/synthetic/citizen_requests.json.
    Validates and returns normalized records adhering to the citizen_request schema.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Synthetic requests file not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    normalized = []
    for item in data:
        record = {
            "id": item["id"],
            "timestamp": item["timestamp"],
            "raw_text": item["raw_text"],
            "translated_text": item.get("translated_text", item["raw_text"]),
            "source_channel": item["source_channel"],
            "detected_language": item["detected_language"],
            "category": item["category"],
            "sub_category": item.get("sub_category"),
            "urgency_level": item.get("urgency_level", "medium"),
            "admin_hierarchy": item["admin_hierarchy"],
            "data_quality": item.get("data_quality", "synthetic"),
            "source": item.get("source", "citizen_input"),
            "source_url": item.get("source_url"),
            "retrieved_at": item.get("retrieved_at", item["timestamp"])
        }
        normalized.append(record)

    return normalized
