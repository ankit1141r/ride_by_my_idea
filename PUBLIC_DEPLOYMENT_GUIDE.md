# 🚀 RideConnect - Public Deployment Guide

This guide will help you deploy the RideConnect ride-hailing platform publicly with its frontend accessible via browser.

## 🎯 Quick Start (Recommended)

### Option 1: Docker Deployment (Easiest - Everything Included)

**Prerequisites:**
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))

**Steps:**
```bash
# Run the deployment script
python deploy_public.py
```

That's it! The script will:
- ✅ Check Docker installation
- ✅ Build all containers (PostgreSQL, Redis, MongoDB, App, Nginx)
- ✅ Run database migrations
- ✅ Seed test data (50 users, 200 rides)
- ✅ Start all services
- ✅ Open the application in your browser

**Access URLs:**
- Main Website: http://localhost/web/
- Rider Dashboard: http://localhost/web/rider-dashboard.html
- Driver Dashboard: http://localhost/web/driver-dashboard.html
- Admin Panel: http://localhost/web/admin.html
- API Documentation: http://localhost/docs

---

### Option 2: Local Deployment (Without Docker)

**Prerequisites:**
- Python 3.8+
- PostgreSQL 12+ (running on localhost:5432)
- Redis 6+ (running on localhost:6379)
- MongoDB 4+ (optional, running on localhost:27017)

**Steps:**
```bash
# Run the local deployment script
python deploy_local.py
```

The script will:
- ✅ Check Python version
- ✅ Install dependencies
- ✅ Run migrations
- ✅ Seed database (optional)
- ✅ Start the server
- ✅ Open in browser

**Access URLs:**
- Main Website: http://localhost:8000/web/
- API Documentation: http://localhost:8000/docs

---

## 🔐 Test Accounts

After deployment, you can login with these pre-seeded accounts:

### Riders
- **Phone:** +919876543210, **Password:** password123
- **Phone:** +919876543211, **Password:** password123
- **Phone:** +919876543212, **Password:** password123

### Drivers
- **Phone:** +919876543200, **Password:** password123
- **Phone:** +919876543201, **Password:** password123
- **Phone:** +919876543202, **Password:** password123

### Admin
- **Phone:** +919999999999, **Password:** admin123

---

## 🌐 Making It Publicly Accessible

### Option A: Using ngrok (Quick & Easy)

1. **Install ngrok:**
   ```bash
   # Download from https://ngrok.com/download
   # Or use package manager
   choco install ngrok  # Windows
   brew install ngrok   # macOS
   ```

2. **Start ngrok tunnel:**
   ```bash
   # If using Docker (port 80)
   ngrok http 80
   
   # If using local deployment (port 8000)
   ngrok http 8000
   ```

3. **Share the URL:**
   ngrok will provide a public URL like: `https://abc123.ngrok.io`
   Share this URL with anyone to access your platform!

**Pros:**
- ✅ Instant public access
- ✅ HTTPS included
- ✅ No server setup needed

**Cons:**
- ⚠️ URL changes on restart (free tier)
- ⚠️ Limited bandwidth (free tier)

---

### Option B: Deploy to Cloud (Production Ready)

#### 1. Deploy to Heroku (Free Tier Available)

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create your-rideconnect-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Add Redis
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set JWT_SECRET_KEY=your-secret-key
heroku config:set SECRET_KEY=your-app-secret

# Deploy
git push heroku main

# Run migrations
heroku run alembic upgrade head

# Seed database
heroku run python seed_database.py

# Open app
heroku open
```

**Your app will be at:** `https://your-rideconnect-app.herokuapp.com`

---

#### 2. Deploy to Railway (Modern & Easy)

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Connect your repository
5. Railway will auto-detect and deploy!

**Features:**
- ✅ Automatic HTTPS
- ✅ Free tier available
- ✅ Easy database setup
- ✅ Custom domains

---

#### 3. Deploy to DigitalOcean (Full Control)

```bash
# Create a Droplet (Ubuntu 22.04)
# SSH into your server

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone your repository
git clone <your-repo-url>
cd ride-hailing-platform

# Run deployment
python deploy_public.py

# Install Nginx for reverse proxy
sudo apt install nginx

# Configure domain (optional)
# Edit /etc/nginx/sites-available/default
# Point to your droplet's IP
```

**Access via:** `http://your-droplet-ip/web/`

---

#### 4. Deploy to AWS (Enterprise Grade)

