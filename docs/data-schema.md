# Open Data Schemas & Model Specifications

All data structures in Development Priority Intelligence are formal Digital Public Goods adhering to open JSON Schema standards. Individual JSON schemas are located in `/docs/schemas/`.

## Schema Index

1. **`citizen_request`** ([`docs/schemas/citizen_request.json`](schemas/citizen_request.json)):
   Multilingual citizen demand signals captured across voice, text, and messaging channels.
   - Fields: `id`, `timestamp`, `raw_text`, `translated_text`, `source_channel`, `detected_language`, `category`, `sub_category`, `urgency_level`, `admin_hierarchy`, `data_quality`, `source`, `source_url`, `retrieved_at`.

2. **`demographics`** ([`docs/schemas/demographics.json`](schemas/demographics.json)):
   District-level population totals, rural/urban splits, and vulnerability metrics.
   - Fields: `region_id`, `admin_hierarchy`, `population_total`, `population_rural`, `population_urban`, `vulnerability_index`, `census_year` (2011), `projection_source` (NFHS-5), `source`, `source_url`, `retrieved_at`, `data_quality`.

3. **`infrastructure_facility`** ([`docs/schemas/infrastructure_facility.json`](schemas/infrastructure_facility.json)):
   Physical facility inventory (PHCs, CHCs, hospitals, schools, water points).
   - Fields: `facility_id`, `name`, `category`, `facility_type`, `admin_hierarchy`, `status`, `source`, `source_url`, `retrieved_at`, `data_quality`.

4. **`government_project`** ([`docs/schemas/government_project.json`](schemas/government_project.json)):
   Public investment records and capital works.
   - Fields: `project_id`, `name`, `category`, `admin_hierarchy`, `budget_inr_cr`, `status` (`Announced`, `Ongoing`, `Completed`), `start_date`, `completion_date`, `source`, `source_url`, `retrieved_at`, `data_quality`.

5. **`dataset_version`** ([`docs/schemas/dataset_version.json`](schemas/dataset_version.json)):
   Data lineage and ingestion tracking.
   - Fields: `dataset_id`, `dataset_name`, `category`, `version`, `record_count`, `source_url`, `ingested_at`, `data_quality`, `checksum`.

---

## Generic Hierarchy Model
Adheres to `config/india.json` with generic 4-tier abstraction:
`Country (Admin 0) > State (Admin 1) > District (Admin 2) > Locality (Admin 3)`
All records tag `data_quality: "real" | "synthetic"` to guarantee transparent badge rendering in the UI.
