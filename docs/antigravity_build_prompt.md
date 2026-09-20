# Antigravity Build Prompt — Development Priority Intelligence (Track 1)
Paste this whole document into Antigravity as the project brief.

---

## 1. Understand the problem before building anything

**Official brief (Track 1 — AI for Digital Public Infrastructure & Governance, BRICS Theme: Innovation):**
*"Governments across India struggle to consolidate citizen feedback and align it with national infrastructure priorities. Development requests live in fragmented systems, leading to misaligned public spending, unaddressed infrastructure gaps, and no way to measure the impact of large-scale digital public infrastructure initiatives. Build a scalable, multilingual AI platform — designed as a Digital Public Good — that aggregates citizen development requests via voice, text, and messaging apps across diverse linguistic regions. The system should analyse large datasets combining citizen feedback with national demographic data, infrastructure indices, and public investment plans, surfacing demand hotspots and recommending high-priority development projects to national policymakers across BRICS nations."*

This actually contains **three distinct problems**, not one — build for all three, not just the obvious one:

1. **Fragmentation** — citizen feedback arrives through disconnected channels/languages and is never combined with government-held data (demographics, infrastructure, investment). → Needs an ingestion + data-fusion layer.
2. **Misprioritization** — without fusing demand with data, spending doesn't go where need is highest. → Needs a scoring/recommendation engine with explainability, since policymakers must be able to defend a recommendation.
3. **No impact measurement** — this is a separate, backward-looking problem from #2, and it's easy to miss because it reads like an afterthought in the paragraph. Once a project *is* funded, there's currently no way to tell whether it actually reduced the underlying need. This wants a **before/after measurement engine**, not another forecast. Most teams will only build #1 and #2 — explicitly building #3 is a genuine differentiator because it directly answers a named clause in the official problem statement that a purely forward-looking "priority dashboard" does not.

Target user: **national policymakers**, evaluating priorities **across states and regions**, not one city or one constituency. Scope: **BRICS Theme: Innovation** — built for India first, but structurally reusable for other BRICS nations.

---

## 2. The solution, as a workflow (read this before the phase breakdown)

```
CITIZEN                                                    
  │  voice / text / messaging-app request, any language     
  ▼
CAPTURE LAYER  →  Web Speech API (voice→text in browser) or direct text/photo
  ▼
BACKEND (FastAPI)  →  receives request, holds credentials, orchestrates everything below
  ▼
GEMINI — UNDERSTANDING
  ├─ language detection + translation of intent (no separate Translation API needed)
  ├─ category / sub-category / urgency classification
  ├─ location + entity extraction
  └─ semantic clustering (merge duplicate/related requests into one underlying need)
  ▼
STRUCTURED CITIZEN DEMAND  (stored in Firestore, tagged data_quality: real|synthetic)
  ▼
DATA FUSION  ←  demographics + infrastructure inventory + government project records + investment data
  │              (5–8 real datasets from data.gov.in, 2–3 pilot districts across ≥2 states)
  ▼
DETERMINISTIC ANALYTICS ENGINE  (plain code — Gemini never does the arithmetic)
  ├─ Priority Score (0–100): demand × population affected × infra deficit × accessibility × (inverse) existing investment
  ├─ Silent Need Detector: high inferred need + low reported complaints → flag possible underreporting
  ├─ Investment–Demand Mismatch: high demand + low investment → funding gap; high investment + persistent demand → check project effectiveness
  ├─ Existing-Project Check: is a project already targeting this gap? surface it instead of duplicating
  └─ IMPACT MEASUREMENT ENGINE (the piece most teams skip):
        for each project marked "Completed" in the government dataset, compare the
        Priority Score / complaint volume for its category+region BEFORE the completion
        date vs AFTER it (using request timestamps). Output a measured Impact Score,
        clearly labeled as based on available data, not a guarantee. This is the direct
        answer to "no way to measure the impact of digital public infrastructure initiatives."
  ▼
GEMINI — EXPLANATION
  └─ turns the actual numbers above into a grounded justification: "Healthcare accessibility
     in District X is ranked #1 because of 8,240 related requests, 250,000 people affected,
     an 18km average distance to the nearest facility, and no funded project currently
     addressing it." Gemini explains; it never invents the ranking.
  ▼
POLICYMAKER DASHBOARD  (multi-region, national framing)
  ├─ Map (Leaflet + OpenStreetMap): state/district selector, priority overlay
  ├─ Ranked recommendations with full evidence trail
  ├─ Silent Need flags, Investment-Demand Mismatch view
  ├─ Impact Measurement view: "here's what happened after past projects were funded"
  ├─ Natural-language query box ("districts with high healthcare demand, low investment") — Gemini parses it into a structured filter; the backend executes the filter deterministically
  └─ REAL DATA / SYNTHETIC DEMO DATA badge on every panel, driven by data_quality field
```

