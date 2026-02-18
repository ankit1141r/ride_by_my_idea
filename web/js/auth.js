// Authentication Management
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.userType = null;
        this.loadUserFromStorage();
    }

    // Load user data from localStorage
    loadUserFromStorage() {
        const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
        const userType = localStorage.getItem(STORAGE_KEYS.USER_TYPE);
        const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);

        if (userData && userType && token) {
            this.currentUser = JSON.parse(userData);
            this.userType = userType;
            this.updateUIForLoggedInUser();
        }
    }

    // Check if user is logged in
    isLoggedIn() {
        return !!this.currentUser && !!localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    }

    // Get current user
    getCurrentUser() {
        return this.currentUser;
    }

    // Get user type
    getUserType() {
        return this.userType;
    }

    // Login user
    async login(phoneNumber, password) {
        try {
            const response = await apiService.login({
                phone: phoneNumber,
                password: password
            });

            this.currentUser = response.user;
            this.userType = response.user.user_type;
            
            showToast(SUCCESS_MESSAGES.LOGIN_SUCCESS);
            this.updateUIForLoggedInUser();
            
            // Redirect based on user type
            setTimeout(() => {
                this.redirectAfterLogin();
            }, 1000);
            
            return response;
        } catch (error) {
            // Extract error message properly
            let errorMessage = ERROR_MESSAGES.INVALID_CREDENTIALS;
            
            if (error instanceof Error) {
                errorMessage = error.message;
            } else if (typeof error === 'string') {
                errorMessage = error;
            } else if (error && error.message) {
                errorMessage = error.message;
            } else if (error && error.detail) {
                errorMessage = error.detail;
            }
            
            showToast(errorMessage, 'error');
            throw error;
        }
    }

    // Register user
    async register(userData) {
        try {
            // Validate data
            this.validateRegistrationData(userData);

            const response = await apiService.register(userData);
            
            // Store user data if registration includes login
            if (response.access_token) {
                apiService.setToken(response.access_token);
                localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(response.user));
                localStorage.setItem(STORAGE_KEYS.USER_TYPE, response.user.user_type);
                this.currentUser = response.user;
                this.userType = response.user.user_type;
            }
            
            showToast(SUCCESS_MESSAGES.REGISTRATION_SUCCESS);
            
            // Close register modal and redirect to dashboard
            closeModal('registerModal');
            
            // If we have a token, redirect to dashboard
            if (response.access_token) {
                setTimeout(() => {
                    this.redirectAfterLogin();
                }, 1000);
            } else {
                // Otherwise show login modal
                showLoginModal();
            }
            
            return response;
        } catch (error) {
            // Extract error message properly
            let errorMessage = ERROR_MESSAGES.NETWORK_ERROR;
            
            if (error instanceof Error) {
                errorMessage = error.message;
            } else if (typeof error === 'string') {
                errorMessage = error;
            } else if (error && error.message) {
                errorMessage = error.message;
            } else if (error && error.detail) {
                errorMessage = error.detail;
            }
            
            showToast(errorMessage, 'error');
            throw error;
        }
    }

    // Validate registration data
    validateRegistrationData(userData) {
        if (!userData.name || userData.name.trim().length < 2) {
            throw new Error('Name must be at least 2 characters long');
        }

        if (!VALIDATION.PHONE.test(userData.phone_number)) {
            throw new Error(ERROR_MESSAGES.INVALID_PHONE);
        }

        if (!VALIDATION.EMAIL.test(userData.email)) {
            throw new Error(ERROR_MESSAGES.INVALID_EMAIL);
        }

        if (!userData.password || userData.password.length < 6) {
            throw new Error(ERROR_MESSAGES.PASSWORD_TOO_SHORT);
        }

        // Driver-specific validation
        if (userData.user_type === 'driver') {
            if (!userData.license_number || userData.license_number.trim().length < 5) {
                throw new Error('License number is required for drivers');
            }

            if (!userData.vehicle_registration || userData.vehicle_registration.trim().length < 5) {
                throw new Error('Vehicle registration is required for drivers');
            }

            if (!userData.vehicle_make || !userData.vehicle_model || !userData.vehicle_color) {
                throw new Error('Vehicle details are required for drivers');
            }

            if (!userData.insurance_expiry) {
                throw new Error('Insurance expiry date is required for drivers');
            }

            // Check if insurance expiry is at least 30 days in future
            const expiryDate = new Date(userData.insurance_expiry);
            const thirtyDaysFromNow = new Date();
            thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);

            if (expiryDate < thirtyDaysFromNow) {
                throw new Error('Insurance must be valid for at least 30 days');
            }
        }
    }

    // Logout user
    logout() {
        this.currentUser = null;
        this.userType = null;
        apiService.logout();
        this.updateUIForLoggedOutUser();
        showToast('Logged out successfully');
    }

    // Update UI for logged in user
    updateUIForLoggedInUser() {
        // Hide auth buttons, show user menu
        const navMenu = document.querySelector('.nav-menu');
        if (navMenu && this.currentUser) {
            navMenu.innerHTML = `
                <a href="#" class="nav-link">Dashboard</a>
                <div class="user-menu">
                    <button class="btn btn-outline" onclick="authManager.showUserMenu()">
                        <i class="fas fa-user"></i>
                        ${this.currentUser.name}
                    </button>
                </div>
            `;
        }

        // Redirect to appropriate dashboard
        if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
            this.redirectAfterLogin();
        }
    }

    // Update UI for logged out user
    updateUIForLoggedOutUser() {
        const navMenu = document.querySelector('.nav-menu');
        if (navMenu) {
            navMenu.innerHTML = `
                <a href="#home" class="nav-link">Home</a>
                <a href="#features" class="nav-link">Features</a>
                <a href="#about" class="nav-link">About</a>
                <button class="btn btn-outline" onclick="showLoginModal()">Login</button>
                <button class="btn btn-primary" onclick="showRegisterModal()">Sign Up</button>
            `;
        }
    }

    // Show user menu
    showUserMenu() {
        // Create dropdown menu
        const existingMenu = document.querySelector('.user-dropdown');
        if (existingMenu) {
            existingMenu.remove();
            return;
        }

        const dropdown = document.createElement('div');
        dropdown.className = 'user-dropdown';
        dropdown.innerHTML = `
            <div class="dropdown-content">
                <a href="${this.userType === 'driver' ? 'driver-dashboard.html' : 'rider-dashboard.html'}">
                    <i class="fas fa-tachometer-alt"></i> Dashboard
                </a>
                <a href="#" onclick="authManager.showProfile()">
                    <i class="fas fa-user"></i> Profile
                </a>
                <a href="#" onclick="authManager.logout()">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        `;

        // Position dropdown
        const userMenu = document.querySelector('.user-menu');
        if (userMenu) {
            userMenu.appendChild(dropdown);
        }

        // Close dropdown when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closeDropdown(e) {
                if (!dropdown.contains(e.target)) {
                    dropdown.remove();
                    document.removeEventListener('click', closeDropdown);
                }
            });
        }, 100);
    }

    // Redirect after login based on user type
    redirectAfterLogin() {
        if (this.userType === 'driver') {
            window.location.href = 'driver-dashboard.html';
        } else {
            window.location.href = 'rider-dashboard.html';
        }
    }

    // Show profile modal
    showProfile() {
        // Implementation for profile modal
        console.log('Show profile modal');
    }

    // Phone verification
    async sendVerificationCode(phoneNumber) {
        try {
            await apiService.sendVerificationCode(phoneNumber);
            showToast('Verification code sent to your phone');
        } catch (error) {
            handleAPIError(error);
            throw error;
        }
    }

    async confirmVerificationCode(phoneNumber, code) {
        try {
            const response = await apiService.confirmVerificationCode(phoneNumber, code);
            showToast('Phone number verified successfully');
            return response;
        } catch (error) {
            handleAPIError(error);
            throw error;
        }
    }
}

