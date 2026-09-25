// Evidence Panel and Tab Content Renderers

function dataBadge(quality) {
  if (quality === "real") {
    return `<span class="badge badge-real" aria-label="Real Data">✓ REAL DATA</span>`;
  }
  return `<span class="badge badge-synthetic" aria-label="Synthetic Demo Data">⚡ SYNTHETIC DEMO DATA</span>`;
}

// ---- Evidence Panel ----
function renderEvidencePanel(district, explanationData) {
  const panel = document.getElementById("evidence-panel");
  if (!panel) return;

  if (!district) {
    panel.innerHTML = `
      <div class="panel-empty-state">
        <div class="empty-icon">🗺️</div>
        <p>Click a district on the map to view the full evidence panel.</p>
      </div>`;
    return;
  }

  const breakdown = district.score_breakdown || {};
  const projStatus = district.existing_project_status || "gap_unaddressed";
  const projName = district.matching_projects?.[0]?.name || "None found";
  const projBadge = projStatus === "active_project_found"
    ? `<span class="status-chip chip-ongoing">● Ongoing Project</span>`
    : projStatus === "completed_project_found"
    ? `<span class="status-chip chip-completed">✓ Completed Project</span>`
    : `<span class="status-chip chip-gap">✗ No Active Project</span>`;

  const explanation = explanationData?.explanation || "Loading explanation...";
  const footnote = explanationData?.footnote || "";

  panel.innerHTML = `
    <div class="evidence-header">
      <h3>${district.district_name} <span class="state-tag">${district.admin1}</span></h3>
      ${dataBadge(district.data_quality || "real")}
    </div>

    <div class="score-display">
      <div class="score-ring" style="--score: ${district.priority_score}">
        <span class="score-value">${district.priority_score}</span>
        <span class="score-label">/ 100</span>
      </div>
      <div class="score-meta">
        <div class="rank-badge">Rank #${district.rank || 1}</div>
        <div class="sector-tag">${(district.sector || "healthcare").replace("_", " & ")}</div>
      </div>
    </div>

    <div class="card">
      <h4 data-i18n="score_breakdown">Score Component Breakdown</h4>
      <div class="breakdown-chart">${renderBreakdownSVG(breakdown)}</div>
    </div>

    <div class="card stats-grid">
      <div class="stat-item"><span class="stat-value">${district.population ? (district.population / 100000).toFixed(1) + ' L' : 'N/A'}</span><span class="stat-label">Population</span></div>
      <div class="stat-item"><span class="stat-value">${district.facilities_count ?? 'N/A'}</span><span class="stat-label">Facilities</span></div>
      <div class="stat-item"><span class="stat-value">₹${district.existing_investment_cr ?? 'N/A'} Cr</span><span class="stat-label">Investment</span></div>
      <div class="stat-item"><span class="stat-value">${district.citizen_demand_count ?? 'N/A'}</span><span class="stat-label">Requests</span></div>
    </div>

    <div class="card">
      <h4 data-i18n="why_this_ranking">Why This Ranking</h4>
      <p class="explanation-text">${explanation}</p>
      <p class="footnote-text">📌 ${footnote || 'Grounded in verified metrics.'}</p>
    </div>

    <div class="card">
      <h4 data-i18n="project_check">Existing Government Project</h4>
      ${projBadge}
      <p class="project-name">${projName}</p>
    </div>
  `;

  updateUIElements();
}

