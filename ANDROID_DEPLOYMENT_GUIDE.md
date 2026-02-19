# Android App Deployment Guide

## Current Status

⚠️ **The Android app is NOT ready for deployment yet.**

### Completed Features (Tasks 1-3.1):
- ✅ Project setup and core infrastructure
- ✅ Authentication module (OTP login)
- ✅ AuthViewModel with state management
- ✅ Login and OTP verification UI screens
- ✅ BiometricAuthManager implementation

### Missing Critical Features:
- ❌ Network layer (Retrofit/OkHttp interceptors)
- ❌ Room database for local storage
- ❌ Location services and Google Maps
- ❌ WebSocket for real-time communication
- ❌ Ride request functionality
- ❌ Payment integration
- ❌ Push notifications
- ❌ And 30+ more tasks...

**Progress: ~8% complete (3 of 38 major tasks)**

---

## When Ready: Deployment Options

### Option 1: Install via USB (Debug Build)

**Prerequisites:**
- Android Studio installed on your computer
- USB cable to connect your phone
- Developer options enabled on your phone

**Steps:**

1. **Enable Developer Options on Your Phone:**
   ```
   Settings → About Phone → Tap "Build Number" 7 times
   Settings → Developer Options → Enable "USB Debugging"
   ```

2. **Connect Your Phone:**
   ```bash
   # Connect phone via USB
   # Accept USB debugging prompt on phone
   
   # Verify connection
   adb devices
   ```

3. **Build and Install:**
   ```bash
   cd android-ride-hailing
   
   # Build and install Rider App
   ./gradlew :rider-app:installDebug
   
   # Or build and install Driver App
   ./gradlew :driver-app:installDebug
   ```

4. **Launch the App:**
   - Find "RideConnect Rider" or "RideConnect Driver" in your app drawer
   - Tap to launch

### Option 2: Generate APK File

**Steps:**

1. **Build Debug APK:**
   ```bash
   cd android-ride-hailing
   
   # For Rider App
   ./gradlew :rider-app:assembleDebug
   
   # APK location:
   # rider-app/build/outputs/apk/debug/rider-app-debug.apk
   ```

2. **Transfer APK to Phone:**
   - Email the APK to yourself
   - Use Google Drive/Dropbox
   - Transfer via USB cable
   - Use ADB: `adb install rider-app/build/outputs/apk/debug/rider-app-debug.apk`

3. **Install on Phone:**
   - Enable "Install from Unknown Sources" in Settings
   - Open the APK file
   - Tap "Install"

### Option 3: Release Build (Production)

**Prerequisites:**
- Keystore file for signing
- Google Play Console account (for Play Store)

**Steps:**

1. **Create Keystore:**
   ```bash
   keytool -genkey -v -keystore rideconnect.keystore \
     -alias rideconnect -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Configure Signing:**
   Create `keystore.properties`:
   ```properties
   storePassword=YOUR_STORE_PASSWORD
   keyPassword=YOUR_KEY_PASSWORD
   keyAlias=rideconnect
   storeFile=../rideconnect.keystore
   ```

3. **Build Release APK:**
   ```bash
   ./gradlew :rider-app:assembleRelease
   ```

4. **Install:**
   ```bash
   adb install rider-app/build/outputs/apk/release/rider-app-release.apk
   ```

---

## Testing the App (When Ready)

### Backend Setup Required

The app needs the FastAPI backend running:

1. **Start Backend Server:**
   ```bash
   python run.py
   ```

2. **Configure App to Connect:**
   - For emulator: Backend at `http://10.0.2.2:8000`
   - For physical device: Backend at `http://YOUR_COMPUTER_IP:8000`
   
3. **Update Network Config:**
   Edit `core/network/src/main/kotlin/com/rideconnect/core/network/di/NetworkModule.kt`:
   ```kotlin
   private const val BASE_URL = "http://YOUR_IP:8000/api/"
   ```

### Test Features

Once deployed, you can test:
- ✅ Phone number login
- ✅ OTP verification
- ✅ Biometric authentication (if device supports it)
- ❌ Everything else (not implemented yet)

---

## Current Limitations

1. **No Backend Connection:** Network layer not implemented
2. **No Real Functionality:** Only authentication screens work
3. **No Data Persistence:** Room database not set up
4. **No Maps:** Google Maps integration pending
5. **No Ride Features:** Core ride functionality not built

---

## Recommended Next Steps

### To Make App Deployable:

1. **Complete Core Infrastructure (Tasks 4-9):**
   - Network layer with Retrofit
   - Room database
   - Location services
   - Google Maps integration
   - WebSocket communication

2. **Implement Ride Features (Tasks 10-16):**
   - Profile management
   - Ride request/acceptance
   - Real-time tracking
   - Payment processing

3. **Add Supporting Features (Tasks 17-24):**
   - Push notifications
   - Chat functionality
   - Emergency features
   - Offline mode

**Estimated Time:** 4-6 weeks of development

---

## Quick Deploy Script (For Future Use)

```bash
#!/bin/bash
# deploy_android.sh

echo "🚀 Deploying RideConnect Android App"

# Check if device is connected
if ! adb devices | grep -q "device$"; then
    echo "❌ No Android device connected"
    exit 1
fi

# Build and install
cd android-ride-hailing
./gradlew :rider-app:installDebug

echo "✅ App installed successfully!"
echo "📱 Launch 'RideConnect Rider' from your app drawer"
```

---

## Troubleshooting

### "App not installed" Error
- Enable "Install from Unknown Sources"
- Check if old version exists (uninstall first)
- Verify APK is not corrupted

### "USB Debugging not authorized"
- Check phone for authorization prompt
- Revoke USB debugging authorizations and try again

### App Crashes on Launch
- Check Logcat: `adb logcat | grep RideConnect`
- Verify backend is running
- Check network configuration

---

## Contact & Support

For deployment issues:
1. Check Android Studio Logcat
2. Verify all dependencies are installed
3. Ensure backend server is accessible
4. Review error messages in app

---

**Note:** This guide will be updated as more features are implemented.
