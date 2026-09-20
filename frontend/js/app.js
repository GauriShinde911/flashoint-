// Development Priority Intelligence - Frontend Controller
const API_BASE = "http://localhost:8000/api/v1";

// Pilot Regions Coordinate Reference
const PILOT_COORDINATES = [
  { name: "Pune", state: "Maharashtra", lat: 18.5204, lon: 73.8567, score: 76.5, sector: "healthcare" },
  { name: "Thane", state: "Maharashtra", lat: 19.2183, lon: 72.9781, score: 79.2, sector: "water_sanitation" },
  { name: "Varanasi", state: "Uttar Pradesh", lat: 25.3176, lon: 82.9739, score: 48.6, sector: "healthcare" },
  { name: "Gorakhpur", state: "Uttar Pradesh", lat: 26.7606, lon: 83.3732, score: 84.1, sector: "healthcare" }
];

let mapInstance = null;
let markers = [];

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  loadPriorities();
  loadImpactAudit();
  initVoiceCapture();
});

// Initialize Leaflet Map
function initMap() {
  const mapEl = document.getElementById("map-container");
  if (!mapEl) return;

  // Center over India
  mapInstance = L.map("map-container").setView([21.5, 78.9], 5);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(mapInstance);

  renderMapMarkers(PILOT_COORDINATES);
}

function renderMapMarkers(data) {
  if (!mapInstance) return;

  markers.forEach(m => mapInstance.removeLayer(m));
  markers = [];

  data.forEach(item => {
    let color = "#10b981";
    if (item.score >= 75) color = "#f43f5e";
    else if (item.score >= 50) color = "#f59e0b";

    const circleMarker = L.circleMarker([item.lat, item.lon], {
      radius: 12,
      fillColor: color,
      color: "#ffffff",
      weight: 2,
      opacity: 1,
      fillOpacity: 0.85
    }).addTo(mapInstance);

    circleMarker.bindPopup(`
      <div style="color: #0b0f19; font-family: 'Plus Jakarta Sans', sans-serif;">
        <strong style="font-size: 1.05rem;">${item.name}, ${item.state}</strong><br>
        <span style="color: #64748b; text-transform: capitalize;">Sector: ${item.sector.replace('_', ' ')}</span><br>
        <div style="margin-top: 6px; font-weight: 700; color: ${color};">Priority Score: ${item.score} / 100</div>
      </div>
    `);

    markers.push(circleMarker);
  });
}

// Load Priority Recommendations
async function loadPriorities() {
  const container = document.getElementById("rankings-container");
  try {
    const res = await fetch(`${API_BASE}/priorities`);
    if (!res.ok) throw new Error("Backend offline");
    const data = await res.json();
    renderPriorities(data);
  } catch (err) {
    console.warn("Using offline fallback data for priorities:", err);
    // Offline resilient fallback
    const fallback = [
      {
        rank: 1,
        district_name: "Gorakhpur",
        state_name: "Uttar Pradesh",
        sector: "healthcare",
        priority_score: 84.1,
        grounded_explanation: "Gorakhpur (Uttar Pradesh) is ranked #1 for healthcare due to an affected population of 44.4 lakh, 31 facilities against an estimated target, 260 citizen grievance reports, and comparatively low existing investment of ₹5.0 Cr.",
        silent_need_flag: false,
        mismatch_status: "underfunded_hotspot"
      },
      {
        rank: 2,
        district_name: "Thane",
        state_name: "Maharashtra",
        sector: "water_sanitation",
        priority_score: 79.2,
        grounded_explanation: "Thane (Maharashtra) is prioritized for water & sanitation due to rapid peri-urban expansion affecting 110 lakh residents, 245 grievance reports regarding pipeline breaks, and ₹6.2 Cr current allocation.",
        silent_need_flag: false,
        mismatch_status: "underfunded_hotspot"
      },
      {
        rank: 3,
        district_name: "Pune",
        state_name: "Maharashtra",
        sector: "healthcare",
        priority_score: 76.5,
        grounded_explanation: "Pune (Maharashtra) rural blocks demonstrate significant healthcare deficits with 210 requests for primary health facilities across 94.3 lakh citizens with ₹14.5 Cr ongoing expenditure.",
        silent_need_flag: true,
        mismatch_status: "balanced"
      },
      {
        rank: 4,
        district_name: "Varanasi",
        state_name: "Uttar Pradesh",
        sector: "healthcare",
        priority_score: 48.6,
        grounded_explanation: "Varanasi (Uttar Pradesh) reflects moderate priority score 48.6 with 42 facilities, 95 citizen requests, and active public investments of ₹22.0 Cr already addressing major hospital requirements.",
        silent_need_flag: false,
        mismatch_status: "balanced"
      }
    ];
    renderPriorities(fallback);
  }
}

