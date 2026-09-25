// Main Application Orchestrator

let allDistricts = [];
let selectedDistrict = null;

async function loadAllData() {
  try {
    allDistricts = await getDistrictsAPI();
  } catch (e) {
    console.error("Failed to load districts:", e);
    allDistricts = [];
  }
}

async function onSelectDistrict(district) {
  selectedDistrict = district;
  let explanationData = null;
  try {
    explanationData = await getDistrictExplanationAPI(district.district_name);
  } catch (e) {
    console.warn("Explanation fetch failed, using district data only.");
  }
  renderEvidencePanel(district, explanationData);
  updateUIElements();
}

function setupFilters() {
  const stateSelect = document.getElementById("filter-state");
  const qualitySelect = document.getElementById("filter-quality");

  [stateSelect, qualitySelect].forEach(el => {
    if (el) {
      el.addEventListener("change", applyFilters);
    }
  });
}

function applyFilters() {
  const stateVal = document.getElementById("filter-state")?.value || "all";
  const qualityVal = document.getElementById("filter-quality")?.value || "all";

  let filtered = [...allDistricts];
  if (stateVal !== "all") filtered = filtered.filter(d => d.admin1 === stateVal);
  if (qualityVal !== "all") filtered = filtered.filter(d => d.data_quality === qualityVal);

  renderMapMarkers(filtered, onSelectDistrict);
  renderRankedTab(filtered);

  window.selectDistrictRow = function(dname) {
    const target = filtered.find(d => d.district_name.toLowerCase() === dname.toLowerCase());
    if (target) onSelectDistrict(target);
    activateTab("ranked");
  };
}

function setupTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(btn => {
    btn.addEventListener("click", () => {
      activateTab(btn.dataset.tab);
    });
    btn.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        activateTab(btn.dataset.tab);
      }
    });
  });
}

function activateTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.tab === tabId);
    btn.setAttribute("aria-selected", btn.dataset.tab === tabId);
  });
  document.querySelectorAll(".tab-panel").forEach(panel => {
    panel.classList.toggle("active", panel.id === `tab-${tabId}-panel`);
  });
}

function setupLangSwitcher() {
  document.querySelectorAll(".lang-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".lang-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      setLanguage(btn.dataset.lang);
    });
  });
}

async function renderFooter() {
  const footer = document.getElementById("datasets-footer");
  if (!footer) return;
  try {
    const data = await getDatasetsAPI();
    const datasets = data.datasets || [];
    const note = data.census_honesty_note || "";

    const dsHtml = datasets.map(d => `
      <div class="ds-item">
        <strong>${d.dataset_name}</strong>
        ${d.data_quality === "real"
          ? `<span class="badge badge-real">REAL DATA</span>`
          : `<span class="badge badge-synthetic">SYNTHETIC DEMO DATA</span>`}
        <span class="ds-meta">v${d.version} · ${d.record_count} records · ${d.ingested_at?.slice(0,10) || 'N/A'}</span>
      </div>`).join("");

    footer.innerHTML = `
      <div class="footer-datasets"><h4>📦 Data Sources & Versions</h4>${dsHtml}</div>
      <div class="census-note">📋 <em>${note}</em></div>`;
  } catch (e) {
    footer.innerHTML = `<p>Dataset metadata unavailable.</p>`;
  }
}

async function main() {
  // Language switcher
  setupLangSwitcher();

  // Load core data
  await loadAllData();

  // Initialize map
  initMap();
  renderMapMarkers(allDistricts, onSelectDistrict);

  // Default evidence panel
  renderEvidencePanel(null, null);

  // Filters
  setupFilters();
  applyFilters();

  // Tabs setup
  setupTabs();

  // Render tab-specific content
  renderRankedTab(allDistricts);

  // Silent Needs
  getSilentNeedsAPI().then(renderSilentNeedsTab).catch(() => renderSilentNeedsTab([]));

  // Mismatches
  getMismatchesAPI().then(m => renderMismatchTab(m, allDistricts)).catch(() => renderMismatchTab([], allDistricts));

  // Impact
  getImpactAPI().then(renderImpactTab).catch(() => renderImpactTab([]));

  // AI Command Center
  renderCommandTab();

  // Submit Request
  renderSubmitRequestTab();

  // Footer
  renderFooter();

  // Enable row selection from ranked table
  window.selectDistrictRow = function(dname) {
    const target = allDistricts.find(d => d.district_name.toLowerCase() === dname.toLowerCase());
    if (target) onSelectDistrict(target);
    activateTab("ranked");
  };

  // Activate first tab
  activateTab("ranked");
}

document.addEventListener("DOMContentLoaded", main);
