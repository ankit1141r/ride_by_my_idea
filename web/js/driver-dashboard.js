// Driver Dashboard JavaScript
class DriverDashboard {
    constructor() {
        this.isOnline = false;
        this.currentRide = null;
        this.currentRequest = null;
        this.requestTimer = null;
        this.websocket = null;
        this.location = null;
        this.locationWatcher = null;
        this.stats = {
            todayHours: 0,
            todayRides: 0,
            todayEarnings: 0,
            weekEarnings: 0,
            monthEarnings: 0,
            totalRides: 0,
            totalEarnings: 0,
            avgRating: 5.0,
            acceptanceRate: 100
        };

        this.init();
    }

    async init() {
        // Check authentication
        if (!authManager.isAuthenticated() || authManager.getUserType() !== 'driver') {
            window.location.href = '/';
            return;
        }

        // Initialize dashboard
        this.setupEventListeners();
        await this.loadDriverProfile();
        await this.loadStats();
        this.startLocationTracking();
        this.connectWebSocket();
        
        // Load initial data
        await this.loadRideHistory();
        await this.loadEarnings();
    }

    setupEventListeners() {
        // Availability toggle
        const availabilityToggle = document.getElementById('availabilityToggle');
        if (availabilityToggle) {
            availabilityToggle.addEventListener('change', (e) => {
                this.toggleAvailability(e.target.checked);
            });
        }

        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                if (section) {
                    showSection(section);
                }
            });
        });

        // Vehicle form
        const vehicleForm = document.getElementById('updateVehicleForm');
        if (vehicleForm) {
            vehicleForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateVehicle();
            });
        }

        // Star rating
        document.querySelectorAll('#starRating .fas').forEach(star => {
            star.addEventListener('click', (e) => {
                const rating = parseInt(e.target.dataset.rating);
                this.setStarRating(rating);
            });
        });

        // History filters
        const historyFilter = document.getElementById('historyFilter');
        const dateFilter = document.getElementById('dateFilter');
        
        if (historyFilter) {
            historyFilter.addEventListener('change', () => this.loadRideHistory());
        }
        
        if (dateFilter) {
            dateFilter.addEventListener('change', () => this.loadRideHistory());
        }
    }

    async loadDriverProfile() {
        try {
            const user = authManager.getUser();
            
            // Update profile display
            document.getElementById('profileName').textContent = user.full_name || 'Driver';
            document.getElementById('profilePhone').textContent = user.phone_number || '';
            
            // Load vehicle info if available
            await this.loadVehicleInfo();
            
        } catch (error) {
            console.error('Error loading driver profile:', error);
            showToast('Failed to load profile information', 'error');
        }
    }

    async loadVehicleInfo() {
        try {
            const user = authManager.getUser();
            const response = await apiService.request(`/api/drivers/vehicle/${user.id}`);
            
            if (response.vehicle) {
                const vehicle = response.vehicle;
                const vehicleInfo = document.getElementById('vehicleInfo');
                
                vehicleInfo.innerHTML = `
                    <div class="vehicle-detail">
                        <span class="label">Registration:</span>
                        <span class="value">${vehicle.registration_number}</span>
                    </div>
                    <div class="vehicle-detail">
                        <span class="label">Vehicle:</span>
                        <span class="value">${vehicle.make} ${vehicle.model}</span>
                    </div>
                    <div class="vehicle-detail">
                        <span class="label">Color:</span>
                        <span class="value">${vehicle.color}</span>
                    </div>
                    <div class="vehicle-detail">
                        <span class="label">Insurance:</span>
                        <span class="value ${this.isInsuranceExpiring(vehicle.insurance_expiry) ? 'text-warning' : ''}">${this.formatDate(vehicle.insurance_expiry)}</span>
                    </div>
                `;

                // Pre-fill update form
                document.getElementById('vehicleRegistration').value = vehicle.registration_number;
                document.getElementById('vehicleMake').value = vehicle.make;
                document.getElementById('vehicleModel').value = vehicle.model;
                document.getElementById('vehicleColor').value = vehicle.color;
                document.getElementById('insuranceExpiry').value = vehicle.insurance_expiry;
            }
        } catch (error) {
            console.error('Error loading vehicle info:', error);
        }
    }

    async loadStats() {
        try {
            // Load earnings and ride statistics
            const earningsResponse = await apiService.getPaymentHistory();
            const ridesResponse = await apiService.getRideHistory({ driver_id: authManager.getUser().id });
            
            // Calculate today's stats
            const today = new Date().toDateString();
            const todayRides = ridesResponse.rides?.filter(ride => 
                new Date(ride.created_at).toDateString() === today && 
                ride.status === 'completed'
            ) || [];
            
            this.stats.todayRides = todayRides.length;
            this.stats.todayEarnings = todayRides.reduce((sum, ride) => sum + (ride.final_fare || 0), 0);
            
            // Calculate weekly and monthly stats
            const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
            const monthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
            
            const weekRides = ridesResponse.rides?.filter(ride => 
                new Date(ride.created_at) >= weekAgo && ride.status === 'completed'
            ) || [];
            
            const monthRides = ridesResponse.rides?.filter(ride => 
                new Date(ride.created_at) >= monthAgo && ride.status === 'completed'
            ) || [];
            
            this.stats.weekEarnings = weekRides.reduce((sum, ride) => sum + (ride.final_fare || 0), 0);
            this.stats.monthEarnings = monthRides.reduce((sum, ride) => sum + (ride.final_fare || 0), 0);
            
            // Total stats
            const completedRides = ridesResponse.rides?.filter(ride => ride.status === 'completed') || [];
            this.stats.totalRides = completedRides.length;
            this.stats.totalEarnings = completedRides.reduce((sum, ride) => sum + (ride.final_fare || 0), 0);
            
            // Load rating
            await this.loadRating();
            
            this.updateStatsDisplay();
            
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async loadRating() {
        try {
            const user = authManager.getUser();
            const response = await apiService.getRatingSummary(user.id);
            
            if (response.average_rating) {
                this.stats.avgRating = response.average_rating;
                
                // Update rating display
                const ratingStars = document.getElementById('profileRating');
                const ratingValue = document.getElementById('ratingValue');
                
                if (ratingStars && ratingValue) {
                    this.updateStarDisplay(ratingStars, response.average_rating);
                    ratingValue.textContent = response.average_rating.toFixed(1);
                }
            }
        } catch (error) {
            console.error('Error loading rating:', error);
        }
    }

    updateStatsDisplay() {
        // Update availability section stats
        document.getElementById('todayHours').textContent = this.formatHours(this.stats.todayHours);
        document.getElementById('todayRides').textContent = this.stats.todayRides;
        document.getElementById('todayEarnings').textContent = `₹${this.stats.todayEarnings}`;
        
        // Update earnings section
        document.getElementById('todayEarningsDetail').textContent = `₹${this.stats.todayEarnings}`;
        document.getElementById('todayRidesDetail').textContent = `${this.stats.todayRides} rides`;
        document.getElementById('weekEarnings').textContent = `₹${this.stats.weekEarnings}`;
        document.getElementById('monthEarnings').textContent = `₹${this.stats.monthEarnings}`;
        
        // Update profile stats
        document.getElementById('totalRides').textContent = this.stats.totalRides;
        document.getElementById('totalEarnings').textContent = `₹${this.stats.totalEarnings}`;
        document.getElementById('avgRating').textContent = this.stats.avgRating.toFixed(1);
        document.getElementById('acceptanceRate').textContent = `${this.stats.acceptanceRate}%`;
    }

    async toggleAvailability(available) {
        try {
            if (available && !this.location) {
                showToast('Getting your location...', 'info');
                await this.getCurrentLocation();
            }

            const response = await apiService.setDriverAvailability(available, this.location);
            
            this.isOnline = available;
            this.updateAvailabilityUI(available);
            
            if (available) {
                showToast('You are now online and will receive ride requests', 'success');
                this.startLocationTracking();
            } else {
                showToast('You are now offline', 'info');
                this.stopLocationTracking();
            }
            
        } catch (error) {
            console.error('Error toggling availability:', error);
            handleAPIError(error);
            
            // Reset toggle on error
            document.getElementById('availabilityToggle').checked = this.isOnline;
        }
    }

    updateAvailabilityUI(available) {
        const statusText = document.getElementById('statusText');
        const statusDescription = document.getElementById('statusDescription');
        
        if (available) {
            statusText.textContent = "You're Online";
            statusDescription.textContent = "Ready to receive ride requests";
            statusText.className = 'text-success';
        } else {
            statusText.textContent = "You're Offline";
            statusDescription.textContent = "Turn on to start receiving ride requests";
            statusText.className = '';
        }
    }

    async getCurrentLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation not supported'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.location = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    resolve(this.location);
                },
                (error) => {
                    reject(new Error('Location permission denied'));
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        });
    }

    startLocationTracking() {
        if (!this.isOnline || this.locationWatcher) return;

        this.locationWatcher = navigator.geolocation.watchPosition(
            async (position) => {
                this.location = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };

                try {
                    await apiService.updateDriverLocation(this.location);
                } catch (error) {
                    console.error('Error updating location:', error);
                }
            },
            (error) => {
                console.error('Location tracking error:', error);
            },
            { enableHighAccuracy: true, maximumAge: 30000, timeout: 15000 }
        );
    }

    stopLocationTracking() {
        if (this.locationWatcher) {
            navigator.geolocation.clearWatch(this.locationWatcher);
            this.locationWatcher = null;
        }
    }

    connectWebSocket() {
        if (this.websocket) return;

        const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
        this.websocket = new WebSocket(`${WS_CONFIG.URL}?token=${token}`);

        this.websocket.onopen = () => {
            console.log('WebSocket connected');
        };

        this.websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            // Reconnect after delay
            setTimeout(() => this.connectWebSocket(), WS_CONFIG.RECONNECT_INTERVAL);
        };

        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case WS_MESSAGE_TYPES.RIDE_REQUEST:
                this.showRideRequest(data.ride);
                break;
            case WS_MESSAGE_TYPES.RIDE_CANCEL:
                this.hideRideRequest();
                showToast('Ride request was cancelled', 'info');
                break;
            case WS_MESSAGE_TYPES.RIDE_START:
                this.handleRideStart(data.ride);
                break;
            case WS_MESSAGE_TYPES.RIDE_COMPLETE:
                this.handleRideComplete(data.ride);
                break;
            default:
                console.log('Unknown WebSocket message:', data);
        }
    }

    showRideRequest(ride) {
        this.currentRequest = ride;
        
        const requestCard = document.getElementById('rideRequestCard');
        const requestDetails = document.getElementById('rideRequestDetails');
        
        // Calculate distance and estimated earnings
        const distance = this.calculateDistance(
            this.location.latitude, this.location.longitude,
            ride.pickup_latitude, ride.pickup_longitude
        );
        
        const estimatedEarnings = Math.round(ride.estimated_fare * 0.8); // 80% to driver
        
        requestDetails.innerHTML = `
            <div class="request-info">
                <div class="pickup-location">
                    <i class="fas fa-map-marker-alt text-success"></i>
                    <div>
                        <strong>Pickup</strong>
                        <p>${ride.pickup_address}</p>
                    </div>
                </div>
                <div class="dropoff-location">
                    <i class="fas fa-flag text-danger"></i>
                    <div>
                        <strong>Destination</strong>
                        <p>${ride.dropoff_address}</p>
                    </div>
                </div>
                <div class="request-stats">
                    <div class="stat">
                        <span class="label">Distance to pickup</span>
                        <span class="value">${distance.toFixed(1)} km</span>
                    </div>
                    <div class="stat">
                        <span class="label">Estimated fare</span>
                        <span class="value">₹${ride.estimated_fare}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Your earnings</span>
                        <span class="value">₹${estimatedEarnings}</span>
                    </div>
                </div>
            </div>
        `;
        
        requestCard.style.display = 'block';
        
        // Start countdown timer
        this.startRequestTimer();
    }

    hideRideRequest() {
        const requestCard = document.getElementById('rideRequestCard');
        requestCard.style.display = 'none';
        
        this.currentRequest = null;
        this.stopRequestTimer();
    }

    startRequestTimer() {
        let timeLeft = 30;
        const timerElement = document.getElementById('requestTimer');
        
        this.requestTimer = setInterval(() => {
            timeLeft--;
            timerElement.textContent = `${timeLeft}s`;
            
            if (timeLeft <= 0) {
                this.rejectRide();
            }
        }, 1000);
    }

    stopRequestTimer() {
        if (this.requestTimer) {
            clearInterval(this.requestTimer);
            this.requestTimer = null;
        }
    }

    async acceptRide() {
        if (!this.currentRequest) return;
        
        try {
            showLoading();
            
            // Send acceptance via WebSocket
            this.websocket.send(JSON.stringify({
                type: WS_MESSAGE_TYPES.RIDE_ACCEPT,
                ride_id: this.currentRequest.id
            }));
            
            this.hideRideRequest();
            showToast('Ride accepted! Navigating to pickup location.', 'success');
            
            // Switch to current ride section
            showSection('current-ride');
            
        } catch (error) {
            console.error('Error accepting ride:', error);
            handleAPIError(error);
        } finally {
            hideLoading();
        }
    }

    async rejectRide() {
        if (!this.currentRequest) return;
        
        try {
            // Send rejection via WebSocket
            this.websocket.send(JSON.stringify({
                type: WS_MESSAGE_TYPES.RIDE_REJECT,
                ride_id: this.currentRequest.id
            }));
            
            this.hideRideRequest();
            
        } catch (error) {
            console.error('Error rejecting ride:', error);
        }
    }

    handleRideStart(ride) {
        this.currentRide = ride;
        this.showCurrentRide(ride);
        showSection('current-ride');
        showToast('Ride started! Drive safely.', 'success');
    }

    handleRideComplete(ride) {
        this.currentRide = null;
        this.hideCurrentRide();
        
        // Show rating modal
        this.showRatingModal(ride);
        
        // Update stats
        this.loadStats();
    }

    showCurrentRide(ride) {
        const noRideElement = document.getElementById('noCurrentRide');
        const rideCardElement = document.getElementById('currentRideCard');
        
        noRideElement.style.display = 'none';
        
        rideCardElement.innerHTML = `
            <div class="ride-header">
                <h3>Ride in Progress</h3>
                <span class="ride-status ${ride.status}">${ride.status.replace('_', ' ').toUpperCase()}</span>
            </div>
            
            <div class="rider-info">
                <div class="rider-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="rider-details">
                    <h4>${ride.rider_name || 'Rider'}</h4>
                    <p>${ride.rider_phone || ''}</p>
                </div>
                <button class="btn btn-outline btn-small" onclick="window.open('tel:${ride.rider_phone}')">
                    <i class="fas fa-phone"></i>
                    Call
                </button>
            </div>
            
            <div class="ride-route">
                <div class="route-point">
                    <i class="fas fa-map-marker-alt text-success"></i>
                    <div>
                        <strong>Pickup</strong>
                        <p>${ride.pickup_address}</p>
                    </div>
                </div>
                <div class="route-line"></div>
                <div class="route-point">
                    <i class="fas fa-flag text-danger"></i>
                    <div>
                        <strong>Destination</strong>
                        <p>${ride.dropoff_address}</p>
                    </div>
                </div>
            </div>
            
            <div class="ride-actions">
                ${ride.status === 'matched' ? `
                    <button class="btn btn-primary btn-large" onclick="driverDashboard.startRide()">
                        <i class="fas fa-play"></i>
                        Start Ride
                    </button>
                ` : ''}
                ${ride.status === 'in_progress' ? `
                    <button class="btn btn-success btn-large" onclick="driverDashboard.completeRide()">
                        <i class="fas fa-check"></i>
                        Complete Ride
                    </button>
                ` : ''}
                <button class="btn btn-danger btn-outline" onclick="driverDashboard.cancelCurrentRide()">
                    <i class="fas fa-times"></i>
                    Cancel Ride
                </button>
            </div>
        `;
        
        rideCardElement.style.display = 'block';
    }

    hideCurrentRide() {
        const noRideElement = document.getElementById('noCurrentRide');
        const rideCardElement = document.getElementById('currentRideCard');
        
        noRideElement.style.display = 'block';
        rideCardElement.style.display = 'none';
    }

    async startRide() {
        if (!this.currentRide) return;
        
        try {
            showLoading();
            await apiService.startRide(this.currentRide.id);
            
            this.currentRide.status = 'in_progress';
            this.showCurrentRide(this.currentRide);
            
            showToast('Ride started successfully!', 'success');
            
        } catch (error) {
            console.error('Error starting ride:', error);
            handleAPIError(error);
        } finally {
            hideLoading();
        }
    }

    async completeRide() {
        if (!this.currentRide) return;
        
        try {
            showLoading();
            
            const completionData = {
                end_latitude: this.location?.latitude,
                end_longitude: this.location?.longitude
            };
            
            await apiService.completeRide(this.currentRide.id, completionData);
            
            showToast('Ride completed successfully!', 'success');
            
        } catch (error) {
            console.error('Error completing ride:', error);
            handleAPIError(error);
        } finally {
            hideLoading();
        }
    }

    async cancelCurrentRide() {
        if (!this.currentRide) return;
        
        const reason = prompt('Please provide a reason for cancellation:');
        if (!reason) return;
        
        try {
            showLoading();
            await apiService.cancelRide(this.currentRide.id, reason);
            
            this.currentRide = null;
            this.hideCurrentRide();
            
            showToast('Ride cancelled', 'info');
            
        } catch (error) {
            console.error('Error cancelling ride:', error);
            handleAPIError(error);
        } finally {
            hideLoading();
        }
    }

    showRatingModal(ride) {
        const modal = document.getElementById('ratingModal');
        const riderInfo = document.getElementById('ratingRiderInfo');
        
        riderInfo.innerHTML = `
            <div class="rider-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="rider-details">
                <h4>${ride.rider_name || 'Rider'}</h4>
                <p>Ride completed • ₹${ride.final_fare}</p>
            </div>
        `;
        
        // Reset rating
        this.setStarRating(5);
        document.getElementById('ratingComment').value = '';
        
        modal.style.display = 'block';
        this.currentRatingRide = ride;
    }

    setStarRating(rating) {
        const stars = document.querySelectorAll('#starRating .fas');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
        this.selectedRating = rating;
    }

    async submitRating() {
        if (!this.currentRatingRide || !this.selectedRating) return;
        
        try {
            showLoading();
            
            const ratingData = {
                ride_id: this.currentRatingRide.id,
                rated_user_id: this.currentRatingRide.rider_id,
                rating: this.selectedRating,
                review: document.getElementById('ratingComment').value || null
            };
            
            await apiService.submitRating(ratingData);
            
            closeModal('ratingModal');
            showToast('Thank you for your feedback!', 'success');
            
            this.currentRatingRide = null;
            
        } catch (error) {
            console.error('Error submitting rating:', error);
            handleAPIError(error);
        } finally {
            hideLoading();
        }
    }

    async loadRideHistory() {
        try {
            const filter = document.getElementById('historyFilter')?.value || 'all';
            const date = document.getElementById('dateFilter')?.value;
            
            const params = {
                driver_id: authManager.getUser().id
            };
            
            if (filter !== 'all') {
                params.status = filter;
            }
            
            if (date) {
                params.date = date;
            }
            
            const response = await apiService.getRideHistory(params);
            this.displayRideHistory(response.rides || []);
            
        } catch (error) {
            console.error('Error loading ride history:', error);
            handleAPIError(error);
        }
    }

    displayRideHistory(rides) {
        const historyList = document.getElementById('rideHistoryList');
        
        if (rides.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-history"></i>
                    <h3>No rides found</h3>
                    <p>Your completed rides will appear here</p>
                </div>
            `;
            return;
        }
        
        historyList.innerHTML = rides.map(ride => `
            <div class="history-item">
                <div class="ride-info">
                    <div class="ride-route">
                        <div class="route-point">
                            <i class="fas fa-circle text-success"></i>
                            <span>${ride.pickup_address}</span>
                        </div>
                        <div class="route-point">
                            <i class="fas fa-circle text-danger"></i>
                            <span>${ride.dropoff_address}</span>
                        </div>
                    </div>
                    <div class="ride-meta">
                        <span class="ride-date">${this.formatDateTime(ride.created_at)}</span>
                        <span class="ride-status ${ride.status}">${ride.status.replace('_', ' ')}</span>
                    </div>
                </div>
                <div class="ride-earnings">
                    <span class="amount">₹${ride.final_fare || ride.estimated_fare}</span>
                    <span class="distance">${ride.distance_km?.toFixed(1) || '0'} km</span>
                </div>
            </div>
        `).join('');
    }

    async loadEarnings() {
        try {
            const response = await apiService.getPaymentHistory();
            this.displayPayouts(response.payouts || []);
            
        } catch (error) {
            console.error('Error loading earnings:', error);
        }
    }

    displayPayouts(payouts) {
        const payoutsList = document.getElementById('payoutsList');
        
        if (payouts.length === 0) {
            payoutsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-wallet"></i>
                    <h3>No payouts yet</h3>
                    <p>Your earnings will be processed within 24 hours</p>
                </div>
            `;
            return;
        }
        
        payoutsList.innerHTML = payouts.map(payout => `
            <div class="payout-item">
                <div class="payout-info">
                    <span class="payout-date">${this.formatDate(payout.created_at)}</span>
                    <span class="payout-rides">${payout.ride_count} rides</span>
                </div>
                <div class="payout-amount">
                    <span class="amount">₹${payout.amount}</span>
                    <span class="status ${payout.status}">${payout.status}</span>
                </div>
            </div>
        `).join('');
    }

    async updateVehicle() {
        try {
            showLoading();
            
            const vehicleData = {
                registration_number: document.getElementById('vehicleRegistration').value,
                make: document.getElementById('vehicleMake').value,
                model: document.getElementById('vehicleModel').value,
                color: document.getElementById('vehicleColor').value,
                insurance_expiry: document.getElementById('insuranceExpiry').value
            };
            
            await apiService.updateVehicle(vehicleData);
            
            closeModal('updateVehicleModal');
            showToast('Vehicle information updated successfully!', 'success');
            
            // Reload vehicle info
            await this.loadVehicleInfo();
            
        } catch (error) {
            console.error('Error updating vehicle:', error);
            handleAPIError(error);
        } finally {
            hideLoading();
        }
    }

    // Utility methods
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    formatHours(hours) {
        const h = Math.floor(hours);
        const m = Math.floor((hours - h) * 60);
        return `${h}h ${m}m`;
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString();
    }

    isInsuranceExpiring(expiryDate) {
        const expiry = new Date(expiryDate);
        const thirtyDaysFromNow = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
        return expiry <= thirtyDaysFromNow;
    }

    updateStarDisplay(container, rating) {
        const stars = container.querySelectorAll('.fas');
        const fullStars = Math.floor(rating);
        
        stars.forEach((star, index) => {
            if (index < fullStars) {
                star.className = 'fas fa-star';
            } else {
                star.className = 'far fa-star';
            }
        });
    }
}

// Global functions for HTML onclick handlers
window.showUpdateVehicleModal = function() {
    document.getElementById('updateVehicleModal').style.display = 'block';
};

window.submitRating = function() {
    driverDashboard.submitRating();
};

// Initialize driver dashboard when page loads
let driverDashboard;
document.addEventListener('DOMContentLoaded', () => {
    driverDashboard = new DriverDashboard();
});