function renderPriorities(items) {
  const container = document.getElementById("rankings-container");
  if (!container) return;

  container.innerHTML = items.map(item => {
    let scoreClass = "score-low";
    if (item.priority_score >= 75) scoreClass = "score-critical";
    else if (item.priority_score >= 50) scoreClass = "score-moderate";

    let alertTag = "";
    if (item.silent_need_flag) {
      alertTag = `<span class="badge" style="background: rgba(192, 132, 252, 0.2); color: #c084fc; border: 1px solid #c084fc;">Silent Need Detected</span>`;
    } else if (item.mismatch_status === "underfunded_hotspot") {
      alertTag = `<span class="badge" style="background: rgba(244, 63, 94, 0.2); color: #f43f5e; border: 1px solid #f43f5e;">Funding Deficit Hotspot</span>`;
    }

    return `
      <div class="rank-card">
        <div class="rank-card-header">
          <div class="rank-title">
            <span class="rank-num">#${item.rank}</span>
            <span>${item.district_name}, ${item.state_name}</span>
            <span style="font-size: 0.75rem; color: var(--text-muted); text-transform: capitalize;">(${item.sector.replace('_', ' ')})</span>
          </div>
          <div class="score-badge ${scoreClass}">${item.priority_score}</div>
        </div>
        ${alertTag ? `<div style="margin-bottom: 0.4rem;">${alertTag}</div>` : ''}
        <div class="rank-explanation">${item.grounded_explanation}</div>
      </div>
    `;
  }).join("");
}

// Load Post-Project Impact Audit
async function loadImpactAudit() {
  const tbody = document.getElementById("impact-table-body");
  try {
    const res = await fetch(`${API_BASE}/impact`);
    if (!res.ok) throw new Error("Backend offline");
    const data = await res.json();
    renderImpactAudit(data);
  } catch (err) {
    const fallback = [
      {
        project_name: "100-Bed Sub-District Hospital Upgradation",
        district: "Pune",
        state: "Maharashtra",
        sector: "healthcare",
        completion_date: "2025-06-15",
        pre_complaints_count: 184,
        post_complaints_count: 38,
        impact_percentage: 79.3,
        verification_status: "Verified Significant Reduction"
      },
      {
        project_name: "Rural Piped Drinking Water Network (Phase II)",
        district: "Thane",
        state: "Maharashtra",
        sector: "water_sanitation",
        completion_date: "2025-03-10",
        pre_complaints_count: 210,
        post_complaints_count: 45,
        impact_percentage: 78.6,
        verification_status: "Verified Significant Reduction"
      },
      {
        project_name: "All-Weather Rural Connectivity Arterial Road",
        district: "Gorakhpur",
        state: "Uttar Pradesh",
        sector: "roads_transport",
        completion_date: "2025-01-20",
        pre_complaints_count: 142,
        post_complaints_count: 98,
        impact_percentage: 31.0,
        verification_status: "Moderate Improvement"
      }
    ];
    renderImpactAudit(fallback);
  }
}

function renderImpactAudit(items) {
  const tbody = document.getElementById("impact-table-body");
  if (!tbody) return;

  tbody.innerHTML = items.map(p => `
    <tr>
      <td><strong>${p.project_name}</strong></td>
      <td>${p.district}, ${p.state}</td>
      <td style="text-transform: capitalize;">${p.sector.replace('_', ' ')}</td>
      <td>${p.completion_date}</td>
      <td><span style="color: #f43f5e; font-weight: 600;">${p.pre_complaints_count}</span> complaints</td>
      <td><span style="color: #34d399; font-weight: 600;">${p.post_complaints_count}</span> complaints</td>
      <td class="impact-positive">-${p.impact_percentage}%</td>
      <td><span class="status-badge">${p.verification_status}</span></td>
    </tr>
  `).join("");
}

// Web Speech API Voice Capture Integration
function initVoiceCapture() {
  const voiceBtn = document.getElementById("voice-btn");
  const voiceText = document.getElementById("voice-text");
  const textInput = document.getElementById("request-input");
  const submitBtn = document.getElementById("submit-request-btn");
  const simOutput = document.getElementById("sim-output");

  if (!voiceBtn || !textInput) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  let isRecording = false;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "mr-IN"; // Default support for Marathi/Hindi/English

    recognition.onstart = () => {
      isRecording = true;
      voiceBtn.classList.add("recording");
      voiceText.textContent = "Listening...";
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      textInput.value = transcript;
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      isRecording = false;
      voiceBtn.classList.remove("recording");
      voiceText.textContent = "Record Voice";
    };

    recognition.onend = () => {
      isRecording = false;
      voiceBtn.classList.remove("recording");
      voiceText.textContent = "Record Voice";
    };

    voiceBtn.addEventListener("click", () => {
      if (!isRecording) {
        recognition.start();
      } else {
        recognition.stop();
      }
    });
  } else {
    voiceBtn.addEventListener("click", () => {
      alert("Browser Web Speech API not supported in this browser. Please type your message.");
    });
  }

  submitBtn.addEventListener("click", () => {
    const text = textInput.value.trim();
    if (!text) return;

    simOutput.innerHTML = `
      <div style="width: 100%;">
        <div style="color: var(--accent-cyan); font-weight: 700; margin-bottom: 0.5rem;">
          Gemini Understanding & Classification Output:
        </div>
        <div style="background: rgba(255,255,255,0.04); padding: 0.75rem; border-radius: 8px; font-size: 0.8rem; line-height: 1.5;">
          <strong>Detected Intent:</strong> Urgent infrastructure requirement<br>
          <strong>Sector Classification:</strong> Healthcare / Facilities<br>
          <strong>Extracted Entity:</strong> Haveli Block, Pune District<br>
          <strong>Urgency Score:</strong> High (Critical Needs Identified)<br>
          <strong>Cluster Assignment:</strong> CLUSTER-HEA-PUN<br>
          <strong>Quality Tag:</strong> <span style="color: #fbbf24; font-weight: 600;">SYNTHETIC DEMO DATA</span>
        </div>
      </div>
    `;
  });
}
