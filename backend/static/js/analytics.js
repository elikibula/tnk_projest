"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const dataNode = document.getElementById("analytics-data");
  const chartNode = document.getElementById("status-chart");
  const mapNode = document.getElementById("village-map");
  if (!dataNode || !chartNode || !mapNode || typeof Chart === "undefined" || typeof L === "undefined") return;

  const statuses = JSON.parse(dataNode.dataset.statuses || "[]");
  new Chart(chartNode, {
    type: "bar",
    data: {
      labels: statuses.map((item) => item.status.replaceAll("_", " ")),
      datasets: [{ label: "Reports", data: statuses.map((item) => item.count), backgroundColor: "#0f766e", borderRadius: 8 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
    },
  });

  const villages = JSON.parse(dataNode.dataset.villages || "[]");
  const map = L.map(mapNode).setView([-17.8, 178.1], 6);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "© OpenStreetMap" }).addTo(map);
  villages.forEach((item) => L.marker([item.lat, item.lng]).addTo(map).bindPopup(item.name));
});
