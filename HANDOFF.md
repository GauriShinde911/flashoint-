# Project Handoff & Status — Development Priority Intelligence

## Status Table

| STEP | Title | Status |
| :--- | :--- | :--- |
| **STEP 0** | Scaffold (Layout, LICENSE, .env.example, CREDITS, README, HANDOFF, /health) | **DONE** |
| **STEP 1** | Data schema + storage layer (SQLite local default, config/india.json) | **DONE** |
| **STEP 2** | Healthcare vertical slice: real data (Loaders, pilot districts, ingest.py) | TODO |
| **STEP 3** | Synthetic citizen requests (150–300 requests, en/hi/mr, time-spread) | TODO |
| **STEP 4** | Scoring engine (deterministic, weights.json, District C>A>B test) | TODO |
| **STEP 5** | Impact Measurement Engine (Pre vs Post completion comparison) | TODO |
| **STEP 6** | Gemini understanding layer (ADK / pipeline, USE_MOCK_GEMINI) | TODO |
| **STEP 7** | Gemini explanation layer + NL query (/explain, /query) | TODO |
| **STEP 8** | Backend API completion (CORS, validation, endpoints, tests) | TODO |
| **STEP 9** | Policymaker dashboard (Leaflet multi-region, Impact view, Voice input) | TODO |
| **STEP 10** | Deploy config (render.yaml, Firebase Hosting, GitHub Actions) | TODO |
| **STEP 11** | BRICS + DPG docs (ARCHITECTURE.md, README.md, honest census note) | TODO |
| **STEP 12** | Submission docs (BRIEF_DESCRIPTION.md, DEMO_SCRIPT.md, PITCH_OUTLINE.md) | TODO |
| **STEP 13** | (Optional) Photo evidence via Gemini multimodal | TODO |

---

## How to Run

### Environment Setup
```bash
# Copy template
cp .env.example .env

# Required environment variables (.env):
# GEMINI_API_KEY=your_key_here
# USE_MOCK_GEMINI=true   (set true to run offline without quota usage)
# STORAGE_BACKEND=sqlite (local zero-setup SQLite store)
```

### Install Dependencies & Run Tests
```bash
pip install -r backend/requirements.txt
python -m pytest tests/
```

### Run Backend API
```bash
uvicorn backend.app.main:app --reload --port 8000
```

---

## What Works
- Repo structure and baseline health endpoints (`/health` and `/api/health`).
- Open JSON Schemas in `docs/schemas/` for: `citizen_request`, `demographics`, `infrastructure_facility`, `government_project`, and `dataset_version`.
- Pluggable storage architecture (`backend/app/storage/base.py`) with zero-setup local SQLite implementation (`backend/app/storage/sqlite_store.py`) storing to `data/dpi_local.db`.
- Generic administrative hierarchy & multilingual configuration in `config/india.json`.
- 100% test pass across health and storage modules (`tests/test_storage.py`, `tests/test_health.py`).

## Known Gaps
- Real data ingestion scripts and loaders for the 3 pilot districts across 2 states to be implemented in STEP 2.

---

## MANUAL TASKS
- Live API keys for Gemini (`GEMINI_API_KEY`) can be added to `.env` when testing non-mock mode.
- Government dataset downloads (`data.gov.in`) will be managed via loaders in STEP 2.

---

## NEXT STEP
Proceed to **STEP 2 — Healthcare vertical slice: real data**. Following `DATASET_GUIDE.md`, write loaders for National Hospital Directory (geo-coded), All India Health Centres Directory, and Census 2011 / NFHS-5 district population figures for 3 pilot districts across at least 2 states (e.g. Pune & Thane in Maharashtra, Varanasi in UP). Normalize into our schemas, tag metadata (`source`, `source_url`, `retrieved_at`, `data_quality: "real"`), and implement a rerunnable `scripts/ingest.py` with dataset version tracking.
