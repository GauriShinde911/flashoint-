import os
import tempfile
import pytest
import gc
from backend.app.storage.sqlite_store import SQLiteStore

@pytest.fixture
def temp_store():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = SQLiteStore(db_path=path)
    yield store
    del store
    gc.collect()
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass

def test_storage_citizen_request(temp_store):
    req = {
        "id": "REQ-TEST-1",
        "category": "healthcare",
        "admin_hierarchy": {"country_code": "IND", "admin1": "Maharashtra", "admin2": "Pune"},
        "data_quality": "synthetic",
        "raw_text": "Need PHC in village"
    }
    saved_id = temp_store.save_citizen_request(req)
    assert saved_id == "REQ-TEST-1"
    
    results = temp_store.get_citizen_requests(category="healthcare")
    assert len(results) == 1
    assert results[0]["id"] == "REQ-TEST-1"
    assert results[0]["raw_text"] == "Need PHC in village"

def test_storage_facilities_and_projects(temp_store):
    fac = {
        "facility_id": "FAC-001",
        "name": "District Hospital",
        "category": "healthcare",
        "facility_type": "District Hospital",
        "admin_hierarchy": {"country_code": "IND", "admin1": "Maharashtra", "admin2": "Pune"},
        "data_quality": "real"
    }
    temp_store.save_infrastructure_facility(fac)
    facs = temp_store.get_infrastructure_facilities(admin2="Pune", category="healthcare")
    assert len(facs) == 1
    assert facs[0]["name"] == "District Hospital"

    proj = {
        "project_id": "PRJ-001",
        "name": "Rural Hospital Upgradation",
        "category": "healthcare",
        "admin_hierarchy": {"country_code": "IND", "admin1": "Maharashtra", "admin2": "Pune"},
        "status": "Completed",
        "budget_inr_cr": 12.5,
        "data_quality": "real"
    }
    temp_store.save_government_project(proj)
    projs = temp_store.get_government_projects(admin2="Pune", status="Completed")
    assert len(projs) == 1
    assert projs[0]["budget_inr_cr"] == 12.5

def test_storage_demographics_and_version(temp_store):
    demo = {
        "region_id": "IND-MH-PUN",
        "admin_hierarchy": {"country_code": "IND", "admin1": "Maharashtra", "admin2": "Pune"},
        "population_total": 9429408,
        "source": "Census 2011",
        "retrieved_at": "2026-09-20T10:00:00Z",
        "data_quality": "real"
    }
    temp_store.save_demographics(demo)
    retrieved = temp_store.get_demographics("Pune")
    assert retrieved is not None
    assert retrieved["population_total"] == 9429408

    version = {
        "dataset_id": "hospitals_v1",
        "dataset_name": "National Hospital Directory",
        "category": "healthcare",
        "version": "2026.09",
        "record_count": 86,
        "source_url": "https://data.gov.in",
        "ingested_at": "2026-09-20T10:00:00Z",
        "data_quality": "real"
    }
    temp_store.record_dataset_version(version)
    versions = temp_store.get_dataset_versions()
    assert len(versions) == 1
    assert versions[0]["dataset_id"] == "hospitals_v1"
