# Dataset Guide — Real Sources + Worked Test Case for Scoring Engine

Development Priority Intelligence relies on verified open government datasets fused with citizen demand signals. This guide details verified sources, critical demographic data notes, and a worked test case to validate the Priority Score logic.

---

## 1. Verified Real Datasets (India)

### Healthcare (Primary Category)
- **National Hospital Directory with Geo Code** (`data.gov.in`, mirrored on `aikosh.indiaai.gov.in`):
  - Live geo-referenced inventory of public and private hospitals, facility levels, bed counts, and specialties.
- **All India Health Centres Directory** (`data.gov.in`):
  - Geo-coded Primary Health Centres (PHCs), Community Health Centres (CHCs), and Sub-Centres across districts.
- **NFHS-5 (National Family Health Survey 2019–21)** (MoHFW / IIPS):
  - Standard district-level health and maternal/child health indicators.
- **HMIS (Health Management Information System)** (`nhm.gov.in`):
  - Facility operational performance and service delivery volumes.

### Education
- **UDISE+ (Unified District Information System for Education Plus)**:
  - Ministry of Education district and school-level infrastructure indicators (pupil-teacher ratios, functional classrooms, electricity, sanitation).

### Water & Sanitation
- **Jal Jeevan Mission Dashboard** (`ejalshakti.gov.in`):
  - Real-time district-wise tap water connection coverage (Har Ghar Jal status).

### Roads & Connectivity
- **PMGSY (Pradhan Mantri Gram Sadak Yojana)** & **MoRTH**:
  - Habitation-level rural road connectivity, paved network length, and habitations without all-weather road access.

### Public Investment & Government Projects
- Scheme-wise expenditure via `data.gov.in` and ministry dashboard releases (e.g. PMGSY financial records, NHM state programme implementation plans).
- Normalization into a unified schema: `project_id`, `name`, `sector`, `location`, `status` (`Announced`, `Ongoing`, `Completed`), `budget_inr_cr`, `completion_date`.

---

## 2. Critical Demographics Note: Census 2011 & NFHS-5

> [!IMPORTANT]
> **Do not assume a live "2026 Census" dataset exists.** India's decennial census (delayed from 2021) is currently ongoing in phases concluding March 1, 2027, and has not yet been released.
> **Methodology:**
> 1. Baseline population, village, and administrative boundaries are drawn from **Census 2011** (the last published national census).
> 2. Recent growth and socioeconomic distributions are projected using **NFHS-5 (2019-21)** district estimates.
> 3. Disclosed transparently in all metadata and documentation.

---

## 3. Worked Sanity Check for the Priority Scoring Engine

Before running on live datasets, the scoring engine must be evaluated against this reference scenario:

| District | Population | Hospitals | Health Infra Gap | Existing Investment | Citizen Demand (Requests) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **District A** | 12 Lakh | 8 | High | ₹10 Cr | 185 |
| **District B** | 8 Lakh | 12 | Low | ₹18 Cr | 42 |
| **District C** | 15 Lakh | 5 | High | ₹6 Cr | 231 |

### Expected Relative Behavior:
1. **District C ranks #1 (Highest Priority)**: Largest population (15 lakh), fewest facilities (5), high gap, highest citizen demand (231), lowest current investment (₹6 Cr).
2. **District A ranks #2 (Moderate Priority)**: High gap and solid demand, moderate population and funding.
3. **District B ranks #3 (Lowest Priority)**: Smallest population, most facilities (12), low gap, low demand (42), highest investment (₹18 Cr).

### Gemini Grounded Explanation Requirement:
Grounded strictly in deterministic metrics without inventing facts:
> *"District C is prioritized because it combines a large affected population (15 lakh), a severe infrastructure shortfall (5 hospitals), high citizen-reported demand (231 requests), and comparatively low existing investment (₹6 Cr) — no equivalent major project currently addresses this gap."*

---

## 4. Synthetic Citizen Demand Dataset Generation Rules

- **Volume:** 150–300 records distributed across 2–3 pilot districts in ≥2 states (e.g., Pune/Thane in Maharashtra, Varanasi/Gorakhpur in Uttar Pradesh).
- **Languages:** English, Hindi (हिन्दी), and Marathi (मराठी).
- **Tagging:** Every synthetic record must contain `data_quality: "synthetic"` and trigger the `"SYNTHETIC DEMO DATA"` UI badge in the dashboard.
- **Lexical Variance:** Varied phrasing for identical underlying infrastructure needs to test the Gemini ADK clustering and classification pipeline (e.g. "no proper hospital nearby", "PHC is 20km away", "गाव में डॉक्टर नहीं है", "प्राथमिक आरोग्य केंद्र खूप लांब आहे").