// Create global auth manager instance
const authManager = new AuthManager();

// Modal management functions
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
}

function showRegisterModal(userType = 'rider') {
    const modal = document.getElementById('registerModal');
    modal.style.display = 'block';
    
    // Set default user type
    const userTypeButtons = modal.querySelectorAll('.user-type-btn');
    userTypeButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.type === userType) {
            btn.classList.add('active');
        }
    });
    
    // Show/hide driver fields
    toggleDriverFields(userType === 'driver');
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function toggleDriverFields(show) {
    const driverFields = document.getElementById('driverFields');
    if (driverFields) {
        driverFields.style.display = show ? 'block' : 'none';
        
        // Set required attribute on driver fields
        const inputs = driverFields.querySelectorAll('input');
        inputs.forEach(input => {
            input.required = show;
        });
    }
}

// Event listeners for auth forms
document.addEventListener('DOMContentLoaded', function() {
    // User type selector
    const userTypeButtons = document.querySelectorAll('.user-type-btn');
    userTypeButtons.forEach(button => {
        button.addEventListener('click', function() {
            userTypeButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            toggleDriverFields(this.dataset.type === 'driver');
        });
    });

    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const phoneNumber = document.getElementById('loginPhone').value;
            const password = document.getElementById('loginPassword').value;
            
            try {
                await authManager.login(phoneNumber, password);
                closeModal('loginModal');
            } catch (error) {
                // Error already handled in authManager.login
            }
        });
    }

    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const activeUserType = document.querySelector('.user-type-btn.active');
            const userType = activeUserType ? activeUserType.dataset.type : 'rider';
            
            const userData = {
                name: document.getElementById('registerName').value,
                phone_number: document.getElementById('registerPhone').value,
                email: document.getElementById('registerEmail').value,
                password: document.getElementById('registerPassword').value,
                user_type: userType
            };
            
            // Add driver-specific fields
            if (userType === 'driver') {
                userData.license_number = document.getElementById('licenseNumber').value;
                userData.vehicle_registration = document.getElementById('vehicleRegistration').value;
                userData.vehicle_make = document.getElementById('vehicleMake').value;
                userData.vehicle_model = document.getElementById('vehicleModel').value;
                userData.vehicle_color = document.getElementById('vehicleColor').value;
                userData.insurance_expiry = document.getElementById('insuranceExpiry').value;
            }
            
            try {
                await authManager.register(userData);
            } catch (error) {
                // Error already handled in authManager.register
            }
        });
    }

    // Close modals when clicking outside
    window.addEventListener('click', function(e) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });

    // Initialize auth state
    if (authManager.isLoggedIn()) {
        authManager.updateUIForLoggedInUser();
    }
});