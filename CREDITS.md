# Credits & Open Source Citations

This project is built as a **Digital Public Good (DPG)** under the [MIT License](LICENSE). In accordance with hackathon guidelines, all public datasets, open-source libraries, and foundational models used in this platform are cited below.

---

## 1. Public Government Datasets

| Dataset | Publisher / Source | Coverage | License / Terms |
|---|---|---|---|
| **National Hospital Directory with Geo-Code** | Ministry of Health & Family Welfare / [data.gov.in](https://data.gov.in/resource/national-hospital-directory-geo-code) | Geocoded hospitals across Pune, Thane, Varanasi | Government Open Data License - India (GODL) |
| **All India Health Centres Directory** | Ministry of Health & Family Welfare / [data.gov.in](https://data.gov.in) | Primary Health Centres (PHCs) & Community Health Centres (CHCs) | Government Open Data License - India (GODL) |
| **Primary Census Abstract (Census 2011)** | Office of the Registrar General & Census Commissioner, India / [censusindia.gov.in](https://censusindia.gov.in) | Total, rural, and urban populations by district | Open Government Data / Public Record |
| **National Family Health Survey (NFHS-5, 2019–2021)** | International Institute for Population Sciences (IIPS) & MoHFW / [rchiips.org/nfhs](http://rchiips.org/nfhs/factsheet_NFHS-5.shtml) | District-level health indicators & vulnerability scores | Public Health Information / MoHFW |

> **Note on Demographics**: India's 2021 decennial census was postponed indefinitely due to COVID-19. Therefore, following current Government of India and NITI Aayog planning conventions, baseline populations are drawn from Census 2011 and cross-indexed with NFHS-5 (2019–2021) district fact sheets.

---

## 2. Artificial Intelligence & Foundational Models

| Technology | Provider | Usage in Platform |
|---|---|---|
| **Gemini 1.5 Flash** | Google AI Studio / Google DeepMind | Multilingual understanding (en/hi/mr), entity extraction, policymaker explanations, and natural language query parsing |
| **Web Speech API** | W3C Standard (Browser native) | Client-side multilingual speech-to-text for citizen voice input |

---

## 3. Open Source Software & Frameworks

| Library | License | Usage |
|---|---|---|
| **FastAPI** | MIT License | High-performance Python backend API framework |
| **Pydantic** | MIT License | Data validation and schema enforcement |
| **SQLite** | Public Domain | Zero-configuration local relational database |
| **Leaflet.js** | BSD 2-Clause License | Interactive mapping and geospatial visualization |
| **Uvicorn** | BSD 3-Clause License | ASGI web server implementation |
| **Pytest** | MIT License | Automated testing and verification suite |
