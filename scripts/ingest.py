"""
Rerunnable ingestion script for Development Priority Intelligence.
Loads real healthcare infrastructure and demographics for pilot districts,
normalizes into open schemas, and records dataset version metadata.
"""

import os
import sys
from datetime import datetime, timezone

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.storage import get_storage
from backend.app.loaders.hospital_loader import load_hospitals
from backend.app.loaders.health_centre_loader import load_health_centres
from backend.app.loaders.demographics_loader import load_demographics
from backend.app.loaders.synthetic_requests_loader import load_synthetic_requests
from backend.app.loaders.projects_loader import load_government_projects

def run_ingestion():
    store = get_storage()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


    print("==========================================================")
    print("STARTING DATA INGESTION PIPELINE (Healthcare Slice & Citizen Demand)")
    print("==========================================================")

    # 1. Ingest National Hospital Directory
    try:
        hospitals = load_hospitals()
        for h in hospitals:
            store.save_infrastructure_facility(h)
        store.record_dataset_version({
            "dataset_id": "national_hospital_directory_v1",
            "dataset_name": "National Hospital Directory with Geo Code",
            "category": "healthcare",
            "version": "2026.09",
            "record_count": len(hospitals),
            "source_url": "https://data.gov.in/resource/national-hospital-directory-geo-code",
            "ingested_at": now_iso,
            "data_quality": "real"
        })
        print(f"[SUCCESS] Ingested {len(hospitals)} hospitals from National Hospital Directory")
    except Exception as e:
        print(f"[ERROR] Failed to ingest hospitals: {e}")
        raise

    # 2. Ingest All India Health Centres Directory
    try:
        centres = load_health_centres()
        for c in centres:
            store.save_infrastructure_facility(c)
        store.record_dataset_version({
            "dataset_id": "all_india_health_centres_v1",
            "dataset_name": "All India Health Centres Directory",
            "category": "healthcare",
            "version": "2026.09",
            "record_count": len(centres),
            "source_url": "https://data.gov.in/resource/all-india-health-centres-directory",
            "ingested_at": now_iso,
            "data_quality": "real"
        })
        print(f"[SUCCESS] Ingested {len(centres)} health centres from All India Health Centres Directory")
    except Exception as e:
        print(f"[ERROR] Failed to ingest health centres: {e}")
        raise

    # 3. Ingest Census 2011 / NFHS-5 Demographics
    try:
        demographics = load_demographics()
        for d in demographics:
            store.save_demographics(d)
        store.record_dataset_version({
            "dataset_id": "census_nfhs5_demographics_v1",
            "dataset_name": "Census 2011 Demographics & NFHS-5 District Estimates",
            "category": "demographics",
            "version": "2026.09",
            "record_count": len(demographics),
            "source_url": "https://censusindia.gov.in / http://rchiips.org/nfhs/",
            "ingested_at": now_iso,
            "data_quality": "real"
        })
        print(f"[SUCCESS] Ingested demographics for {len(demographics)} pilot districts (Pune, Thane, Varanasi)")
    except Exception as e:
        print(f"[ERROR] Failed to ingest demographics: {e}")
        raise

    # 4. Ingest Synthetic Citizen Requests
    try:
        requests = load_synthetic_requests()
        for req in requests:
            store.save_citizen_request(req)
        store.record_dataset_version({
            "dataset_id": "synthetic_citizen_requests_v1",
            "dataset_name": "Multilingual Synthetic Citizen Demand Dataset",
            "category": "citizen_requests",
            "version": "2026.09",
            "record_count": len(requests),
            "source_url": None,
            "ingested_at": now_iso,
            "data_quality": "synthetic"
        })
        print(f"[SUCCESS] Ingested {len(requests)} synthetic citizen requests across Pune, Thane, Varanasi")
    except Exception as e:
        print(f"[ERROR] Failed to ingest synthetic citizen requests: {e}")
        raise

    # 5. Ingest Government Projects
    try:
        projects = load_government_projects()
        for proj in projects:
            store.save_government_project(proj)
        store.record_dataset_version({
            "dataset_id": "completed_government_projects_v1",
            "dataset_name": "Completed & Ongoing Public Projects Registry",
            "category": "government_projects",
            "version": "2026.09",
            "record_count": len(projects),
            "source_url": None,
            "ingested_at": now_iso,
            "data_quality": "synthetic"
        })
        print(f"[SUCCESS] Ingested {len(projects)} government project records")
    except Exception as e:
        print(f"[ERROR] Failed to ingest government projects: {e}")
        raise

    print("==========================================================")
    print("INGESTION COMPLETE — Real & Synthetic data populated into SQLite store")
    print("==========================================================")


if __name__ == "__main__":
    run_ingestion()