// ---- Tab 1: Ranked Recommendations ----
function renderRankedTab(districts) {
  const container = document.getElementById("tab-ranked-content");
  if (!container) return;

  if (!districts || districts.length === 0) {
    container.innerHTML = `<div class="panel-empty-state"><p>No district data available.</p></div>`;
    return;
  }

  const rows = districts.map(d => `
    <tr class="table-row" onclick="window.selectDistrictRow('${d.district_name}')" tabindex="0" aria-label="Select ${d.district_name}">
      <td><strong>#${d.rank}</strong></td>
      <td>${d.district_name} ${dataBadge(d.data_quality)}</td>
      <td>${d.admin1}</td>
      <td>${(d.sector || "").replace(/_/g, " ")}</td>
      <td><span class="score-pill score-${d.priority_score >= 75 ? 'high' : d.priority_score >= 50 ? 'med' : 'low'}">${d.priority_score}</span></td>
      <td>${d.citizen_demand_count ?? 'N/A'} requests</td>
    </tr>`).join("");

  container.innerHTML = `
    <table class="data-table" aria-label="Ranked districts table">
      <thead>
        <tr><th>Rank</th><th>District</th><th>State</th><th>Sector</th><th>Score</th><th>Demand</th></tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
}

// ---- Tab 2: Silent Needs ----
function renderSilentNeedsTab(silentNeeds) {
  const container = document.getElementById("tab-silent-content");
  if (!container) return;

  if (!silentNeeds || silentNeeds.length === 0) {
    container.innerHTML = `<div class="panel-empty-state"><p>✅ No silent need flags found for current filters.</p></div>`;
    return;
  }

  const cards = silentNeeds.map(sn => `
    <div class="alert-card alert-silent">
      <div class="alert-header">
        <span>🔇 ${sn.district} <span class="state-tag">${sn.admin1 || ''}</span></span>
        <span class="severity-badge">Severity: ${sn.silent_need_severity ?? 'N/A'}</span>
      </div>
      <p>${sn.reason}</p>
      <div class="stats-grid" style="margin-top:8px;">
        <div class="stat-item"><span class="stat-value">${sn.population ? (sn.population/100000).toFixed(1)+'L' : 'N/A'}</span><span class="stat-label">Population</span></div>
        <div class="stat-item"><span class="stat-value">${sn.facilities_count ?? 'N/A'}</span><span class="stat-label">Facilities</span></div>
        <div class="stat-item"><span class="stat-value">${sn.citizen_demand_count ?? 'N/A'}</span><span class="stat-label">Reports</span></div>
      </div>
    </div>`).join("");

  container.innerHTML = cards;
}

// ---- Tab 3: Investment-Demand Mismatch ----
function renderMismatchTab(mismatches, districts) {
  const container = document.getElementById("tab-mismatch-content");
  if (!container) return;

  const scatter = `<div class="card"><h4>District Investment vs. Demand Scatter</h4>${renderQuadrantScatterSVG(districts || [])}</div>`;

  let listHtml = "";
  if (!mismatches || mismatches.length === 0) {
    listHtml = `<div class="panel-empty-state"><p>✅ No major mismatches detected.</p></div>`;
  } else {
    listHtml = mismatches.map(m => `
      <div class="alert-card ${m.mismatch_type === 'UNDER_FUNDED_HIGH_DEMAND' ? 'alert-danger' : 'alert-warning'}">
        <div class="alert-header">
          <strong>${m.district} <span class="state-tag">${m.admin1 || ''}</span></strong>
          <span class="chip chip-${m.mismatch_type === 'UNDER_FUNDED_HIGH_DEMAND' ? 'red' : 'amber'}">${m.mismatch_type.replace(/_/g,' ')}</span>
        </div>
        <p>${m.description}</p>
      </div>`).join("");
  }

  container.innerHTML = scatter + listHtml;
}

// ---- Tab 4: Impact Measurement ----
function renderImpactTab(impacts) {
  const container = document.getElementById("tab-impact-content");
  if (!container) return;

  if (!impacts || impacts.length === 0) {
    container.innerHTML = `<div class="panel-empty-state"><p>No completed projects available for impact measurement.</p></div>`;
    return;
  }

  const cards = impacts.filter(i => i.is_measurable).map(i => {
    const pct = i.percentage_change || 0;
    const pctClass = pct <= -40 ? "positive-impact" : pct < 0 ? "mod-impact" : "neutral-impact";
    const preW = Math.min(100, Math.max(4, (i.pre_completion_request_count / Math.max(i.pre_completion_request_count, i.post_completion_request_count, 1)) * 100));
    const postW = Math.min(100, Math.max(4, (i.post_completion_request_count / Math.max(i.pre_completion_request_count, i.post_completion_request_count, 1)) * 100));

    return `
      <div class="card impact-card">
        <div class="impact-header">
          <h4>${i.project_name}</h4>
          ${dataBadge(i.data_quality || "synthetic")}
        </div>
        <div class="impact-meta">
          <span>📍 ${i.admin2 || 'N/A'}</span>
          <span>🏗️ ${(i.sector || "").replace(/_/g, " ")}</span>
          <span>✅ Completed: ${i.completion_date || 'N/A'}</span>
          <span>⏱️ Window: ${i.window_days} days each side</span>
        </div>
        <div class="before-after-chart">
          <div>
            <div class="bar-label">Before Completion: <strong>${i.pre_completion_request_count} requests</strong></div>
            <div class="bar-track"><div class="bar-fill bar-before" style="width:${preW}%"></div></div>
          </div>
          <div style="margin-top:8px;">
            <div class="bar-label">After Completion: <strong>${i.post_completion_request_count} requests</strong></div>
            <div class="bar-track"><div class="bar-fill bar-after" style="width:${postW}%"></div></div>
          </div>
        </div>
        <div class="impact-result ${pctClass}">
          ${pct <= 0 ? '▼' : '▲'} ${Math.abs(pct).toFixed(1)}% change — <em>${i.impact_summary}</em>
        </div>
        <p class="disclaimer-text">⚠️ ${i.disclaimer}</p>
      </div>`;
  }).join("");

  container.innerHTML = cards || `<div class="panel-empty-state"><p>No measurable impact data available.</p></div>`;
}

// ---- Tab 5: AI Command Center ----
function renderCommandTab() {
  const container = document.getElementById("tab-command-content");
  if (!container) return;

  const examples = [
    "Show under-funded healthcare districts in Maharashtra",
    "Which districts have the highest demand but lowest investment?",
    "List all water sanitation issues in Uttar Pradesh"
  ];

  container.innerHTML = `
    <div class="command-center">
      <div class="card">
        <h4>🤖 Policymaker Natural Language Query</h4>
        <p>Ask a question — the system converts it to a structured filter and executes it deterministically.</p>
        <div class="query-input-row">
          <input type="text" id="nl-query-input" placeholder="e.g. Show high-priority healthcare districts..." aria-label="Natural language query input"/>
          <button id="nl-query-btn" class="btn-primary" aria-label="Execute query">Execute</button>
        </div>
        <div class="example-queries">
          ${examples.map(e => `<button class="btn-example" onclick="document.getElementById('nl-query-input').value='${e}'">${e}</button>`).join("")}
        </div>
      </div>
      <div id="query-result-panel" class="card" style="display:none;">
        <div id="query-filter-display"></div>
        <div id="query-results-table"></div>
      </div>
    </div>`;

  document.getElementById("nl-query-btn").addEventListener("click", async () => {
    const queryText = document.getElementById("nl-query-input").value.trim();
    if (!queryText) return;

    const resultPanel = document.getElementById("query-result-panel");
    const filterDisplay = document.getElementById("query-filter-display");
    const resultsTable = document.getElementById("query-results-table");

    filterDisplay.innerHTML = `<div class="loading-state">⏳ Processing query...</div>`;
    resultPanel.style.display = "block";

    const data = await postQueryAPI(queryText);

    filterDisplay.innerHTML = `
      <h4>Structured Filter (transparent)</h4>
      <pre class="filter-json">${JSON.stringify(data.structured_filter, null, 2)}</pre>
      <p class="interpretation-text">💡 ${data.interpretation}</p>
      <p><strong>${data.result_count} district(s) matched.</strong></p>`;

    if (data.results && data.results.length > 0) {
      const rows = data.results.map(d => `
        <tr><td>#${d.rank}</td><td>${d.district_name} ${dataBadge(d.data_quality)}</td>
        <td>${d.admin1}</td>
        <td><span class="score-pill score-${d.priority_score >= 75 ? 'high' : 'med'}">${d.priority_score}</span></td></tr>`).join("");
      resultsTable.innerHTML = `<table class="data-table"><thead><tr><th>Rank</th><th>District</th><th>State</th><th>Score</th></tr></thead><tbody>${rows}</tbody></table>`;
    } else {
      resultsTable.innerHTML = `<p>No districts matched the filter.</p>`;
    }
  });
}

// ---- Tab 6: Submit Request ----
function renderSubmitRequestTab() {
  const container = document.getElementById("tab-submit-content");
  if (!container) return;

  const speechSupported = isSpeechSupported();

  container.innerHTML = `
    <div class="card">
      <h4>📝 Submit a Citizen Development Request</h4>
      <p>Report an infrastructure issue in your area. Your request will be analysed and categorised by the system.</p>

      <div class="form-group">
        <label for="req-lang">Language</label>
        <select id="req-lang" aria-label="Request language">
          <option value="en">English</option>
          <option value="hi">हिन्दी</option>
          <option value="mr">मराठी</option>
        </select>
      </div>

      <div class="form-group">
        <label for="req-district">District</label>
        <select id="req-district" aria-label="Select district">
          <option value="Pune">Pune</option>
          <option value="Thane">Thane</option>
          <option value="Varanasi">Varanasi</option>
        </select>
      </div>

      <div class="form-group">
        <label for="req-channel">Channel</label>
        <select id="req-channel" aria-label="Select channel">
          <option value="text">Text</option>
          <option value="voice">Voice</option>
          <option value="messaging_app">Messaging App</option>
        </select>
      </div>

      <div class="form-group">
        <label for="req-text">Describe your issue</label>
        <div class="textarea-row">
          <textarea id="req-text" rows="4" placeholder="e.g. No primary health centre in our block. Nearest hospital is 20km away." aria-label="Describe your infrastructure issue"></textarea>
          <button id="mic-btn" class="btn-mic" title="${speechSupported ? 'Click to start voice input' : 'Voice input not supported in this browser'}" aria-label="Voice input" ${speechSupported ? '' : 'disabled'}>
            🎤
          </button>
        </div>
        ${!speechSupported ? '<p class="voice-unsupported-msg">⚠️ Voice input requires a modern browser (Chrome, Edge recommended).</p>' : '<p class="voice-hint" id="voice-status">Click 🎤 to dictate your request</p>'}
      </div>

      <button id="req-submit-btn" class="btn-primary" aria-label="Submit request">Submit Request</button>
    </div>

    <div id="req-result-panel" class="card" style="display:none;"></div>`;

  // Mic button handler
  if (speechSupported) {
    const micBtn = document.getElementById("mic-btn");
    const statusEl = document.getElementById("voice-status");

    micBtn.addEventListener("click", () => {
      const lang = document.getElementById("req-lang").value;
      if (isListening) {
        stopListening();
        micBtn.textContent = "🎤";
        if (statusEl) statusEl.textContent = "Click 🎤 to dictate your request";
      } else {
        micBtn.textContent = "⏹️";
        if (statusEl) statusEl.textContent = "Listening... speak now.";
        startListening(lang, (transcript) => {
          document.getElementById("req-text").value = transcript;
        }, () => {
          micBtn.textContent = "🎤";
          if (statusEl) statusEl.textContent = "Voice input captured.";
        });
      }
    });
  }

  // Submit handler
  document.getElementById("req-submit-btn").addEventListener("click", async () => {
    const rawText = document.getElementById("req-text").value.trim();
    if (!rawText) { alert("Please describe your issue before submitting."); return; }

    const resultPanel = document.getElementById("req-result-panel");
    resultPanel.innerHTML = `<div class="loading-state">⏳ Analysing your request...</div>`;
    resultPanel.style.display = "block";

    const payload = {
      raw_text: rawText,
      detected_language: document.getElementById("req-lang").value,
      source_channel: document.getElementById("req-channel").value,
      district: document.getElementById("req-district").value
    };

    const result = await postCitizenRequestAPI(payload);
    const analysis = result.analysis || {};
    const record = result.record || {};

    resultPanel.innerHTML = `
      <h4>✅ Request Submitted</h4>
      ${dataBadge(record.data_quality || "synthetic")}
      <div class="stats-grid" style="margin-top:12px;">
        <div class="stat-item"><span class="stat-value">${analysis.category?.replace(/_/g,' ') || 'N/A'}</span><span class="stat-label">Category</span></div>
        <div class="stat-item"><span class="stat-value">${analysis.urgency_level || 'N/A'}</span><span class="stat-label">Urgency</span></div>
        <div class="stat-item"><span class="stat-value">${analysis.detected_language?.toUpperCase() || 'N/A'}</span><span class="stat-label">Language</span></div>
        <div class="stat-item"><span class="stat-value">${analysis.admin_hierarchy?.admin2 || 'N/A'}</span><span class="stat-label">District</span></div>
      </div>
      <p><strong>Cluster ID:</strong> ${analysis.cluster_id || 'N/A'}</p>
      <p><strong>Request ID:</strong> <code>${record.id || 'N/A'}</code></p>`;
  });
}
