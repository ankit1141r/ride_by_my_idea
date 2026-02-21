// API Configuration
const API_CONFIG = {
    BASE_URL: window.location.origin || 'http://192.168.1.3:8001',
    ENDPOINTS: {
        // Authentication
        REGISTER: '/api/auth/register',
        LOGIN: '/api/auth/login',
        VERIFY_SEND: '/api/auth/verify/send',
        VERIFY_CONFIRM: '/api/auth/verify/confirm',
        
        // Rides
        RIDE_REQUEST: '/api/rides/request',
        RIDE_HISTORY: '/api/rides/history',
        RIDE_DETAILS: '/api/rides',
        RIDE_START: '/api/rides/{id}/start',
        RIDE_COMPLETE: '/api/rides/{id}/complete',
        RIDE_CANCEL: '/api/rides/{id}/cancel',
        RIDE_ROUTE: '/api/rides/{id}/route',
        
        // Drivers
        DRIVER_AVAILABILITY: '/api/drivers/availability',
        DRIVER_VEHICLE: '/api/drivers/vehicle',
        
        // Payments
        PAYMENT_PROCESS: '/api/payments/process',
        PAYMENT_HISTORY: '/api/payments/history',
        
        // Ratings
        RATING_SUBMIT: '/api/ratings',
        RATING_SUMMARY: '/api/ratings/summary',
        
        // Emergency
        EMERGENCY_CONTACTS: '/api/users/emergency-contacts',
        EMERGENCY_ALERT: '/api/rides/{id}/emergency',
        RIDE_SHARE: '/api/rides/{id}/share',
        
        // System
        HEALTH: '/health',
        METRICS: '/metrics'
    }
};

// WebSocket Configuration
const WS_CONFIG = {
    URL: `ws://${window.location.host || '192.168.1.3:8001'}/ws`,
    RECONNECT_INTERVAL: 5000,
    MAX_RECONNECT_ATTEMPTS: 5
};

// App Configuration
const APP_CONFIG = {
    NAME: 'RideConnect',
    VERSION: '1.0.0',
    GOOGLE_MAPS_API_KEY: '', // Add your Google Maps API key here
    INDORE_BOUNDS: {
        LAT_MIN: 22.6,
        LAT_MAX: 22.8,
        LON_MIN: 75.7,
        LON_MAX: 75.9
    },
    DEFAULT_LOCATION: {
        latitude: 22.7196,
        longitude: 75.8577,
        address: 'Rajwada, Indore'
    },
    FARE_CONFIG: {
        BASE_FARE: 30,
        PER_KM_RATE: 12,
        CURRENCY: '₹'
    }
};

// Local Storage Keys
const STORAGE_KEYS = {
    ACCESS_TOKEN: 'rideconnect_token',
    USER_DATA: 'rideconnect_user',
    USER_TYPE: 'rideconnect_user_type',
    LAST_LOCATION: 'rideconnect_last_location'
};

// Event Types
const EVENT_TYPES = {
    USER_LOGGED_IN: 'user_logged_in',
    USER_LOGGED_OUT: 'user_logged_out',
    RIDE_REQUESTED: 'ride_requested',
    RIDE_MATCHED: 'ride_matched',
    RIDE_STARTED: 'ride_started',
    RIDE_COMPLETED: 'ride_completed',
    LOCATION_UPDATED: 'location_updated'
};

// WebSocket Message Types
const WS_MESSAGE_TYPES = {
    RIDE_REQUEST: 'ride_request',
    RIDE_MATCH: 'ride_match',
    RIDE_ACCEPT: 'ride_accept',
    RIDE_REJECT: 'ride_reject',
    LOCATION_UPDATE: 'location_update',
    DRIVER_ARRIVAL: 'driver_arrival',
    RIDE_START: 'ride_start',
    RIDE_COMPLETE: 'ride_complete'
};

// Validation Patterns
const VALIDATION = {
    PHONE: /^\+91[6-9]\d{9}$/,
    EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    LICENSE: /^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{7}$/,
    VEHICLE_REG: /^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$/
};

// Error Messages
const ERROR_MESSAGES = {
    NETWORK_ERROR: 'Network error. Please check your connection.',
    INVALID_CREDENTIALS: 'Invalid phone number or password.',
    PHONE_EXISTS: 'Phone number already registered.',
    INVALID_PHONE: 'Please enter a valid Indian phone number.',
    INVALID_EMAIL: 'Please enter a valid email address.',
    PASSWORD_TOO_SHORT: 'Password must be at least 6 characters.',
    LOCATION_PERMISSION_DENIED: 'Location permission denied. Please enable location access.',
    OUTSIDE_SERVICE_AREA: 'Service is only available in Indore city.',
    NO_DRIVERS_AVAILABLE: 'No drivers available in your area. Please try again later.'
};

// Success Messages
const SUCCESS_MESSAGES = {
    REGISTRATION_SUCCESS: 'Account created successfully! Please verify your phone number.',
    LOGIN_SUCCESS: 'Welcome back!',
    RIDE_REQUESTED: 'Ride requested successfully. Looking for nearby drivers...',
    RIDE_CANCELLED: 'Ride cancelled successfully.',
    RATING_SUBMITTED: 'Thank you for your feedback!',
    PROFILE_UPDATED: 'Profile updated successfully.'
};