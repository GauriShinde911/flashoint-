import os
import json
from typing import Dict, Any, Optional

DEFAULT_WEIGHTS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../config/weights.json")
)

def load_weights(weights_path: str = DEFAULT_WEIGHTS_PATH) -> Dict[str, Any]:
    """Loads weights configuration file."""
    if os.path.exists(weights_path):
        with open(weights_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "weights": {
            "demand": 0.30,
            "population": 0.25,
            "infra_deficit": 0.25,
            "accessibility": 0.10,
            "inverse_investment": 0.10
        },
        "normalization_bounds": {
            "demand_max": 300,
            "population_max": 2000000,
            "infra_facilities_max": 20,
            "investment_max_cr": 25.0
        }
    }

def calculate_priority_score(
    population: int,
    facilities_count: int,
    citizen_demand_count: int,
    existing_investment_cr: float,
    infra_deficit_score: Optional[float] = None,
    accessibility_score: Optional[float] = None,
    weights_path: str = DEFAULT_WEIGHTS_PATH
) -> Dict[str, Any]:
    """
    Computes deterministic Priority Score (0–100) for a region.
    Formula:
    Priority Score = w_demand * S_demand + w_pop * S_pop + w_gap * S_gap + w_access * S_access + w_inv * S_inv
    Returns a dictionary exposing all normalized inputs, breakdown, and weights used.
    """
    config = load_weights(weights_path)
    weights = config["weights"]
    bounds = config["normalization_bounds"]

    # 1. Normalize Demand
    demand_max = bounds.get("demand_max", 300)
    s_demand = min(100.0, (citizen_demand_count / demand_max) * 100.0) if demand_max > 0 else 0.0

    # 2. Normalize Population
    pop_max = bounds.get("population_max", 2000000)
    s_pop = min(100.0, (population / pop_max) * 100.0) if pop_max > 0 else 0.0

    # 3. Normalize Infra Deficit Gap
    if infra_deficit_score is not None:
        # Scale 0-1 to 0-100 if needed
        s_gap = infra_deficit_score * 100.0 if infra_deficit_score <= 1.0 else min(100.0, infra_deficit_score)
    else:
        fac_max = bounds.get("infra_facilities_max", 20)
        gap_ratio = max(0.0, 1.0 - (facilities_count / fac_max)) if fac_max > 0 else 1.0
        s_gap = gap_ratio * 100.0

    # 4. Normalize Accessibility
    if accessibility_score is not None:
        s_access = accessibility_score * 100.0 if accessibility_score <= 1.0 else min(100.0, accessibility_score)
    else:
        # Fewer facilities per 100k population = higher accessibility penalty / deficit
        fac_per_lakh = (facilities_count / (population / 100000.0)) if population > 0 else 0.0
        s_access = max(0.0, min(100.0, 100.0 - (fac_per_lakh * 10.0)))

    # 5. Normalize Inverse Investment (Lower investment = higher priority)
    inv_max = bounds.get("investment_max_cr", 25.0)
    inv_ratio = max(0.0, 1.0 - (existing_investment_cr / inv_max)) if inv_max > 0 else 1.0
    s_inv = inv_ratio * 100.0

    # Weighted Sum
    total_score = (
        weights["demand"] * s_demand +
        weights["population"] * s_pop +
        weights["infra_deficit"] * s_gap +
        weights["accessibility"] * s_access +
        weights["inverse_investment"] * s_inv
    )

    final_score = round(max(0.0, min(100.0, total_score)), 2)

    return {
        "priority_score": final_score,
        "input_summary": {
            "population": population,
            "facilities_count": facilities_count,
            "citizen_demand_count": citizen_demand_count,
            "existing_investment_cr": existing_investment_cr,
            "raw_infra_deficit_score": infra_deficit_score,
            "raw_accessibility_score": accessibility_score
        },
        "breakdown": {
            "demand": {"raw": citizen_demand_count, "normalized_score": round(s_demand, 2), "weight": weights["demand"]},
            "population": {"raw": population, "normalized_score": round(s_pop, 2), "weight": weights["population"]},
            "infra_deficit": {"normalized_score": round(s_gap, 2), "weight": weights["infra_deficit"]},
            "accessibility": {"normalized_score": round(s_access, 2), "weight": weights["accessibility"]},
            "inverse_investment": {"raw_cr": existing_investment_cr, "normalized_score": round(s_inv, 2), "weight": weights["inverse_investment"]}
        },
        "weights_used": weights
    }
