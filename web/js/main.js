// Main application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
    
    // Set up navigation
    setupNavigation();
    
    // Set up smooth scrolling
    setupSmoothScrolling();
    
    // Load statistics
    loadStatistics();
    
    // Set up mobile menu
    setupMobileMenu();
    
    // Set up scroll animations
    setupScrollAnimations();
    
    // Add particle effects
    addParticleEffects();
});

// Initialize application
function initializeApp() {
    console.log('RideConnect Web App Initialized');
    
    // Check API health
    checkAPIHealth();
    
    // Load user session if exists
    if (authManager.isLoggedIn()) {
        console.log('User logged in:', authManager.getCurrentUser());
    }
}

// Check API health
async function checkAPIHealth() {
    try {
        const health = await apiService.getHealth();
        console.log('API Health:', health);
        
        if (health.status !== 'healthy') {
            showToast('Backend service is not fully operational', 'warning');
        }
    } catch (error) {
        console.error('API Health Check Failed:', error);
        showToast('Unable to connect to backend service', 'error');
    }
}

// Setup navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Handle internal navigation
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

// Setup smooth scrolling
function setupSmoothScrolling() {
    // Add smooth scrolling to all anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const targetId = href.substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80; // Account for fixed navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Load statistics from API
async function loadStatistics() {
    try {
        const metrics = await apiService.getMetrics();
        
        // Update counters with animation
        animateCounter('rideCount', 1000);
        animateCounter('driverCount', 50);
        animateCounter('userCount', 500);
        
    } catch (error) {
        console.error('Failed to load statistics:', error);
        // Use default values if API fails
    }
}

// Animate counter numbers
function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const duration = 2000; // 2 seconds
    const startValue = 0;
    const increment = targetValue / (duration / 16); // 60 FPS
    let currentValue = startValue;
    
    const timer = setInterval(() => {
        currentValue += increment;
        
        if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(timer);
        }
        
        element.textContent = Math.floor(currentValue) + '+';
    }, 16);
}

// Setup mobile menu
function setupMobileMenu() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
        
        // Close menu when clicking on a link
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
    }
}

// Utility functions
function formatCurrency(amount) {
    return `${APP_CONFIG.FARE_CONFIG.CURRENCY}${amount}`;
}

function formatDistance(distance) {
    return `${distance.toFixed(1)} km`;
}

function formatTime(minutes) {
    if (minutes < 60) {
        return `${minutes} min`;
    } else {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours}h ${mins}m`;
    }
}

function formatPhoneNumber(phone) {
    // Format +919876543210 to +91 98765 43210
    if (phone.startsWith('+91')) {
        const number = phone.substring(3);
        return `+91 ${number.substring(0, 5)} ${number.substring(5)}`;
    }
    return phone;
}

// Location utilities
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported'));
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            position => {
                const location = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                
                // Check if location is within Indore bounds
                if (isLocationInIndore(location)) {
                    resolve(location);
                } else {
                    reject(new Error(ERROR_MESSAGES.OUTSIDE_SERVICE_AREA));
                }
            },
            error => {
                let message = ERROR_MESSAGES.LOCATION_PERMISSION_DENIED;
                
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        message = ERROR_MESSAGES.LOCATION_PERMISSION_DENIED;
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message = 'Location information is unavailable';
                        break;
                    case error.TIMEOUT:
                        message = 'Location request timed out';
                        break;
                }
                
                reject(new Error(message));
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutes
            }
        );
    });
}

function isLocationInIndore(location) {
    const bounds = APP_CONFIG.INDORE_BOUNDS;
    return (
        location.latitude >= bounds.LAT_MIN &&
        location.latitude <= bounds.LAT_MAX &&
        location.longitude >= bounds.LON_MIN &&
        location.longitude <= bounds.LON_MAX
    );
}

// WebSocket connection management
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = WS_CONFIG.MAX_RECONNECT_ATTEMPTS;
        this.reconnectInterval = WS_CONFIG.RECONNECT_INTERVAL;
        this.messageHandlers = new Map();
    }
    
    connect() {
        if (!authManager.isLoggedIn()) {
            console.log('User not logged in, skipping WebSocket connection');
            return;
        }
        
        const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
        const wsUrl = `${WS_CONFIG.URL}?token=${token}`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                showToast('Connected to real-time service', 'success');
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.log('Max reconnection attempts reached');
            showToast('Lost connection to real-time service', 'error');
        }
    }
    
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.error('WebSocket not connected');
        }
    }
    
    handleMessage(message) {
        console.log('WebSocket message received:', message);
        
        const handler = this.messageHandlers.get(message.type);
        if (handler) {
            handler(message);
        } else {
            console.log('No handler for message type:', message.type);
        }
    }
    
    addMessageHandler(type, handler) {
        this.messageHandlers.set(type, handler);
    }
    
    removeMessageHandler(type) {
        this.messageHandlers.delete(type);
    }
}

// Create global WebSocket manager
const wsManager = new WebSocketManager();

// Initialize WebSocket connection when user logs in
document.addEventListener(EVENT_TYPES.USER_LOGGED_IN, () => {
    wsManager.connect();
});

// Disconnect WebSocket when user logs out
document.addEventListener(EVENT_TYPES.USER_LOGGED_OUT, () => {
    wsManager.disconnect();
});

// Add CSS for mobile menu and user dropdown
const additionalCSS = `
.nav-menu.active {
    display: flex;
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    background: white;
    flex-direction: column;
    padding: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.nav-toggle.active span:nth-child(1) {
    transform: rotate(-45deg) translate(-5px, 6px);
}

.nav-toggle.active span:nth-child(2) {
    opacity: 0;
}

.nav-toggle.active span:nth-child(3) {
    transform: rotate(45deg) translate(-5px, -6px);
}

.user-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    z-index: 1000;
}

.dropdown-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    padding: 0.5rem 0;
    min-width: 200px;
}

