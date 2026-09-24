from typing import List, Dict, Any

def detect_investment_mismatches(districts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detects mismatches between public financial investment and actual citizen demand / deficit.
    Identifies over-funded areas with low demand and under-funded areas with critical demand.
    """
    mismatches = []

    for d in districts_data:
        district_id = d.get("district_id") or d.get("admin2")
        investment_cr = d.get("existing_investment_cr", 0.0)
        demand_count = d.get("citizen_demand_count", 0)
        facilities_count = d.get("facilities_count", 0)

        # Under-funded despite high demand
        if demand_count >= 150 and investment_cr <= 8.0:
            mismatches.append({
                "district": district_id,
                "admin1": d.get("admin1"),
                "mismatch_type": "UNDER_FUNDED_HIGH_DEMAND",
                "investment_cr": investment_cr,
                "citizen_demand_count": demand_count,
                "facilities_count": facilities_count,
                "description": f"Critical demand ({demand_count} requests) and only {facilities_count} facilities, but existing investment is low at ₹{investment_cr} Cr."
            })

        # Over-funded despite low demand
        elif demand_count <= 50 and investment_cr >= 15.0:
            mismatches.append({
                "district": district_id,
                "admin1": d.get("admin1"),
                "mismatch_type": "OVER_FUNDED_LOW_DEMAND",
                "investment_cr": investment_cr,
                "citizen_demand_count": demand_count,
                "facilities_count": facilities_count,
                "description": f"High investment (₹{investment_cr} Cr) allocated, but citizen-reported demand is low ({demand_count} requests) with adequate facilities ({facilities_count})."
            })

    return mismatches