This workflow is what Antigravity should build — the phases below just sequence it.

---

## 3. Product identity

**Name:** Development Priority Intelligence
**One-liner:** An AI platform that turns fragmented citizen requests, government data, and investment records into explainable development priorities and measured project impact — built for India, structurally reusable across BRICS nations.

---

## 4. Judging weights (design toward these)

1. AI/Technical Execution — 25%
2. Problem-Solution Fit — 20%
3. Depth & Reach Across India — 20%
4. Deployability & Scalability — 20%
5. Impact Potential — 15%

Mandatory Build checklist: (1) functioning end-to-end flow, (2) Google AI integration, (3) real or clearly-labeled realistic data, (4) built for India — multiple states/regions, not one city, (5) multilingual/voice support.
Mandatory rules: Google AI required; Digital Public Good design (open license, open schemas, modular); BRICS cross-border applicability; cite any reused open-source code.

---

## 5. Which tools need a GCP billing account (card) vs which don't

Decide the stack on this basis — it's the real constraint, not effort or time.

**Free, no card, use as the default stack:**
| Tool | Google? | Note |
|---|---|---|
| Gemini API | Google | Free key from aistudio.google.com |
| Google ADK | Google | Open-source orchestration library, runs on your Gemini key |
| Gemini multimodal (image input) | Google | Handles photo-evidence directly — no Vertex AI Vision needed |
| Firebase (Spark/free plan): Firestore, Auth, Hosting | Google | Free tier needs no card |
| BigQuery Sandbox | Google | Free up to 10GB storage / 1TB query per month |
| Leaflet.js + OpenStreetMap | Not Google | Map visualization — no key |
| Browser Web Speech API | Not Google (browser-native) | Voice capture only — label it as capture, not AI, in the deck |
| GitHub Actions | Not Google (GitHub) | Scheduled ingestion refresh |
| Render (free web service tier) | Not Google | Hosts the FastAPI backend — verified as of 2026 to need no card (750 hrs/month, cold start after ~15 min idle) |

**Require GCP billing, even at free-tier usage — optional, only if you get hackathon credits:**
| Tool | Why gated | Substitute used instead |
|---|---|---|
| Vertex AI (AutoML/custom training) | Needs billing | Not substituted — genuinely optional |
| Cloud Speech-to-Text / TTS / Translation | Needs billing | Web Speech API for capture; Gemini for language understanding |
| Cloud Run / Cloud Functions | Needs billing | Render free tier — same backend code, swap deploy target later |
| Cloud Scheduler | Needs billing | GitHub Actions |
| Google Maps Platform | Needs billing | Leaflet + OpenStreetMap |
| Full BigQuery beyond Sandbox | Needs billing at scale | BigQuery Sandbox or Firestore |

Architecture note: don't remove the backend to dodge billing. A real backend (FastAPI) keeps the Gemini key server-side, centralizes scoring/validation, and is a stronger "Deployability" story — just host it on Render instead of Cloud Run. Cloud Run stays as the documented upgrade path once you have credits/billing.

Verify current free-tier limits before building — they change, and this table is the current best understanding, not a permanent guarantee.

---

## 6. Build phases

**Phase 1 — Data foundation**
- Data model: citizen requests (id, text, language, category, location, timestamp, source-channel [voice/text/messaging-app], urgency), demographics, infrastructure inventory, government projects (name, location, sector, status, investment, dates). Every record carries `source`, `source_url`, `retrieved_at`, `data_quality` (`real`|`synthetic`).
- Load 5–8 real datasets from data.gov.in covering **2–3 pilot districts across ≥2 states** — one pilot area fails the "scale across states" requirement. **See `DATASET_GUIDE.md` for the specific verified datasets to pull, per category, plus a worked numeric example to test your scoring engine against before wiring the full dashboard. It also flags an important correction: don't assume "2026 Census" data exists — India's next census is still being conducted and isn't released yet, so population figures should come from Census 2011 (last published) plus NFHS-5 district estimates, stated honestly in the README.**
- Generate a clearly-labeled synthetic citizen-request dataset (150–300 records, multiple languages, tagged by source-channel including "messaging app" as its own channel type — full WhatsApp Business API integration is a documented production step, not built now).
- Backend stores everything in Firestore (or BigQuery Sandbox for SQL-style analytics).
- Rerunnable ingestion/update script with `dataset_version` tracking, triggered by a GitHub Actions scheduled workflow.

**Phase 2 — Understanding (Gemini + ADK)**
- Gemini: language detection, classification, entity extraction, semantic clustering — all through the backend, key never exposed to the browser.
- Structure as an ADK agent pipeline (ingestion agent → classification agent → synthesis agent → scoring engine handoff) rather than one-shot prompting. Additive to a working Gemini pipeline, not a replacement for one that already works.
- Voice: Web Speech API captures and transcribes client-side, backend receives text.

