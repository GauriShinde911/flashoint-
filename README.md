# Development Priority Intelligence (DPI)
### Multilingual AI & Deterministic Analytics Platform for Digital Public Infrastructure
**Track 1: AI for Digital Public Infrastructure & Governance (BRICS Theme: Innovation)**  
*Designed as a Digital Public Good (DPG) | MIT Licensed | Powered by Google AI*

---

## 🏛️ Executive Summary

Governments struggle to consolidate citizen feedback and align it with national infrastructure priorities. Development requests live in fragmented systems, leading to misaligned public spending, unaddressed infrastructure deficits, and zero visibility into the true impact of completed public works.

**Development Priority Intelligence (DPI)** is an open-source, multilingual AI platform designed as a **Digital Public Good (DPG)**. It:
1. **Aggregates** citizen development requests via voice, text, and messaging channels across regional languages (English, Hindi, Marathi).
2. **Understands & Clusters** citizen intent using **Google Gemini 1.5 Flash**.
3. **Fuses** citizen feedback with official demographic baselines (**Census 2011 + NFHS-5**), geo-coded infrastructure registries (**data.gov.in**), and public investment outlays.
4. **Computes Deterministic Priority Scores** (0–100) and detects **Silent Need** (underreported vulnerable areas) and **Investment Mismatches**.
5. **Measures Impact** by comparing pre- and post-commissioning complaint volumes for completed government projects.

---

## 🎯 The Three Core Problem Pillars

| Pillar | The Problem in Governance | How DPI Solves It |
|---|---|---|
| **1. Fragmentation** | Citizen complaints arrive in regional languages across disjointed silos (helplines, petitions, messaging apps) disconnected from spatial planning. | Multilingual input (voice/text) normalized by Gemini into structured schema with geo-entities and category tags. |
| **2. Misprioritization** | Budget allocations often favor vocal districts or political priorities rather than acute ground deficits. | Multi-factor deterministic scoring fusing population vulnerability, infrastructure per capita, and citizen demand. |
| **3. No Impact Measurement** | Once an infrastructure project is inaugurated, agencies rarely track whether citizen pain points were actually resolved. | Automated Before-vs-After impact engine evaluating complaint reduction post project completion date. |

---

## 🤖 Google AI Architecture

DPI implements a strict **separation between deterministic mathematics and natural language AI**:

```
Citizen Input (Voice/Text/Chat)
            │
            ▼
┌──────────────────────────────────────────────┐
│       Google Gemini 1.5 Flash Pipeline       │
│  Stage 1: Multilingual Detection (en/hi/mr)  │
│  Stage 2: Category Classification            │
│  Stage 3: Geo & Entity Extraction            │
│  Stage 4: Semantic Need Clustering           │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│        Deterministic Analytics Engine        │
│  • Priority Score (0–100)                    │
│  • Silent Need Detector (Vulnerability Index)│
│  • Investment-Demand Mismatch Engine         │
│  • Impact Measurement Engine (Before/After)  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│        Gemini Grounded Explanation Agent     │
│  Translates mathematical scores & citations  │
│  into natural-language policy justifications │
│  + Answers policymaker conversational queries│
└──────────────────────────────────────────────┘
```

* **No Hallucinated Mathematics:** Gemini never invents scores or budgets; it strictly contextualizes figures calculated by the deterministic Python core.
* **Offline Mock Mode:** Includes full fallback mocks (`USE_MOCK_GEMINI=true`) allowing the platform to run offline and execute all 139 automated tests without consuming API quotas.

---

## 📊 Real Datasets & Governance Disclosures

In strict compliance with open-data standards and real governance realities:

