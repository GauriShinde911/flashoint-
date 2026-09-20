import pytest
from backend.app.loaders.hospital_loader import load_hospitals
from backend.app.loaders.health_centre_loader import load_health_centres
from backend.app.loaders.demographics_loader import load_demographics
from backend.app.storage import get_storage

def test_loaders_data_integrity():
    hospitals = load_hospitals()
    assert len(hospitals) > 0
    for h in hospitals:
        assert h["data_quality"] == "real"
        assert "source" in h
        assert "source_url" in h
        assert "retrieved_at" in h
        assert h["category"] == "healthcare"
        assert h["admin_hierarchy"]["country_code"] == "IND"
        assert h["admin_hierarchy"]["admin1"] in ["Maharashtra", "Uttar Pradesh"]

    centres = load_health_centres()
    assert len(centres) > 0
    for c in centres:
        assert c["data_quality"] == "real"
        assert "source" in c
        assert "source_url" in c

    demographics = load_demographics()
    assert len(demographics) == 3
    districts = [d["admin_hierarchy"]["admin2"] for d in demographics]
    assert "Pune" in districts
    assert "Thane" in districts
    assert "Varanasi" in districts
    for d in demographics:
        assert d["data_quality"] == "real"
        assert d["population_total"] > 1_000_000

def test_ingestion_storage_state():
    store = get_storage()
    pune_facilities = store.get_infrastructure_facilities(admin2="Pune", category="healthcare")
    assert len(pune_facilities) > 0

    pune_demo = store.get_demographics("Pune")
    assert pune_demo is not None
    assert pune_demo["population_total"] == 9429408

    versions = store.get_dataset_versions()
    assert len(versions) >= 3
    dataset_ids = [v["dataset_id"] for v in versions]
    assert "national_hospital_directory_v1" in dataset_ids
    assert "all_india_health_centres_v1" in dataset_ids
    assert "census_nfhs5_demographics_v1" in dataset_ids
