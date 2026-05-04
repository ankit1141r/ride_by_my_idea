/**
 * Shared navigation component for all pages.
 * Injects a top nav bar with links to all panels based on login state.
 */

(function () {
    function getBasePath() {
        // Works whether served from /web/ or root
        const path = window.location.pathname;
        if (path.includes('/web/')) return '/web/';
        return './';
    }

    function currentPage() {
        return window.location.pathname.split('/').pop() || 'index.html';
    }

    function isLoggedIn() {
        return !!localStorage.getItem('rideconnect_token');
    }

    function getUserType() {
        return localStorage.getItem('rideconnect_user_type') || 'rider';
    }

    function getUserName() {
        try {
            const u = JSON.parse(localStorage.getItem('rideconnect_user') || '{}');
            return u.name || 'User';
        } catch { return 'User'; }
    }

    function logout() {
        localStorage.removeItem('rideconnect_token');
        localStorage.removeItem('rideconnect_user');
        localStorage.removeItem('rideconnect_user_type');
        window.location.href = getBasePath() + 'index.html';
    }

    function buildNav() {
        const base = getBasePath();
        const page = currentPage();
        const loggedIn = isLoggedIn();
        const userType = getUserType();

        // Don't inject on pages that already have a full dashboard nav
        const dashboardPages = ['rider-dashboard.html', 'driver-dashboard.html', 'admin.html'];
        if (dashboardPages.includes(page)) {
            // Just add a "Back to Home" link to existing navs
            addHomeLink(base);
            return;
        }

        // For index.html — update nav to show dashboard link if logged in
        if (page === 'index.html' || page === '') {
            if (loggedIn) {
                updateIndexNav(base, userType, getUserName());
            }
        }
    }

    function addHomeLink(base) {
        const nav = document.querySelector('.nav-logo');
        if (!nav) return;
        nav.style.cursor = 'pointer';
        nav.onclick = () => { window.location.href = base + 'index.html'; };
    }

    function updateIndexNav(base, userType, userName) {
        const navMenu = document.querySelector('.nav-menu');
        if (!navMenu) return;

        const dashboardUrl = userType === 'driver'
            ? base + 'driver-dashboard.html'
            : base + 'rider-dashboard.html';

        navMenu.innerHTML = `
            <a href="${base}index.html#home" class="nav-link">Home</a>
            <a href="${base}index.html#features" class="nav-link">Features</a>
            <a href="${dashboardUrl}" class="nav-link">
                <i class="fas fa-tachometer-alt"></i> My Dashboard
            </a>
            ${userType === 'driver'
                ? `<a href="${base}driver-dashboard.html" class="nav-link">Driver Panel</a>`
                : `<a href="${base}rider-dashboard.html" class="nav-link">Rider Panel</a>`
            }
            <div class="user-menu" style="position:relative;display:inline-block;">
                <button class="btn btn-outline" id="userMenuBtn">
                    <i class="fas fa-user"></i> ${userName} ▾
                </button>
                <div id="userDropdown" style="display:none;position:absolute;right:0;top:110%;background:#fff;border:1px solid #ddd;border-radius:8px;min-width:160px;box-shadow:0 4px 12px rgba(0,0,0,.1);z-index:1000;">
                    <a href="${dashboardUrl}" style="display:block;padding:10px 16px;color:#333;text-decoration:none;border-bottom:1px solid #eee;">
                        <i class="fas fa-tachometer-alt"></i> Dashboard
                    </a>
                    <a href="${base}admin.html" style="display:block;padding:10px 16px;color:#333;text-decoration:none;border-bottom:1px solid #eee;">
                        <i class="fas fa-shield-alt"></i> Admin Panel
                    </a>
                    <a href="#" onclick="window.__navLogout()" style="display:block;padding:10px 16px;color:#e74c3c;text-decoration:none;">
                        <i class="fas fa-sign-out-alt"></i> Logout
                    </a>
                </div>
            </div>
        `;

        // Toggle dropdown
        const btn = document.getElementById('userMenuBtn');
        const dropdown = document.getElementById('userDropdown');
        if (btn && dropdown) {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
            });
            document.addEventListener('click', () => { dropdown.style.display = 'none'; });
        }
    }

    // Expose logout globally
    window.__navLogout = logout;

    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', buildNav);
    } else {
        buildNav();
    }

    // Also patch dashboard nav logout buttons to use this logout
    window.addEventListener('DOMContentLoaded', function () {
        // Patch authManager.logout if it exists
        if (window.authManager) {
            const orig = window.authManager.logout.bind(window.authManager);
            window.authManager.logout = function () {
                orig();
                window.location.href = getBasePath() + 'index.html';
            };
        }
    });
})();
