# Project Handoff & Status — Development Priority Intelligence

## Status Table

| STEP | Title | Status |
| :--- | :--- | :--- |
| **STEP 0** | Scaffold (Layout, LICENSE, .env.example, CREDITS, README, HANDOFF, /health) | **DONE** |
| **STEP 1** | Data schema + storage layer (SQLite local default, config/india.json) | **DONE** |
| **STEP 2** | Healthcare vertical slice: real data (Loaders, pilot districts, ingest.py) | **DONE** |
| **STEP 3** | Synthetic citizen requests (150–300 requests, en/hi/mr, time-spread) | **DONE** |
| **STEP 4** | Scoring engine (deterministic, weights.json, District C>A>B test) | **DONE** |
| **STEP 5** | Impact Measurement Engine (Pre vs Post completion comparison) | **DONE** |
| **STEP 6** | Policymaker Dashboard (plain HTML+CSS+JS, Leaflet, 6 tabs, Voice, Offline fallback) | **DONE** |
| **STEP 7** | Gemini understanding layer (ADK / pipeline, USE_MOCK_GEMINI) | **DONE** |
| **STEP 8** | Gemini explanation layer + NL query (/explain, /query endpoints) | TODO |
| **STEP 9** | Backend API completion (CORS, validation, endpoints, tests) | TODO |
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
- **Deterministic Priority Scoring Engine (STEP 4)**:
  - Implemented in `backend/engine/scoring.py` with configurable weights in `config/weights.json`.
  - Exposes per-input breakdowns and exact weight lineage with every score.
  - Includes **Silent Need Detector** (`backend/engine/silent_need_detector.py`) identifying high-pop, high-deficit regions with low reporting.
  - Includes **Investment-Demand Mismatch Detector** (`backend/engine/mismatch_detector.py`) highlighting over-funded vs under-funded districts.
  - Includes **Existing-Project Check** (`backend/engine/project_check.py`) evaluating ongoing and completed government project coverage.
  - Verified with Worked Sanity Check (`tests/test_worked_example.py`) strictly asserting score order: **District C > District A > District B**.
- **Impact Measurement Engine (STEP 5)**:
  - Implemented in `backend/engine/impact_engine.py`.
  - Compares citizen request volume in equal time windows (e.g. 90/180 days) BEFORE vs AFTER project completion dates.
  - Seeded 3 completed government projects (`data/synthetic/completed_projects.json`) with before/after request timestamps demonstrating demand reduction.
  - Includes mandatory disclaimer: `"based on available data, not a guarantee"`.
- **Tests**: 68/70 tests passing across all test modules. The 2 pre-existing integration tests (`test_ingestion_storage_state`, `test_storage_synthetic_requests`) require running `python scripts/ingest.py` to seed the SQLite DB first — they pass after seeding.
- **Gemini Understanding Layer (STEP 7)**:
  - Restructured `backend/services/gemini_service.py` as a clean 4-stage pipeline:
    - Stage 1: Language detection (en/hi/mr via Devanagari heuristics)
    - Stage 2: Category/urgency classification (healthcare, water_sanitation, roads_transport, education; critical urgency bump on emergency words)
    - Stage 3: Location + entity extraction (3 pilot districts, BRICS-generic admin hierarchy)
    - Stage 4: Semantic cluster ID generation (CLUSTER-{CAT}-{DISTRICT})
  - `USE_MOCK_GEMINI=true` → fully deterministic offline path, no API key needed
  - `USE_MOCK_GEMINI=false` → live Gemini 1.5-flash with graceful deterministic fallback
  - Gemini API key held server-side only; never exposed to browser
  - 44 new unit tests added in `tests/test_gemini_service.py`; all pass offline

## Known Gaps
- `POST /requests` uses a simple district heuristic for location extraction. In STEP 8, the Gemini explanation layer (`/explain`) will be upgraded with a proper live Gemini rewrite prompt and the NL query parser (`/query`) will support broader state/sector combinations beyond the 3 pilot districts.

---

## MANUAL TASKS
- Set `GEMINI_API_KEY` in `.env` if testing non-mock Gemini queries.
- For production expansion beyond pilot districts, full national data.gov.in CSV extracts can be fetched and loaded with the same loader contracts.

---

## What works in STEP 6 (Frontend Dashboard)
- **Leaflet map** showing all 3 pilot districts (Pune, Thane, Varanasi) with colour-coded priority circles.
- **6 tabs**: Ranked Recommendations, Silent Need Flags, Investment-Demand Mismatch, Impact Measurement, AI Command Center, Submit Request.
- **Right evidence panel**: score ring, breakdown bar chart (SVG), stats, explanation, project status.
- **Language switcher**: English / हिन्दी / मराठी via `i18n.js` dictionary.
- **Offline Demo Mode**: falls back to `frontend/mock/*.json` when backend is unreachable.
- **Voice input** via Web Speech API on Submit Request form (Chrome/Edge only).
- **No build tooling**: pure HTML + CSS + vanilla JS, Leaflet via CDN.
- To run: `python -m http.server 3000` inside `frontend/`.

---

## NEXT STEP
Proceed to **STEP 8 — Gemini explanation layer + NL query endpoints**. Upgrade `generate_grounded_explanation` to use a richer Gemini prompt that cites actual numbers (population, demand, investment) in the generated text and is testable with mock. Upgrade `parse_natural_language_query` to support compound queries (multi-sector, multi-district) and add backend-side filter execution validation. Endpoints: `GET /explain/{district_name}` and `POST /query`. Add unit + integration tests. Target: all 70/70 tests passing after running ingest.py.
