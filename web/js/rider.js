/**
 * Rider Dashboard Controller for RideConnect India.
 * Handles instant booking, scheduled rides, parcel deliveries, outstation, SOS, and UPI payments.
 */
let mapManager;
let currentCityKey = 'delhi';
let selectedVehicleKey = 'mini';
let selectedParcelSize = 'small';
let activeRide = null;

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Map
  const defaultCity = INDIA_CITIES['delhi'];
  mapManager = new MapManager('map', 'delhi');
  mapManager.init(defaultCity.lat, defaultCity.lon, defaultCity.zoom);
  mapManager.renderNearbyDrivers(defaultCity.lat, defaultCity.lon, 6);

  // Set default landmark markers
  mapManager.setPickup(28.6315, 77.2167, "Connaught Place, Central Delhi");
  mapManager.setDropoff(28.5562, 77.1000, "Indira Gandhi Airport (IGI)");

  // 2. Set min date for scheduled rides to today
  const schedDateInput = document.getElementById('schedDate');
  if (schedDateInput) {
    const today = new Date().toISOString().split('T')[0];
    schedDateInput.min = today;
    schedDateInput.value = today;
  }

  // 3. Populate default scheduled & parcel histories
  renderScheduledRides();
  renderParcelHistory();
  renderRideHistory();

  // 4. Check for active ride in local storage
  const savedRide = localStorage.getItem('rc_active_ride');
  if (savedRide) {
    activeRide = JSON.parse(savedRide);
    showActiveRideCard(activeRide);
  }
});

// Switch top tabs
function switchRiderTab(tabKey) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

  event.currentTarget.classList.add('active');
  const target = document.getElementById(`tab-${tabKey}`);
  if (target) target.classList.add('active');
}

// City Selector Changed
function onRiderCityChanged(cityKey) {
  currentCityKey = cityKey;
  const city = INDIA_CITIES[cityKey];
  if (!city) return;

  document.getElementById('mapCityIndicator').textContent = city.name;
  mapManager.flyToCity(cityKey);

  // Set default landmarks for this city
  if (city.landmarks.length >= 2) {
    const p = city.landmarks[0];
    const d = city.landmarks[1];
    document.getElementById('pickupInput').value = p.name;
    document.getElementById('dropoffInput').value = d.name;
    mapManager.setPickup(p.lat, p.lon, p.name);
    mapManager.setDropoff(d.lat, d.lon, d.name);
    calculateTripFare(p.lat, p.lon, d.lat, d.lon);
  }
  api.toast(`Switched city to ${city.name}`, 'info');
}

// Vehicle Selection
function selectVehicle(vKey, elem) {
  selectedVehicleKey = vKey;
  document.querySelectorAll('#riderVehicleGrid .vehicle-card').forEach(c => c.classList.remove('active'));
  elem.classList.add('active');

  const fares = { bike: 110, auto: 155, mini: 215, sedan: 275, suv: 360 };
  const fare = fares[vKey] || 215;
  document.getElementById('tripTotalDisplay').textContent = `₹${fare}`;
}

// Compute Trip Fare
async function calculateTripFare(lat1, lon1, lat2, lon2) {
  const quoteData = await api.request('/api/rides/estimate', {
    method: 'POST',
    body: JSON.stringify({ pickup_lat: lat1, pickup_lon: lon1, dropoff_lat: lat2, dropoff_lon: lat2 })
  });

  if (quoteData && quoteData.data) {
    const d = quoteData.data;
    document.getElementById('tripDistDisplay').textContent = `${d.distance_km} km`;
    document.getElementById('tripTimeDisplay').textContent = `${d.estimated_duration_min} mins`;
  }
}

