# Pitch Deck Outline (10–12 Slides)
**Competition:** Build with AI: Code for Communities (Hack2skill & Google)  
**Track:** AI for Digital Public Infrastructure & Governance  
**Project:** Development Priority Intelligence (DPI)

---

### Slide 1: Title & Vision
* **Title:** Development Priority Intelligence (DPI)
* **Tagline:** Multilingual AI & Deterministic Analytics for National Infrastructure Planning
* **Category:** Track 1: AI for Digital Public Infrastructure & Governance (BRICS Theme: Innovation)
* **Presenters:** Team Name / Contact Info

---

### Slide 2: The Core Governance Problem
* **3 Disconnects in Public Capital Allocation:**
  1. *Fragmented Demand:* Citizen grievances are trapped in disjointed call centers and petitions across 22+ regional languages.
  2. *Misprioritization:* Budget spending often follows political pressure rather than acute infrastructure deficits.
  3. *Zero Accountability / No Impact Measurement:* Governments spend billions on infrastructure without any mechanism to measure if completed public works actually solved citizen pain points.

---

### Slide 3: The Solution — Development Priority Intelligence
* **A Digital Public Good (DPG):** Open-source, modular, and privacy-first.
* **Core Value Proposition:**
  * Aggregates citizen voice & text in regional languages.
  * Fuses citizen voice with official statistical baselines (Census 2011 + NFHS-5) and geocoded facility directories.
  * Computes deterministic priority scores to recommend high-impact projects.
  * Automatically measures post-commissioning impact.

---

### Slide 4: AI & System Architecture
* **Strict Separation of Math and Language:**
  * **Deterministic Python Engine:** Computes 0–100 Priority Scores, Silent Need flags, and Before/After Impact ratios. Zero hallucination.
  * **Google Gemini 1.5 Flash:** Powers the 4-stage understanding pipeline (Detection, Classification, Entity Extraction, Semantic Clustering) + Grounded Explanations.
* *Visual:* Architecture flowchart from `ARCHITECTURE.md`.

---

### Slide 5: The Citizen Voice Experience (Frontend Demo)
* **Accessibility First:**
  * Dual-portal architecture: Public Citizen Portal vs. Protected Policymaker Intelligence Suite.
  * Multilingual Web Speech API (voice recording in Hindi, Marathi, English).
  * Category quick-selectors (Healthcare, Water, Roads, Education) with automatic instant tracking ID.

---

### Slide 6: Grounded in Real Government Data
* **No Fabricated Data:**
  * **Hospitals & PHCs:** Verified geocoded registries from `data.gov.in` (National Hospital Directory & Health Centres Directory).
  * **Demographics:** Census 2011 baseline combined with latest **NFHS-5 (2019–2021)** vulnerability indicators.
  * **Pilot Coverage:** Multi-region validation across 3 districts in 2 states: Pune (MH), Thane (MH), and Varanasi (UP).

---

### Slide 7: Groundbreaking Feature 1 — The Silent Need Detector
* **Why it matters:** The most vulnerable rural communities often file the fewest digital complaints due to connectivity or literacy gaps.
* **Algorithm:** Flags regions where infrastructure per capita is critically low ($\text{Deficit} \ge \tau_{\text{high}}$) yet reported complaints are near zero ($\text{Demand} \le \tau_{\text{low}}$).
* Prevents public spending from unfairly favoring connected urban centers.

---

### Slide 8: Groundbreaking Feature 2 — The Impact Measurement Engine
* **Closing the Governance Loop:**
  * Directly solves the 3rd clause of the problem statement.
  * Continuously monitors citizen feedback after a project's completion date ($T_{\text{complete}}$).
  * Measures complaint reduction ($\Delta \text{Complaints}$) to prove Return on Public Investment (ROPI).

---

### Slide 9: Policymaker Decision Support with Gemini
* **Evidence-Grounded Explanations:** Gemini generates clear, objective policy briefs citing exact formulas, population counts, and facility ratios so officials can defend budget allocations before parliaments and auditors.
* **Natural Language Querying:** Policymakers can ask plain-English questions (*"Where is maternal healthcare lagging in UP?"*) to query complex multi-table datasets.

---

### Slide 10: BRICS & Cross-Border Scalability
* **Global by Design (Rule 04 Compliance):**
  * Generic 4-tier hierarchy: `Admin 0 (Country)` $\rightarrow$ `Admin 1 (State)` $\rightarrow$ `Admin 2 (District)` $\rightarrow$ `Admin 3 (Locality)`.
  * Plug-and-play onboarding for Brazil (IBGE data), South Africa (Stats SA), and other BRICS nations.
  * 100% open JSON Schemas; zero proprietary vendor lock-in.

---

### Slide 11: Production Scale-Up on Google Cloud
* **Transitioning from Prototype to National Scale:**
  * **Compute:** Containerized deployment to **Google Cloud Run**.
  * **Big Data:** Migration to **BigQuery** for sub-second spatial queries over 100M+ nationwide records.
  * **Enterprise AI:** Scaling to **Vertex AI** with search grounding and fine-tuned governance agents.
  * **Maps:** Integration with **Google Maps Platform** for accurate travel-time routing.

---

### Slide 12: Team, Roadmap & Conclusion
* **Summary of Impact:** Eliminates fragmented citizen data, directs spending to where need is highest, and verifies that public funds deliver real results.
* **Next 6 Months:** Pilot deployment with state urban development authorities; onboarding water and transport ministries.
* **Links:** Live Demo URL, GitHub Repository, and Contact Details.
