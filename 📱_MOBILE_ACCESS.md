# 📱 Mobile Access - Quick Guide

## 🚀 Start Server for Mobile Access

### Windows
```bash
START_MOBILE.bat
```
(Double-click the file)

### Mac/Linux
```bash
chmod +x START_MOBILE.sh
./START_MOBILE.sh
```

### Or use Python directly
```bash
python start_mobile.py
```

---

## 📱 Access from Your Mobile

### Step 1: Connect to Same WiFi
Make sure your mobile and computer are on the **same WiFi network**.

### Step 2: Get the URL
The script will show you a URL like:
```
http://192.168.1.100:8000/web/
```

### Step 3: Open on Mobile
1. Open browser on your mobile (Chrome/Safari)
2. Type the URL shown by the script
3. Login with test credentials

---

## 🔐 Test Login

**Rider:**
- Phone: `+919876543210`
- Password: `password123`

**Driver:**
- Phone: `+919876543200`
- Password: `password123`

---

## 🔥 If It Doesn't Work

### Fix 1: Allow Python Through Firewall (Windows)

1. Search "Windows Defender Firewall"
2. Click "Allow an app through firewall"
3. Click "Change settings"
4. Find "Python" and check BOTH boxes
5. Click OK

### Fix 2: Check Same WiFi

- Computer and mobile must be on same network
- Not using mobile data
- Not using VPN

### Fix 3: Use ngrok (Works from Anywhere)

```bash
# 1. Download ngrok from https://ngrok.com/download

# 2. Start server
python start_mobile.py

# 3. In another terminal
ngrok http 8000

# 4. Use the https URL on mobile
```

---

## ✅ Quick Checklist

- [ ] Server running (`python start_mobile.py`)
- [ ] Mobile on same WiFi as computer
- [ ] Firewall allows Python
- [ ] Using correct IP address
- [ ] URL includes `:8000/web/`
- [ ] Using mobile browser (not app)

---

## 💡 Pro Tip: Add to Home Screen

### Android
1. Open URL in Chrome
2. Menu → Add to Home screen
3. Works like an app!

### iPhone
1. Open URL in Safari
2. Share → Add to Home Screen
3. Works like an app!

---

## 📚 Full Guide

For detailed troubleshooting and advanced options, see:
- **`MOBILE_ACCESS_GUIDE.md`** - Complete mobile access guide

---

## 🎉 That's It!

Your platform is now accessible from your mobile browser!

**Enjoy testing on mobile! 📱**
