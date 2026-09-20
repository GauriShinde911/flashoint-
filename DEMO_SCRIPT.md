# Demo Script: Development Priority Intelligence (3–5 Minutes)

**Target Audience:** Hackathon Judges, Policymakers, Public Sector Evaluators  
**Key Differentiators to Emphasize:**
1. Multi-region cross-state national dashboard (not just a single city).
2. Deterministic scoring with grounded, evidence-backed Gemini justifications.
3. Silent Need Detector & Investment-Demand Mismatch.
4. **Before/After Impact Measurement Engine** (evaluating past completed projects).

---

## Act 1: The Problem & Ingestion (0:00 – 1:00)

- **Narrator:**
  *"Governments receive millions of citizen requests, but they live in fragmented silos. Worse, funding decisions frequently overlook real infrastructure deficits, and once projects are built, nobody measures whether citizen complaints actually dropped."*
- **Action on Screen:**
  - Open the **Citizen Voice & Messaging Portal**.
  - Speak in Hindi or Marathi using Web Speech API: *"हवेली तालुक्यात नवीन प्राथमिक आरोग्य केंद्राची तातडीने गरज आहे."* (Need a new PHC urgently in Haveli taluka).
  - Show immediate transcription and Gemini language normalization into structured intent with zero manual categorization.
  - Highlight the `"SYNTHETIC DEMO DATA"` or `"REAL DATA"` badge to demonstrate transparent data integrity.

---

## Act 2: Multi-Region National Command Center (1:00 – 2:30)

- **Action on Screen:**
  - Switch to the **Policymaker Dashboard**.
  - Display the Leaflet map showing multiple pilot districts across states (Maharashtra: Pune, Thane; Uttar Pradesh: Varanasi, Gorakhpur).
  - Point out that this is built for national and state leadership, not isolated municipal complaints.
- **Narrator:**
  *"Here is our multi-region view. The platform fuses Census 2011 and NFHS-5 demographics with official facility directories from data.gov.in and real investment outlays."*
- **Highlight Engine Results:**
  - Click on **District C / Pune rural block**: Show Priority Score.
  - Read Gemini's grounded explanation: *"Prioritized because 15 lakh residents share only 5 facilities, with 231 citizen requests and only ₹6 Cr invested."* Show that the numbers match the deterministic calculations exactly.
  - Point out the **Silent Need Alert**: Flagging an area with high infant mortality and low health facilities, where digital complaints were low due to connectivity issues.

---

## Act 3: The Differentiator — Impact Measurement Engine (2:30 – 3:45)

- **Action on Screen:**
  - Click the **"Project Impact Measurement"** tab.
  - Select a completed government project: *e.g., "Upgradation of Sub-District Hospital, Completed August 2024"*.
- **Narrator:**
  *"This is what most platforms miss. DPI doesn't just predict future projects; it audits past public spending. By comparing citizen complaints in the 6 months before project completion against the 6 months after, our engine computes a verified Impact Score."*
- **Result on Screen:**
  - Show: Pre-Completion Complaints: 184 → Post-Completion: 38 (79.3% reduction in healthcare access grievances).
  - Clearly show the label: *"Verified Reduction — Based on available post-commissioning reporting data."*

---

## Act 4: Natural Language Query & BRICS Architecture (3:45 – 4:30)

- **Action on Screen:**
  - In the AI Query Bar, type: *"Show me districts in Maharashtra with high water sanitation demand but under ₹10 Cr allocated"*.
  - Show Gemini parsing this into structured filters and executing deterministically.
  - Conclude with the **BRICS generic architecture**: Showing how the Admin 0–3 schema instantly adapts to Brazil, South Africa, and other partners as a Digital Public Good.