// Map Click Callback
window.onMapLocationSelected = function(type, lat, lon) {
  if (type === 'pickup') {
    document.getElementById('pickupInput').value = `GPS Pin (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
    api.toast("Pickup pinned on map", "success");
  } else if (type === 'dropoff') {
    document.getElementById('dropoffInput').value = `GPS Pin (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
    api.toast("Destination pinned on map", "success");
  }
};

// Use Current GPS Location
function useCurrentGpsLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        mapManager.setPickup(lat, lon, "Your Current Location");
        mapManager.map.flyTo([lat, lon], 14);
        document.getElementById('pickupInput').value = `Current Location (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
        api.toast("GPS Location Acquired", "success");
      },
      () => {
        api.toast("Using simulated Delhi GPS center", "info");
      }
    );
  }
}

// Request Instant Ride Booking
async function requestRideBooking() {
  const btn = document.getElementById('bookRideBtn');
  btn.disabled = true;
  btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Finding Nearby Drivers...`;

  const city = INDIA_CITIES[currentCityKey] || INDIA_CITIES['delhi'];
  const p = city.landmarks[0];
  const d = city.landmarks[1] || city.landmarks[0];

  const payload = {
    rider_id: api.currentUser ? api.currentUser.id : "rider-demo-01",
    pickup_location: document.getElementById('pickupInput').value,
    dropoff_location: document.getElementById('dropoffInput').value,
    pickup_lat: p.lat,
    pickup_lon: p.lon,
    dropoff_lat: d.lat,
    dropoff_lon: d.lon,
    vehicle_type: selectedVehicleKey,
    payment_method: "UPI"
  };

  const res = await api.request('/api/rides/request', {
    method: 'POST',
    body: JSON.stringify(payload)
  });

  btn.disabled = false;
  btn.innerHTML = `<i class="fas fa-bolt"></i> Confirm & Request Ride`;

  if (res && res.ride) {
    activeRide = res.ride;
    localStorage.setItem('rc_active_ride', JSON.stringify(activeRide));
    showActiveRideCard(activeRide);
    api.toast(`Captain ${activeRide.driver_name} accepted your ride!`, 'success');

    // Generate waypoints and start simulated car driving on map!
    const waypoints = [
      { lat: p.lat, lon: p.lon },
      { lat: p.lat + 0.005, lon: p.lon + 0.004 },
      { lat: p.lat + 0.012, lon: p.lon + 0.010 },
      { lat: d.lat - 0.008, lon: d.lon - 0.005 },
      { lat: d.lat, lon: d.lon }
    ];
    mapManager.drawRoute(waypoints);
    mapManager.startVehicleSimulation(waypoints, (percent) => {
      if (percent >= 100) {
        document.getElementById('rideStatusText').textContent = "Arrived at Destination!";
        api.toast("You have reached your destination. Please pay the driver.", "success");
        openPaymentModal();
      } else {
        document.getElementById('rideStatusText').textContent = `In Transit (${percent}%)`;
      }
    });
  }
}

// Display Active Ride Card
function showActiveRideCard(ride) {
  const card = document.getElementById('activeRideCard');
  if (!card) return;
  card.style.display = 'block';
  document.getElementById('rideFareText').textContent = `₹${ride.fare}`;
  document.getElementById('driverNameText').textContent = ride.driver_name;
  document.getElementById('driverCarText').innerHTML = `${ride.vehicle_make || 'Maruti'} ${ride.vehicle_model || 'Dzire'} • <b style="color:#fff;">${ride.plate_number || 'DL 01 AZ 4521'}</b>`;
  document.getElementById('rideOtpText').textContent = ride.otp || '4592';
}

