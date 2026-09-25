// Leaflet Map Handler for Multi-Region Pilot Districts

let mapInstance = null;
let markersLayerGroup = null;

function getMarkerColor(score) {
  if (score >= 75) return "#ef4444"; // Red for Critical High Priority
  if (score >= 50) return "#f59e0b"; // Amber for Medium Priority
  return "#10b981"; // Emerald Green for Lower Priority
}

function getMarkerRadius(score) {
  return Math.max(10, Math.min(26, (score / 100) * 24));
}

function initMap() {
  const mapContainer = document.getElementById("leaflet-map");
  if (!mapContainer || mapInstance) return;

  // Center map across Maharashtra and Uttar Pradesh pilot regions
  mapInstance = L.map("leaflet-map").setView([21.5, 78.5], 6);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(mapInstance);

  markersLayerGroup = L.layerGroup().addTo(mapInstance);

  // Add map legend
  const legend = L.control({ position: "bottomright" });
  legend.onAdd = function () {
    const div = L.DomUtil.create("div", "map-legend-card");
    div.innerHTML = `
      <strong>Priority Score Legend</strong><br>
      <div><span class="legend-dot dot-red"></span> 75 – 100 (Critical Need)</div>
      <div><span class="legend-dot dot-amber"></span> 50 – 74 (Moderate Need)</div>
      <div><span class="legend-dot dot-green"></span> 0 – 49 (Baseline Need)</div>
    `;
    return div;
  };
  legend.addTo(mapInstance);
}

function renderMapMarkers(districts, onSelectDistrictCallback) {
  if (!mapInstance) initMap();
  markersLayerGroup.clearLayers();

  if (!districts || districts.length === 0) return;

  const bounds = [];

  districts.forEach(d => {
    const lat = d.lat || 18.52;
    const lon = d.lon || 73.85;
    bounds.push([lat, lon]);

    const score = d.priority_score || 50;
    const color = getMarkerColor(score);
    const radius = getMarkerRadius(score);

    const marker = L.circleMarker([lat, lon], {
      radius: radius,
      fillColor: color,
      color: "#ffffff",
      weight: 2,
      opacity: 0.9,
      fillOpacity: 0.75
    });

    const badgeClass = d.data_quality === "real" ? "badge-real" : "badge-synthetic";
    const badgeText = d.data_quality === "real" ? "REAL DATA" : "SYNTHETIC DEMO DATA";

    marker.bindPopup(`
      <div class="map-popup-content">
        <span class="badge ${badgeClass}">${badgeText}</span>
        <h4>${d.district_name} (${d.admin1})</h4>
        <p><strong>Priority Score:</strong> ${score}/100 (Rank #${d.rank || 1})</p>
        <p><strong>Sector:</strong> ${d.sector || 'healthcare'}</p>
        <p><strong>Population:</strong> ${d.population ? d.population.toLocaleString() : 'N/A'}</p>
        <button class="btn-popup-select" onclick="window.selectDistrictFromMap('${d.district_name}')">View Full Evidence Panel</button>
      </div>
    `);

    marker.on("click", () => {
      if (onSelectDistrictCallback) {
        onSelectDistrictCallback(d);
      }
    });

    markersLayerGroup.addLayer(marker);
  });

  if (bounds.length > 0) {
    mapInstance.fitBounds(bounds, { padding: [40, 40] });
  }

  window.selectDistrictFromMap = function(districtName) {
    const target = districts.find(item => item.district_name.toLowerCase() === districtName.toLowerCase());
    if (target && onSelectDistrictCallback) {
      onSelectDistrictCallback(target);
    }
  };
}
