# 📱 Install Apps on Your Android Device - Preview Guide

**Quick guide to install and test the RideConnect apps on your Android device before Play Store deployment.**

---

## 🎯 Quick Start (3 Simple Steps)

### Step 1: Enable Developer Options on Your Phone

1. Open **Settings** on your Android device
2. Go to **About Phone**
3. Tap **Build Number** 7 times
4. You'll see "You are now a developer!"
5. Go back to **Settings** → **Developer Options**
6. Enable **USB Debugging**

### Step 2: Connect Your Phone to Computer

**On Windows:**
```cmd
cd android-ride-hailing

REM Connect your phone via USB cable
REM Allow USB debugging when prompted on phone

REM Build and install Rider App
gradlew.bat :rider-app:installDebug

REM Build and install Driver App
gradlew.bat :driver-app:installDebug
```

**On Linux/Mac:**
```bash
cd android-ride-hailing

# Connect your phone via USB cable
# Allow USB debugging when prompted on phone

# Build and install Rider App
./gradlew :rider-app:installDebug

# Build and install Driver App
./gradlew :driver-app:installDebug
```

### Step 3: Open the Apps on Your Phone

Look for:
- **RideConnect** (Rider App) - Blue icon
- **RideConnect Driver** (Driver App) - Green icon

That's it! The apps are now installed and ready to test.

---

## 📋 Detailed Instructions

### Method 1: Direct Install via USB (Recommended)

#### Prerequisites
- Android device with Android 8.0 or higher
- USB cable
- Android Studio installed (or just Android SDK Platform Tools)

#### Step-by-Step

**1. Prepare Your Device**

Enable Developer Options:
- Settings → About Phone → Tap Build Number 7 times
- Settings → Developer Options → Enable USB Debugging
- Connect USB cable
- Allow USB debugging when prompted (check "Always allow")

**2. Verify Connection**

```cmd
REM Windows
cd android-ride-hailing
adb devices

REM You should see your device listed
REM Example output:
REM List of devices attached
REM ABC123XYZ    device
```

```bash
# Linux/Mac
cd android-ride-hailing
adb devices

# You should see your device listed
```

**3. Build and Install**

**Install Rider App:**
```cmd
REM Windows
gradlew.bat :rider-app:installDebug

REM Linux/Mac
./gradlew :rider-app:installDebug
```

**Install Driver App:**
```cmd
REM Windows
gradlew.bat :driver-app:installDebug

REM Linux/Mac
./gradlew :driver-app:installDebug
```

**4. Launch Apps**

The apps will appear in your app drawer:
- RideConnect (Rider)
- RideConnect Driver

---

### Method 2: Install APK Manually

If you prefer to install without USB connection:

#### Step 1: Build APK Files

**On Windows:**
```cmd
cd android-ride-hailing

REM Build Rider App APK
gradlew.bat :rider-app:assembleDebug

REM Build Driver App APK
gradlew.bat :driver-app:assembleDebug
```

**On Linux/Mac:**
```bash
cd android-ride-hailing

# Build Rider App APK
./gradlew :rider-app:assembleDebug

# Build Driver App APK
./gradlew :driver-app:assembleDebug
```

#### Step 2: Locate APK Files

APKs will be created at:
- `rider-app/build/outputs/apk/debug/rider-app-debug.apk`
- `driver-app/build/outputs/apk/debug/driver-app-debug.apk`

#### Step 3: Transfer to Phone

**Option A: USB Transfer**
1. Connect phone via USB
2. Copy APK files to phone's Download folder

**Option B: Cloud Transfer**
1. Upload APKs to Google Drive / Dropbox
2. Download on your phone

**Option C: Email**
1. Email APKs to yourself
2. Download attachments on phone

#### Step 4: Install APKs

1. On your phone, go to **Settings** → **Security**
2. Enable **Install from Unknown Sources** (or **Install Unknown Apps**)
3. Open **Files** app or **Downloads**
4. Tap on `rider-app-debug.apk`
5. Tap **Install**
6. Repeat for `driver-app-debug.apk`

---

### Method 3: Wireless Install (ADB over WiFi)

For wireless installation without USB cable:

#### Step 1: Connect via USB First

```cmd
REM Connect phone via USB
adb tcpip 5555
```

#### Step 2: Get Phone's IP Address

On your phone:
- Settings → About Phone → Status → IP Address
- Example: 192.168.1.100

#### Step 3: Connect Wirelessly

```cmd
REM Disconnect USB cable
adb connect 192.168.1.100:5555

REM Verify connection
adb devices
```

#### Step 4: Install Apps

```cmd
REM Windows
gradlew.bat :rider-app:installDebug
gradlew.bat :driver-app:installDebug

REM Linux/Mac
./gradlew :rider-app:installDebug
./gradlew :driver-app:installDebug
```

---

## 🧪 Testing Checklist

### Basic Functionality Test

**Rider App:**
- [ ] App launches successfully
- [ ] Login screen appears
- [ ] Can enter phone number
- [ ] UI looks correct
- [ ] Navigation works
- [ ] Map displays (if Google Maps API key configured)
- [ ] Dark mode toggle works
- [ ] Language switch works (English/Hindi)

**Driver App:**
- [ ] App launches successfully
- [ ] Login screen appears
- [ ] Can enter phone number
- [ ] UI looks correct
- [ ] Navigation drawer opens
- [ ] Map displays (if Google Maps API key configured)
- [ ] Online/offline toggle visible
- [ ] Dark mode toggle works

### Visual Inspection

- [ ] App icon looks good
- [ ] Splash screen displays
- [ ] Colors and theme look correct
- [ ] Text is readable
- [ ] Buttons are properly sized
- [ ] No layout issues
- [ ] Animations are smooth

