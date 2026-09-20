# BRICS Cross-Border Adaptation Guide

Development Priority Intelligence is built to be easily configured and deployed in any BRICS nation (Brazil, Russia, India, China, South Africa, etc.) without redesigning the platform.

---

## 1. Modular Hierarchy Mapping

When onboarding a new country, map its administrative layers to the platform's generic `Admin 0` through `Admin 3` fields:

```
[Admin 0] Country
    │
    └── [Admin 1] First-Level State / Province / Federal Subject
            │
            └── [Admin 2] District / Municipality / Rayon / County
                    │
                    └── [Admin 3] Ward / Locality / Sub-district / Commune
```

### Country Configuration Examples:
- **India (`IND`):** Country → State → District → Sub-district/Block
- **Brazil (`BRA`):** País → Estado → Município → Distrito/Bairro
- **South Africa (`ZAF`):** Country → Province → District Municipality → Local Ward

---

## 2. Onboarding Steps for a New Nation

1. **Update Geography Config (`config.py` or `.env`):**
   ```python
   DEFAULT_COUNTRY = "BRA"
   ADMIN1_LABEL = "Estado"
   ADMIN2_LABEL = "Município"
   CURRENCY_CODE = "BRL"
   ```
2. **Ingest Country Baseline Datasets:**
   - Place population and boundary GeoJSON files in `data/raw/demographics/`.
   - Ingest hospital and school directories conforming to `docs/data-schema.md`.
3. **Configure Local Language Support in Gemini Prompts:**
   - Gemini handles translation and semantic extraction natively (e.g. Portuguese for Brazil, Russian for Russia).
4. **Deploy Dashboard:**
   - Leaflet automatically adjusts bounding box and coordinates according to the country GeoJSON.
   - The deterministic Priority Scoring and Impact Measurement formulas remain 100% reusable.
