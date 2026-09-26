# System Architecture Blueprint — Development Priority Intelligence

## 1. Architectural Philosophy

1. **Separation of Arithmetic and Natural Language:**
   - **Deterministic Engines compute:** Priority Scores, Silent Need flags, Investment Mismatches, and Impact Percentages are computed exclusively in deterministic Python code. Gemini is **never** asked to perform mathematical calculations.
   - **Gemini explains:** Gemini takes the computed figures, verified data citations, and localized context to generate objective, natural-language justifications for policymakers.
2. **Privacy & Security First:**
   - All API keys, database credentials, and GenAI client configurations reside strictly inside the FastAPI backend. The frontend client never touches the Gemini API key.
3. **Multi-Region & Cross-Border Generalization:**
   - The platform operates on a generic 4-tier administrative hierarchy (`Admin 0` through `Admin 3`), making it directly deployable across BRICS member states.

---

## 2. End-to-End Data Flow

```mermaid
flowchart TD
    subgraph Citizen Interface
        A1[Voice Input / Web Speech API] --> B[FastAPI Gateway /api/v1/requests]
        A2[Text Input / Form] --> B
        A3[Messaging App Webhook / WhatsApp API] --> B
    end

    subgraph Backend - Ingestion & Understanding
        B --> C[Gemini Understanding Agent]
        C -->|Language Detection| D1[Standardized Intent]
        C -->|Category Classification| D2[Sector Tag: Health/Water/Roads/Edu]
        C -->|Entity & Geo Extraction| D3[Location & Urgency]
        C -->|Semantic Clustering| D4[Aggregated Demand Hotspots]
    end

    subgraph Data Fusion Layer
        D4 --> E[Fusion Engine]
        F1[(Census 2011 + NFHS-5)] --> E
        F2[(National Hospital Directory)] --> E
        F3[(PMGSY & Jal Jeevan Datasets)] --> E
        F4[(Public Investment Records)] --> E
    end

    subgraph Deterministic Analytics Engine
        E --> G1[Priority Scoring Engine]
        E --> G2[Silent Need Detector]
        E --> G3[Investment-Demand Mismatch Engine]
        E --> G4[Impact Measurement Engine]
    end

    subgraph Grounded Explanation Layer
        G1 & G2 & G3 & G4 --> H[Gemini Explanation Agent]
        H -->|Grounded in exact computed numbers| I[Structured Evidence Payload]
    end

    subgraph Policymaker Dashboard
        I --> J1[Leaflet.js Geospatial Multi-Region Map]
        I --> J2[Ranked Priority Recommendations Panel]
        I --> J3[Post-Project Impact Assessment View]
        I --> J4[Policymaker NL Query Command Bar]
    end
```

---

## 3. The 4 Analytical Engines (Plain Python Implementation)

### 3.1. Priority Scoring Engine
Calculates an objective score from 0 to 100 for every sector and administrative unit:
$$\text{Priority Score} = \min\left(100, \, w_1 \cdot \text{Demand} + w_2 \cdot \text{PopAffected} + w_3 \cdot \text{InfraDeficit} + w_4 \cdot \text{AccessDeficit} - w_5 \cdot \text{ExistingInvestment}\right)$$
- **Demand:** Number of clustered citizen complaints normalized by time and population.
- **PopAffected:** Target demographic slice (e.g., rural population, women/infant cohort).
- **InfraDeficit:** Existing facilities per capita compared to national minimum standard.
- **AccessDeficit:** Average travel distance to nearest operational facility.
- **ExistingInvestment:** Inverse scaling of active/ongoing capital expenditures in the target sector.

### 3.2. Silent Need Detector
Flags regions with acute socioeconomic vulnerability but disproportionately low digital complaint volumes (often caused by low digital literacy, poor connectivity, or marginalized communities):
$$\text{Silent Need Flag} = \text{True} \quad \text{if } \text{InfraDeficit} \ge \tau_{\text{high}} \quad \text{and} \quad \text{ReportedDemand} \le \tau_{\text{low}}$$
Surfaces alerts like: *"High risk of underreporting in Block X — severe healthcare deficit detected despite minimal digital complaints."*

### 3.3. Investment–Demand Mismatch Engine
Identifies misaligned public finance:
- **Underfunded Hotspot:** High Citizen Demand + High Infrastructure Deficit + Zero/Low Ongoing Capital Outlay.
- **Ineffective Expenditure Warning:** High Existing Investment + Persistent or Increasing Citizen Complaints.

