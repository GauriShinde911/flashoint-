from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

def parse_iso_timestamp(ts_str: str) -> Optional[datetime]:
    """Parses ISO timestamp string to datetime object."""
    if not ts_str:
        return None
    cleaned = ts_str.rstrip("Z").split(".")[0]
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            pass
    return None

def measure_project_impact(
    project: Dict[str, Any],
    citizen_requests: List[Dict[str, Any]],
    window_days: int = 90
) -> Dict[str, Any]:
    """
    Compares citizen request volume in equal time windows BEFORE vs AFTER a project's completion date.
    Calculates impact metrics and attaches mandatory disclaimer badge text.
    """
    proj_id = project.get("project_id") or project.get("id", "UNKNOWN")
    proj_name = project.get("name", "Unnamed Project")
    status = project.get("status", "")
    completion_date_str = project.get("completion_date")

    if status.lower() != "completed" or not completion_date_str:
        return {
            "project_id": proj_id,
            "project_name": proj_name,
            "status": status,
            "is_measurable": False,
            "reason": "Project is not completed or missing completion date.",
            "disclaimer": "based on available data, not a guarantee"
        }

    completion_dt = parse_iso_timestamp(completion_date_str)
    if not completion_dt:
        return {
            "project_id": proj_id,
            "project_name": proj_name,
            "status": status,
            "is_measurable": False,
            "reason": f"Invalid completion date format: {completion_date_str}",
            "disclaimer": "based on available data, not a guarantee"
        }

    # Define Equal Windows
    pre_start = completion_dt - timedelta(days=window_days)
    pre_end = completion_dt
    post_start = completion_dt
    post_end = completion_dt + timedelta(days=window_days)

    proj_admin2 = (project.get("admin_hierarchy", {}).get("admin2") or project.get("location", "")).lower()
    proj_sector = (project.get("sector") or project.get("category", "")).lower()

    pre_requests = []
    post_requests = []

    for req in citizen_requests:
        req_admin2 = (req.get("admin_hierarchy", {}).get("admin2") or "").lower()
        req_category = (req.get("category") or "").lower()

        # Match region & sector if specified
        if proj_admin2 and req_admin2 and proj_admin2 != req_admin2:
            continue
        if proj_sector and req_category and proj_sector != req_category:
            continue

        req_dt = parse_iso_timestamp(req.get("timestamp"))
        if not req_dt:
            continue

        if pre_start <= req_dt < pre_end:
            pre_requests.append(req)
        elif post_start <= req_dt <= post_end:
            post_requests.append(req)

    pre_count = len(pre_requests)
    post_count = len(post_requests)

    volume_change = post_count - pre_count
    if pre_count > 0:
        pct_change = round(((post_count - pre_count) / pre_count) * 100.0, 2)
    else:
        pct_change = 0.0 if post_count == 0 else 100.0

    if pct_change <= -40.0:
        impact_summary = "Significant Demand Reduction (High Positive Impact)"
    elif pct_change < 0.0:
        impact_summary = "Moderate Demand Reduction (Positive Impact)"
    elif pct_change == 0.0:
        impact_summary = "No Measured Change"
    else:
        impact_summary = "Demand Increased (Persistent / Emerging Need)"

    return {
        "project_id": proj_id,
        "project_name": proj_name,
        "sector": project.get("sector") or project.get("category"),
        "admin2": project.get("admin_hierarchy", {}).get("admin2") or project.get("location"),
        "completion_date": completion_date_str,
        "is_measurable": True,
        "window_days": window_days,
        "window_periods": {
            "pre_window": {"start": pre_start.strftime("%Y-%m-%d"), "end": pre_end.strftime("%Y-%m-%d")},
            "post_window": {"start": post_start.strftime("%Y-%m-%d"), "end": post_end.strftime("%Y-%m-%d")}
        },
        "pre_completion_request_count": pre_count,
        "post_completion_request_count": post_count,
        "volume_change": volume_change,
        "percentage_change": pct_change,
        "impact_summary": impact_summary,
        "data_quality": project.get("data_quality", "synthetic"),
        "disclaimer": "based on available data, not a guarantee"
    }
