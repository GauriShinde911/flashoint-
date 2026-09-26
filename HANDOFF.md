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
| **STEP 8** | Gemini explanation layer + NL query (/explain, /query endpoints) | **DONE** |
| **STEP 9** | Backend API completion (CORS, validation, endpoints, tests) | **DONE** |
| **STEP 10** | Deploy config (render.yaml, Firebase Hosting, GitHub Actions) | **DONE** |
| **STEP 11** | BRICS + DPG docs (ARCHITECTURE.md, README.md, honest census note, CREDITS.md) | **DONE** |
| **STEP 12** | Submission docs (BRIEF_DESCRIPTION.md, DEMO_SCRIPT.md, PITCH_OUTLINE.md) | **DONE** |
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
- **Backend API Completion (STEP 9)**:
  - Reorganized routes using FastAPI `APIRouter` with `/api/v1` prefix and backward-compatible root alias mounts.
  - Strict Pydantic Field validation for `SubmitRequestModel` (`raw_text` length 1–2000, `source_channel` enum `"voice"`|`"text"`|`"messaging_app"`) and `QueryModel` (`query` length 1–500), returning 422 HTTP errors on invalid input.
  - Tightened CORS configuration in `backend/app/config.py` with configurable origin lists via `ALLOWED_ORIGINS` env var (wildcard `*` removed).
  - Resolved Python 3.12 `datetime.utcnow()` deprecation warnings with `datetime.now(timezone.utc)`.
- **BRICS & DPG Documentation (STEP 11)**:
  - Completely rewrote `README.md` with executive summary, problem pillars, Gemini architecture diagram, real data disclosure, BRICS mapping, and Google Cloud production roadmap.
  - Expanded `ARCHITECTURE.md` with Section 5 (Country Onboarding Workflow for Brazil/South Africa) and Section 6 (Google Cloud Production Scale-Up).
  - Populated `CREDITS.md` with official government citations (`data.gov.in`, Census 2011, NFHS-5) and open source licenses.
- **Hackathon Submission Package (STEP 12)**:
  - Created `docs/submission/BRIEF_DESCRIPTION.md` (2–3 line summary options).
  - Created `docs/submission/DEMO_SCRIPT.md` (minute-by-minute 3–5 min video recording script).
  - Created `docs/submission/PITCH_OUTLINE.md` (10–12 slide deck outline).
- **Citizen / Policymaker Portal Separation**:
  - Created `frontend/login.html` with dual-role authentication (Citizen vs. Policymaker).
  - Created `frontend/citizen.html` dedicated citizen submission portal with voice input and multilingual UI.
  - Added authentication guard and sign-out logic to `frontend/index.html`.
- **Tests**: **139/139 tests passing** (100% pass rate).

## Known Gaps
- Request-level rate limiting not yet enforced (optional production feature).

---

## MANUAL TASKS
- Set `GEMINI_API_KEY` in `.env` if testing non-mock Gemini queries.
- Deploy live: Push backend to Render (`render.yaml`) and frontend to Firebase/Vercel (`firebase.json`).

---

## NEXT STEP
Proceed to **STEP 13 — (Optional) Photo evidence via Gemini multimodal** and **Live Cloud Deployment**. Tasks: (1) add image upload in `citizen.html` allowing citizens to attach infrastructure photo evidence, (2) integrate Gemini vision endpoint to extract damage assessment from images, (3) verify live deployment on Render and Firebase.


