// Admin Panel JavaScript
class AdminPanel {
    constructor() {
        this.currentSection = 'dashboard';
        this.refreshInterval = null;
        
        this.init();
    }

    async init() {
        // Check authentication - admin access only
        if (!authManager.isAuthenticated()) {
            window.location.href = '/';
            return;
        }

        // For demo purposes, allow any authenticated user to access admin
        // In production, you'd check for admin role
        
        this.setupEventListeners();
        await this.loadDashboardData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                if (section) {
                    this.showSection(section);
                }
            });
        });

        // Search and filters
        document.getElementById('userSearch')?.addEventListener('input', () => this.loadUsers());
        document.getElementById('userFilter')?.addEventListener('change', () => this.loadUsers());
        
        document.getElementById('driverSearch')?.addEventListener('input', () => this.loadDrivers());
        document.getElementById('driverFilter')?.addEventListener('change', () => this.loadDrivers());
        
        document.getElementById('rideSearch')?.addEventListener('input', () => this.loadRides());
        document.getElementById('rideFilter')?.addEventListener('change', () => this.loadRides());
        document.getElementById('rideDateFilter')?.addEventListener('change', () => this.loadRides());

        // Payment tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                this.showPaymentTab(tab);
            });
        });

        document.getElementById('transactionFilter')?.addEventListener('change', () => this.loadTransactions());
        document.getElementById('transactionDateFilter')?.addEventListener('change', () => this.loadTransactions());
        document.getElementById('payoutFilter')?.addEventListener('change', () => this.loadPayouts());
    }

    showSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.dashboard-section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(section).classList.add('active');

        this.currentSection = section;

        // Load section data
        switch (section) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'users':
                this.loadUsers();
                break;
            case 'drivers':
                this.loadDrivers();
                break;
            case 'rides':
                this.loadRides();
                break;
            case 'payments':
                this.loadTransactions();
                this.loadPayouts();
                break;
            case 'system':
                this.loadSystemStatus();
                break;
        }
    }

    showPaymentTab(tab) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tab).classList.add('active');
    }

    async loadDashboardData() {
        try {
            // Load overview statistics
            const [users, rides, payments] = await Promise.all([
                this.fetchUsers(),
                this.fetchRides(),
                this.fetchPayments()
            ]);

            // Calculate stats
            const totalUsers = users.length;
            const totalDrivers = users.filter(u => u.user_type === 'driver').length;
            const totalRides = rides.length;
            const totalRevenue = rides
                .filter(r => r.status === 'completed')
                .reduce((sum, r) => sum + (r.final_fare || 0), 0);

            // Today's stats
            const today = new Date().toDateString();
            const todayUsers = users.filter(u => 
                new Date(u.created_at).toDateString() === today
            ).length;
            const todayRides = rides.filter(r => 
                new Date(r.created_at).toDateString() === today
            ).length;
            const todayRevenue = rides
                .filter(r => 
                    new Date(r.created_at).toDateString() === today && 
                    r.status === 'completed'
                )
                .reduce((sum, r) => sum + (r.final_fare || 0), 0);

            // Update UI
            document.getElementById('totalUsers').textContent = totalUsers;
            document.getElementById('totalDrivers').textContent = totalDrivers;
            document.getElementById('totalRides').textContent = totalRides;
            document.getElementById('totalRevenue').textContent = `₹${totalRevenue}`;

            document.getElementById('usersChange').textContent = `+${todayUsers} today`;
            document.getElementById('driversOnline').textContent = `${Math.floor(totalDrivers * 0.3)} online`;
            document.getElementById('ridesChange').textContent = `+${todayRides} today`;
            document.getElementById('revenueChange').textContent = `+₹${todayRevenue} today`;

            // Load recent activity
            this.loadRecentActivity(rides.slice(-10));

            // Load system health
            this.loadSystemHealth();

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            showToast('Failed to load dashboard data', 'error');
        }
    }

    loadRecentActivity(recentRides) {
        const activityList = document.getElementById('recentActivity');
        
        if (recentRides.length === 0) {
            activityList.innerHTML = '<p>No recent activity</p>';
            return;
        }

        activityList.innerHTML = recentRides.map(ride => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas fa-${this.getRideIcon(ride.status)}"></i>
                </div>
                <div class="activity-content">
                    <p>Ride ${ride.status.replace('_', ' ')} - ₹${ride.final_fare || ride.estimated_fare}</p>
                    <span class="activity-time">${this.formatTimeAgo(ride.created_at)}</span>
                </div>
            </div>
        `).join('');
    }

    async loadSystemHealth() {
        try {
            const health = await apiService.getHealth();
            const metrics = await apiService.getMetrics();

            const healthContainer = document.getElementById('systemHealth');
            healthContainer.innerHTML = `
                <div class="health-item">
                    <span class="health-label">API Status</span>
                    <span class="health-status success">Online</span>
                </div>
                <div class="health-item">
                    <span class="health-label">Database</span>
                    <span class="health-status ${health.database ? 'success' : 'error'}">
                        ${health.database ? 'Connected' : 'Disconnected'}
                    </span>
                </div>
                <div class="health-item">
                    <span class="health-label">Redis</span>
                    <span class="health-status ${health.redis ? 'success' : 'error'}">
                        ${health.redis ? 'Connected' : 'Disconnected'}
                    </span>
                </div>
                <div class="health-item">
                    <span class="health-label">Uptime</span>
                    <span class="health-value">${metrics.uptime || '0s'}</span>
                </div>
            `;

        } catch (error) {
            console.error('Error loading system health:', error);
            const healthContainer = document.getElementById('systemHealth');
            healthContainer.innerHTML = '<p class="error">Failed to load system health</p>';
        }
    }

    async loadUsers() {
        try {
            const users = await this.fetchUsers();
            const search = document.getElementById('userSearch')?.value.toLowerCase() || '';
            const filter = document.getElementById('userFilter')?.value || 'all';

            let filteredUsers = users.filter(user => {
                const matchesSearch = !search || 
                    user.full_name?.toLowerCase().includes(search) ||
                    user.phone_number?.includes(search);
                
                const matchesFilter = filter === 'all' || 
                    (filter === 'rider' && user.user_type === 'rider') ||
                    (filter === 'active' && user.is_active) ||
                    (filter === 'suspended' && !user.is_active);

                return matchesSearch && matchesFilter;
            });

            this.displayUsers(filteredUsers);

        } catch (error) {
            console.error('Error loading users:', error);
            showToast('Failed to load users', 'error');
        }
    }

    displayUsers(users) {
        const tbody = document.getElementById('usersTable');
        
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No users found</td></tr>';
            return;
        }

        tbody.innerHTML = users.map(user => `
            <tr>
                <td>
                    <div class="user-info">
                        <div class="user-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div>
                            <strong>${user.full_name || 'N/A'}</strong>
                            <br><small>${user.email || 'No email'}</small>
                        </div>
                    </div>
                </td>
                <td>${user.phone_number}</td>
                <td><span class="badge ${user.user_type}">${user.user_type}</span></td>
                <td>${this.formatDate(user.created_at)}</td>
                <td>
                    <span class="status ${user.is_active ? 'active' : 'inactive'}">
                        ${user.is_active ? 'Active' : 'Suspended'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-small btn-outline" onclick="adminPanel.viewUser('${user.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-small ${user.is_active ? 'btn-warning' : 'btn-success'}" 
                            onclick="adminPanel.toggleUserStatus('${user.id}', ${!user.is_active})">
                        <i class="fas fa-${user.is_active ? 'ban' : 'check'}"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async loadDrivers() {
        try {
            const users = await this.fetchUsers();
            const drivers = users.filter(u => u.user_type === 'driver');
            
            const search = document.getElementById('driverSearch')?.value.toLowerCase() || '';
            const filter = document.getElementById('driverFilter')?.value || 'all';

            let filteredDrivers = drivers.filter(driver => {
                const matchesSearch = !search || 
                    driver.full_name?.toLowerCase().includes(search) ||
                    driver.phone_number?.includes(search);
                
                // For demo, simulate driver statuses
                const isOnline = Math.random() > 0.7;
                const matchesFilter = filter === 'all' || 
                    (filter === 'online' && isOnline) ||
                    (filter === 'offline' && !isOnline) ||
                    (filter === 'suspended' && !driver.is_active) ||
                    (filter === 'pending_verification' && Math.random() > 0.8);

                return matchesSearch && matchesFilter;
            });

            this.displayDrivers(filteredDrivers);

        } catch (error) {
            console.error('Error loading drivers:', error);
            showToast('Failed to load drivers', 'error');
        }
    }

    displayDrivers(drivers) {
        const tbody = document.getElementById('driversTable');
        
        if (drivers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No drivers found</td></tr>';
            return;
        }

        tbody.innerHTML = drivers.map(driver => {
            const isOnline = Math.random() > 0.7;
            const rating = (4 + Math.random()).toFixed(1);
            
            return `
                <tr>
                    <td>
                        <div class="user-info">
                            <div class="user-avatar">
                                <i class="fas fa-user"></i>
                            </div>
                            <div>
                                <strong>${driver.full_name || 'N/A'}</strong>
                                <br><small>ID: ${driver.id.substring(0, 8)}</small>
                            </div>
                        </div>
                    </td>
                    <td>${driver.phone_number}</td>
                    <td>
                        <div class="vehicle-info">
                            <strong>Maruti Swift</strong>
                            <br><small>MP09AB1234</small>
                        </div>
                    </td>
                    <td>
                        <div class="rating-display">
                            <span class="rating-value">${rating}</span>
                            <div class="stars">
                                ${this.generateStars(parseFloat(rating))}
                            </div>
                        </div>
                    </td>
                    <td>
                        <span class="status ${isOnline ? 'online' : 'offline'}">
                            ${isOnline ? 'Online' : 'Offline'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-small btn-outline" onclick="adminPanel.viewDriver('${driver.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-small ${driver.is_active ? 'btn-warning' : 'btn-success'}" 
                                onclick="adminPanel.toggleDriverStatus('${driver.id}', ${!driver.is_active})">
                            <i class="fas fa-${driver.is_active ? 'ban' : 'check'}"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    async loadRides() {
        try {
            const rides = await this.fetchRides();
            const search = document.getElementById('rideSearch')?.value.toLowerCase() || '';
            const filter = document.getElementById('rideFilter')?.value || 'all';
            const date = document.getElementById('rideDateFilter')?.value;

            let filteredRides = rides.filter(ride => {
                const matchesSearch = !search || 
                    ride.id.toLowerCase().includes(search) ||
                    ride.pickup_address?.toLowerCase().includes(search) ||
                    ride.dropoff_address?.toLowerCase().includes(search);
                
                const matchesFilter = filter === 'all' || ride.status === filter;
                
                const matchesDate = !date || 
                    new Date(ride.created_at).toDateString() === new Date(date).toDateString();

                return matchesSearch && matchesFilter && matchesDate;
            });

            this.displayRides(filteredRides);

        } catch (error) {
            console.error('Error loading rides:', error);
            showToast('Failed to load rides', 'error');
        }
    }

    displayRides(rides) {
        const tbody = document.getElementById('ridesTable');
        
        if (rides.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No rides found</td></tr>';
            return;
        }

        tbody.innerHTML = rides.map(ride => `
            <tr>
                <td>
                    <strong>${ride.id.substring(0, 8)}</strong>
                    <br><small>${this.formatDateTime(ride.created_at)}</small>
                </td>
                <td>
                    <div class="user-info">
                        <strong>${ride.rider_name || 'Rider'}</strong>
                        <br><small>${ride.rider_phone || ''}</small>
                    </div>
                </td>
                <td>
                    <div class="user-info">
                        <strong>${ride.driver_name || 'Not assigned'}</strong>
                        <br><small>${ride.driver_phone || ''}</small>
                    </div>
                </td>
                <td>
                    <div class="route-info">
                        <div class="route-point">
                            <i class="fas fa-circle text-success"></i>
                            <span>${this.truncateAddress(ride.pickup_address)}</span>
                        </div>
                        <div class="route-point">
                            <i class="fas fa-circle text-danger"></i>
                            <span>${this.truncateAddress(ride.dropoff_address)}</span>
                        </div>
                    </div>
                </td>
                <td>
                    <strong>₹${ride.final_fare || ride.estimated_fare}</strong>
                    <br><small>${ride.distance_km?.toFixed(1) || '0'} km</small>
                </td>
                <td>
                    <span class="status ${ride.status}">${ride.status.replace('_', ' ')}</span>
                </td>
                <td>
                    <button class="btn btn-small btn-outline" onclick="adminPanel.viewRide('${ride.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async loadTransactions() {
        try {
            // For demo, generate sample transactions
            const transactions = this.generateSampleTransactions();
            const filter = document.getElementById('transactionFilter')?.value || 'all';
            const date = document.getElementById('transactionDateFilter')?.value;

            let filteredTransactions = transactions.filter(transaction => {
                const matchesFilter = filter === 'all' || transaction.status === filter;
                const matchesDate = !date || 
                    new Date(transaction.created_at).toDateString() === new Date(date).toDateString();

                return matchesFilter && matchesDate;
            });

            this.displayTransactions(filteredTransactions);

        } catch (error) {
            console.error('Error loading transactions:', error);
            showToast('Failed to load transactions', 'error');
        }
    }

    displayTransactions(transactions) {
        const tbody = document.getElementById('transactionsTable');
        
        if (transactions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No transactions found</td></tr>';
            return;
        }

        tbody.innerHTML = transactions.map(transaction => `
            <tr>
                <td>
                    <strong>${transaction.id}</strong>
                    <br><small>${transaction.gateway_transaction_id}</small>
                </td>
                <td>
                    <strong>${transaction.ride_id.substring(0, 8)}</strong>
                </td>
                <td>
                    <strong>₹${transaction.amount}</strong>
                </td>
                <td>
                    <span class="badge ${transaction.gateway}">${transaction.gateway}</span>
                </td>
                <td>
                    <span class="status ${transaction.status}">${transaction.status}</span>
                </td>
                <td>${this.formatDateTime(transaction.created_at)}</td>
                <td>
                    <button class="btn btn-small btn-outline" onclick="adminPanel.viewTransaction('${transaction.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async loadPayouts() {
        try {
            // For demo, generate sample payouts
            const payouts = this.generateSamplePayouts();
            const filter = document.getElementById('payoutFilter')?.value || 'all';

            let filteredPayouts = payouts.filter(payout => {
                return filter === 'all' || payout.status === filter;
            });

            this.displayPayouts(filteredPayouts);

        } catch (error) {
            console.error('Error loading payouts:', error);
            showToast('Failed to load payouts', 'error');
        }
    }

    displayPayouts(payouts) {
        const tbody = document.getElementById('payoutsTable');
        
        if (payouts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No payouts found</td></tr>';
            return;
        }

        tbody.innerHTML = payouts.map(payout => `
            <tr>
                <td>
                    <div class="user-info">
                        <strong>${payout.driver_name}</strong>
                        <br><small>${payout.driver_phone}</small>
                    </div>
                </td>
                <td>
                    <strong>${payout.period}</strong>
                </td>
                <td>
                    <strong>${payout.ride_count}</strong>
                </td>
                <td>
                    <strong>₹${payout.amount}</strong>
                </td>
                <td>
                    <span class="status ${payout.status}">${payout.status}</span>
                </td>
                <td>
                    <button class="btn btn-small btn-outline" onclick="adminPanel.processPayout('${payout.id}')">
                        <i class="fas fa-credit-card"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async loadSystemStatus() {
        try {
            const [health, metrics] = await Promise.all([
                apiService.getHealth(),
                apiService.getMetrics()
            ]);

            // Database status
            const databaseStatus = document.getElementById('databaseStatus');
            databaseStatus.innerHTML = `
                <div class="status-item">
                    <span class="status-label">PostgreSQL</span>
                    <span class="status-indicator ${health.database ? 'success' : 'error'}"></span>
                </div>
                <div class="status-item">
                    <span class="status-label">Redis</span>
                    <span class="status-indicator ${health.redis ? 'success' : 'error'}"></span>
                </div>
                <div class="status-item">
                    <span class="status-label">MongoDB</span>
                    <span class="status-indicator success"></span>
                </div>
            `;

            // Services status
            const servicesStatus = document.getElementById('servicesStatus');
            servicesStatus.innerHTML = `
                <div class="status-item">
                    <span class="status-label">Twilio SMS</span>
                    <span class="status-indicator success"></span>
                </div>
                <div class="status-item">
                    <span class="status-label">Google Maps</span>
                    <span class="status-indicator success"></span>
                </div>
                <div class="status-item">
                    <span class="status-label">Razorpay</span>
                    <span class="status-indicator success"></span>
                </div>
                <div class="status-item">
                    <span class="status-label">Paytm</span>
                    <span class="status-indicator success"></span>
                </div>
            `;

            // Performance metrics
            const performanceMetrics = document.getElementById('performanceMetrics');
            performanceMetrics.innerHTML = `
                <div class="metric-item">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value">${metrics.uptime || '0s'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Total Requests</span>
                    <span class="metric-value">${metrics.total_requests || 0}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Avg Response Time</span>
                    <span class="metric-value">${metrics.avg_response_time || '0ms'}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Error Rate</span>
                    <span class="metric-value">${metrics.error_rate || '0%'}</span>
                </div>
            `;

        } catch (error) {
            console.error('Error loading system status:', error);
            showToast('Failed to load system status', 'error');
        }
    }

    // Data fetching methods
    async fetchUsers() {
        // For demo, return sample users
        return this.generateSampleUsers();
    }

    async fetchRides() {
        // For demo, return sample rides
        return this.generateSampleRides();
    }

    async fetchPayments() {
        // For demo, return sample payments
        return this.generateSampleTransactions();
    }

    // Sample data generators
    generateSampleUsers() {
        const users = [];
        const names = ['Rahul Sharma', 'Priya Patel', 'Amit Kumar', 'Sneha Singh', 'Vikash Gupta', 'Anita Verma'];
        const phones = ['+919876543210', '+919876543211', '+919876543212', '+919876543213', '+919876543214', '+919876543215'];
        
        for (let i = 0; i < 20; i++) {
            users.push({
                id: `user_${i + 1}`,
                full_name: names[i % names.length],
                phone_number: phones[i % phones.length],
                email: `user${i + 1}@example.com`,
                user_type: i < 15 ? 'rider' : 'driver',
                is_active: Math.random() > 0.1,
                created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
            });
        }
        
        return users;
    }

    generateSampleRides() {
        const rides = [];
        const addresses = [
            'Rajwada, Indore', 'Sarafa Bazaar, Indore', 'Palasia Square, Indore',
            'Vijay Nagar, Indore', 'Bhawar Kuan, Indore', 'Treasure Island Mall, Indore'
        ];
        
        for (let i = 0; i < 50; i++) {
            const statuses = ['completed', 'in_progress', 'cancelled', 'matched', 'requested'];
            const status = statuses[Math.floor(Math.random() * statuses.length)];
            
            rides.push({
                id: `ride_${i + 1}`,
                rider_name: `Rider ${i + 1}`,
                rider_phone: `+9198765432${10 + i}`,
                driver_name: status !== 'requested' ? `Driver ${i + 1}` : null,
                driver_phone: status !== 'requested' ? `+9198765432${20 + i}` : null,
                pickup_address: addresses[Math.floor(Math.random() * addresses.length)],
                dropoff_address: addresses[Math.floor(Math.random() * addresses.length)],
                estimated_fare: 50 + Math.floor(Math.random() * 200),
                final_fare: status === 'completed' ? 50 + Math.floor(Math.random() * 200) : null,
                distance_km: 2 + Math.random() * 15,
                status: status,
                created_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
            });
        }
        
        return rides;
    }

    generateSampleTransactions() {
        const transactions = [];
        const gateways = ['razorpay', 'paytm'];
        const statuses = ['completed', 'failed', 'pending'];
        
        for (let i = 0; i < 30; i++) {
            transactions.push({
                id: `txn_${i + 1}`,
                ride_id: `ride_${i + 1}`,
                amount: 50 + Math.floor(Math.random() * 200),
                gateway: gateways[Math.floor(Math.random() * gateways.length)],
                gateway_transaction_id: `gw_${Math.random().toString(36).substring(7)}`,
                status: statuses[Math.floor(Math.random() * statuses.length)],
                created_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
            });
        }
        
        return transactions;
    }

    generateSamplePayouts() {
        const payouts = [];
        const drivers = ['Amit Kumar', 'Vikash Gupta', 'Rajesh Singh', 'Suresh Patel'];
        const phones = ['+919876543220', '+919876543221', '+919876543222', '+919876543223'];
        const statuses = ['pending', 'processed', 'failed'];
        
        for (let i = 0; i < 10; i++) {
            payouts.push({
                id: `payout_${i + 1}`,
                driver_name: drivers[i % drivers.length],
                driver_phone: phones[i % phones.length],
                period: `Week ${i + 1}`,
                ride_count: 5 + Math.floor(Math.random() * 20),
                amount: 500 + Math.floor(Math.random() * 2000),
                status: statuses[Math.floor(Math.random() * statuses.length)],
                created_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
            });
        }
        
        return payouts;
    }

    // Action methods
    async viewUser(userId) {
        showToast('User details modal would open here', 'info');
    }

    async viewDriver(driverId) {
        showToast('Driver details modal would open here', 'info');
    }

    async viewRide(rideId) {
        showToast('Ride details modal would open here', 'info');
    }

    async viewTransaction(transactionId) {
        showToast('Transaction details modal would open here', 'info');
    }

    async toggleUserStatus(userId, newStatus) {
        try {
            showLoading();
            // In real implementation, make API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            showToast(`User ${newStatus ? 'activated' : 'suspended'} successfully`, 'success');
            this.loadUsers();
            
        } catch (error) {
            console.error('Error toggling user status:', error);
            showToast('Failed to update user status', 'error');
        } finally {
            hideLoading();
        }
    }

    async toggleDriverStatus(driverId, newStatus) {
        try {
            showLoading();
            // In real implementation, make API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            showToast(`Driver ${newStatus ? 'activated' : 'suspended'} successfully`, 'success');
            this.loadDrivers();
            
        } catch (error) {
            console.error('Error toggling driver status:', error);
            showToast('Failed to update driver status', 'error');
        } finally {
            hideLoading();
        }
    }

    async processPayout(payoutId) {
        try {
            showLoading();
            // In real implementation, make API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            showToast('Payout processed successfully', 'success');
            this.loadPayouts();
            
        } catch (error) {
            console.error('Error processing payout:', error);
            showToast('Failed to process payout', 'error');
        } finally {
            hideLoading();
        }
    }

    async seedDatabase() {
        try {
            showLoading();
            
            // Create seed data API call
            const response = await fetch(`${API_CONFIG.BASE_URL}/api/admin/seed`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                showToast('Database seeded with test data successfully!', 'success');
                this.loadDashboardData();
            } else {
                throw new Error('Failed to seed database');
            }
            
        } catch (error) {
            console.error('Error seeding database:', error);
            showToast('Failed to seed database. Creating sample data locally.', 'warning');
            
            // For demo, just refresh the data
            this.loadDashboardData();
        } finally {
            hideLoading();
        }
    }

    async clearCache() {
        try {
            showLoading();
            // In real implementation, make API call to clear Redis cache
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            showToast('Cache cleared successfully', 'success');
            
        } catch (error) {
            console.error('Error clearing cache:', error);
            showToast('Failed to clear cache', 'error');
        } finally {
            hideLoading();
        }
    }

    async exportData() {
        try {
            showLoading();
            
            // Generate CSV data
            const users = await this.fetchUsers();
            const rides = await this.fetchRides();
            
            const csvData = this.generateCSV(users, rides);
            this.downloadCSV(csvData, 'rideconnect_data.csv');
            
            showToast('Data exported successfully', 'success');
            
        } catch (error) {
            console.error('Error exporting data:', error);
            showToast('Failed to export data', 'error');
        } finally {
            hideLoading();
        }
    }

    generateCSV(users, rides) {
        let csv = 'Type,ID,Name,Phone,Status,Created\n';
        
        users.forEach(user => {
            csv += `User,${user.id},${user.full_name},${user.phone_number},${user.is_active ? 'Active' : 'Inactive'},${user.created_at}\n`;
        });
        
        rides.forEach(ride => {
            csv += `Ride,${ride.id},${ride.rider_name},${ride.rider_phone},${ride.status},${ride.created_at}\n`;
        });
        
        return csv;
    }

    downloadCSV(csvData, filename) {
        const blob = new Blob([csvData], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    startAutoRefresh() {
        // Refresh dashboard data every 30 seconds
        this.refreshInterval = setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboardData();
            }
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    // Utility methods
    getRideIcon(status) {
        const icons = {
            'requested': 'clock',
            'matched': 'handshake',
            'in_progress': 'car',
            'completed': 'check-circle',
            'cancelled': 'times-circle'
        };
        return icons[status] || 'question-circle';
    }

    generateStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        let stars = '';
        
        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star"></i>';
        }
        
        if (hasHalfStar) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        }
        
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        for (let i = 0; i < emptyStars; i++) {
            stars += '<i class="far fa-star"></i>';
        }
        
        return stars;
    }

    truncateAddress(address) {
        return address && address.length > 30 ? address.substring(0, 30) + '...' : address;
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString();
    }

    formatTimeAgo(dateString) {
        const now = new Date();
        const date = new Date(dateString);
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${diffDays}d ago`;
    }
}

// Initialize admin panel when page loads
let adminPanel;
document.addEventListener('DOMContentLoaded', () => {
    adminPanel = new AdminPanel();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (adminPanel) {
        adminPanel.stopAutoRefresh();
    }
});