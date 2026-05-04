# Quick Deploy Guide - Get Live in 10 Minutes

This guide will get your Ride-Hailing Platform live on the internet in about 10 minutes using Railway.

## Why Railway?

- ✅ Free tier available ($5 credit/month)
- ✅ Automatic SSL certificates
- ✅ One-click database provisioning
- ✅ GitHub integration
- ✅ Zero configuration needed
- ✅ Automatic deployments on git push

## Step-by-Step Deployment

### Step 1: Sign Up for Railway (2 minutes)

1. Go to [railway.app](https://railway.app)
2. Click "Login" and sign in with GitHub
3. Authorize Railway to access your repositories

### Step 2: Create New Project (1 minute)

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your ride-hailing-platform repository
4. Railway will automatically detect it's a Python app

### Step 3: Add Databases (2 minutes)

1. In your project dashboard, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Click "New" again
4. Select "Database" → "Add Redis"
5. (Optional) Add MongoDB if you want location data storage

Railway will automatically:
- Create the databases
- Generate connection strings
- Inject them as environment variables

### Step 4: Configure Environment Variables (3 minutes)

1. Click on your app service (not the databases)
2. Go to "Variables" tab
3. Click "Raw Editor"
4. Paste this configuration:

```env
# Required - Generate strong random keys
SECRET_KEY=your-super-secret-key-change-this-to-random-string
JWT_SECRET_KEY=your-jwt-secret-key-change-this-to-random-string

# Application Settings
APP_ENV=production
DEBUG=false
APP_NAME=Ride-Hailing Platform

# Google Maps (Get from: https://console.cloud.google.com/)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Twilio SMS (Get from: https://www.twilio.com/console)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Payment Gateway (Optional - can add later)
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
PAYTM_MERCHANT_ID=
PAYTM_MERCHANT_KEY=

# City Configuration (Indore by default)
INDORE_LAT_MIN=22.6
INDORE_LAT_MAX=22.8
INDORE_LON_MIN=75.7
INDORE_LON_MAX=75.9

# Ride Matching Configuration
INITIAL_SEARCH_RADIUS_KM=5
SEARCH_RADIUS_EXPANSION_KM=2
MATCH_TIMEOUT_SECONDS=120

# Fare Configuration (in INR)
BASE_FARE=30
PER_KM_RATE=12
FARE_PROTECTION_THRESHOLD=0.20
```

**Important:** Replace these values:
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `JWT_SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `GOOGLE_MAPS_API_KEY` - Get from Google Cloud Console
- Twilio credentials - Get from Twilio Console

### Step 5: Deploy! (2 minutes)

1. Click "Deploy" or just push to your GitHub repository
2. Railway will automatically:
   - Install dependencies
   - Run database migrations
   - Start your application
3. Wait for deployment to complete (usually 1-2 minutes)

### Step 6: Get Your URL

1. Go to "Settings" tab
2. Under "Domains", you'll see your Railway URL
3. It will look like: `https://your-app-name.up.railway.app`
4. Click to open your live application!

## Verify Deployment

Test these URLs (replace with your Railway URL):

1. **Health Check:**
   ```
   https://your-app.up.railway.app/health
   ```
   Should return: `{"status": "healthy"}`

2. **API Documentation:**
   ```
   https://your-app.up.railway.app/docs
   ```
   Should show interactive API docs

3. **Web Interface:**
   ```
   https://your-app.up.railway.app/web/
   ```
   Should show the landing page

4. **Admin Panel:**
   ```
   https://your-app.up.railway.app/web/admin.html
   ```
   Should show admin dashboard

## Seed Test Data (Optional)

To add test users and rides:

1. In Railway dashboard, click on your app service
2. Click "Settings" → "Deploy"
3. Under "Custom Start Command", temporarily change to:
   ```
   alembic upgrade head && python seed_database.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Redeploy
5. After deployment, change it back to:
   ```
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

Or use Railway's shell:
1. Click "Settings" → "Deploy" → "Shell"
2. Run: `python seed_database.py`

## Add Custom Domain (Optional)

1. Go to "Settings" → "Domains"
2. Click "Custom Domain"
3. Enter your domain (e.g., `rideconnect.com`)
4. Update your DNS records as shown
5. Railway will automatically provision SSL certificate

## Monitor Your Application

### View Logs
1. Click "Deployments" tab
2. Click on latest deployment
3. View real-time logs

### Check Metrics
1. Click "Metrics" tab
2. View CPU, Memory, Network usage

### Set Up Alerts
1. Click "Settings" → "Alerts"
2. Configure email notifications for:
   - Deployment failures
   - High resource usage
   - Application crashes

## Automatic Deployments

Railway automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway will:
1. Detect the push
2. Build your application
3. Run migrations
4. Deploy new version
5. Zero downtime!

## Cost Estimate

Railway pricing:
- **Free Tier:** $5 credit/month (enough for small projects)
- **Hobby Plan:** $5/month + usage
- **Pro Plan:** $20/month + usage

Typical monthly cost for this app:
- Small traffic: **Free** (within $5 credit)
- Medium traffic: **$10-20/month**
- High traffic: **$30-50/month**

## Troubleshooting

### Deployment Failed
1. Check logs in Railway dashboard
2. Verify all environment variables are set
3. Ensure requirements.txt is up to date

### Database Connection Error
1. Verify PostgreSQL service is running
2. Check if DATABASE_URL is automatically injected
3. Restart the application

### Application Not Responding
1. Check if port is set correctly (Railway uses $PORT)
2. Verify health check endpoint works
3. Check resource limits

### Static Files Not Loading
1. Ensure web/ directory is in repository
2. Check nginx service is running
3. Verify file paths in docker-compose.yml

## Next Steps

After deployment:

1. **Test Everything:**
   - Register a user
   - Book a test ride
   - Test payment flow
   - Check admin panel

2. **Configure Production Settings:**
   - Add real payment gateway credentials
   - Set up Twilio for SMS
   - Configure Google Maps API

3. **Set Up Monitoring:**
   - Enable error tracking (Sentry)
   - Set up uptime monitoring
   - Configure backup strategy

4. **Launch:**
   - Announce to users
   - Share your URL
   - Collect feedback

## Support

Need help?

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Project Issues:** GitHub Issues

## Alternative: One-Command Deploy

If you have Railway CLI installed:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up

# Open in browser
railway open
```

That's it! Your ride-hailing platform is now live! 🎉

---

**Pro Tips:**

1. **Generate Strong Keys:**
   ```bash
   # On Linux/Mac
   openssl rand -hex 32
   
   # On Windows (PowerShell)
   -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
   ```

2. **Monitor Costs:**
   - Check Railway dashboard regularly
   - Set up billing alerts
   - Optimize resource usage

3. **Backup Strategy:**
   - Railway auto-backs up databases
   - Export data regularly
   - Keep local backups

4. **Security:**
   - Never commit .env files
   - Rotate keys regularly
   - Use strong passwords
   - Enable 2FA on Railway account

---

**Estimated Time:** 10 minutes
**Difficulty:** Easy
**Cost:** Free tier available
