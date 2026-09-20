"""
Deterministic Analytics Engine for Development Priority Intelligence
Implements:
1. Priority Score (0 - 100)
2. Silent Need Detector
3. Investment-Demand Mismatch Detector
4. Post-Project Impact Measurement Engine
"""

from typing import Dict, List, Any

def compute_priority_score(
    population: int,
    facilities_count: int,
    demand_count: int,
    existing_investment_cr: float,
    infra_gap_level: str = "High"  # "High", "Medium", "Low"
) -> Dict[str, Any]:
    """
    Computes an objective, normalized Priority Score between 0 and 100.
    Code handles all arithmetic deterministically.
    """
    # 1. Population factor (normalized assuming reference scale 500,000 to 2,500,000)
    pop_norm = min(1.0, max(0.0, population / 2_000_000.0))
    
    # 2. Demand factor (normalized reference 0 to 300 requests)
    demand_norm = min(1.0, max(0.0, demand_count / 250.0))
    
    # 3. Infrastructure Deficit (facility ratio + qualitative gap tier)
    facilities_per_lakh = (facilities_count / (population / 100_000.0)) if population > 0 else 0
    # National target benchmark is ~1.5 to 2.0 facilities per lakh
    infra_shortfall = max(0.0, min(1.0, (1.5 - facilities_per_lakh) / 1.5))
    gap_multiplier = {"High": 1.0, "Medium": 0.6, "Low": 0.2}.get(infra_gap_level, 0.5)
    infra_deficit_score = 0.6 * infra_shortfall + 0.4 * gap_multiplier

    # 4. Inverse Investment Factor (high investment dampens urgency since funds are allocated)
    # Reference range 0 to 25 Cr
    inv_factor = max(0.0, min(1.0, 1.0 - (existing_investment_cr / 25.0)))

    # Weighted Composite Score (0 to 100)
    # Weights: Demand (30%), Infra Deficit (30%), Population (25%), Inverse Investment (15%)
    raw_score = (
        0.30 * demand_norm +
        0.30 * infra_deficit_score +
        0.25 * pop_norm +
        0.15 * inv_factor
    ) * 100.0

    score = round(max(0.0, min(100.0, raw_score)), 1)

    return {
        "priority_score": score,
        "components": {
            "demand_norm": round(demand_norm, 3),
            "pop_norm": round(pop_norm, 3),
            "infra_deficit_score": round(infra_deficit_score, 3),
            "inv_factor": round(inv_factor, 3),
            "facilities_per_lakh": round(facilities_per_lakh, 2)
        }
    }

def detect_silent_need(
    infra_gap_level: str,
    demand_count: int,
    vulnerability_index: float = 0.8
) -> bool:
    """
    Flags regions where infrastructural need is severe but citizen complaints are suspiciously low,
    often due to digital illiteracy, lack of network coverage, or social marginalization.
    """
    return (infra_gap_level == "High") and (demand_count < 50) and (vulnerability_index >= 0.7)

def detect_investment_mismatch(
    priority_score: float,
    existing_investment_cr: float,
    demand_count: int
) -> str:
    """
    Categorizes financial mismatch:
    - 'underfunded_hotspot': High need/demand with minimal funding
    - 'ineffective_expenditure': High investment but persistent grievances
    - 'balanced': Funding aligns with need
    """
    if priority_score >= 70.0 and existing_investment_cr < 8.0:
        return "underfunded_hotspot"
    elif existing_investment_cr >= 15.0 and demand_count >= 150:
        return "ineffective_expenditure"
    return "balanced"

def compute_impact_measurement(
    pre_complaints: int,
    post_complaints: int
) -> Dict[str, Any]:
    """
    Computes before vs after project impact for completed public works.
    Direct answer to Clause 3: measuring impact of digital/physical public infrastructure.
    """
    if pre_complaints <= 0:
        impact_pct = 0.0
    else:
        impact_pct = round(((pre_complaints - post_complaints) / pre_complaints) * 100.0, 1)

    if impact_pct >= 50.0:
        status = "Verified Significant Reduction"
    elif impact_pct > 15.0:
        status = "Moderate Improvement"
    elif impact_pct >= -10.0:
        status = "Marginal or Stagnant Impact"
    else:
        status = "Persistent Deficit (Need Escalated)"

    return {
        "pre_complaints": pre_complaints,
        "post_complaints": post_complaints,
        "impact_percentage": impact_pct,
        "verification_status": status
    }