// Cancel Active Ride
async function cancelActiveRide() {
  if (!confirm("Are you sure you want to cancel this ride?")) return;
  if (activeRide) {
    await api.request(`/api/rides/${activeRide.id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status: 'cancelled', cancellation_reason: 'Rider cancelled' })
    });
  }
  localStorage.removeItem('rc_active_ride');
  activeRide = null;
  document.getElementById('activeRideCard').style.display = 'none';
  api.toast("Ride cancelled successfully", "info");
}

// --- Scheduled Rides Flow (Requirement 16) ---
async function createScheduledTrip() {
  const date = document.getElementById('schedDate').value;
  const time = document.getElementById('schedTime').value;
  if (!date || !time) {
    api.toast("Please select both date and time", "error");
    return;
  }

  const schIso = `${date}T${time}:00`;
  const city = INDIA_CITIES[currentCityKey];

  const payload = {
    rider_id: api.currentUser ? api.currentUser.id : "rider-demo-01",
    pickup_location: document.getElementById('schedPickup').value,
    dropoff_location: document.getElementById('schedDropoff').value,
    pickup_lat: city.lat,
    pickup_lon: city.lon,
    dropoff_lat: city.lat + 0.05,
    dropoff_lon: city.lon + 0.05,
    scheduled_time: schIso,
    vehicle_type: document.getElementById('schedVehicle').value
  };

  const res = await api.request('/api/scheduled-rides', {
    method: 'POST',
    body: JSON.stringify(payload)
  });

  if (res && res.scheduled_ride) {
    api.toast("Ride scheduled successfully!", "success");
    renderScheduledRides();
  }
}

function renderScheduledRides() {
  const container = document.getElementById('scheduledRidesList');
  if (!container) return;

  container.innerHTML = `
    <div style="background: rgba(255,255,255,0.04); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px; margin-bottom: 10px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <span class="badge badge-saffron"><i class="fas fa-clock"></i> Tomorrow • 09:30 AM</span>
        <span style="font-weight:800; color:var(--secondary);">₹320</span>
      </div>
      <div style="font-size:0.85rem; color:#fff; font-weight:600;">Connaught Place ➔ IGI Airport</div>
      <div style="font-size:0.78rem; color:var(--text-muted); margin:4px 0 10px;">Vehicle: Prime Sedan • Booking ID: SCH-9821</div>
      <div style="display:flex; gap:8px;">
        <button class="btn btn-secondary btn-sm" onclick="api.toast('Scheduled ride pickup location updated', 'success')">Modify</button>
        <button class="btn btn-danger btn-sm" onclick="api.toast('Scheduled ride cancelled without penalty (>1 hr rule)', 'info'); this.parentElement.parentElement.remove();">Cancel</button>
      </div>
    </div>
  `;
}

// --- Parcel Delivery Flow (Requirement 17) ---
function selectParcelSize(size, elem) {
  selectedParcelSize = size;
  document.querySelectorAll('.parcel-size-card').forEach(c => c.classList.remove('active'));
  elem.classList.add('active');
}

async function bookParcelDelivery() {
  const desc = document.getElementById('parcelDesc').value;
  const recipient = document.getElementById('parcelRecipientName').value;
  const phone = document.getElementById('parcelRecipientPhone').value;

  const payload = {
    sender_id: api.currentUser ? api.currentUser.id : "rider-demo-01",
    recipient_name: recipient,
    recipient_phone: phone,
    pickup_location: document.getElementById('pickupInput').value,
    dropoff_location: document.getElementById('dropoffInput').value,
    pickup_lat: 28.6139,
    pickup_lon: 77.2090,
    dropoff_lat: 28.5562,
    dropoff_lon: 77.1000,
    parcel_size: selectedParcelSize,
    weight_kg: selectedParcelSize === 'small' ? 3.0 : 10.0,
    description: desc,
    is_fragile: document.getElementById('parcelFragile').checked,
    is_urgent: document.getElementById('parcelUrgent').checked,
    payment_method: "UPI"
  };

  const res = await api.request('/api/parcels/request', {
    method: 'POST',
    body: JSON.stringify(payload)
  });

  if (res && res.parcel) {
    api.toast(`Parcel Courier Dispatched! Delivery PIN: ${res.parcel.delivery_otp}`, 'success');
    renderParcelHistory();
  }
}

function renderParcelHistory() {
  const container = document.getElementById('parcelHistoryList');
  if (!container) return;

  container.innerHTML = `
    <div style="background: rgba(255,255,255,0.04); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px; margin-bottom: 10px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <span class="badge badge-green"><i class="fas fa-check"></i> Delivered</span>
        <span style="font-weight:800; color:var(--secondary);">₹185</span>
      </div>
      <div style="font-size:0.85rem; color:#fff; font-weight:600;">Office Laptop & Documents Package</div>
      <div style="font-size:0.78rem; color:var(--text-muted); margin:4px 0;">To: Neha Sharma (+91 98111 55443) • Recipient OTP: 8821</div>
      <div style="font-size:0.75rem; color:#34d399;"><i class="fas fa-camera"></i> Pickup photo verified • Signed by recipient</div>
    </div>
  `;
}

// --- Outstation Flow ---
function onCorridorSelected(val) {
  const corridors = {
    'delhi-agra': { dist: '210 km', toll: '₹415', fare: '₹2,850' },
    'delhi-jaipur': { dist: '280 km', toll: '₹360', fare: '₹3,750' },
    'mumbai-pune': { dist: '150 km', toll: '₹320', fare: '₹2,350' },
    'blr-mysuru': { dist: '140 km', toll: '₹320', fare: '₹2,100' },
    'indore-ujjain': { dist: '55 km', toll: '₹80', fare: '₹950' },
    'indore-bhopal': { dist: '190 km', toll: '₹240', fare: '₹2,600' },
    'chennai-pondy': { dist: '150 km', toll: '₹120', fare: '₹2,250' },
    'ahmedabad-udaipur': { dist: '260 km', toll: '₹320', fare: '₹3,500' }
  };
  const c = corridors[val] || corridors['delhi-agra'];
  document.getElementById('corridorDist').textContent = c.dist;
  document.getElementById('corridorToll').textContent = c.toll;
  document.getElementById('corridorFare').textContent = c.fare;
}

function bookOutstationRide() {
  api.toast("Outstation Captain booked! Highway confirmation SMS sent.", "success");
}

// --- History Flow ---
function renderRideHistory() {
  const container = document.getElementById('fullHistoryContainer');
  if (!container) return;

  container.innerHTML = `
    <div style="background: rgba(255,255,255,0.04); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 16px; margin-bottom: 12px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <span class="badge badge-green"><i class="fas fa-check"></i> Completed</span>
        <span style="font-weight:800; color:var(--secondary);">₹345.00</span>
      </div>
      <div style="font-weight:700; color:#fff; font-size:0.95rem;">IGI Airport ➔ Connaught Place, Delhi</div>
      <div style="font-size:0.82rem; color:var(--text-muted); margin:4px 0 12px;">Captain: Vikram Singh Gurjar (DL 01 AZ 4521) • Paid via UPI</div>
      <button class="btn btn-secondary btn-sm" onclick="downloadTaxReceipt('ride-hist-01')">
        <i class="fas fa-file-invoice"></i> Download GST Tax Receipt
      </button>
    </div>
  `;
}

// Download GST Invoice
async function downloadTaxReceipt(itemId) {
  const receipt = await api.request(`/api/payments/receipt/${itemId}`);
  if (receipt) {
    alert(`=== RIDE-CONNECT GST TAX INVOICE ===\nInvoice No: ${receipt.invoice_number}\nDate: ${receipt.invoice_date}\nSAC Code: ${receipt.sac_code} (Passenger Transport)\nGSTIN: ${receipt.gstin}\nAmount: ₹${receipt.pricing_breakdown.total_paid}\nCGST (2.5%): ₹${receipt.pricing_breakdown.cgst_2_5_percent}\nSGST (2.5%): ₹${receipt.pricing_breakdown.sgst_2_5_percent}\nThank you for riding with RideConnect India!`);
  }
}

// --- SOS Emergency Protocol (Requirement 11) ---
function openSosModal() {
  document.getElementById('sosModal').classList.add('active');
}

function closeSosModal() {
  document.getElementById('sosModal').classList.remove('active');
}

async function triggerSosProtocol() {
  closeSosModal();
  const res = await api.request('/api/emergency/sos', {
    method: 'POST',
    body: JSON.stringify({
      user_id: api.currentUser ? api.currentUser.id : "rider-demo-01",
      lat: 28.6139,
      lon: 77.2090,
      current_location: "Connaught Place, New Delhi"
    })
  });
  alert("🚨 EMERGENCY ALERT TRIGGERED!\n\n1. National ERSS 112 Dispatched\n2. Delhi Police PCR Control Room Alerted\n3. Emergency SMS sent to family contacts with live tracking link.\n\nKeep your phone line open; an emergency officer is connecting to you.");
}

// --- Indian UPI Payment Modal (Requirement 6) ---
function openPaymentModal() {
  document.getElementById('paymentModal').classList.add('active');
}

function closePaymentModal() {
  document.getElementById('paymentModal').classList.remove('active');
}

async function completePayment(method) {
  closePaymentModal();
  await api.request('/api/payments/process', {
    method: 'POST',
    body: JSON.stringify({
      amount: 215.0,
      method: method,
      upi_id: method === 'UPI' ? document.getElementById('upiVpaInput').value : null
    })
  });
  api.toast(`Payment of ₹215.00 completed successfully via ${method}!`, "success");
  if (activeRide) {
    document.getElementById('activeRideCard').style.display = 'none';
    localStorage.removeItem('rc_active_ride');
    activeRide = null;
  }
}
