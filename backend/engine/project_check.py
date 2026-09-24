from typing import List, Dict, Any

def check_existing_projects(
    admin2: str,
    category: str,
    projects_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Checks if ongoing or completed public projects address a given district and sector.
    Returns status ('active_project_found', 'completed_project_found', 'gap_unaddressed')
    and details of matching projects.
    """
    matching = []
    total_budget = 0.0

    for proj in projects_list:
        proj_loc = proj.get("admin_hierarchy", {}).get("admin2") or proj.get("location")
        proj_cat = proj.get("sector") or proj.get("category")

        if proj_loc and proj_loc.lower() == admin2.lower():
            if not category or (proj_cat and proj_cat.lower() == category.lower()):
                matching.append(proj)
                total_budget += proj.get("budget_inr_cr", 0.0)

    if not matching:
        return {
            "status": "gap_unaddressed",
            "has_matching_project": False,
            "matching_projects_count": 0,
            "total_budget_inr_cr": 0.0,
            "projects": []
        }

    has_ongoing = any(p.get("status") in ["Ongoing", "Announced"] for p in matching)
    has_completed = any(p.get("status") == "Completed" for p in matching)

    status_str = "active_project_found" if has_ongoing else ("completed_project_found" if has_completed else "projects_found")

    return {
        "status": status_str,
        "has_matching_project": True,
        "matching_projects_count": len(matching),
        "total_budget_inr_cr": round(total_budget, 2),
        "projects": matching
    }
