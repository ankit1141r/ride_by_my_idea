// API Service Layer
class APIService {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token);
        } else {
            localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        }
    }

    // Get authentication headers
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    // Generic API request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(options.auth !== false),
            ...options
        };

        try {
            showLoading();
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        } finally {
            hideLoading();
        }
    }

    // Authentication APIs
    async register(userData) {
        // Format data for backend
        const formattedData = {
            name: userData.name,
            phone: userData.phone_number,
            email: userData.email,
            password: userData.password,
            user_type: userData.user_type
        };
        
        // Add driver-specific fields
        if (userData.user_type === 'driver') {
            formattedData.license_number = userData.license_number;
            formattedData.vehicle_registration = userData.vehicle_registration;
            formattedData.vehicle_make = userData.vehicle_make;
            formattedData.vehicle_model = userData.vehicle_model;
            formattedData.vehicle_color = userData.vehicle_color;
            formattedData.insurance_expiry = userData.insurance_expiry;
        }
        
        return this.request(API_CONFIG.ENDPOINTS.REGISTER, {
            method: 'POST',
            body: JSON.stringify(formattedData),
            auth: false
        });
    }

    async login(credentials) {
        const response = await this.request(API_CONFIG.ENDPOINTS.LOGIN, {
            method: 'POST',
            body: JSON.stringify(credentials),
            auth: false
        });

        if (response.access_token) {
            this.setToken(response.access_token);
            localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(response.user));
            localStorage.setItem(STORAGE_KEYS.USER_TYPE, response.user.user_type);
        }

        return response;
    }

    async sendVerificationCode(phoneNumber) {
        return this.request(API_CONFIG.ENDPOINTS.VERIFY_SEND, {
            method: 'POST',
            body: JSON.stringify({ phone_number: phoneNumber }),
            auth: false
        });
    }

    async confirmVerificationCode(phoneNumber, code) {
        return this.request(API_CONFIG.ENDPOINTS.VERIFY_CONFIRM, {
            method: 'POST',
            body: JSON.stringify({ 
                phone_number: phoneNumber, 
                verification_code: code 
            }),
            auth: false
        });
    }

    // Ride APIs
    async requestRide(rideData) {
        return this.request(API_CONFIG.ENDPOINTS.RIDE_REQUEST, {
            method: 'POST',
            body: JSON.stringify(rideData)
        });
    }

    async getRideHistory(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? 
            `${API_CONFIG.ENDPOINTS.RIDE_HISTORY}?${queryString}` : 
            API_CONFIG.ENDPOINTS.RIDE_HISTORY;
        
        return this.request(endpoint);
    }

    async getRideDetails(rideId) {
        return this.request(`${API_CONFIG.ENDPOINTS.RIDE_DETAILS}/${rideId}`);
    }

    async startRide(rideId) {
        return this.request(API_CONFIG.ENDPOINTS.RIDE_START.replace('{id}', rideId), {
            method: 'POST'
        });
    }

    async completeRide(rideId, completionData) {
        return this.request(API_CONFIG.ENDPOINTS.RIDE_COMPLETE.replace('{id}', rideId), {
            method: 'POST',
            body: JSON.stringify(completionData)
        });
    }

    async cancelRide(rideId, reason = '') {
        return this.request(API_CONFIG.ENDPOINTS.RIDE_CANCEL.replace('{id}', rideId), {
            method: 'POST',
            body: JSON.stringify({ reason })
        });
    }

    async getRideRoute(rideId) {
        return this.request(API_CONFIG.ENDPOINTS.RIDE_ROUTE.replace('{id}', rideId));
    }

    // Driver APIs
    async setDriverAvailability(available, location = null) {
        const data = { available };
        if (location) {
            data.latitude = location.latitude;
            data.longitude = location.longitude;
        }

        return this.request(API_CONFIG.ENDPOINTS.DRIVER_AVAILABILITY, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async registerVehicle(vehicleData) {
        return this.request(API_CONFIG.ENDPOINTS.DRIVER_VEHICLE, {
            method: 'POST',
            body: JSON.stringify(vehicleData)
        });
    }

    async updateVehicle(vehicleData) {
        return this.request(API_CONFIG.ENDPOINTS.DRIVER_VEHICLE, {
            method: 'PUT',
            body: JSON.stringify(vehicleData)
        });
    }

    // Payment APIs
    async processPayment(paymentData) {
        return this.request(API_CONFIG.ENDPOINTS.PAYMENT_PROCESS, {
            method: 'POST',
            body: JSON.stringify(paymentData)
        });
    }

    async getPaymentHistory() {
        return this.request(API_CONFIG.ENDPOINTS.PAYMENT_HISTORY);
    }

    // Rating APIs
    async submitRating(ratingData) {
        return this.request(API_CONFIG.ENDPOINTS.RATING_SUBMIT, {
            method: 'POST',
            body: JSON.stringify(ratingData)
        });
    }

    async getRatingSummary(userId) {
        return this.request(API_CONFIG.ENDPOINTS.RATING_SUMMARY.replace('{user_id}', userId));
    }

    // Emergency APIs
    async getEmergencyContacts() {
        return this.request(API_CONFIG.ENDPOINTS.EMERGENCY_CONTACTS);
    }

    async addEmergencyContact(contactData) {
        return this.request(API_CONFIG.ENDPOINTS.EMERGENCY_CONTACTS, {
            method: 'POST',
            body: JSON.stringify(contactData)
        });
    }

    async removeEmergencyContact(contactId) {
        return this.request(`${API_CONFIG.ENDPOINTS.EMERGENCY_CONTACTS}/${contactId}`, {
            method: 'DELETE'
        });
    }

    async triggerEmergencyAlert(rideId) {
        return this.request(API_CONFIG.ENDPOINTS.EMERGENCY_ALERT.replace('{id}', rideId), {
            method: 'POST'
        });
    }

    async shareRide(rideId) {
        return this.request(API_CONFIG.ENDPOINTS.RIDE_SHARE.replace('{id}', rideId), {
            method: 'POST'
        });
    }

    // System APIs
    async getHealth() {
        return this.request(API_CONFIG.ENDPOINTS.HEALTH, { auth: false });
    }

    async getMetrics() {
        return this.request(API_CONFIG.ENDPOINTS.METRICS, { auth: false });
    }

    // Location APIs
    async searchAddress(query) {
        return this.request(`/api/location/search`, {
            method: 'POST',
            body: JSON.stringify({ query })
        });
    }

    async validateAddress(location) {
        return this.request('/api/location/validate', {
            method: 'POST',
            body: JSON.stringify(location)
        });
    }

    async updateDriverLocation(location) {
        return this.request('/api/location/driver', {
            method: 'POST',
            body: JSON.stringify(location)
        });
    }

    // Logout
    logout() {
        this.setToken(null);
        localStorage.removeItem(STORAGE_KEYS.USER_DATA);
        localStorage.removeItem(STORAGE_KEYS.USER_TYPE);
        localStorage.removeItem(STORAGE_KEYS.LAST_LOCATION);
        
        // Redirect to home page
        window.location.href = '/';
    }
}

// Create global API service instance
const apiService = new APIService();

// Utility functions for loading states
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Toast notification system
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    container.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);

    // Remove on click
    toast.addEventListener('click', () => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    });
}

// Error handling utility
function handleAPIError(error) {
    console.error('API Error:', error);
    
    let message = ERROR_MESSAGES.NETWORK_ERROR;
    
    if (error.message) {
        if (error.message.includes('Invalid credentials')) {
            message = ERROR_MESSAGES.INVALID_CREDENTIALS;
        } else if (error.message.includes('already exists')) {
            message = ERROR_MESSAGES.PHONE_EXISTS;
        } else {
            message = error.message;
        }
    }
    
    showToast(message, 'error');
}