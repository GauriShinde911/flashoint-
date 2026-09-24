import pytest
from backend.engine.scoring import calculate_priority_score
from backend.engine.silent_need_detector import detect_silent_needs
from backend.engine.mismatch_detector import detect_investment_mismatches
from backend.engine.project_check import check_existing_projects

def test_worked_sanity_check_district_c_a_b():
    """
    Validates the worked example from DATASET_GUIDE.md Section 3.
    MUST assert relative priority score order: District C > District A > District B.
    """
    # District A: Pop 12 Lakh, Hospitals 8, Gap High (0.75), Existing Investment ₹10 Cr, Demand 185
    dist_a = calculate_priority_score(
        population=1200000,
        facilities_count=8,
        citizen_demand_count=185,
        existing_investment_cr=10.0,
        infra_deficit_score=0.75,
        accessibility_score=0.60
    )

    # District B: Pop 8 Lakh, Hospitals 12, Gap Low (0.25), Existing Investment ₹18 Cr, Demand 42
    dist_b = calculate_priority_score(
        population=800000,
        facilities_count=12,
        citizen_demand_count=42,
        existing_investment_cr=18.0,
        infra_deficit_score=0.25,
        accessibility_score=0.30
    )

    # District C: Pop 15 Lakh, Hospitals 5, Gap High (0.90), Existing Investment ₹6 Cr, Demand 231
    dist_c = calculate_priority_score(
        population=1500000,
        facilities_count=5,
        citizen_demand_count=231,
        existing_investment_cr=6.0,
        infra_deficit_score=0.90,
        accessibility_score=0.75
    )

    score_a = dist_a["priority_score"]
    score_b = dist_b["priority_score"]
    score_c = dist_c["priority_score"]

    print(f"District C Score: {score_c}")
    print(f"District A Score: {score_a}")
    print(f"District B Score: {score_b}")

    # Core spec assertion: C > A > B
    assert score_c > score_a, f"District C ({score_c}) must score higher than District A ({score_a})"
    assert score_a > score_b, f"District A ({score_a}) must score higher than District B ({score_b})"

    # Breakdown verification
    assert "breakdown" in dist_c
    assert "weights_used" in dist_c
    assert dist_c["breakdown"]["demand"]["raw"] == 231

def test_silent_need_detector():
    districts_data = [
        {
            "admin2": "District C",
            "population": 1500000,
            "facilities_count": 5,
            "citizen_demand_count": 30,  # Low demand despite high pop & few facilities
            "infra_deficit_score": 0.90
        },
        {
            "admin2": "District B",
            "population": 800000,
            "facilities_count": 12,
            "citizen_demand_count": 42,
            "infra_deficit_score": 0.25
        }
    ]

    silent = detect_silent_needs(districts_data)
    assert len(silent) == 1
    assert silent[0]["district"] == "District C"
    assert "Potential digital divide" in silent[0]["reason"]

def test_investment_mismatch_detector():
    districts_data = [
        {
            "admin2": "District C",
            "existing_investment_cr": 6.0,
            "citizen_demand_count": 231,
            "facilities_count": 5
        },
        {
            "admin2": "District B",
            "existing_investment_cr": 18.0,
            "citizen_demand_count": 42,
            "facilities_count": 12
        }
    ]

    mismatches = detect_investment_mismatches(districts_data)
    assert len(mismatches) == 2
    types = [m["mismatch_type"] for m in mismatches]
    assert "UNDER_FUNDED_HIGH_DEMAND" in types
    assert "OVER_FUNDED_LOW_DEMAND" in types

def test_check_existing_projects():
    projects = [
        {
            "project_id": "PROJ-101",
            "name": "Upgrade PHC to CHC",
            "sector": "healthcare",
            "admin_hierarchy": {"admin2": "Pune"},
            "status": "Ongoing",
            "budget_inr_cr": 12.5
        }
    ]

    res_pune = check_existing_projects(admin2="Pune", category="healthcare", projects_list=projects)
    assert res_pune["has_matching_project"] is True
    assert res_pune["status"] == "active_project_found"

    res_varanasi = check_existing_projects(admin2="Varanasi", category="healthcare", projects_list=projects)
    assert res_varanasi["has_matching_project"] is False
    assert res_varanasi["status"] == "gap_unaddressed"
