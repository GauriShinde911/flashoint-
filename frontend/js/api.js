// API Client with automatic backend detection and mock fallback

let isOfflineMode = false;

function showOfflineNotice(show) {
  const noticeEl = document.getElementById("offline-notice");
  if (noticeEl) {
    noticeEl.style.display = show ? "block" : "none";
  }
}

async function fetchWithFallback(endpoint, mockFile) {
  const primaryUrl = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(primaryUrl, { credentials: "omit" });
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);
    const data = await response.json();
    isOfflineMode = false;
    showOfflineNotice(false);
    return data;
  } catch (err) {
    console.warn(`Backend endpoint ${endpoint} unreachable. Falling back to mock file: ${mockFile}`);
    isOfflineMode = true;
    showOfflineNotice(true);
    const mockResponse = await fetch(`./mock/${mockFile}`);
    return await mockResponse.json();
  }
}

async function getDistrictsAPI() {
  return await fetchWithFallback("/districts", "districts.json");
}

async function getDistrictExplanationAPI(districtName) {
  return await fetchWithFallback(`/explain/${districtName}`, `explain_${districtName.toLowerCase()}.json`);
}

async function getSilentNeedsAPI() {
  return await fetchWithFallback("/silent-needs", "silent_needs.json");
}

async function getMismatchesAPI() {
  return await fetchWithFallback("/mismatches", "mismatches.json");
}

async function getImpactAPI() {
  return await fetchWithFallback("/impact", "impact.json");
}

async function getDatasetsAPI() {
  return await fetchWithFallback("/datasets", "datasets.json");
}

async function postQueryAPI(queryText) {
  try {
    const res = await fetch(`${API_BASE_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: queryText })
    });
    if (!res.ok) throw new Error("Backend query error");
    return await res.json();
  } catch (err) {
    console.warn("Query API failed, executing mock filter.");
    return {
      query: queryText,
      structured_filter: { state: "Maharashtra", sector: "healthcare", sort: "priority_score_desc" },
      interpretation: "Mock query filter executed offline.",
      result_count: 2,
      results: await getDistrictsAPI()
    };
  }
}

async function postCitizenRequestAPI(reqPayload) {
  try {
    const res = await fetch(`${API_BASE_URL}/requests`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reqPayload)
    });
    if (!res.ok) throw new Error("Backend submission error");
    return await res.json();
  } catch (err) {
    console.warn("Submit Request API failed, executing offline mock response.");
    return {
      status: "success",
      message: "Processed in Offline Demo Mode.",
      analysis: {
        category: "healthcare",
        sub_category: "phc_shortage",
        urgency_level: "high",
        detected_language: reqPayload.detected_language || "en",
        admin_hierarchy: { admin1: "Maharashtra", admin2: reqPayload.district || "Pune" },
        cluster_id: `CLUSTER-HEA-${(reqPayload.district || "PUN").slice(0,3).toUpperCase()}`
      },
      record: {
        id: `REQ-OFFLINE-${Date.now().toString().slice(-6)}`,
        data_quality: "synthetic"
      }
    };
  }
}