### 3.4. Impact Measurement Engine (Before vs. After)
Directly answers the third clause of the official brief.
For any public project marked as `"Completed"` in the government records with completion timestamp $T_{\text{complete}}$:
1. Calculates $\text{Complaints}_{\text{Pre}}$ and $\text{PriorityScore}_{\text{Pre}}$ in the interval $[T_{\text{complete}} - \Delta t, T_{\text{complete}}]$.
2. Calculates $\text{Complaints}_{\text{Post}}$ and $\text{PriorityScore}_{\text{Post}}$ in the interval $[T_{\text{complete}}, T_{\text{complete}} + \Delta t]$.
3. Computes the **Measured Impact Delta**:
$$\text{Impact Ratio} = \frac{\text{Complaints}_{\text{Pre}} - \text{Complaints}_{\text{Post}}}{\text{Complaints}_{\text{Pre}}} \times 100\%$$
Clearly labeled in the dashboard: *"Based on available post-commissioning reporting data."*

---

## 4. BRICS Generic Administrative Hierarchy

To ensure cross-border reusability across India, Brazil, South Africa, and other nations, the schema abstracts geography into standardized levels:

| Generic Level | India Implementation | Brazil Example | South Africa Example |
| :--- | :--- | :--- | :--- |
| **Admin 0 (Country)** | India (`IND`) | Brazil (`BRA`) | South Africa (`ZAF`) |
| **Admin 1 (State / Province)** | State (e.g. Maharashtra, UP) | State (e.g. São Paulo, Bahia) | Province (e.g. Gauteng) |
| **Admin 2 (District / Municipality)**| District (e.g. Pune, Varanasi) | Municipality (Município) | District Municipality |
| **Admin 3 (Sub-District / Locality)**| Taluka / Block / Ward | Bairro / Distritos | Local Municipality / Ward |

Adapting the platform to a new nation requires only changing configuration files and loading country-specific open data. The entire backend ingestion, agent processing, and scoring logic remain untouched.

---

## 5. Country Onboarding Workflow (e.g. Adding Brazil / South Africa)

To onboard a new BRICS member state:

1. **Step 1: Define Country Configuration (`config/{country_code}.json`)**
   - Specify `country_code` (e.g., `"BRA"`), ISO currency, national languages, and official administrative level labels.
2. **Step 2: Map National Statistical Baselines**
   - Provide demographic data mapped to `docs/schemas/demographics.json` (e.g., Brazilian IBGE census or Stats SA estimates).
3. **Step 3: Ingest Geo-Coded Infrastructure Registries**
   - Load national facility registries (e.g., CNES - Cadastro Nacional de Estabelecimentos de Saúde for Brazil) matching `docs/schemas/infrastructure.json`.
4. **Step 4: Configure Language Pipeline in Gemini**
   - Add national language codes (e.g., Portuguese `"pt"`, Zulu `"zu"`, Afrikaans `"af"`) into `SUPPORTED_LANGUAGES`.
5. **Step 5: Run Ingestion**
   - Execute `python scripts/ingest.py --country BRA`. The scoring formulas, spatial clustering, and dashboard immediately operate on the new territory.

---

## 6. Enterprise Google Cloud Production Scale-Up

To satisfy the hackathon's "Deployability & Scalability" evaluation parameter, the platform was engineered with clear migration paths from open-source prototype to enterprise Google Cloud infrastructure:

```mermaid
flowchart LR
    subgraph Prototype (Zero-Cost DPG)
        A[FastAPI / Local Python]
        B[Local SQLite DB]
        C[Leaflet / OSM Map]
        D[Web Speech API]
        E[Gemini 1.5 Flash via AI Studio]
    end

    subgraph Production Scale-Up (Google Cloud)
        A -.->|Containerize| F[Google Cloud Run Serverless]
        B -.->|Migrate| G[Cloud SQL Postgres + BigQuery]
        C -.->|Upgrade| H[Google Maps Platform / Photorealistic 3D]
        D -.->|Upgrade| I[Google Cloud Speech-to-Text & Translation]
        E -.->|Enterprise Scale| J[Vertex AI + Grounding on BigQuery]
    end
```

1. **Serverless Compute:** Deploy FastAPI container to **Google Cloud Run** for auto-scaling from 0 to 100,000 concurrent citizen submissions.
2. **National Big Data Analytics:** Transition from SQLite to **Google BigQuery** for querying hundreds of millions of nationwide citizen reports against Census shapefiles in seconds.
3. **Enterprise AI & Grounding:** Transition from Google AI Studio to **Vertex AI**, attaching Google Search Grounding and BigQuery vector search to the policymaker explanation agent.
4. **Geospatial Intelligence:** Integrate **Google Maps Platform** APIs (Geocoding, Distance Matrix, Satellite View) to calculate precise citizen travel times to facilities.

