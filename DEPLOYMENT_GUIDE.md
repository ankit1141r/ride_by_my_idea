# 🚀 RideConnect Deployment Guide

## Overview

This guide will help you deploy RideConnect to a public website accessible to users and riders worldwide.

## Deployment Options

### Option 1: Railway.app (Recommended for Quick Start)
- **Cost**: Free tier available
- **Setup Time**: 15 minutes
- **Difficulty**: Easy
- **Best For**: Testing, MVP, small scale

### Option 2: DigitalOcean (Recommended for Production)
- **Cost**: $6/month minimum
- **Setup Time**: 1-2 hours
- **Difficulty**: Medium
- **Best For**: Production, scalable

### Option 3: AWS/Google Cloud/Azure
- **Cost**: Variable (pay as you go)
- **Setup Time**: 2-4 hours
- **Difficulty**: Advanced
- **Best For**: Enterprise, high scale

---

## 🚂 Option 1: Railway.app Deployment (Easiest)

### Prerequisites
- GitHub account
- Railway.app account (free)

### Step 1: Prepare Your Code

1. Create a `requirements.txt` file:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
```

2. Create a `Procfile`:
```
web: uvicorn simple_app:app --host 0.0.0.0 --port $PORT
```

3. Create a `runtime.txt`:
```
python-3.11.0
```

### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/rideconnect.git
git push -u origin main
```

### Step 3: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect and deploy

### Step 4: Add Database

1. In Railway dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will create and link the database

### Step 5: Set Environment Variables

In Railway dashboard, go to Variables and add:
```
DATABASE_URL=<automatically set by Railway>
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
```

### Step 6: Access Your App

Railway will provide a URL like: `https://rideconnect.up.railway.app`

**Total Time**: ~15 minutes
**Cost**: Free (with limits)

---

## 🌊 Option 2: DigitalOcean Deployment (Production Ready)

### Prerequisites
- DigitalOcean account
- Domain name (optional but recommended)
- Basic Linux knowledge

### Step 1: Create a Droplet

1. Log in to DigitalOcean
2. Click "Create" → "Droplets"
3. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month)
   - **CPU**: Regular (1GB RAM)
   - **Datacenter**: Closest to your users
4. Add SSH key (recommended)
5. Create Droplet

### Step 2: Connect to Server

```bash
ssh root@your_droplet_ip
```

### Step 3: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install python3-pip python3-venv nginx postgresql postgresql-contrib -y

# Install certbot for SSL
apt install certbot python3-certbot-nginx -y
```

### Step 4: Set Up Application

```bash
# Create app directory
mkdir -p /var/www/rideconnect
cd /var/www/rideconnect

# Clone your repository
git clone https://github.com/yourusername/rideconnect.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 5: Set Up Database

```bash
# Create database and user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE rideconnect;
CREATE USER rideconnect_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE rideconnect TO rideconnect_user;
\q
```

### Step 6: Configure Environment

Create `.env` file:
```bash
nano /var/www/rideconnect/.env
```

