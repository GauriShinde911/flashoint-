from typing import List, Dict, Any

def detect_silent_needs(districts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identifies regions with high population and high infrastructure deficit
    but low citizen-reported demand. These 'silent needs' highlight areas where
    vulnerable communities may lack digital or voice reporting access.
    """
    silent_needs = []

    for d in districts_data:
        district_id = d.get("district_id") or d.get("admin2")
        population = d.get("population", 0)
        facilities_count = d.get("facilities_count", 0)
        demand_count = d.get("citizen_demand_count", 0)
        infra_deficit = d.get("infra_deficit_score", 0.0)

        # Silent need threshold: Pop > 400,000, Deficit High (few facilities or high score), Demand < 50
        is_high_pop = population >= 400000
        is_high_deficit = (facilities_count <= 6) or (infra_deficit >= 0.6)
        is_low_demand = demand_count < 60

        if is_high_pop and is_high_deficit and is_low_demand:
            severity = round(min(100.0, ((population / 1000000.0) * 40) + ((8 - facilities_count) * 10)), 2)
            silent_needs.append({
                "district": district_id,
                "admin1": d.get("admin1"),
                "population": population,
                "facilities_count": facilities_count,
                "citizen_demand_count": demand_count,
                "silent_need_severity": severity,
                "reason": f"High population ({population:,}) with severe infrastructure deficit ({facilities_count} facilities) but low citizen reporting ({demand_count} requests). Potential digital divide or reporting barrier."
            })

    return sorted(silent_needs, key=lambda x: x["silent_need_severity"], reverse=True)
