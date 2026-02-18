# 🚀 RideConnect - Deployment Instructions

## Quick Start (Choose One Method)

### ⚡ Method 1: Simplest (No Setup Required)

Perfect for testing and demos. No Docker or database setup needed!

```bash
python deploy_simple.py
```

**What happens:**
- ✅ Creates configuration automatically
- ✅ Uses SQLite (no database installation needed)
- ✅ Starts server on http://localhost:8000
- ✅ Opens browser automatically
- ✅ Frontend accessible at http://localhost:8000/web/

**Best for:** Quick testing, demos, development

---

### 🐳 Method 2: Docker (Production-Ready)

Complete platform with all services in containers.

**Requirements:** Docker Desktop ([Download](https://www.docker.com/products/docker-desktop))

```bash
# Windows
DEPLOY_NOW.bat

# Mac/Linux
chmod +x DEPLOY_NOW.sh
./DEPLOY_NOW.sh

# Or manually
python deploy_public.py
```

**What you get:**
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ MongoDB for locations
- ✅ Nginx web server
- ✅ Pre-seeded test data
- ✅ Accessible at http://localhost/web/

**Best for:** Production deployment, full features

---

### 💻 Method 3: Local Development

For developers who want full control.

**Requirements:** Python 3.8+, PostgreSQL, Redis

```bash
python deploy_local.py
```

**Best for:** Development, customization

---

## 🌐 Make It Publicly Accessible

### Option A: ngrok (Instant Public URL)

1. **Install ngrok:** Download from [ngrok.com](https://ngrok.com/download)

2. **Start your server** (using any method above)

3. **Create tunnel:**
   ```bash
   # For simple deployment (port 8000)
   ngrok http 8000
   
   # For Docker deployment (port 80)
   ngrok http 80
   ```

4. **Share the URL:** ngrok gives you a public URL like `https://abc123.ngrok.io`

**Pros:**
- ✅ Instant public access
- ✅ HTTPS included
- ✅ Works from anywhere

**Cons:**
- ⚠️ URL changes on restart (free tier)
- ⚠️ Limited bandwidth

---

### Option B: localtunnel (Alternative to ngrok)

```bash
# Install
npm install -g localtunnel

# Create tunnel
lt --port 8000

# Or with custom subdomain
lt --port 8000 --subdomain my-rideconnect
```

---

### Option C: Cloud Deployment

#### Heroku (Free Tier)

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create my-rideconnect
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
git push heroku main
heroku open
```

#### Railway (Modern & Easy)

1. Go to [railway.app](https://railway.app)
2. Click "Deploy from GitHub"
3. Connect your repo
4. Done! Railway handles everything

#### Render (Free Tier)

1. Go to [render.com](https://render.com)
2. Click "New Web Service"
3. Connect GitHub repo
4. Deploy!

---

## 📱 Access Your Platform

After deployment, you can access:

| Page | URL (Simple) | URL (Docker) |
|------|-------------|--------------|
| Main Website | http://localhost:8000/web/ | http://localhost/web/ |
| Rider Dashboard | http://localhost:8000/web/rider-dashboard.html | http://localhost/web/rider-dashboard.html |
| Driver Dashboard | http://localhost:8000/web/driver-dashboard.html | http://localhost/web/driver-dashboard.html |
| Admin Panel | http://localhost:8000/web/admin.html | http://localhost/web/admin.html |
| API Docs | http://localhost:8000/docs | http://localhost/docs |
| Health Check | http://localhost:8000/health | http://localhost/health |

---

## 🔐 Test Accounts

After seeding the database, use these accounts:

### Riders
- Phone: `+919876543210`, Password: `password123`
- Phone: `+919876543211`, Password: `password123`
- Phone: `+919876543212`, Password: `password123`

### Drivers
- Phone: `+919876543200`, Password: `password123`
- Phone: `+919876543201`, Password: `password123`
- Phone: `+919876543202`, Password: `password123`

### Admin
- Phone: `+919999999999`, Password: `admin123`

---

## 🎯 Quick Test Flow

1. **Open the website** in your browser
2. **Login as Rider** (+919876543210 / password123)
3. **Request a ride** from one location to another
4. **Open Driver Dashboard** in another tab/window
5. **Login as Driver** (+919876543200 / password123)
6. **Accept the ride** from the driver dashboard
7. **Complete the ride** and see the full flow!

---

## 🛠️ Common Commands

### Simple Deployment

```bash
# Start server
python deploy_simple.py

# Or manually
uvicorn app.main:app --reload --port 8000
```

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart
docker-compose restart

# Rebuild after changes
docker-compose build
docker-compose up -d
```

### Database Management

```bash
# Run migrations
alembic upgrade head

# Seed test data
python seed_database.py

# Create new migration
alembic revision --autogenerate -m "description"
```

---

## 🔧 Troubleshooting

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Windows - Find process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Cannot Connect to Database

**Simple Deployment:** Uses SQLite, no setup needed

**Docker Deployment:** Databases start automatically

**Local Deployment:** Make sure PostgreSQL and Redis are running:
```bash
# Check PostgreSQL
psql -h localhost -U postgres

# Check Redis
redis-cli ping
```

### Frontend Not Loading

1. **Check if web folder exists:**
   ```bash
   dir web  # Windows
   ls web   # Mac/Linux
   ```

2. **Clear browser cache:** Ctrl+Shift+Delete

3. **Try incognito mode**

4. **Check server logs** for errors

### Module Not Found

```bash
# Install dependencies
pip install -r requirements.txt

# Or specific package
pip install fastapi uvicorn sqlalchemy
```

---

## 📊 Monitoring

### Check Service Status

```bash
# Simple deployment
curl http://localhost:8000/health

# Docker deployment
docker-compose ps
curl http://localhost/health
```

### View Logs

```bash
# Docker
docker-compose logs -f app
docker-compose logs -f nginx

# Simple deployment
# Logs appear in console
```

### Metrics

Access metrics at:
- http://localhost:8000/metrics (Simple)
- http://localhost/metrics (Docker)

---

## 🎨 Customization

### Change Port

Edit `.env`:
```env
PORT=8001
```

Or run directly:
```bash
uvicorn app.main:app --port 8001
```

### Change Service Area

Edit `.env`:
```env
# Change from Indore to your city
INDORE_LAT_MIN=22.6
INDORE_LAT_MAX=22.8
INDORE_LON_MIN=75.7
INDORE_LON_MAX=75.9
```

### Change Branding

Edit these files:
- `web/index.html` - Main page content
- `web/css/style.css` - Styling
- `web/js/config.js` - Configuration

---

## 🔒 Security for Production

Before going public:

- [ ] Change `JWT_SECRET_KEY` in `.env`
- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=false`
- [ ] Use strong database passwords
- [ ] Enable HTTPS (use ngrok or cloud provider)
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Regular backups

---

## 📚 Additional Resources

- **Full Deployment Guide:** `PUBLIC_DEPLOYMENT_GUIDE.md`
- **Implementation Status:** `IMPLEMENTATION_COMPLETE.md`
- **Quick Test Guide:** `QUICK_TEST_GUIDE.md`
- **Main README:** `README.md`

---

## 🆘 Need Help?

### Documentation
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- This Guide: `DEPLOY_README.md`

### Common Issues
- Port conflicts: Use different port
- Database errors: Check connection settings
- Frontend 404: Ensure `web/` folder exists
- Module errors: Run `pip install -r requirements.txt`

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Server starts without errors
- [ ] Can access http://localhost:8000/web/
- [ ] Can view API docs at /docs
- [ ] Health check returns OK
- [ ] Can login with test account
- [ ] Can navigate between pages
- [ ] API endpoints respond correctly

---

**🚀 Ready to deploy? Choose a method above and get started!**

**Made with ❤️ for the RideConnect Platform**
