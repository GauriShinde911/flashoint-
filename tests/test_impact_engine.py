import pytest
from datetime import datetime, timedelta
from backend.engine.impact_engine import measure_project_impact, parse_iso_timestamp
from backend.app.loaders.projects_loader import load_government_projects
from backend.app.loaders.synthetic_requests_loader import load_synthetic_requests

def test_parse_iso_timestamp():
    dt1 = parse_iso_timestamp("2025-10-01T08:30:00Z")
    assert dt1 == datetime(2025, 10, 1, 8, 30, 0)
    dt2 = parse_iso_timestamp("2025-10-01")
    assert dt2 == datetime(2025, 10, 1, 0, 0, 0)
    assert parse_iso_timestamp(None) is None

def test_measure_project_impact_completed():
    completion_date = "2025-10-01"
    comp_dt = datetime(2025, 10, 1)

    project = {
        "project_id": "PROJ-TEST-001",
        "name": "Thane General Hospital Wing",
        "sector": "healthcare",
        "admin_hierarchy": {"admin2": "Thane"},
        "status": "Completed",
        "completion_date": completion_date,
        "data_quality": "synthetic"
    }

    # Generate 10 requests in Pre-window (30 days before completion)
    requests = []
    for i in range(10):
        ts = (comp_dt - timedelta(days=10 + i)).isoformat() + "Z"
        requests.append({
            "id": f"REQ-PRE-{i}",
            "timestamp": ts,
            "category": "healthcare",
            "admin_hierarchy": {"admin2": "Thane"}
        })

    # Generate 2 requests in Post-window (30 days after completion)
    for i in range(2):
        ts = (comp_dt + timedelta(days=10 + i)).isoformat() + "Z"
        requests.append({
            "id": f"REQ-POST-{i}",
            "timestamp": ts,
            "category": "healthcare",
            "admin_hierarchy": {"admin2": "Thane"}
        })

    res = measure_project_impact(project, requests, window_days=90)

    assert res["is_measurable"] is True
    assert res["pre_completion_request_count"] == 10
    assert res["post_completion_request_count"] == 2
    assert res["volume_change"] == -8
    assert res["percentage_change"] == -80.0
    assert res["disclaimer"] == "based on available data, not a guarantee"
    assert "Significant Demand Reduction" in res["impact_summary"]

def test_measure_project_impact_uncompleted():
    project = {
        "project_id": "PROJ-ONGOING-001",
        "name": "Unfinished PHC Building",
        "sector": "healthcare",
        "status": "Ongoing",
        "completion_date": None
    }
    res = measure_project_impact(project, [], window_days=90)
    assert res["is_measurable"] is False
    assert res["disclaimer"] == "based on available data, not a guarantee"

def test_seeded_projects_impact_measurement():
    projects = load_government_projects()
    requests = load_synthetic_requests()

    assert len(projects) >= 3, "Expected at least 3 seeded completed projects"

    completed_projects = [p for p in projects if p.get("status") == "Completed"]
    assert len(completed_projects) >= 3

    for proj in completed_projects:
        res = measure_project_impact(proj, requests, window_days=180)
        assert res["disclaimer"] == "based on available data, not a guarantee"
        assert "window_periods" in res
        assert res["is_measurable"] is True
