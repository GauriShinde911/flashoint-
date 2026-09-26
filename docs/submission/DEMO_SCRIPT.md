# Demo Video Script (3–5 Minutes)
**Event:** Build with AI: Code for Communities (Hack2skill & Google)  
**Track 1:** AI for Digital Public Infrastructure & Governance  
**Project:** Development Priority Intelligence (DPI)

---

## ⏱️ Video Breakdown

| Timestamp | Screen / Visual | Narration & Key Actions |
|---|---|---|
| **0:00 – 0:45** | **Slide / Title & Problem** | • Introduce the problem: Fragmented citizen feedback, biased budget allocation, and zero ability to track if completed infrastructure actually solved citizen pain points.<br>• Introduce **DPI**: An open-source Digital Public Good powered by Google Gemini and deterministic analytics. |
| **0:45 – 1:30** | **Login & Citizen Portal (`login.html` & `citizen.html`)** | • Show the dual-role login page: separate Citizen and Policymaker entry points.<br>• Sign in as **Citizen**.<br>• Switch language to Hindi / Marathi to show multilingual UI.<br>• Click the microphone icon (**Web Speech API**) and speak a grievance in Hindi/English (e.g. *"Our primary health centre has no doctors and roof is leaking"*).<br>• Submit the request and show instant receipt ID (`REQ-XXXX`). |
| **1:30 – 2:30** | **Policymaker Analytics Dashboard (`index.html`)** | • Sign out and log in as **Policymaker** (`admin` / `dpi@2025`).<br>• Show the multi-region interactive map (Leaflet) displaying pilot districts across 2 states (Pune, Thane in Maharashtra; Varanasi in Uttar Pradesh).<br>• Highlight the **Deterministic Priority Scores** (0–100) combining Census 2011, NFHS-5 vulnerability indices, and real `data.gov.in` hospital/PHC registries.<br>• Point out the **Silent Need Detector**: An alert flagging an underreported rural block where vulnerability is high but digital reports are low. |
| **2:30 – 3:30** | **Google Gemini AI Explanations & Natural Language Query** | • Click on a high-priority district (e.g., Pune or Varanasi).<br>• Click **"Generate Grounded Explanation"** powered by **Gemini 1.5 Flash**.<br>• Point out that Gemini produces an evidence-grounded policy defense citing exact figures and ratios computed by the backend.<br>• Open the **Natural Language Query bar** and type: *"Show healthcare infrastructure gaps in Varanasi"*.<br>• Show Gemini translating conversational query into structured filters and surfacing relevant records. |
| **3:30 – 4:15** | **Impact Measurement Engine (The Differentiator)** | • Switch to the **Impact Measurement tab**.<br>• Explain the Before-vs-After engine: for completed government projects, DPI compares citizen complaint volumes before commissioning vs. after commissioning.<br>• Show the **Measured Impact Delta** (+68% grievance reduction post-project completion). |
| **4:15 – 4:45** | **BRICS Scalability & Google Cloud Roadmap** | • Highlight the generic `Country → Admin1 → Admin2` schema enabling immediate deployment across BRICS nations (Brazil, South Africa).<br>• Conclude with the Google Cloud scale-up path (Google Cloud Run, Vertex AI, BigQuery). |

---

## 💡 Tips for Recording
1. **Audio:** Use a clean microphone or headset in a quiet room.
2. **Speed:** Keep transitions brisk and crisp. Do not wait for long explanations.
3. **Resolution:** Record in 1080p full screen at 60fps.
4. **Key Message:** Emphasize that **mathematics are deterministic** (trustworthy for government audits) while **Google Gemini provides the human understanding, clustering, and policy explanations**.
