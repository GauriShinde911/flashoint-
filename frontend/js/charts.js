// Lightweight SVG Chart Utility

function renderBreakdownSVG(breakdown) {
  if (!breakdown) return "<p>No breakdown data available.</p>";

  const items = [
    { label: "Demand (30%)", score: breakdown.demand?.normalized_score || 0, color: "#3b82f6" },
    { label: "Population (25%)", score: breakdown.population?.normalized_score || 0, color: "#8b5cf6" },
    { label: "Infra Deficit (25%)", score: breakdown.infra_deficit?.normalized_score || 0, color: "#ef4444" },
    { label: "Accessibility (10%)", score: breakdown.accessibility?.normalized_score || 0, color: "#f59e0b" },
    { label: "Inverse Inv (10%)", score: breakdown.inverse_investment?.normalized_score || 0, color: "#10b981" }
  ];

  let svgHtml = `<svg width="100%" height="160" viewBox="0 0 400 160" style="font-family: system-ui, sans-serif; font-size: 12px;">`;

  items.forEach((item, index) => {
    const y = index * 30 + 10;
    const barWidth = (item.score / 100) * 230;

    svgHtml += `
      <text x="5" y="${y + 14}" fill="#475569" font-weight="500">${item.label}</text>
      <rect x="130" y="${y}" width="230" height="18" fill="#f1f5f9" rx="4"/>
      <rect x="130" y="${y}" width="${barWidth}" height="18" fill="${item.color}" rx="4"/>
      <text x="365" y="${y + 14}" fill="#1e293b" font-weight="600">${item.score}</text>
    `;
  });

  svgHtml += `</svg>`;
  return svgHtml;
}

function renderQuadrantScatterSVG(districts) {
  if (!districts || districts.length === 0) return "<p>No district data available for scatter plot.</p>";

  let svg = `<svg width="100%" height="280" viewBox="0 0 500 280" style="font-family: system-ui, sans-serif; font-size: 11px;">`;

  // Draw Quadrant Background Grid
  svg += `
    <rect x="50" y="20" width="200" height="110" fill="#fef2f2" opacity="0.6"/> <!-- High Demand, Low Investment (Under-Funded) -->
    <rect x="250" y="20" width="200" height="110" fill="#f0fdf4" opacity="0.6"/> <!-- High Demand, High Investment -->
    <rect x="50" y="130" width="200" height="110" fill="#f8fafc" opacity="0.6"/> <!-- Low Demand, Low Investment -->
    <rect x="250" y="130" width="200" height="110" fill="#fffbeb" opacity="0.6"/> <!-- Low Demand, High Investment (Over-Funded) -->

    <!-- Axes -->
    <line x1="50" y1="130" x2="450" y2="130" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="4"/>
    <line x1="250" y1="20" x2="250" y2="240" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="4"/>

    <!-- Labels -->
    <text x="60" y="40" fill="#991b1b" font-weight="700">UNDER-FUNDED HIGH DEMAND</text>
    <text x="260" y="40" fill="#166534" font-weight="700">BALANCED HIGH INVESTMENT</text>
    <text x="260" y="230" fill="#92400e" font-weight="700">CHECK EFFECTIVENESS (OVER-FUNDED)</text>

    <!-- Axis Titles -->
    <text x="220" y="265" fill="#64748b" font-weight="600">Existing Investment (₹ Cr)</text>
    <text x="10" y="140" fill="#64748b" font-weight="600" transform="rotate(-90 15 140)">Citizen Demand (Requests)</text>
  `;

  // Plot Points
  districts.forEach(d => {
    const demand = d.citizen_demand_count || 50;
    const inv = d.existing_investment_cr || 10;

    // Scale Inv 0 to 30 Cr -> X 50 to 450
    const x = 50 + (Math.min(30, inv) / 30) * 400;
    // Scale Demand 0 to 300 -> Y 240 to 20
    const y = 240 - (Math.min(300, demand) / 300) * 220;

    const color = d.priority_score >= 75 ? "#ef4444" : (d.priority_score >= 50 ? "#f59e0b" : "#10b981");

    svg += `
      <circle cx="${x}" cy="${y}" r="8" fill="${color}" stroke="#ffffff" stroke-width="2"/>
      <text x="${x + 12}" y="${y + 4}" fill="#1e293b" font-weight="600">${d.district_name}</text>
    `;
  });

  svg += `</svg>`;
  return svg;
}
