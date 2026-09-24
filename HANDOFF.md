# Project Handoff & Status — Development Priority Intelligence

## Status Table

| STEP | Title | Status |
| :--- | :--- | :--- |
| **STEP 0** | Scaffold (Layout, LICENSE, .env.example, CREDITS, README, HANDOFF, /health) | **DONE** |
| **STEP 1** | Data schema + storage layer (SQLite local default, config/india.json) | **DONE** |
| **STEP 2** | Healthcare vertical slice: real data (Loaders, pilot districts, ingest.py) | **DONE** |
| **STEP 3** | Synthetic citizen requests (150–300 requests, en/hi/mr, time-spread) | **DONE** |
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

### Ingest Real & Synthetic Data
```bash
python scripts/ingest.py
```

### Run Tests
```bash
python -m pytest tests/
```

### Run Backend API
```bash
uvicorn backend.app.main:app --reload --port 8000
```

---

## What Works
- **Scaffolding & Architecture**: Fast, lightweight, zero-cost stack with `/health` and `/api/health`.
- **Open Schemas & Storage**: JSON Schemas in `docs/schemas/`, pluggable SQLite storage in `data/dpi_local.db`.
- **Real Healthcare & Demographics Ingestion (STEP 2)**:
  - 3 pilot districts across 2 states: **Pune** (MH), **Thane** (MH), and **Varanasi** (UP).
  - Verified geo-coded hospitals from National Hospital Directory (`data.gov.in`).
  - Verified PHCs and CHCs from All India Health Centres Directory (`data.gov.in`).
  - Real baseline population figures from **Census 2011** combined with **NFHS-5 (2019-21)** district estimates.
  - Lineage tracking via `dataset_version` entries (`national_hospital_directory_v1`, `all_india_health_centres_v1`, `census_nfhs5_demographics_v1`).
- **Synthetic Citizen Demand Ingestion (STEP 3)**:
  - 220 synthetic citizen requests exclusively targeting Pune, Thane, and Varanasi.
  - Multilingual support: English (`en`), Hindi (`hi`), Marathi (`mr`).
  - Channels: `voice`, `text`, `messaging_app`.
  - Phrasing variations per `DATASET_GUIDE.md` across healthcare, water/sanitation, roads/transport, and education.
  - Timestamps spread across 5–450 days ago for before/after impact measurement testing.
  - Tagged with `data_quality: "synthetic"` and recorded in dataset version lineage (`synthetic_citizen_requests_v1`).
- **Tests**: 9/9 tests passing (`test_health.py`, `test_storage.py`, `test_ingest.py`, `test_synthetic_requests.py`).

## Known Gaps
- Deterministic scoring engine (`backend/engine/`) computing Priority Score (0-100) with configurable weights and District C > A > B sanity assertion test to be implemented in STEP 4.

---

## MANUAL TASKS
- Set `GEMINI_API_KEY` in `.env` if testing non-mock Gemini queries.
- For production expansion beyond pilot districts, full national data.gov.in CSV extracts can be fetched and loaded with the same loader contracts.

---

## NEXT STEP
Proceed to **STEP 4 — Scoring engine (deterministic, no Gemini) + sanity test**. Implement `backend/engine/` Priority Score (0–100) = demand x population affected x infra deficit x accessibility x inverse investment, with configurable weights in `config/weights.json` and per-input breakdown returned with every score. Write `tests/test_worked_example.py` asserting District C > A > B per `DATASET_GUIDE.md`. Also implement Silent Need Detector, Investment–Demand Mismatch, and Existing-Project Check.