* **National Hospital Directory with Geo-Code:** Verified operational government hospitals from [data.gov.in](https://data.gov.in).
* **All India Health Centres Directory:** Verified Primary Health Centres (PHCs) and Community Health Centres (CHCs) from [data.gov.in](https://data.gov.in).
* **Demographics (Census 2011 + NFHS-5):**
  > **Official Disclosure:** India's 2021 decennial census was postponed indefinitely due to COVID-19. Following current **NITI Aayog** and Ministry of Health practice, DPI uses **Census 2011 population figures cross-referenced with NFHS-5 (2019–2021) district fact sheets** for vulnerability indices.
* **Pilot Coverage:** Implemented across **3 pilot districts in 2 states**:
  * **Maharashtra:** Pune (IND-MH-PUN) & Thane (IND-MH-THA)
  * **Uttar Pradesh:** Varanasi (IND-UP-VAR)

---

## 🌐 BRICS Cross-Border Generalization

DPI is built to scale across BRICS member states (India, Brazil, South Africa, etc.) through an abstracted 4-tier hierarchy:

| Level | India Implementation | Brazil Mapping | South Africa Mapping |
|---|---|---|---|
| **Admin 0** | Country (`IND`) | Country (`BRA`) | Country (`ZAF`) |
| **Admin 1** | State (e.g., Maharashtra) | Estado (e.g., São Paulo) | Province (e.g., Gauteng) |
| **Admin 2** | District (e.g., Pune) | Município (e.g., Campinas) | District Municipality |
| **Admin 3** | Taluka / Block / Ward | Bairro / Distrito | Local Municipality / Ward |

To onboard a new nation, administrators simply upload country demographic CSVs and facility registries conforming to the open JSON schemas in `docs/schemas/`. No core algorithm changes are required.

---

## ☁️ Production Scale-Up on Google Cloud

DPI was designed with open standards to ensure zero proprietary vendor lock-in as a **Digital Public Good**. When moving from prototype to national deployment using Google Cloud credits:

| Prototype Component | Open Standards (Current) | Production Google Cloud Target |
|---|---|---|
| **AI Layer** | Gemini 1.5 Flash (AI Studio) | **Vertex AI (Gemini 1.5 Pro + Search Grounding)** |
| **Compute** | Uvicorn / Render | **Google Cloud Run (Auto-scaling serverless)** |
| **Database** | SQLite Local Storage | **Cloud SQL (PostgreSQL) + BigQuery Analytics** |
| **Spatial Map** | Leaflet + OpenStreetMap | **Google Maps Platform (Photorealistic 3D / Maps API)** |
| **Voice Processing** | Web Speech API | **Google Cloud Speech-to-Text & Translation API** |
| **Auth & Security** | Session Guard | **Firebase Authentication (Government SSO / e-Pramaan)** |

---

## 🚀 Quickstart & Local Installation

### Prerequisites
* Python 3.10+
* Modern web browser (Chrome / Edge recommended for Web Speech API)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/GauriShinde911/flashoint-.git
cd flashoint-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
```bash
cp .env.example .env
```
Edit `.env`:
```ini
GEMINI_API_KEY=your_google_ai_studio_key_here
USE_MOCK_GEMINI=true   # Set false when you provide a real Gemini key
STORAGE_BACKEND=sqlite
```

### 3. Ingest Real & Synthetic Data
```bash
python scripts/ingest.py
```

### 4. Run Automated Test Suite (139 Tests)
```bash
python -m pytest tests/ -v
```

### 5. Launch Application
**Terminal 1 (Backend API):**
```bash
uvicorn backend.app.main:app --port 8000 --reload
```

**Terminal 2 (Frontend Web Server):**
```bash
python -m http.server 3000 --directory frontend
```

* **Login Portal:** [http://localhost:3000/login.html](http://localhost:3000/login.html)
  * **Citizen:** `citizen` / `citizen123` → Redirects to Citizen Voice/Text Portal (`citizen.html`)
  * **Policymaker:** `admin` / `dpi@2025` → Redirects to Policymaker Intelligence Dashboard (`index.html`)

---

## 📜 Licensing & Open Source Compliance

* **Software License:** [MIT License](LICENSE)
* **Dataset & Library Attributions:** Full credits and citations documented in [CREDITS.md](CREDITS.md)
* **Architecture Blueprint:** Detailed mathematical formulas and schemas in [ARCHITECTURE.md](ARCHITECTURE.md)
