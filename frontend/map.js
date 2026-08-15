import { escapeHtml, money } from './api.js';

let map;
let layerGroup;

function statusColor(status) {
  const value = String(status || '').toLowerCase();
  if (value.includes('planning')) return '#cf7926';
  if (value.includes('construction')) return '#318ba0';
  if (value.includes('complete')) return '#5a9d69';
  return '#7f8b85';
}

export function initializeMap(onSelect) {
  map = L.map('map', { zoomControl: false, preferCanvas: true }).setView([49.2, -84.3], 5);
  // Retain the map on its container for lightweight diagnostics and browser tests.
  map.getContainer()._ontarioBuildMap = map;
  L.control.zoom({ position: 'bottomright' }).addTo(map);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO', maxZoom: 19
  }).addTo(map);
  layerGroup = L.layerGroup().addTo(map);
  map.on('projectselect', (event) => onSelect(event.project));
}

export function renderProjects(projects) {
  layerGroup.clearLayers();
  const bounds = [];
  for (const project of projects) {
    if (project.latitude == null || project.longitude == null) continue;
    const marker = L.circleMarker([project.latitude, project.longitude], {
      radius: project.budget >= 500_000_000 ? 7 : project.budget >= 100_000_000 ? 5.5 : 4,
      color: statusColor(project.status), weight: 1, fillColor: statusColor(project.status), fillOpacity: 0.72
    });
    marker.bindTooltip(`<strong>${escapeHtml(project.project || 'Infrastructure project')}</strong><br>${escapeHtml(project.community || project.area || '')}<br>${money(project.budget)}`);
    marker.on('click', () => map.fire('projectselect', { project }));
    marker.addTo(layerGroup);
    bounds.push([project.latitude, project.longitude]);
  }
  if (bounds.length && bounds.length < 2500) map.fitBounds(bounds, { padding: [35, 35], maxZoom: 8 });
}
