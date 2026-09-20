# Project Handoff & Status — Development Priority Intelligence

## Status Table

| STEP | Title | Status |
| :--- | :--- | :--- |
| **STEP 0** | Scaffold (Layout, LICENSE, .env.example, CREDITS, README, HANDOFF, /health) | **DONE** |
| **STEP 1** | Data schema + storage layer (SQLite local default, config/india.json) | TODO |
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

### Install Dependencies & Run Backend
```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

### Run Tests
```bash
python -m pytest tests/test_health.py
```

### Run Frontend
Open `frontend/index.html` directly in your browser or run:
```bash
python -m http.server 3000 --directory frontend
```

---

## What Works
- Repo structure matching spec: `/backend`, `/frontend`, `/data` (`raw/`, `processed/`, `synthetic/`), `/config`, `/docs`, `/scripts`, `/tests`, `.github/workflows`.
- Complete license (`LICENSE` MIT), `.env.example`, `CREDITS.md`, `README.md` skeleton, and `/docs/antigravity_build_prompt.md` + `/docs/DATASET_GUIDE.md`.
- Working `/health` and `/api/health` endpoints returning JSON service status.

## Known Gaps
- Data schemas and generic location configuration (`config/india.json`) to be implemented in STEP 1.
- SQLite/storage interface layer to be unified in STEP 1.

---

## MANUAL TASKS
- Set `GEMINI_API_KEY` in `.env` if testing live Google GenAI queries (mock mode works without keys).
- Dataset downloads for live government files (`data.gov.in`) will be managed via loaders in STEP 2.

---

## NEXT STEP
Proceed to **STEP 1 — Data schema + storage layer**. We will write `/docs/data-schema.md` and standard JSON Schemas for `citizen_request`, `demographics`, `infrastructure_facility`, `government_project`, and `dataset_version`. Implement the pluggable storage interface with local SQLite as the zero-setup offline default, and create `/config/india.json` with the generic 4-level administrative hierarchy and supported language codes (`en`, `hi`, `mr`).
