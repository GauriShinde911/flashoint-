"""
Sanity check script for Development Priority Intelligence Priority Scoring Engine.
Tests the worked example from DATASET_GUIDE.md:
  District A: 12 lakh pop, 8 hospitals, High gap, Rs 10 Cr investment, 185 requests
  District B: 8 lakh pop, 12 hospitals, Low gap, Rs 18 Cr investment, 42 requests
  District C: 15 lakh pop, 5 hospitals, High gap, Rs 6 Cr investment, 231 requests

Expected Ordering:
  District C (Highest Priority) > District A > District B (Lowest Priority)
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.services.analytics import compute_priority_score

def run_sanity_check():
    districts = {
        "District A": {
            "population": 1_200_000,
            "facilities_count": 8,
            "infra_gap_level": "High",
            "existing_investment_cr": 10.0,
            "demand_count": 185
        },
        "District B": {
            "population": 800_000,
            "facilities_count": 12,
            "infra_gap_level": "Low",
            "existing_investment_cr": 18.0,
            "demand_count": 42
        },
        "District C": {
            "population": 1_500_000,
            "facilities_count": 5,
            "infra_gap_level": "High",
            "existing_investment_cr": 6.0,
            "demand_count": 231
        }
    }

    results = {}
    print("==================================================================")
    print("RUNNING SCORING ENGINE SANITY CHECK (DATASET_GUIDE.md Test Case)")
    print("==================================================================")

    for name, data in districts.items():
        res = compute_priority_score(
            population=data["population"],
            facilities_count=data["facilities_count"],
            demand_count=data["demand_count"],
            existing_investment_cr=data["existing_investment_cr"],
            infra_gap_level=data["infra_gap_level"]
        )
        results[name] = res["priority_score"]
        print(f"{name}: Priority Score = {res['priority_score']} | Components: {res['components']}")

    score_c = results["District C"]
    score_a = results["District A"]
    score_b = results["District B"]

    print("\n----------------- Relative Ordering Verification -----------------")
    print(f"District C ({score_c}) > District A ({score_a}) > District B ({score_b})")

    assert score_c > score_a, f"Expected District C > District A, got {score_c} <= {score_a}"
    assert score_a > score_b, f"Expected District A > District B, got {score_a} <= {score_b}"

    print("\n[SUCCESS] Sanity Check PASSED! The engine produces the expected relative ordering:")
    print("  Rank 1: District C (Highest Priority - severe deficit, high demand, low investment)")
    print("  Rank 2: District A (Moderate Priority)")
    print("  Rank 3: District B (Lowest Priority - adequate facilities, high investment, low demand)")
    print("==================================================================")

if __name__ == "__main__":
    run_sanity_check()