See `DEPLOYMENT.md` for detailed AWS deployment instructions including:
- EC2 instances
- RDS PostgreSQL
- ElastiCache Redis
- Application Load Balancer
- Auto-scaling groups

---

## 📊 Monitoring Your Deployment

### Check Service Status

**Docker Deployment:**
```bash
# View all services
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f nginx
```

**Local Deployment:**
```bash
# Check if server is running
curl http://localhost:8000/health

# View application logs
# (logs are printed to console)
```

### Health Endpoints

- **Health Check:** http://localhost/health
- **Metrics:** http://localhost/metrics
- **API Status:** http://localhost/docs

---

## 🛠️ Common Commands

### Docker Deployment

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose build
docker-compose up -d

# Clean everything (including data)
docker-compose down -v
```

### Local Deployment

```bash
# Start server
python deploy_local.py

# Or manually
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run migrations
alembic upgrade head

# Seed database
python seed_database.py

# Run tests
pytest
```

---

## 🔧 Troubleshooting

### Issue: Port already in use

**Docker (port 80):**
```bash
# Find process using port 80
netstat -ano | findstr :80  # Windows
lsof -i :80                 # macOS/Linux

# Stop the process or change port in docker-compose.yml
```

**Local (port 8000):**
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Or use different port
uvicorn app.main:app --port 8001
```

### Issue: Database connection failed

**Check if databases are running:**
```bash
# PostgreSQL
psql -h localhost -U rideconnect -d rideconnect

# Redis
redis-cli ping

# MongoDB
mongo --host localhost:27017
```

**Docker:** Databases start automatically
**Local:** You need to start them manually

### Issue: Frontend not loading

**Check Nginx (Docker):**
```bash
docker-compose logs nginx
```

**Check file paths:**
- Ensure `web/` directory exists
- Check `web/index.html` is present

**Browser cache:**
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito mode

### Issue: API returns 500 errors

**Check application logs:**
```bash
# Docker
docker-compose logs app

# Local
# Check console output
```

**Common causes:**
- Database not migrated: Run `alembic upgrade head`
- Missing environment variables: Check `.env` file
- External service errors: Check API keys in `.env`

---

## 🎨 Customization

### Change Branding

Edit these files:
- `web/index.html` - Main page
- `web/css/style.css` - Styling
- `web/js/config.js` - Configuration

### Change Service Area

Edit `.env`:
```env
# Change from Indore to your city
INDORE_LAT_MIN=22.6
INDORE_LAT_MAX=22.8
INDORE_LON_MIN=75.7
INDORE_LON_MAX=75.9
```

### Change Fare Rates

Edit `.env`:
```env
BASE_FARE=30.0
PER_KM_RATE=12.0
```

---

## 📱 Mobile Access

The web interface is mobile-responsive! Access from any device:

1. **Same Network:**
   - Find your computer's IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
   - Access from phone: `http://YOUR_IP/web/`

2. **Public Access:**
   - Use ngrok or cloud deployment
   - Share the public URL

---

## 🔒 Security Checklist

Before going public:

- [ ] Change `JWT_SECRET_KEY` in `.env`
- [ ] Change `SECRET_KEY` in `.env`
- [ ] Use strong database passwords
- [ ] Enable HTTPS (use ngrok or cloud provider)
- [ ] Set up rate limiting (already configured in nginx.conf)
- [ ] Configure CORS properly in `app/main.py`
- [ ] Review and update API keys for external services
- [ ] Set `DEBUG=false` in production
- [ ] Set up monitoring and logging
- [ ] Regular backups of database

---

## 📞 Support

### Documentation
- Main README: `README.md`
- Deployment Guide: `DEPLOYMENT.md`
- Implementation Status: `IMPLEMENTATION_COMPLETE.md`
- Quick Test Guide: `QUICK_TEST_GUIDE.md`

### Quick Links
- API Documentation: http://localhost/docs
- Health Check: http://localhost/health
- Admin Panel: http://localhost/web/admin.html

---

## 🎉 Success!

Your RideConnect platform is now deployed and accessible!

**Next Steps:**
1. ✅ Test the rider flow (request ride, track driver)
2. ✅ Test the driver flow (accept rides, complete trips)
3. ✅ Test scheduled rides (book for later)
4. ✅ Test parcel delivery (send packages)
5. ✅ Explore the admin panel (view analytics)

**Share your deployment:**
- Take screenshots
- Share the public URL
- Invite users to test

---

**Made with ❤️ by the RideConnect Team**