### Performance Check

- [ ] App starts quickly (< 2 seconds)
- [ ] Smooth scrolling
- [ ] No lag or stuttering
- [ ] Transitions are smooth

---

## 🔧 Troubleshooting

### Issue: "adb: command not found"

**Solution:** Install Android SDK Platform Tools

**Windows:**
1. Download from: https://developer.android.com/studio/releases/platform-tools
2. Extract to `C:\platform-tools`
3. Add to PATH: System Properties → Environment Variables → Path → Add `C:\platform-tools`

**Linux:**
```bash
sudo apt install android-tools-adb android-tools-fastboot
```

**Mac:**
```bash
brew install android-platform-tools
```

### Issue: "No devices found"

**Solutions:**
1. Check USB cable (try different cable)
2. Enable USB Debugging on phone
3. Allow USB debugging when prompted
4. Try different USB port
5. Install phone's USB drivers (Windows)
6. Run: `adb kill-server` then `adb start-server`

### Issue: "Installation failed"

**Solutions:**
1. Uninstall existing version first
2. Enable "Install from Unknown Sources"
3. Check available storage space
4. Try: `adb uninstall com.rideconnect.rider`
5. Then reinstall

### Issue: App crashes on launch

**Check logs:**
```cmd
adb logcat | findstr "RideConnect"
```

**Common causes:**
- Missing Google Maps API key
- Backend API not accessible
- Firebase configuration missing

### Issue: "Unauthorized device"

**Solution:**
1. Disconnect USB
2. Run: `adb kill-server`
3. Reconnect USB
4. Allow USB debugging on phone (check "Always allow")

---

## 🔑 Configuration for Testing

### Backend API Configuration

The apps are configured to connect to:
- **Development:** `http://10.0.2.2:8000/api/` (Android emulator)
- **Local Network:** `http://YOUR_IP:8000/api/` (Physical device)

To test with your backend:

1. Find your computer's IP address:
   ```cmd
   REM Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. Update API URL in:
   ```kotlin
   // core/network/src/main/kotlin/com/rideconnect/core/network/di/NetworkModule.kt
   private const val BASE_URL = "http://YOUR_IP:8000/api/"
   ```

3. Rebuild and reinstall

### Google Maps API Key

For maps to work, you need a Google Maps API key:

1. Get API key from: https://console.cloud.google.com/
2. Add to `local.properties`:
   ```properties
   MAPS_API_KEY=YOUR_API_KEY_HERE
   ```
3. Rebuild and reinstall

### Firebase Configuration

For push notifications:

1. Download `google-services.json` from Firebase Console
2. Place in:
   - `rider-app/google-services.json`
   - `driver-app/google-services.json`
3. Rebuild and reinstall

---

## 📊 Viewing Logs

### Real-time Logs

```cmd
REM All logs
adb logcat

REM Filter for RideConnect
adb logcat | findstr "RideConnect"

REM Filter for errors
adb logcat *:E

REM Clear and view fresh logs
adb logcat -c
adb logcat
```

### Save Logs to File

```cmd
REM Windows
adb logcat > logs.txt

REM Linux/Mac
adb logcat > logs.txt
```

---

## 🎨 Testing Different Scenarios

### Test Dark Mode
1. Open app
2. Go to Settings
3. Toggle Dark Mode
4. Verify all screens look good

### Test Language Switch
1. Open app
2. Go to Settings
3. Change language to Hindi
4. Verify translations

### Test Offline Mode
1. Open app
2. Enable Airplane mode
3. Try to view ride history
4. Verify offline indicator shows

### Test Permissions
1. Fresh install
2. Open app
3. Verify permission requests:
   - Location permission
   - Notification permission
   - Camera permission (for profile photo)

---

## 🚀 Quick Commands Reference

```cmd
REM Build and install both apps
gradlew.bat :rider-app:installDebug :driver-app:installDebug

REM Uninstall apps
adb uninstall com.rideconnect.rider
adb uninstall com.rideconnect.driver

REM Launch apps
adb shell am start -n com.rideconnect.rider/.MainActivity
adb shell am start -n com.rideconnect.driver/.MainActivity

REM Clear app data
adb shell pm clear com.rideconnect.rider
adb shell pm clear com.rideconnect.driver

REM Take screenshot
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

REM Record screen
adb shell screenrecord /sdcard/demo.mp4
REM (Press Ctrl+C to stop)
adb pull /sdcard/demo.mp4
```

---

## ✅ Ready for Play Store?

After testing on your device, if everything works well:

1. ✅ Apps install successfully
2. ✅ All features work as expected
3. ✅ UI looks polished
4. ✅ Performance is good
5. ✅ No crashes

**Next step:** Follow the **GOOGLE_PLAY_DEPLOYMENT_GUIDE.md** to publish to Play Store!

---

## 💡 Tips

1. **Test on multiple devices** if possible (different screen sizes, Android versions)
2. **Test with poor network** (enable airplane mode, slow 3G)
3. **Test battery usage** (leave app running for a while)
4. **Test with different languages** (English and Hindi)
5. **Test accessibility** (enable TalkBack and try using the app)
6. **Take screenshots** for Play Store listing while testing

---

## 📞 Need Help?

**Common Issues:**
- Device not detected → Check USB debugging, try different cable
- Installation failed → Uninstall old version first
- App crashes → Check logs with `adb logcat`
- Maps not working → Add Google Maps API key

**For more help:**
- See DEVELOPER_GUIDE.md
- Check Android Studio's Logcat
- Email: dev-support@rideconnect.com

---

**Happy Testing! 🎉**

*Once you're satisfied with the preview, proceed to Play Store deployment using the GOOGLE_PLAY_DEPLOYMENT_GUIDE.md*
