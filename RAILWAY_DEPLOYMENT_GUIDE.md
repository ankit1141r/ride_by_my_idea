# 🚂 Railway.app Deployment Guide - RideConnect

Deploy your RideConnect ride-hailing platform to Railway.app with a permanent public URL in minutes!

## 🎯 Why Railway?

- ✅ **Free Tier**: $5 free credit monthly (enough for testing)
- ✅ **Automatic HTTPS**: SSL certificates included
- ✅ **Easy Database Setup**: PostgreSQL, Redis with one click
- ✅ **GitHub Integration**: Auto-deploy on push
- ✅ **Custom Domains**: Add your own domain easily
- ✅ **Environment Variables**: Easy configuration
- ✅ **Logs & Monitoring**: Built-in observability

---

## 📋 Prerequisites

1. **GitHub Account** (to connect your repository)
2. **Railway Account** (sign up at https://railway.app)
3. **Your Code on GitHub** (push your project to GitHub)

---

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Prepare Your Repository

First, make sure your code is on GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Ready for Railway deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Railway

1. **Go to Railway**: https://railway.app
2. **Sign in** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**
6. Railway will automatically detect your Python app!

### Step 3: Add Databases

Railway will create your app, now add databases:

1. **Click "New"** in your project
2. **Select "Database" → "Add PostgreSQL"**
3. **Click "New"** again
4. **Select "Database" → "Add Redis"**

### Step 4: Configure Environment Variables

Click on your web service, go to "Variables" tab, and add:

```env
# Database (Railway provides these automatically)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Application
APP_ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Optional: External Services
GOOGLE_MAPS_API_KEY=your_google_maps_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

### Step 5: Deploy!

Railway will automatically:
- ✅ Install dependencies from `requirements.txt`
- ✅ Run database migrations
- ✅ Start your application
- ✅ Generate a public URL

**Your app will be live at**: `https://your-app-name.up.railway.app`

---

## 📁 Required Files (Already Created)

Railway needs these files in your repository root:

### 1. `railway.json` ✅ (Created)
Tells Railway how to build and run your app

### 2. `Procfile` ✅ (Created)
Defines the start command

### 3. `requirements.txt` ✅ (Already exists)
Python dependencies

### 4. `runtime.txt` ✅ (Created)
Specifies Python version

---

## 🔧 Post-Deployment Setup

### Run Database Migrations

After first deployment, run migrations:

1. Go to your service in Railway
2. Click "Settings" → "Deploy"
3. Add a "Deploy Command":
   ```bash
   alembic upgrade head && python seed_database.py
   ```

Or run manually in Railway CLI:
```bash
railway run alembic upgrade head
railway run python seed_database.py
```

### Access Your Application

Your app will be available at:
- **Main Site**: `https://your-app.up.railway.app/web/`
- **API Docs**: `https://your-app.up.railway.app/docs`
- **Health Check**: `https://your-app.up.railway.app/health`

---

## 🌐 Custom Domain (Optional)

### Add Your Own Domain

1. Go to your service settings
2. Click "Domains"
3. Click "Custom Domain"
4. Enter your domain (e.g., `rideconnect.com`)
5. Add the CNAME record to your DNS:
   ```
   CNAME: your-domain.com → your-app.up.railway.app
   ```

Railway automatically provisions SSL certificates!

---

## 📊 Monitoring & Logs

### View Logs

1. Click on your service
2. Go to "Deployments" tab
3. Click on latest deployment
4. View real-time logs

### Monitor Resources

Railway dashboard shows:
- CPU usage
- Memory usage
- Network traffic
- Request metrics

---

## 💰 Pricing

### Free Tier
- $5 credit per month
- ~500 hours of usage
- Perfect for testing and small projects

### Hobby Plan ($5/month)
- $5 credit + $5 usage
- More resources
- Better for production

### Pro Plan ($20/month)
- $20 credit included
- Priority support
- Team features

---

## 🔄 Continuous Deployment

Railway automatically redeploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push

# Railway automatically deploys! 🚀
```

---

## 🛠️ Troubleshooting

### Issue: Build Fails

**Check logs** in Railway dashboard:
- Look for missing dependencies
- Check Python version compatibility
- Verify environment variables

**Solution**: Update `requirements.txt` or `runtime.txt`

### Issue: Database Connection Error

**Check**:
- PostgreSQL service is running
- `DATABASE_URL` variable is set correctly
- Use Railway's provided connection string

**Solution**: 
```bash
# In Railway Variables tab
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Issue: App Crashes on Start

**Common causes**:
- Missing environment variables
- Database not migrated
- Port configuration

**Solution**:
```bash
# Ensure PORT is set to 8000
PORT=8000

# Run migrations
railway run alembic upgrade head
```

### Issue: Static Files Not Loading

**Check**:
- `web/` directory is in repository
- Nginx configuration (if using)
- File paths are correct

**Solution**: Railway serves static files automatically from your app

---

## 🔒 Security Checklist

Before going live:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=false` in production
- [ ] Use strong database passwords (Railway generates these)
- [ ] Enable Railway's built-in DDoS protection
- [ ] Set up custom domain with HTTPS
- [ ] Configure CORS properly in `app/main.py`
- [ ] Review and update API keys for external services
- [ ] Set up database backups (Railway Pro feature)

---

## 📱 Test Your Deployment

### 1. Health Check
```bash
curl https://your-app.up.railway.app/health
```

### 2. API Documentation
Visit: `https://your-app.up.railway.app/docs`

### 3. Web Interface
Visit: `https://your-app.up.railway.app/web/`

### 4. Test Login
Use pre-seeded accounts:
- **Rider**: +919876543210 / password123
- **Driver**: +919876543200 / password123
- **Admin**: +919999999999 / admin123

---

## 🎉 Success!

Your RideConnect platform is now live on Railway!

**Share your URL**:
- `https://your-app.up.railway.app/web/`

**Next Steps**:
1. Test all features (rides, payments, tracking)
2. Invite users to test
3. Monitor logs and performance
4. Set up custom domain (optional)
5. Configure external services (Google Maps, Twilio, etc.)

---

## 📞 Support

### Railway Documentation
- https://docs.railway.app

### Railway Discord
- https://discord.gg/railway

### Your Project Documentation
- `README.md` - Project overview
- `DEPLOYMENT.md` - General deployment guide
- `PUBLIC_DEPLOYMENT_GUIDE.md` - Public deployment options

---

## 🚀 Quick Commands Reference

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# View logs
railway logs

# Run commands in Railway environment
railway run alembic upgrade head
railway run python seed_database.py

# Open your app
railway open
```

---

**Made with ❤️ for Railway Deployment**

**Your app is now accessible from anywhere in the world! 🌍**
