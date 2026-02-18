# RideConnect Deployment Guide

This guide covers deploying the RideConnect ride-hailing platform in various environments.

## 🚀 Quick Deployment with Docker

### Prerequisites
- Docker and Docker Compose installed
- 4GB+ RAM available
- 10GB+ disk space

### 1. Clone and Deploy
```bash
git clone <repository-url>
cd ride-hailing-platform

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Access the Application
- **Web Interface**: http://localhost/web/
- **Admin Panel**: http://localhost/web/admin.html
- **API Docs**: http://localhost/docs
- **Health Check**: http://localhost/health

### 3. Test with Sample Data
The deployment automatically seeds the database with:
- 50 test users (17 drivers, 33 riders)
- 200 sample rides
- Payment transactions
- Realistic Indian locations (Indore)

## 🛠️ Manual Deployment

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- MongoDB 4+ (optional)
- Nginx (for production)

### 1. Database Setup

#### PostgreSQL
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE rideconnect;
CREATE USER rideconnect WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE rideconnect TO rideconnect;
\q
```

#### Redis
```bash
# Install and start Redis
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### MongoDB (Optional)
```bash
# Install MongoDB
sudo apt install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 2. Application Setup
```bash
# Clone repository
git clone <repository-url>
cd ride-hailing-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### 3. Environment Configuration
Edit `.env` file:

```env
# Database Configuration
DATABASE_URL=postgresql://rideconnect:your_password@localhost/rideconnect
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
SECRET_KEY=your-super-secret-app-key-change-in-production

# External Services (Optional)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
GOOGLE_MAPS_API_KEY=your_google_maps_key
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
PAYTM_MERCHANT_ID=your_paytm_merchant_id
PAYTM_MERCHANT_KEY=your_paytm_merchant_key

# Application Settings
APP_ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### 4. Database Migration and Seeding
```bash
# Run migrations
alembic upgrade head

# Seed with test data
python seed_database.py
```

### 5. Start the Application
```bash
# Production mode
python start_server.py

# Or with gunicorn for production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🌐 Production Deployment

### 1. Nginx Configuration
Create `/etc/nginx/sites-available/rideconnect`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Serve static files
    location /web/ {
        alias /path/to/ride-hailing-platform/web/;
        try_files $uri $uri/ =404;
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
    }

    # Redirect root to web interface
    location = / {
        return 301 /web/;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/rideconnect /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Systemd Service
Create `/etc/systemd/system/rideconnect.service`:

```ini
[Unit]
Description=RideConnect API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/ride-hailing-platform
Environment=PATH=/path/to/ride-hailing-platform/venv/bin
ExecStart=/path/to/ride-hailing-platform/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rideconnect
sudo systemctl start rideconnect
```

### 4. Background Jobs
Add to crontab (`sudo crontab -e`):

```bash
# Reset daily statistics at midnight
0 0 * * * /path/to/venv/bin/python /path/to/app/services/background_jobs.py reset_daily_cancellation_counts
0 0 * * * /path/to/venv/bin/python /path/to/app/services/background_jobs.py reset_daily_availability_hours

# Check insurance expiry daily at 6 AM
0 6 * * * /path/to/venv/bin/python /path/to/app/services/background_jobs.py check_insurance_expiry

# Unsuspend drivers hourly
0 * * * * /path/to/venv/bin/python /path/to/app/services/background_jobs.py unsuspend_drivers_after_24_hours

