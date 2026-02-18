// Rider Dashboard JavaScript
class RiderDashboard {
    constructor() {
        this.currentRide = null;
        this.selectedDriver = null;
        this.rideHistory = [];
        this.emergencyContacts = [];
        this.currentLocation = null;
        
        this.init();
    }

    async init() {
        // Check if user is logged in and is a rider
        if (!authManager.isLoggedIn() || authManager.getUserType() !== 'rider') {
            window.location.href = 'index.html';
            return;
        }

        // Initialize dashboard
        this.setupNavigation();
        this.setupEventListeners();
        this.loadUserProfile();
        this.loadRideHistory();
        this.loadEmergencyContacts();
        this.checkCurrentRide();
        
        // Connect to WebSocket for real-time updates
        this.setupWebSocket();
        
        // Get current location
        this.getCurrentLocation();
    }

    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link[data-section]');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                this.showSection(section);
                
                // Update active nav link
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }

    showSection(sectionId) {
        // Hide all sections
        const sections = document.querySelectorAll('.dashboard-section');
        sections.forEach(section => section.classList.remove('active'));
        
        // Show selected section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // Load section-specific data
        switch (sectionId) {
            case 'ride-history':
                this.loadRideHistory();
                break;
            case 'current-ride':
                this.checkCurrentRide();
                break;
            case 'profile':
                this.loadUserProfile();
                break;
        }
    }

    setupEventListeners() {
        // Ride booking form
        const bookingForm = document.getElementById('rideBookingForm');
        if (bookingForm) {
            bookingForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.searchDrivers();
            });
        }

        // Location inputs for fare estimation
        const pickupInput = document.getElementById('pickupLocation');
        const destinationInput = document.getElementById('destinationLocation');
        
        if (pickupInput && destinationInput) {
            pickupInput.addEventListener('input', () => this.calculateFareEstimate());
            destinationInput.addEventListener('input', () => this.calculateFareEstimate());
        }

        // Emergency contact form
        const contactForm = document.getElementById('addContactForm');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addEmergencyContact();
            });
        }

        // Star rating
        const starRating = document.getElementById('starRating');
        if (starRating) {
            const stars = starRating.querySelectorAll('i');
            stars.forEach((star, index) => {
                star.addEventListener('click', () => {
                    this.setRating(index + 1);
                });
                
                star.addEventListener('mouseenter', () => {
                    this.highlightStars(index + 1);
                });
            });
            
            starRating.addEventListener('mouseleave', () => {
                this.resetStarHighlight();
            });
        }
    }

    async getCurrentLocation() {
        try {
            const location = await getCurrentLocation();
            this.currentLocation = location;
            
            // Update pickup location if empty
            const pickupInput = document.getElementById('pickupLocation');
            if (pickupInput && !pickupInput.value) {
                pickupInput.value = 'Current Location';
            }
        } catch (error) {
            console.error('Failed to get current location:', error);
            showToast(error.message, 'warning');
        }
    }

    async useCurrentLocation(type) {
        try {
            const location = await getCurrentLocation();
            this.currentLocation = location;
            
            const input = document.getElementById(type === 'pickup' ? 'pickupLocation' : 'destinationLocation');
            if (input) {
                input.value = 'Current Location';
                this.calculateFareEstimate();
            }
            
            showToast('Current location set', 'success');
        } catch (error) {
            handleAPIError(error);
        }
    }

    async calculateFareEstimate() {
        const pickupInput = document.getElementById('pickupLocation');
        const destinationInput = document.getElementById('destinationLocation');
        const fareEstimate = document.getElementById('fareEstimate');
        
        if (!pickupInput.value || !destinationInput.value) {
            fareEstimate.style.display = 'none';
            return;
        }

        // Mock fare calculation (in real app, this would call the API)
        const distance = 5.2; // Mock distance
        const baseFare = APP_CONFIG.FARE_CONFIG.BASE_FARE;
        const perKmRate = APP_CONFIG.FARE_CONFIG.PER_KM_RATE;
        const estimatedFare = baseFare + (distance * perKmRate);

        document.getElementById('fareAmount').textContent = formatCurrency(estimatedFare);
        document.getElementById('distanceInfo').textContent = formatDistance(distance);
        fareEstimate.style.display = 'block';
    }

    async searchDrivers() {
        const pickupInput = document.getElementById('pickupLocation');
        const destinationInput = document.getElementById('destinationLocation');
        
        if (!pickupInput.value || !destinationInput.value) {
            showToast('Please enter both pickup and destination', 'error');
            return;
        }

        try {
            showLoading();
            
            // Prepare ride request data
            const rideData = {
                pickup_location: {
                    latitude: this.currentLocation?.latitude || APP_CONFIG.DEFAULT_LOCATION.latitude,
                    longitude: this.currentLocation?.longitude || APP_CONFIG.DEFAULT_LOCATION.longitude,
                    address: pickupInput.value
                },
                destination: {
                    latitude: APP_CONFIG.DEFAULT_LOCATION.latitude + 0.01,
                    longitude: APP_CONFIG.DEFAULT_LOCATION.longitude + 0.01,
                    address: destinationInput.value
                }
            };

            const response = await apiService.requestRide(rideData);
            
            if (response.ride_id) {
                showToast(SUCCESS_MESSAGES.RIDE_REQUESTED, 'success');
                this.showDriverSearchResults(response);
            }
            
        } catch (error) {
            handleAPIError(error);
        } finally {
            hideLoading();
        }
    }

    showDriverSearchResults(rideResponse) {
        const resultsDiv = document.getElementById('driverSearchResults');
        const driversList = document.getElementById('driversList');
        
        // Mock driver data (in real app, this would come from the API)
        const mockDrivers = [
            {
                driver_id: 'driver1',
                name: 'Rajesh Kumar',
                rating: 4.8,
                total_rides: 245,
                distance_km: 0.8,
                eta_minutes: 3,
                vehicle: {
                    registration_number: 'MP09AB1234',
                    make: 'Maruti',
                    model: 'Swift',
                    color: 'White'
                }
            },
            {
                driver_id: 'driver2',
                name: 'Amit Sharma',
                rating: 4.6,
                total_rides: 189,
                distance_km: 1.2,
                eta_minutes: 5,
                vehicle: {
                    registration_number: 'MP09CD5678',
                    make: 'Hyundai',
                    model: 'i20',
                    color: 'Blue'
                }
            }
        ];

        driversList.innerHTML = mockDrivers.map(driver => `
            <div class="driver-card" onclick="riderDashboard.selectDriver('${driver.driver_id}')">
                <div class="driver-header">
                    <div class="driver-info">
                        <h4>${driver.name}</h4>
                        <div class="driver-rating">
                            <i class="fas fa-star"></i>
                            <span>${driver.rating}</span>
                            <span>(${driver.total_rides} rides)</span>
                        </div>
                    </div>
                    <div class="eta-info">
                        <div>${driver.eta_minutes} min away</div>
                        <div class="driver-distance">${formatDistance(driver.distance_km)}</div>
                    </div>
                </div>
                <div class="vehicle-info">
                    <span><i class="fas fa-car"></i> ${driver.vehicle.make} ${driver.vehicle.model}</span>
                    <span><i class="fas fa-palette"></i> ${driver.vehicle.color}</span>
                    <span><i class="fas fa-id-card"></i> ${driver.vehicle.registration_number}</span>
                </div>
            </div>
        `).join('');

        resultsDiv.style.display = 'block';
    }

    selectDriver(driverId) {
        // Remove previous selection
        const driverCards = document.querySelectorAll('.driver-card');
        driverCards.forEach(card => card.classList.remove('selected'));
        
        // Select new driver
        const selectedCard = document.querySelector(`[onclick="riderDashboard.selectDriver('${driverId}')"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
            this.selectedDriver = driverId;
            
            // Add confirm button
            this.showConfirmRideButton();
        }
    }

    showConfirmRideButton() {
        const resultsHeader = document.querySelector('.results-header');
        let confirmBtn = document.getElementById('confirmRideBtn');
        
        if (!confirmBtn) {
            confirmBtn = document.createElement('button');
            confirmBtn.id = 'confirmRideBtn';
            confirmBtn.className = 'btn btn-primary';
            confirmBtn.innerHTML = '<i class="fas fa-check"></i> Confirm Ride';
            confirmBtn.onclick = () => this.confirmRide();
            resultsHeader.appendChild(confirmBtn);
        }
    }

    async confirmRide() {
        if (!this.selectedDriver) {
            showToast('Please select a driver', 'error');
            return;
        }

        try {
            showLoading();
            
            // In real app, this would confirm the ride with the selected driver
            showToast('Ride confirmed! Driver is on the way.', 'success');
            
            // Hide search results and show current ride
            document.getElementById('driverSearchResults').style.display = 'none';
            this.showSection('current-ride');
            this.loadCurrentRide();
            
        } catch (error) {
            handleAPIError(error);
        } finally {
            hideLoading();
        }
    }

    cancelSearch() {
        document.getElementById('driverSearchResults').style.display = 'none';
        this.selectedDriver = null;
    }

    async loadCurrentRide() {
        // Mock current ride data
        const mockRide = {
            ride_id: 'ride123',
            status: 'driver_arriving',
            driver: {
                name: 'Rajesh Kumar',
                phone_number: '+919876543210',
                rating: 4.8,
                vehicle: {
                    registration_number: 'MP09AB1234',
                    make: 'Maruti',
                    model: 'Swift',
                    color: 'White'
                }
            },
            pickup_location: {
                address: 'Rajwada, Indore'
            },
            destination: {
                address: 'Treasure Island Mall, Indore'
            },
            estimated_fare: 85,
            eta_minutes: 3
        };

        this.currentRide = mockRide;
        this.displayCurrentRide(mockRide);
    }

    displayCurrentRide(ride) {
        const noRideDiv = document.getElementById('noCurrentRide');
        const rideCard = document.getElementById('currentRideCard');
        
        if (!ride) {
            noRideDiv.style.display = 'block';
            rideCard.style.display = 'none';
            return;
        }

        noRideDiv.style.display = 'none';
        rideCard.style.display = 'block';

        const statusText = {
            'requested': 'Looking for drivers...',
            'matched': 'Driver assigned',
            'driver_arriving': 'Driver is on the way',
            'in_progress': 'Ride in progress',
            'completed': 'Ride completed'
        };

        rideCard.innerHTML = `
            <div class="ride-status">
                <div class="status-indicator"></div>
                <span class="status-text">${statusText[ride.status] || ride.status}</span>
            </div>
            
            <div class="ride-details">
                <div class="ride-location pickup-location">
                    <i class="fas fa-circle"></i>
                    <span>${ride.pickup_location.address}</span>
                </div>
                <div class="ride-location destination-location">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>${ride.destination.address}</span>
                </div>
            </div>

            <div class="driver-details">
                <h4>Driver: ${ride.driver.name}</h4>
                <p><i class="fas fa-car"></i> ${ride.driver.vehicle.make} ${ride.driver.vehicle.model} (${ride.driver.vehicle.color})</p>
                <p><i class="fas fa-id-card"></i> ${ride.driver.vehicle.registration_number}</p>
                <p><i class="fas fa-star"></i> ${ride.driver.rating} rating</p>
                ${ride.eta_minutes ? `<p><i class="fas fa-clock"></i> Arriving in ${ride.eta_minutes} minutes</p>` : ''}
            </div>

            <div class="ride-actions">
                <button class="btn btn-outline" onclick="riderDashboard.callDriver()">
                    <i class="fas fa-phone"></i>
                    Call Driver
                </button>
                <button class="btn btn-outline" onclick="riderDashboard.shareRide()">
                    <i class="fas fa-share"></i>
                    Share Ride
                </button>
                <button class="btn btn-danger" onclick="riderDashboard.cancelRide()">
                    <i class="fas fa-times"></i>
                    Cancel Ride
                </button>
                <button class="btn btn-danger" onclick="riderDashboard.emergencyAlert()">
                    <i class="fas fa-exclamation-triangle"></i>
                    Emergency
                </button>
            </div>
        `;
    }

    async checkCurrentRide() {
        try {
            // In real app, check for active rides from API
            // For now, use mock data if we have a current ride
            if (this.currentRide) {
                this.displayCurrentRide(this.currentRide);
            } else {
                this.displayCurrentRide(null);
            }
        } catch (error) {
            console.error('Failed to check current ride:', error);
            this.displayCurrentRide(null);
        }
    }

    async loadRideHistory() {
        try {
            const history = await apiService.getRideHistory();
            this.rideHistory = history.rides || [];
            this.displayRideHistory();
        } catch (error) {
            console.error('Failed to load ride history:', error);
            // Use mock data
            this.displayMockRideHistory();
        }
    }

    displayMockRideHistory() {
        const mockHistory = [
            {
                ride_id: 'ride001',
                date: '2024-02-15T10:30:00Z',
                pickup_location: { address: 'Rajwada, Indore' },
                destination: { address: 'Treasure Island Mall, Indore' },
                status: 'completed',
                final_fare: 85,
                driver_name: 'Rajesh Kumar'
            },
            {
                ride_id: 'ride002',
                date: '2024-02-14T15:45:00Z',
                pickup_location: { address: 'Palasia Square, Indore' },
                destination: { address: 'Vijay Nagar, Indore' },
                status: 'completed',
                final_fare: 65,
                driver_name: 'Amit Sharma'
            },
            {
                ride_id: 'ride003',
                date: '2024-02-13T09:15:00Z',
                pickup_location: { address: 'Sarafa Bazaar, Indore' },
                destination: { address: 'Airport, Indore' },
                status: 'cancelled',
                final_fare: 0,
                driver_name: null
            }
        ];

        this.displayRideHistory(mockHistory);
    }

    displayRideHistory(history = this.rideHistory) {
        const historyList = document.getElementById('rideHistoryList');
        
        if (!history || history.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-history"></i>
                    <h3>No Ride History</h3>
                    <p>Your completed rides will appear here</p>
                </div>
            `;
            return;
        }

        historyList.innerHTML = history.map(ride => `
            <div class="history-item">
                <div class="history-header">
                    <span class="ride-date">${new Date(ride.date).toLocaleDateString()}</span>
                    <span class="ride-status-badge status-${ride.status}">${ride.status}</span>
                </div>
                <div class="history-details">
                    <div class="history-locations">
                        <div class="pickup-location">
                            <i class="fas fa-circle"></i>
                            ${ride.pickup_location.address}
                        </div>
                        <div class="destination-location">
                            <i class="fas fa-map-marker-alt"></i>
                            ${ride.destination.address}
                        </div>
                        ${ride.driver_name ? `<div class="driver-name">Driver: ${ride.driver_name}</div>` : ''}
                    </div>
                    <div class="history-fare">
                        <div class="fare-value">${formatCurrency(ride.final_fare)}</div>
                        ${ride.status === 'completed' ? '<button class="btn btn-outline btn-small" onclick="riderDashboard.downloadReceipt(\'' + ride.ride_id + '\')">Receipt</button>' : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadUserProfile() {
        const user = authManager.getCurrentUser();
        if (!user) return;

        // Update profile display
        document.getElementById('profileName').textContent = user.name;
        document.getElementById('profilePhone').textContent = formatPhoneNumber(user.phone_number);
        
        // Load user statistics (mock data)
        document.getElementById('totalRides').textContent = '12';
        document.getElementById('totalSpent').textContent = '₹1,240';
        document.getElementById('avgRating').textContent = '4.8';
        document.getElementById('ratingValue').textContent = '4.8';
    }

    async loadEmergencyContacts() {
        try {
            const contacts = await apiService.getEmergencyContacts();
            this.emergencyContacts = contacts.contacts || [];
            this.displayEmergencyContacts();
        } catch (error) {
            console.error('Failed to load emergency contacts:', error);
            this.displayEmergencyContacts([]);
        }
    }

    displayEmergencyContacts(contacts = this.emergencyContacts) {
        const contactsList = document.getElementById('emergencyContactsList');
        
        if (!contacts || contacts.length === 0) {
            contactsList.innerHTML = '<p class="text-muted">No emergency contacts added</p>';
            return;
        }

        contactsList.innerHTML = contacts.map(contact => `
            <div class="contact-item">
                <div class="contact-info">
                    <h5>${contact.name}</h5>
                    <p>${formatPhoneNumber(contact.phone_number)} • ${contact.relationship_type}</p>
                </div>
                <div class="contact-actions">
                    <button class="btn-icon btn-danger" onclick="riderDashboard.removeEmergencyContact('${contact.contact_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    async addEmergencyContact() {
        const name = document.getElementById('contactName').value;
        const phone = document.getElementById('contactPhone').value;
        const relationship = document.getElementById('contactRelation').value;

        if (!name || !phone || !relationship) {
            showToast('Please fill all fields', 'error');
            return;
        }

        if (this.emergencyContacts.length >= 3) {
            showToast('Maximum 3 emergency contacts allowed', 'error');
            return;
        }

        try {
            const contactData = {
                name: name,
                phone_number: phone,
                relationship_type: relationship
            };

            await apiService.addEmergencyContact(contactData);
            showToast('Emergency contact added successfully', 'success');
            
            closeModal('addContactModal');
            document.getElementById('addContactForm').reset();
            this.loadEmergencyContacts();
            
        } catch (error) {
            handleAPIError(error);
        }
    }

    async removeEmergencyContact(contactId) {
        if (!confirm('Are you sure you want to remove this contact?')) {
            return;
        }

        try {
            await apiService.removeEmergencyContact(contactId);
            showToast('Emergency contact removed', 'success');
            this.loadEmergencyContacts();
        } catch (error) {
            handleAPIError(error);
        }
    }

    // Ride actions
    callDriver() {
        if (this.currentRide && this.currentRide.driver) {
            window.open(`tel:${this.currentRide.driver.phone_number}`);
        }
    }

    async shareRide() {
        if (!this.currentRide) return;

        try {
            const response = await apiService.shareRide(this.currentRide.ride_id);
            showToast('Ride shared with emergency contacts', 'success');
        } catch (error) {
            handleAPIError(error);
        }
    }

    async cancelRide() {
        if (!this.currentRide) return;

        if (!confirm('Are you sure you want to cancel this ride?')) {
            return;
        }

        try {
            await apiService.cancelRide(this.currentRide.ride_id);
            showToast('Ride cancelled successfully', 'success');
            this.currentRide = null;
            this.checkCurrentRide();
        } catch (error) {
            handleAPIError(error);
        }
    }

    async emergencyAlert() {
        if (!this.currentRide) return;

        if (!confirm('This will send an emergency alert. Continue?')) {
            return;
        }

        try {
            await apiService.triggerEmergencyAlert(this.currentRide.ride_id);
            showToast('Emergency alert sent!', 'success');
        } catch (error) {
            handleAPIError(error);
        }
    }

    async downloadReceipt(rideId) {
        try {
            // In real app, this would download the PDF receipt
            showToast('Receipt download started', 'success');
        } catch (error) {
            handleAPIError(error);
        }
    }

    // Rating system
    setRating(rating) {
        this.selectedRating = rating;
        this.highlightStars(rating);
    }

    highlightStars(rating) {
        const stars = document.querySelectorAll('#starRating i');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    resetStarHighlight() {
        if (this.selectedRating) {
            this.highlightStars(this.selectedRating);
        } else {
            const stars = document.querySelectorAll('#starRating i');
            stars.forEach(star => star.classList.remove('active'));
        }
    }

    async submitRating() {
        if (!this.selectedRating) {
            showToast('Please select a rating', 'error');
            return;
        }

        const comment = document.getElementById('ratingComment').value;

        try {
            const ratingData = {
                ride_id: this.currentRide.ride_id,
                rating: this.selectedRating,
                review_text: comment
            };

            await apiService.submitRating(ratingData);
            showToast(SUCCESS_MESSAGES.RATING_SUBMITTED, 'success');
            
            closeModal('ratingModal');
            this.selectedRating = null;
            document.getElementById('ratingComment').value = '';
            this.resetStarHighlight();
            
        } catch (error) {
            handleAPIError(error);
        }
    }

    setupWebSocket() {
        // Add WebSocket message handlers for ride updates
        wsManager.addMessageHandler(WS_MESSAGE_TYPES.RIDE_MATCH, (message) => {
            showToast('Driver found! They are on their way.', 'success');
            this.loadCurrentRide();
        });

        wsManager.addMessageHandler(WS_MESSAGE_TYPES.DRIVER_ARRIVAL, (message) => {
            showToast('Your driver has arrived!', 'success');
        });

        wsManager.addMessageHandler(WS_MESSAGE_TYPES.RIDE_START, (message) => {
            showToast('Your ride has started', 'success');
            this.loadCurrentRide();
        });

        wsManager.addMessageHandler(WS_MESSAGE_TYPES.RIDE_COMPLETE, (message) => {
            showToast('Ride completed! Please rate your experience.', 'success');
            this.showRatingModal();
            this.currentRide = null;
            this.checkCurrentRide();
        });
    }

    showRatingModal() {
        document.getElementById('ratingModal').style.display = 'block';
    }
}

// Global functions for HTML onclick handlers
window.riderDashboard = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.riderDashboard = new RiderDashboard();
});

// Global functions
function showSection(sectionId) {
    if (window.riderDashboard) {
        window.riderDashboard.showSection(sectionId);
    }
}

function useCurrentLocation(type) {
    if (window.riderDashboard) {
        window.riderDashboard.useCurrentLocation(type);
    }
}

function cancelSearch() {
    if (window.riderDashboard) {
        window.riderDashboard.cancelSearch();
    }
}

function showAddContactModal() {
    document.getElementById('addContactModal').style.display = 'block';
}

function submitRating() {
    if (window.riderDashboard) {
        window.riderDashboard.submitRating();
    }
}