Add:
```
DATABASE_URL=postgresql://rideconnect_user:your_secure_password@localhost/rideconnect
SECRET_KEY=your-very-secret-key-here
ENVIRONMENT=production
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### Step 7: Set Up Systemd Service

Create service file:
```bash
nano /etc/systemd/system/rideconnect.service
```

Add:
```ini
[Unit]
Description=RideConnect FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/rideconnect
Environment="PATH=/var/www/rideconnect/venv/bin"
ExecStart=/var/www/rideconnect/venv/bin/uvicorn simple_app:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl enable rideconnect
systemctl start rideconnect
systemctl status rideconnect
```

### Step 8: Configure Nginx

Create Nginx config:
```bash
nano /etc/nginx/sites-available/rideconnect
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /web/ {
        alias /var/www/rideconnect/web/;
        try_files $uri $uri/ =404;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/rideconnect /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 9: Set Up SSL (HTTPS)

```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow prompts to:
- Enter email
- Agree to terms
- Choose to redirect HTTP to HTTPS

### Step 10: Configure Domain DNS

In your domain registrar (GoDaddy, Namecheap, etc.):

Add A records:
```
Type: A
Name: @
Value: your_droplet_ip

Type: A
Name: www
Value: your_droplet_ip
```

Wait 5-60 minutes for DNS propagation.

### Step 11: Test Deployment

Visit: `https://your-domain.com`

**Total Time**: 1-2 hours
**Cost**: $6/month + domain ($10-15/year)

---

## 🔧 Production Enhancements

### 1. Database Migration

Update `simple_app.py` to use PostgreSQL:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### 2. Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 3. JWT Authentication

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 4. Environment Configuration

Create `config.py`:
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    environment: str = "development"
    allowed_hosts: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 5. Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/rideconnect/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 6. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/auth/register")
@limiter.limit("5/minute")
async def register_user(request: Request, user: UserRegister):
    # ... registration logic
```

### 7. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8. Monitoring

Install monitoring tools:
```bash
pip install prometheus-fastapi-instrumentator
```

Add to app:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## 📱 Mobile App Considerations

### Progressive Web App (PWA)

Add `manifest.json`:
```json
{
  "name": "RideConnect",
  "short_name": "RideConnect",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#667eea",
  "theme_color": "#667eea",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

Add service worker for offline support.

### Native Apps

Consider building native apps with:
- **React Native**: Cross-platform (iOS + Android)
- **Flutter**: Cross-platform with great performance
- **Native**: Swift (iOS) + Kotlin (Android)

---

## 🔐 Security Checklist

- [ ] Use HTTPS (SSL certificate)
- [ ] Hash passwords with bcrypt
- [ ] Implement JWT authentication
- [ ] Add rate limiting
- [ ] Validate all inputs
- [ ] Use environment variables for secrets
- [ ] Enable CORS properly
- [ ] Add CSRF protection
- [ ] Implement request validation
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Monitor for suspicious activity
- [ ] Backup database regularly

---

## 📊 Monitoring & Maintenance

### Set Up Monitoring

1. **Uptime Monitoring**: UptimeRobot (free)
2. **Error Tracking**: Sentry
3. **Analytics**: Google Analytics
4. **Performance**: New Relic or DataDog

### Regular Maintenance

```bash
# Update system
apt update && apt upgrade -y

# Update Python packages
pip install --upgrade -r requirements.txt

# Backup database
pg_dump rideconnect > backup_$(date +%Y%m%d).sql

# Check logs
tail -f /var/log/rideconnect/app.log

# Monitor resources
htop
```

---

## 💰 Cost Estimation

### Railway.app (Free Tier)
- **Hosting**: Free (with limits)
- **Database**: Free (500MB)
- **Total**: $0/month

### DigitalOcean (Production)
- **Droplet**: $6/month
- **Database**: $15/month (managed)
- **Domain**: $12/year
- **Total**: ~$22/month

### AWS (Enterprise)
- **EC2**: $10-50/month
- **RDS**: $15-100/month
- **Load Balancer**: $20/month
- **Total**: $45-170/month

---

## 🎯 Next Steps

1. **Choose deployment option** based on your needs
2. **Follow the guide** for your chosen platform
3. **Test thoroughly** before going live
4. **Set up monitoring** to track performance
5. **Plan for scaling** as users grow

---

## 🆘 Troubleshooting

### Server won't start
```bash
# Check logs
journalctl -u rideconnect -n 50

# Check if port is in use
netstat -tulpn | grep 8000

# Restart service
systemctl restart rideconnect
```

### Database connection issues
```bash
# Test database connection
psql -U rideconnect_user -d rideconnect

# Check PostgreSQL status
systemctl status postgresql
```

### Nginx errors
```bash
# Test configuration
nginx -t

# Check logs
tail -f /var/log/nginx/error.log

# Restart Nginx
systemctl restart nginx
```

### SSL certificate issues
```bash
# Renew certificate
certbot renew

# Test renewal
certbot renew --dry-run
```

---

## 📞 Support

Need help with deployment? Common issues:

1. **DNS not propagating**: Wait 24-48 hours
2. **SSL certificate fails**: Check domain DNS first
3. **Database connection fails**: Verify credentials in .env
4. **502 Bad Gateway**: Check if app is running
5. **CORS errors**: Update allowed origins

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Server/hosting set up
- [ ] Database configured
- [ ] Environment variables set
- [ ] SSL certificate installed
- [ ] Domain DNS configured
- [ ] Application running
- [ ] Nginx configured
- [ ] Firewall rules set
- [ ] Monitoring enabled
- [ ] Backups configured
- [ ] Security hardened
- [ ] Performance tested
- [ ] Documentation updated

---

**Ready to deploy? Choose your option and follow the guide!** 🚀

For questions or issues, refer to the troubleshooting section or check the logs.