# Route deviation monitoring every 30 seconds (use systemd timer instead)
# */1 * * * * /path/to/venv/bin/python /path/to/app/services/background_jobs.py check_route_deviations
```

## ☁️ Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance
- Launch Ubuntu 20.04 LTS instance (t3.medium or larger)
- Configure security groups (ports 80, 443, 22)
- Attach Elastic IP

#### 2. RDS Database
- Create PostgreSQL RDS instance
- Configure security groups for EC2 access
- Update DATABASE_URL in .env

#### 3. ElastiCache Redis
- Create Redis cluster
- Update REDIS_URL in .env

#### 4. Application Load Balancer
- Create ALB with target group
- Configure health checks on /health
- Add SSL certificate

### Google Cloud Platform

#### 1. Compute Engine
- Create VM instance (e2-standard-2 or larger)
- Configure firewall rules

#### 2. Cloud SQL
- Create PostgreSQL instance
- Configure authorized networks

#### 3. Memorystore Redis
- Create Redis instance
- Update connection details

### Azure Deployment

#### 1. Virtual Machine
- Create Ubuntu VM (Standard_B2s or larger)
- Configure Network Security Group

#### 2. Azure Database for PostgreSQL
- Create flexible server
- Configure firewall rules

#### 3. Azure Cache for Redis
- Create Redis cache instance

## 📊 Monitoring and Logging

### 1. Application Monitoring
```bash
# Install monitoring tools
pip install prometheus-client grafana-api

# Configure metrics endpoint
# Already available at /metrics
```

### 2. Log Management
```bash
# Configure log rotation
sudo nano /etc/logrotate.d/rideconnect

/path/to/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

### 3. Health Monitoring
Set up monitoring for:
- `/health` endpoint
- Database connectivity
- Redis connectivity
- API response times
- Error rates

## 🔒 Security Checklist

### Application Security
- [ ] Change default JWT_SECRET_KEY
- [ ] Set strong SECRET_KEY
- [ ] Configure CORS origins properly
- [ ] Enable HTTPS in production
- [ ] Set up rate limiting
- [ ] Configure firewall rules

### Database Security
- [ ] Use strong database passwords
- [ ] Restrict database access to application servers
- [ ] Enable SSL for database connections
- [ ] Regular database backups
- [ ] Monitor for suspicious queries

### Infrastructure Security
- [ ] Keep OS and packages updated
- [ ] Configure fail2ban for SSH protection
- [ ] Use SSH keys instead of passwords
- [ ] Regular security audits
- [ ] Monitor system logs

## 🔄 Backup and Recovery

### Database Backup
```bash
# PostgreSQL backup
pg_dump -h localhost -U rideconnect rideconnect > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U rideconnect rideconnect | gzip > $BACKUP_DIR/rideconnect_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "rideconnect_*.sql.gz" -mtime +30 -delete
```

### Redis Backup
```bash
# Redis backup (automatic with RDB)
redis-cli BGSAVE

# Copy RDB file
cp /var/lib/redis/dump.rdb /backups/redis_$(date +%Y%m%d).rdb
```

## 🚨 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
journalctl -u rideconnect -f

# Check database connection
python -c "from app.database import engine; print('DB OK')"

# Check Redis connection
redis-cli ping
```

#### High Memory Usage
```bash
# Monitor memory
htop
free -h

# Check for memory leaks
ps aux --sort=-%mem | head
```

#### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U rideconnect -d rideconnect

# Check connection limits
SELECT * FROM pg_stat_activity;
```

#### Performance Issues
```bash
# Check API metrics
curl http://localhost:8000/metrics

# Monitor database queries
# Enable slow query logging in PostgreSQL

# Check Redis performance
redis-cli --latency
```

## 📈 Scaling

### Horizontal Scaling
1. **Load Balancer**: Distribute traffic across multiple app instances
2. **Database Read Replicas**: Scale read operations
3. **Redis Cluster**: Scale caching layer
4. **CDN**: Serve static assets globally

### Vertical Scaling
1. **Increase CPU/RAM**: Scale up server resources
2. **Database Optimization**: Add indexes, optimize queries
3. **Connection Pooling**: Optimize database connections
4. **Caching Strategy**: Implement application-level caching

## 🎯 Production Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Security measures in place

### Post-Deployment
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] WebSocket connections working
- [ ] Background jobs running
- [ ] Monitoring alerts configured
- [ ] Performance baseline established

### Ongoing Maintenance
- [ ] Regular security updates
- [ ] Database maintenance
- [ ] Log rotation configured
- [ ] Backup verification
- [ ] Performance monitoring
- [ ] Capacity planning

---

For additional support, refer to the main README.md and SYSTEM_STATUS.md files.