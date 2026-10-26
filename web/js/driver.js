/**
 * Driver Dashboard Controller for RideConnect India.
 * Handles online availability, incoming ride radar, 30s timers, navigation lifecycle, and earnings.
 */
let driverMapManager;
let isDriverOnline = true;
let countdownTimer = null;
let currentTripState = 'idle'; // idle, assigned, arrived, in_transit, completed

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Map
  const delhi = INDIA_CITIES['delhi'];
  driverMapManager = new MapManager('driver-map', 'delhi');
  driverMapManager.init(delhi.lat, delhi.lon, 13);

  // Mark driver vehicle marker
  driverMapManager.setPickup(28.6139, 77.2090, "You (Captain Vikram)");

  // 2. Trigger an incoming request simulation after 3 seconds to demonstrate radar
  setTimeout(() => {
    if (isDriverOnline) {
      showIncomingRequest();
    }
  }, 2500);
});

// Toggle Online / Offline
function toggleDriverOnlineStatus() {
  isDriverOnline = !isDriverOnline;
  const card = document.getElementById('beaconCard');
  const title = document.getElementById('beaconTitle');
  const sub = document.getElementById('beaconSubtitle');
  const btn = document.getElementById('toggleOnlineBtn');

  if (isDriverOnline) {
    card.classList.remove('offline');
    title.textContent = "You're ONLINE";
    sub.textContent = "Ready to receive nearby rides & parcels";
    btn.className = "btn btn-success";
    btn.innerHTML = `<span class="pulse-dot"></span> <span>Go Offline</span>`;
    api.toast("You are now ONLINE. Radar scanning...", "success");

    // Re-trigger incoming order simulation
    setTimeout(() => { if (isDriverOnline) showIncomingRequest(); }, 4000);
  } else {
    card.classList.add('offline');
    title.textContent = "You're OFFLINE";
    sub.textContent = "Turn ON to start receiving trip requests";
    btn.className = "btn btn-secondary";
    btn.innerHTML = `<i class="fas fa-power-off"></i> <span>Go Online</span>`;
    document.getElementById('incomingRequestCard').style.display = 'none';
    if (countdownTimer) clearInterval(countdownTimer);
    api.toast("You are now OFFLINE", "info");
  }
}

// Show Incoming Request Modal with 30s timer
function showIncomingRequest() {
  const card = document.getElementById('incomingRequestCard');
  card.style.display = 'block';

  let timeLeft = 30;
  const timerElem = document.getElementById('reqTimer');
  timerElem.textContent = `${timeLeft}s`;

  if (countdownTimer) clearInterval(countdownTimer);
  countdownTimer = setInterval(() => {
    timeLeft--;
    timerElem.textContent = `${timeLeft}s`;
    if (timeLeft <= 0) {
      clearInterval(countdownTimer);
      card.style.display = 'none';
      api.toast("Request timed out. Driver reassigned.", "warning");
    }
  }, 1000);
}

// Accept Request
function acceptIncomingRequest() {
  if (countdownTimer) clearInterval(countdownTimer);
  document.getElementById('incomingRequestCard').style.display = 'none';
  document.getElementById('driverNavCard').style.display = 'block';

  currentTripState = 'assigned';
  document.getElementById('tripActionBtn').innerHTML = `<i class="fas fa-location-dot"></i> Mark Arrived`;

  api.toast("Ride Accepted! Navigating to Passenger Pickup...", "success");

  // Draw pickup route
  const waypoints = [
    { lat: 28.6139, lon: 77.2090 },
    { lat: 28.6250, lon: 77.2120 },
    { lat: 28.6315, lon: 77.2167 }
  ];
  driverMapManager.drawRoute(waypoints);
}

// Decline Request
function declineIncomingRequest() {
  if (countdownTimer) clearInterval(countdownTimer);
  document.getElementById('incomingRequestCard').style.display = 'none';
  api.toast("Ride declined. Next captain searching...", "info");
}

// Advance Trip Lifecycle
function advanceTripLifecycle() {
  const btn = document.getElementById('tripActionBtn');
  const instruction = document.getElementById('navInstruction');

  if (currentTripState === 'assigned') {
    currentTripState = 'arrived';
    btn.innerHTML = `<i class="fas fa-play"></i> Verify OTP & Start Trip`;
    instruction.textContent = "Arrived at Pickup! Waiting for passenger Aarav Patel.";
    api.toast("Arrived at Pickup. Enter Rider's OTP.", "info");
  } else if (currentTripState === 'arrived') {
    const enteredOtp = prompt("Ask rider for 4-digit start PIN (Demo OTP: 4592):", "4592");
    if (enteredOtp) {
      currentTripState = 'in_transit';
      btn.className = "btn btn-success btn-sm";
      btn.innerHTML = `<i class="fas fa-check-circle"></i> Complete Trip`;
      instruction.textContent = "En route to IGI Airport Terminal 3. Maintain smooth driving.";
      api.toast("OTP Verified! Trip Started.", "success");

      // Draw dropoff route
      const waypoints = [
        { lat: 28.6315, lon: 77.2167 },
        { lat: 28.6000, lon: 77.1600 },
        { lat: 28.5562, lon: 77.1000 }
      ];
      driverMapManager.drawRoute(waypoints);
      driverMapManager.startVehicleSimulation(waypoints, (percent) => {
        if (percent >= 100) {
          api.toast("Arrived at Destination!", "success");
        }
      });
    }
  } else if (currentTripState === 'in_transit') {
    currentTripState = 'completed';
    document.getElementById('driverNavCard').style.display = 'none';
    
    // Update earnings
    const netElem = document.getElementById('driverNetEarnings');
    const tripsElem = document.getElementById('driverTripCount');
    netElem.textContent = "₹2,697";
    tripsElem.textContent = "9";
    
    alert("🎉 TRIP COMPLETED!\n\nGross Fare: ₹275.00\nPlatform Fee (10%): ₹27.50\nYour Net Earnings: +₹247.50\nPayment: Paid via UPI (Auto-credited to bank account)");
    api.toast("Earnings updated. Scanning for next request...", "success");
  }
}

// Call Passenger Simulator
function callRiderSimulator() {
  alert("📞 Connecting masked VoIP call to Passenger Aarav Patel (+91 98765 43210)... Phone connected.");
}

// Update Driver Preferences
function updateDriverPrefs() {
  api.toast("Preferences saved to captain profile", "success");
}
