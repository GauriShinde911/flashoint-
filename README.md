# Development Priority Intelligence (DPI)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Track 1](https://img.shields.io/badge/Track%201-AI%20for%20Digital%20Public%20Infrastructure%20%26%20Governance-brightgreen)](#)
[![BRICS Theme](https://img.shields.io/badge/BRICS%20Theme-Innovation-orange)](#)
[![Digital Public Good](https://img.shields.io/badge/DPG-Compliant-success)](#)

An open-source, multilingual AI platform designed as a **Digital Public Good (DPG)** that aggregates citizen development requests across diverse linguistic regions, fuses them with national infrastructure, demographic, and financial data, surfaces demand hotspots, recommends explainable development priorities, and **measures the actual impact of completed public infrastructure projects**.

---

## 1. Problem Statement: Three Distinct Challenges

Official Track 1 problem statements often get reduced to a simple complaint dashboard. Development Priority Intelligence addresses the complete problem comprising three distinct challenges:

1. **Fragmentation (Data Silos & Linguistic Barriers):**
   Citizen feedback arrives through disjointed channels (voice calls, SMS, WhatsApp/messaging apps, petitions) in dozens of regional languages, completely isolated from government-held GIS, infrastructure directories, and demographic censuses.
2. **Misprioritization (Opaque Resource Allocation):**
   Public spending often bypasses high-need areas due to lack of objective data fusion. Policymakers lack explainable, evidence-backed priority rankings that show exactly *why* a project is recommended over another.
3. **No Impact Measurement (Post-Completion Blindspot):**
   Once projects are funded and marked "Completed," governments have no systematic way to assess whether citizen demand decreased or infrastructure accessibility improved in that target region. DPI introduces a dedicated **Before-and-After Impact Measurement Engine**.

---

## 2. Core Architecture & Workflow

```
CITIZEN CHANNELS (Voice / Text / Messaging)
  │ (Multilingual: English, Hindi, Marathi, etc.)
  ▼
CAPTURE LAYER (Browser Web Speech API + REST Endpoint)
  ▼
FASTAPI BACKEND (Secure key management, validation, orchestration)
  ▼
GEMINI UNDERSTANDING LAYER (Google GenAI / ADK)
  ├─ Language Detection & Intent Translation
  ├─ Category Classification (Health, Water, Road, Education)
  ├─ Location & Entity Extraction
  └─ Semantic Clustering (Merges redundant requests into single demand hotspots)
  ▼
DATA FUSION LAYER
  ├─ Census 2011 + NFHS-5 Demographics
  ├─ National Hospital & Health Centre Directories (data.gov.in)
  ├─ Jal Jeevan Mission & PMGSY Infrastructure Inventories
  └─ Ministry Public Investment Plans
  ▼
DETERMINISTIC ANALYTICS ENGINE (Pure Code — No AI Arithmetic Hallucinations)
  ├─ Priority Score (0–100) = Demand × Population × Infra Deficit × Access Deficit × (1 / Investment)
  ├─ Silent Need Detector = High Inferred Gap + Low Citizen Reports (Flags underreporting)
  ├─ Investment–Demand Mismatch = High Need + Low Funding OR High Funding + Persistent Need
  ├─ Existing-Project Check = Avoid duplicate allocations
  └─ IMPACT MEASUREMENT ENGINE = Compares Pre vs Post completion-date complaint volume & priority
  ▼
GEMINI GROUNDED EXPLANATION LAYER
  └─ Converts exact computed figures into clear policymaker justifications (Never invents numbers)
  ▼
POLICYMAKER DASHBOARD
  ├─ Multi-Region Interactive Map (Leaflet.js + OpenStreetMap)
  ├─ Ranked Recommendations with Full Evidence Trails
  ├─ Silent Need & Investment Mismatch Panels
  ├─ Impact Measurement Analysis (Past projects' real-world performance)
  ├─ Natural Language Query Console ("Policymaker Command Center")
  └─ Explicit "REAL DATA" / "SYNTHETIC DEMO DATA" Badges
```

---

## 3. Technology Stack (Free & Open Tier Only)

Built entirely using tools that require **no paid credit cards or restricted enterprise tiers**:

| Component | Tool / Technology | Role |
| :--- | :--- | :--- |
| **Generative AI** | Google Gemini API (`gemini-2.5-flash`) | Intent parsing, translation, classification, semantic clustering, grounded explanation |
| **Agent Orchestration** | Google GenAI SDK / ADK principles | Multi-step agent ingestion and synthesis pipeline |
| **Backend** | Python 3.11+ / FastAPI | High-performance async API, deterministic scoring logic |
| **Frontend** | Vanilla JavaScript, HTML5, Modern CSS | Lightweight, reactive, high-aesthetic responsive dashboard |
| **Mapping & GIS** | Leaflet.js + OpenStreetMap | Interactive multi-state/district geospatial overlays (no Google Maps API key required) |
| **Voice Capture** | Browser Web Speech API | Client-side voice-to-text capture (labeled as capture, not model AI) |
| **Deployment** | Render (Backend) + Firebase Hosting / Static (Frontend) | Free-tier deployable without GCP billing cards |

---

## 4. Pilot Scope: Multi-Region Indian Implementation

To satisfy the national and cross-state evaluation requirements, the platform includes pilot coverage across **multiple states and districts**:

1. **Maharashtra (Western Region):**
   - **Pune District:** Semi-urban and rural blocks with high digital engagement.
   - **Thane District:** Rapidly expanding peripheral settlements with water/sanitation demands.
2. **Uttar Pradesh (Northern Region):**
   - **Varanasi District:** Dense demographic coverage with active healthcare and infrastructure initiatives.
   - **Gorakhpur District:** High rural population density with health facility expansion projects.

### Data Disclosure & Quality Transparency
- **Real Infrastructure & Demographic Data:** Sourced directly from `data.gov.in` (National Hospital Directory, Health Centres Directory), NFHS-5 district fact sheets, and Census 2011.
- **Demographics Note:** India's 2021 decennial census was postponed and remains in progress through March 1, 2027. Population numbers are sourced from Census 2011 baseline numbers combined with NFHS-5 projections.
- **Synthetic Citizen Requests:** 150–300 realistic multilingual requests (English, Hindi, Marathi) generated to test multi-channel ingestion, clustering, and edge-case detection. All synthetic records carry `data_quality: "synthetic"` and are visibly badged in the UI.

---

## 5. BRICS Cross-Border Adaptability

Designed from the ground up with a generic administrative hierarchy:
```
Country (Admin 0) ──> State / Province (Admin 1) ──> District / Municipality (Admin 2) ──> Locality / Ward (Admin 3)
```
- **Plug-and-Play Configuration:** Onboarding a new country (e.g. Brazil, South Africa) requires only localized datasets and administrative boundary GeoJSONs.
- **Core Reusability:** The scoring mathematics, Gemini agent clustering pipeline, and Leaflet visualization remain 100% identical. See [`docs/brics_adaptation_guide.md`](docs/brics_adaptation_guide.md) for step-by-step instructions.

---

## 6. Digital Public Good (DPG) Principles

- **Open License:** MIT License permitting open reuse and governance adaptation.
- **Open Schemas:** Completely documented JSON schemas in [`docs/data-schema.md`](docs/data-schema.md).
- **No Vendor Lock-In:** Core deterministic logic runs in pure Python; AI layer works with standard GenAI REST endpoints.

---

## 7. Quick Start & Setup

### Prerequisites
- Python 3.10+
- Google Gemini API Key (Get a free key from [Google AI Studio](https://aistudio.google.com/))

### Installation
```bash
# 1. Clone repository
git clone https://github.com/GauriShinde911/flashoint-.git
cd flashoint-

# 2. Setup virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and supply your GEMINI_API_KEY
```

### Running Sanity Check & Synthetic Data Generation
```bash
# Verify the Priority Scoring engine logic against the reference test case (Districts A, B, C)
python data/scripts/sanity_check_scoring.py

# Generate or refresh synthetic citizen requests
python data/scripts/generate_synthetic_data.py
```

### Running the Application
```bash
# Start FastAPI backend
uvicorn backend.app.main:app --reload --port 8000

# Open the frontend
# Open frontend/index.html in any modern web browser or serve via:
python -m http.server 3000 --directory frontend
```
Visit `http://localhost:3000` to interact with the Policymaker Dashboard.
