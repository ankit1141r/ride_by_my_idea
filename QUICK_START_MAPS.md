# Quick Start: Google Maps Autocomplete

## 🚀 Get Started in 3 Steps

### Step 1: Get Your API Key (5 minutes)

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable these APIs:
   - Maps JavaScript API
   - Places API
   - Geocoding API
4. Create credentials → API Key
5. Copy your API key

### Step 2: Add API Key (30 seconds)

Open `web/js/config.js` and add your key:

```javascript
GOOGLE_MAPS_API_KEY: 'AIzaSy...',  // Paste your key here
```

### Step 3: Test It! (1 minute)

1. Server is already running at: http://localhost:8001
2. Open: http://localhost:8001/web/rider-dashboard.html
3. Click "Book Ride"
4. Start typing in "Pickup Location" - you should see suggestions!

## ✨ What You Get

- 🔍 Real-time location suggestions as you type
- 📍 Accurate coordinates for pickup and destination
- 💰 Automatic fare calculation based on distance
- 🗺️ Reverse geocoding for "Use Current Location"
- 🎨 Beautiful styled dropdown matching your app

## 🎯 Try These Locations (Indore)

- Rajwada
- Treasure Island Mall
- Sarafa Bazaar
- Vijay Nagar
- Palasia Square

## 📱 Works On

✅ Desktop browsers
✅ Mobile browsers
✅ Tablets

## 🆓 Free Tier

Google Maps offers $200/month free credit:
- ~28,000 autocomplete requests
- ~40,000 geocoding requests

Perfect for development and testing!

## ❓ Not Working?

Check browser console (F12) for errors:
- "API key not configured" → Add key to config.js
- "Failed to load" → Check if APIs are enabled
- No suggestions → Verify internet connection

## 📚 Full Documentation

See `GOOGLE_MAPS_SETUP.md` for complete setup guide and troubleshooting.

---

**Ready to go!** Just add your API key and start typing! 🎉
