"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const node = document.getElementById("analytics-data");
  if (!node || typeof Chart === "undefined") return;
  const comparison = JSON.parse(node.dataset.comparison || "{}");
  const trends = JSON.parse(node.dataset.trends || "[]");
  const comparisonCanvas = document.getElementById("location-comparison-chart");
  if (comparisonCanvas) new Chart(comparisonCanvas, {type: "bar", data: {labels: comparison.labels || [], datasets: [{label: "Reporting completion %", data: comparison.completion || [], backgroundColor: "#0f766e", borderRadius: 6}]}, options: {responsive: true, maintainAspectRatio: false, indexAxis: "y", plugins: {legend: {display: false}}, scales: {x: {beginAtZero: true, max: 100}}}});
  const trendCanvas = document.getElementById("analytics-trend-chart");
  if (trendCanvas) new Chart(trendCanvas, {type: "line", data: {labels: trends.map(item => item.period), datasets: [{label: "Completion %", data: trends.map(item => item.completion), borderColor: "#0f766e", backgroundColor: "rgba(15,118,110,.12)", tension: .25, yAxisID: "percentage"}, {label: "Population", data: trends.map(item => item.population_has_data ? item.population : null), borderColor: "#2563eb", tension: .25, yAxisID: "count"}]}, options: {responsive: true, maintainAspectRatio: false, interaction: {mode: "index", intersect: false}, scales: {percentage: {position: "left", beginAtZero: true, max: 100}, count: {position: "right", beginAtZero: true, grid: {drawOnChartArea: false}}}}});
  const mapNode = document.getElementById("village-map");
  if (mapNode && typeof L !== "undefined") {
    const map = L.map(mapNode).setView([-17.8, 178.1], 6);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {attribution: "© OpenStreetMap"}).addTo(map);
    JSON.parse(node.dataset.villages || "[]").forEach(item => L.marker([item.lat, item.lng]).addTo(map).bindPopup(item.name));
  }
});
