/**
 * Admin & Dispatch Operations Controller for RideConnect India.
 * Handles Pan-India fleet visualization, driver KYC approvals, and city filters.
 */
let adminMap;
let fleetMarkers = [];

const SEEDED_ADMIN_DRIVERS = [
  { id: "del-01", name: "Vikram Singh Gurjar", city: "Delhi NCR", car: "Maruti Dzire", plate: "DL 01 AZ 4521", dl: "DL-1420110012345", aadhaar: "Verified", rating: 4.92, lat: 28.6139, lon: 77.2090, kyc: "verified" },
  { id: "del-02", name: "Ramesh Kumar Auto", city: "Delhi NCR", car: "Bajaj Compact RE", plate: "DL 1R 8872", dl: "DL-1420110099881", aadhaar: "Verified", rating: 4.85, lat: 28.6315, lon: 77.2167, kyc: "verified" },
  { id: "mum-01", name: "Sanjay Jadhav", city: "Mumbai", car: "Toyota Innova", plate: "MH 02 EE 7890", dl: "MH-0220140023412", aadhaar: "Verified", rating: 4.95, lat: 19.0760, lon: 72.8777, kyc: "verified" },
  { id: "mum-02", name: "Deepak Kamble", city: "Mumbai", car: "Honda Shine", plate: "MH 03 BV 1294", dl: "MH-0320180011234", aadhaar: "Verified", rating: 4.88, lat: 19.0664, lon: 72.8687, kyc: "verified" },
  { id: "blr-01", name: "Manjunath Gowda", city: "Bengaluru", car: "Tata Tiago EV", plate: "KA 05 MN 3421", dl: "KA-0520160034123", aadhaar: "Verified", rating: 4.90, lat: 12.9716, lon: 77.5946, kyc: "verified" },
  { id: "hyd-01", name: "Mohammed Abdul Rasheed", city: "Hyderabad", car: "Hyundai Aura", plate: "TS 09 UA 9912", dl: "TS-0920150045612", aadhaar: "Verified", rating: 4.93, lat: 17.3850, lon: 78.4867, kyc: "verified" },
  { id: "ind-01", name: "Surendra Chouhan", city: "Indore", car: "Piaggio Ape", plate: "MP 09 R 7654", dl: "MP-0920120034123", aadhaar: "Verified", rating: 4.89, lat: 22.7196, lon: 75.8577, kyc: "verified" },
  { id: "ind-02", name: "Anil Verma (Outstation)", city: "Indore", car: "Ertiga ZXi", plate: "MP 09 TA 3344", dl: "MP-0920100012345", aadhaar: "Verified", rating: 4.96, lat: 22.7533, lon: 75.8937, kyc: "verified" },
  { id: "chn-01", name: "Karthik Subramanian", city: "Chennai", car: "WagonR VXi", plate: "TN 07 CE 6123", dl: "TN-0720170067812", aadhaar: "Verified", rating: 4.87, lat: 13.0827, lon: 80.2707, kyc: "verified" },
  { id: "kol-01", name: "Subhashish Roy", city: "Kolkata", car: "Tata Tigor", plate: "WB 02 AB 8745", dl: "WB-0220130098712", aadhaar: "Verified", rating: 4.91, lat: 22.5726, lon: 88.3639, kyc: "verified" }
];

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Map centered on India
  initAdminMap();

  // 2. Render Driver KYC Table
  renderDriverKycTable(SEEDED_ADMIN_DRIVERS);
});

function initAdminMap() {
  const el = document.getElementById('admin-map');
  if (!el || typeof L === 'undefined') return;

  adminMap = L.map('admin-map', {
    zoomControl: true,
    attributionControl: false
  }).setView([21.7679, 78.8718], 5); // Center of India

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    maxZoom: 18,
    subdomains: 'abcd'
  }).addTo(adminMap);

  renderFleetMarkers(SEEDED_ADMIN_DRIVERS);
}

function renderFleetMarkers(drivers) {
  fleetMarkers.forEach(m => adminMap.removeLayer(m));
  fleetMarkers = [];

  drivers.forEach(d => {
    const marker = L.marker([d.lat, d.lon], {
      icon: L.divIcon({
        className: 'admin-marker',
        html: `
          <div style="background:#ff6b00; border:2px solid #fff; border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:12px; box-shadow:0 4px 10px rgba(0,0,0,0.5);">
            <i class="fas fa-car"></i>
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      })
    }).addTo(adminMap).bindPopup(`
      <b>${d.name}</b><br>
      City: ${d.city}<br>
      Vehicle: ${d.car} (${d.plate})<br>
      Rating: ${d.rating} ⭐ • <span style="color:#10b981;">Online</span>
    `);
    fleetMarkers.push(marker);
  });
}

function renderDriverKycTable(drivers) {
  const tbody = document.getElementById('driverKycTbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  drivers.forEach(d => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        <div style="font-weight:700; color:#fff;">${d.name}</div>
        <div style="font-size:0.75rem; color:var(--text-muted);">ID: DRV-${d.id}</div>
      </td>
      <td>${d.city}</td>
      <td>
        <div style="color:#fff;">${d.car}</div>
        <div style="font-size:0.78rem; color:#60a5fa; font-weight:700;">${d.plate}</div>
      </td>
      <td><code>${d.dl}</code></td>
      <td><span class="badge badge-green"><i class="fas fa-check"></i> ${d.aadhaar}</span></td>
      <td><i class="fas fa-star" style="color:#f59e0b;"></i> ${d.rating}</td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="alert('Driver profile and uploaded documents verified.')">
          <i class="fas fa-eye"></i> View Docs
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function onAdminCityFilterChange(val) {
  if (val === 'all') {
    adminMap.flyTo([21.7679, 78.8718], 5);
    renderDriverKycTable(SEEDED_ADMIN_DRIVERS);
    renderFleetMarkers(SEEDED_ADMIN_DRIVERS);
    document.getElementById('statOnlineDrivers').textContent = SEEDED_ADMIN_DRIVERS.length;
  } else {
    const city = INDIA_CITIES[val];
    if (city) {
      adminMap.flyTo([city.lat, city.lon], 11);
      const filtered = SEEDED_ADMIN_DRIVERS.filter(d => d.city.toLowerCase().includes(val));
      renderDriverKycTable(filtered.length ? filtered : SEEDED_ADMIN_DRIVERS);
      document.getElementById('statOnlineDrivers').textContent = filtered.length || 1;
    }
  }
}
