# 🚂 Railway Quick Start - 5 Minutes to Live!

## Step 1: Push to GitHub (2 minutes)

```bash
git init
git add .
git commit -m "Ready for Railway"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Step 2: Deploy to Railway (2 minutes)

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway auto-detects and deploys!

## Step 3: Add Databases (1 minute)

1. Click "New" → "Database" → "Add PostgreSQL"
2. Click "New" → "Database" → "Add Redis"

## Step 4: Set Environment Variables

Click your service → "Variables" → Add these:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SECRET_KEY=change-this-to-random-string
JWT_SECRET_KEY=change-this-to-random-string
APP_ENV=production
DEBUG=false
PORT=8000
```

## Step 5: Access Your App! 🎉

Your app is live at: `https://your-app.up.railway.app/web/`

### Test Accounts:
- **Rider**: +919876543210 / password123
- **Driver**: +919876543200 / password123
- **Admin**: +919999999999 / admin123

---

## 🔄 Update Your App

```bash
git add .
git commit -m "Update"
git push
# Railway auto-deploys!
```

---

## 📞 Need Help?

Read the full guide: `RAILWAY_DEPLOYMENT_GUIDE.md`

---

**That's it! Your ride-hailing platform is now public! 🌍**