.dropdown-content a {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    color: #374151;
    text-decoration: none;
    transition: background 0.2s ease;
}

.dropdown-content a:hover {
    background: #f3f4f6;
}

@media (max-width: 768px) {
    .nav-menu {
        display: none;
    }
}
`;

// Add the CSS to the document
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);


// Setup scroll animations
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Observe all elements with fade-in-scroll class
    const animatedElements = document.querySelectorAll('.fade-in-scroll');
    animatedElements.forEach(el => observer.observe(el));
}

// Add particle effects to hero section
function addParticleEffects() {
    const hero = document.querySelector('.hero');
    if (!hero) return;
    
    const particleCount = 20;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 10 + 's';
        particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
        hero.appendChild(particle);
    }
}

// Enhanced button ripple effect
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn') || e.target.closest('.btn')) {
        const button = e.target.classList.contains('btn') ? e.target : e.target.closest('.btn');
        
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        ripple.style.left = e.offsetX + 'px';
        ripple.style.top = e.offsetY + 'px';
        
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
});

// Add parallax effect to hero section
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const heroContent = document.querySelector('.hero-content');
    const heroImage = document.querySelector('.hero-image');
    
    if (heroContent) {
        heroContent.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
    
    if (heroImage) {
        heroImage.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// Add hover effect to navigation links
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.classList.add('animated-underline');
});

// Enhanced modal animations
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.classList.add('scale-in');
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.classList.remove('scale-in');
        }
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

// Add glow effect to feature icons on hover
const featureIcons = document.querySelectorAll('.feature-icon');
featureIcons.forEach(icon => {
    icon.addEventListener('mouseenter', function() {
        this.classList.add('glow-effect');
    });
    
    icon.addEventListener('mouseleave', function() {
        this.classList.remove('glow-effect');
    });
});


// Add scroll-to-top button
function addScrollToTopButton() {
    const button = document.createElement('button');
    button.className = 'scroll-to-top';
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.setAttribute('aria-label', 'Scroll to top');
    document.body.appendChild(button);
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            button.classList.add('visible');
        } else {
            button.classList.remove('visible');
        }
    });
    
    // Scroll to top on click
    button.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Add navbar scroll effect
function addNavbarScrollEffect() {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// Initialize enhanced features
document.addEventListener('DOMContentLoaded', function() {
    addScrollToTopButton();
    addNavbarScrollEffect();
});

// Add loading progress indicator
function showProgressIndicator() {
    let progress = document.querySelector('.progress-indicator');
    
    if (!progress) {
        progress = document.createElement('div');
        progress.className = 'progress-indicator';
        document.body.appendChild(progress);
    }
    
    progress.style.width = '0%';
    progress.style.display = 'block';
    
    return {
        update: (percent) => {
            progress.style.width = percent + '%';
        },
        complete: () => {
            progress.style.width = '100%';
            setTimeout(() => {
                progress.style.display = 'none';
            }, 300);
        }
    };
}

// Enhanced API calls with progress indicator
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const progressIndicator = showProgressIndicator();
    progressIndicator.update(30);
    
    return originalFetch.apply(this, args)
        .then(response => {
            progressIndicator.update(70);
            return response;
        })
        .finally(() => {
            progressIndicator.complete();
        });
};

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key closes modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block') {
                const modalId = modal.id;
                closeModal(modalId);
            }
        });
    }
    
    // Ctrl/Cmd + K for search (if implemented)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Implement search functionality
    }
});

// Add smooth reveal animations for images
function addImageRevealAnimations() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        img.style.opacity = '0';
        img.style.transform = 'scale(0.95)';
        img.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        img.addEventListener('load', function() {
            this.style.opacity = '1';
            this.style.transform = 'scale(1)';
        });
    });
}

// Initialize image animations
document.addEventListener('DOMContentLoaded', addImageRevealAnimations);

// Add performance monitoring
if ('PerformanceObserver' in window) {
    const perfObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            if (entry.entryType === 'navigation') {
                console.log('Page load time:', entry.loadEventEnd - entry.fetchStart, 'ms');
            }
        }
    });
    
    perfObserver.observe({ entryTypes: ['navigation'] });
}

// Add service worker for offline support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/sw.js')
        //     .then(registration => console.log('SW registered:', registration))
        //     .catch(error => console.log('SW registration failed:', error));
    });
}
