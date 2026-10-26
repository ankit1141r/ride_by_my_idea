/**
 * Interactive Leaflet Map Manager for Pan-India RideConnect.
 * Supports smooth city flyTo, vehicle markers, route polylines, and simulated live GPS navigation.
 */
class MapManager {
  constructor(mapContainerId = 'map', defaultCity = 'delhi') {
    this.containerId = mapContainerId;
    this.map = null;
    this.pickupMarker = null;
    this.dropoffMarker = null;
    this.vehicleMarker = null;
    this.routePolyline = null;
    this.driverMarkers = [];
    this.currentCity = defaultCity;
    this.animationTimer = null;
  }

  init(centerLat = 28.6139, centerLon = 77.2090, zoom = 12) {
    const el = document.getElementById(this.containerId);
    if (!el || typeof L === 'undefined') {
      console.warn('Map container or Leaflet library not found.');
      return;
    }

    if (this.map) {
      this.map.remove();
    }

    this.map = L.map(this.containerId, {
      zoomControl: true,
      attributionControl: false
    }).setView([centerLat, centerLon], zoom);

    // High quality OpenStreetMap / CartoDB Dark/Voyager tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd'
    }).addTo(this.map);

    // Click on map to place pin
    this.map.on('click', (e) => {
      this.handleMapClick(e.latlng.lat, e.latlng.lng);
    });

    return this.map;
  }

  flyToCity(cityKey) {
    if (!this.map) return;
    const city = INDIA_CITIES[cityKey.toLowerCase()];
    if (city) {
      this.currentCity = cityKey.toLowerCase();
      this.map.flyTo([city.lat, city.lon], city.zoom || 12, {
        duration: 1.5,
        easeLinearity: 0.25
      });
      this.renderNearbyDrivers(city.lat, city.lon);
    }
  }

  createCustomIcon(iconClass, color, size = 32) {
    return L.divIcon({
      className: 'custom-map-icon',
      html: `
        <div style="
          width: ${size}px; height: ${size}px;
          background: ${color};
          border: 2px solid #ffffff;
          border-radius: 50%;
          box-shadow: 0 4px 12px rgba(0,0,0,0.4);
          display: flex; align-items: center; justify-content: center;
          color: #ffffff; font-size: ${size * 0.45}px;
        ">
          <i class="fas ${iconClass}"></i>
        </div>
      `,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2]
    });
  }

  setPickup(lat, lon, label = "Pickup") {
    if (!this.map) return;
    if (this.pickupMarker) this.map.removeLayer(this.pickupMarker);
    this.pickupMarker = L.marker([lat, lon], {
      icon: this.createCustomIcon('fa-circle-dot', '#10b981', 34)
    }).addTo(this.map).bindPopup(`<b>Pickup:</b> ${label}`).openPopup();
  }

  setDropoff(lat, lon, label = "Destination") {
    if (!this.map) return;
    if (this.dropoffMarker) this.map.removeLayer(this.dropoffMarker);
    this.dropoffMarker = L.marker([lat, lon], {
      icon: this.createCustomIcon('fa-location-dot', '#ef4444', 34)
    }).addTo(this.map).bindPopup(`<b>Dropoff:</b> ${label}`);
  }

  drawRoute(waypoints) {
    if (!this.map || !waypoints || waypoints.length === 0) return;
    if (this.routePolyline) this.map.removeLayer(this.routePolyline);

    const latlngs = waypoints.map(w => [w.lat, w.lon]);
    this.routePolyline = L.polyline(latlngs, {
      color: '#ff6b00',
      weight: 5,
      opacity: 0.85,
      lineCap: 'round',
      lineJoin: 'round',
      dashArray: '8, 8'
    }).addTo(this.map);

    this.map.fitBounds(this.routePolyline.getBounds(), { padding: [40, 40] });
  }

  // Animates vehicle moving along the route during an active ride
  startVehicleSimulation(waypoints, onProgress) {
    if (!this.map || !waypoints || waypoints.length === 0) return;
    if (this.vehicleMarker) this.map.removeLayer(this.vehicleMarker);
    if (this.animationTimer) clearInterval(this.animationTimer);

    let idx = 0;
    const startPoint = waypoints[0];
    this.vehicleMarker = L.marker([startPoint.lat, startPoint.lon], {
      icon: this.createCustomIcon('fa-car', '#ff6b00', 36)
    }).addTo(this.map).bindPopup('<b>Driver</b> (Live)');

    this.animationTimer = setInterval(() => {
      idx++;
      if (idx >= waypoints.length) {
        clearInterval(this.animationTimer);
        if (onProgress) onProgress(100, waypoints[waypoints.length - 1]);
        return;
      }
      const pt = waypoints[idx];
      this.vehicleMarker.setLatLng([pt.lat, pt.lon]);
      const percent = Math.round((idx / waypoints.length) * 100);
      if (onProgress) onProgress(percent, pt);
    }, 1200);
  }

  renderNearbyDrivers(centerLat, centerLon, count = 5) {
    if (!this.map) return;
    // Clear old driver markers
    this.driverMarkers.forEach(m => this.map.removeLayer(m));
    this.driverMarkers = [];

    const icons = ['fa-car', 'fa-bus-simple', 'fa-motorcycle'];
    for (let i = 0; i < count; i++) {
      const offsetLat = centerLat + (Math.random() - 0.5) * 0.04;
      const offsetLon = centerLon + (Math.random() - 0.5) * 0.04;
      const ic = icons[i % icons.length];
      const marker = L.marker([offsetLat, offsetLon], {
        icon: this.createCustomIcon(ic, '#3b82f6', 28)
      }).addTo(this.map);
      this.driverMarkers.push(marker);
    }
  }

  handleMapClick(lat, lon) {
    if (!this.pickupMarker) {
      this.setPickup(lat, lon, "Selected on Map");
      if (window.onMapLocationSelected) window.onMapLocationSelected('pickup', lat, lon);
    } else if (!this.dropoffMarker) {
      this.setDropoff(lat, lon, "Selected on Map");
      if (window.onMapLocationSelected) window.onMapLocationSelected('dropoff', lat, lon);
    } else {
      // Reset and set new pickup
      this.setPickup(lat, lon, "New Pickup");
      if (this.dropoffMarker) {
        this.map.removeLayer(this.dropoffMarker);
        this.dropoffMarker = null;
      }
      if (this.routePolyline) {
        this.map.removeLayer(this.routePolyline);
        this.routePolyline = null;
      }
      if (window.onMapLocationSelected) window.onMapLocationSelected('pickup', lat, lon);
    }
  }
}

window.MapManager = MapManager;