**Phase 3 — Deterministic analytics (the core differentiators)**
- Priority Score, Silent Need Detector, Investment–Demand Mismatch, Existing-Project Check — all in plain code, not Gemini.
- **Impact Measurement Engine** — compare pre/post completion-date demand signals for projects marked "Completed," producing a measured (not projected) impact figure per project. Build this in Phase 3, not as an afterthought — it directly answers the named "no way to measure impact" problem.
- Gemini explanation layer: takes the actual numbers above and produces grounded, evidence-cited justifications — never invents a ranking.

**Phase 4 — Multi-region policymaker dashboard**
- Map (Leaflet + OpenStreetMap): state/district selector, priority overlay across all loaded pilot regions side by side — not a single-region view.
- Ranked recommendations, Silent Need flags, Investment-Demand Mismatch view, and the Impact Measurement view (what happened after past projects).
- Natural-language query box: Gemini parses the question into a structured filter; the backend executes it deterministically against real data ("Policymaker AI Command Center").
- REAL DATA / SYNTHETIC DEMO DATA badge on every panel and figure, driven by `data_quality`.
- Deploy: frontend on Firebase Hosting, backend on Render — both free, no card. This is the mandatory core; it must be fully working end-to-end before anything below is attempted.

**Phase 5 — Optional enhancements (build after Phase 1–4 work)**
- Vertex AI AutoML demand forecasting, layered on the existing Priority Score as a "projected demand" figure — only if GCP billing/credits are available; otherwise document as the production roadmap.
- Photo-evidence: citizen attaches a photo, Gemini's own multimodal input (same free key, no Vertex AI Vision needed) verifies severity and feeds it into urgency scoring. This is free, so it can be added anytime once the core flow works.

---

## 7. BRICS cross-border design

Model the location hierarchy generically — **Country → Administrative Level 1 → Administrative Level 2 → Locality** — configured for India (Country → State → District → Village) as the default instance, not hardcoded into the schema or logic. Document in `ARCHITECTURE.md` exactly what changes to onboard a new country (config, datasets, languages) vs what's structurally reusable (ingestion, scoring engine, ADK agents, dashboard). This satisfies the explicit BRICS rule and is a genuine differentiator most teams will skip.

## 8. Digital Public Good requirements

- Open license (MIT or Apache-2.0) in the repo root.
- Data schemas in open formats (JSON Schema/CSV), documented in `/docs/data-schema.md`.
- No proprietary dependencies beyond what's necessary.
- README states explicitly: "Designed as a Digital Public Good: open license, open schemas, modular, reusable across regions, runnable on free-tier infrastructure."

## 9. Explicit "do not build"

- No generic chatbot with no data backing.
- No complaint-ticketing system dressed up as "AI platform."
- No unexplained priority score — every score must show its inputs.
- No fabricated real-time claims for data that's actually static/batch.
- Don't stuff in Google products (Earth Engine, Dialogflow, full Vertex AI suite) that aren't doing real work in the demo — judges notice technology-name-stuffing.

## 10. Deliverables (maps to the 5 submission-package items)

- `README.md` — problem (all three sub-problems from Section 1), solution, AI approach, target user, BRICS note, DPG note, real-vs-synthetic disclosure. (Item 1: source code entry point.)
- `BRIEF_DESCRIPTION.md` — required 2–3 line summary, written once the MVP is stable. (Item 4.)
- `DEMO_SCRIPT.md` — 3–5 minute walkthrough script, showing the multi-region dashboard and the Impact Measurement view explicitly — these are the two things a generic team won't have. (Item 2.)
- `PITCH_OUTLINE.md` — 10–12 slides: the three-part problem, solution, AI approach (Gemini + ADK), data sources, differentiators (Silent Need, Investment-Demand Mismatch, Impact Measurement, photo-evidence), scaling across India's states, BRICS reuse, deployability on free-tier infra, impact, team, ask. (Item 3.)
- `.env.example` + Render/Firebase deploy config. (Item 5: deployed link.)
- `LICENSE` (MIT/Apache-2.0), `CREDITS.md` (cite any reused open-source components).

## 11. Build instruction to Antigravity

Scaffold the repo (frontend/backend/data/docs + deliverable files above). Build Phase 1 → 2 → 3 → 4 in that order — this is the mandatory core, must be fully working, deployed, and demoable using only the free/no-card tools in Section 5. Commit at each phase boundary so there is always a working state. Only after Phase 4 works end-to-end, attempt Phase 5 (Vertex AI forecasting if billing is available; photo-evidence anytime since it's free). Do not let Phase 5 destabilize the working core.
