# 📱 RideConnect Android Applications

Native Android applications for the RideConnect ride-hailing platform, built with Kotlin and Jetpack Compose.

## 🎯 Overview

This project contains two separate Android applications:

1. **Rider App** (`rider-app`) - For passengers requesting and managing rides
2. **Driver App** (`driver-app`) - For drivers accepting and completing ride requests

Both apps share common core modules and integrate with the existing FastAPI backend.

## 🏗️ Architecture

### Multi-Module Structure

```
android-ride-hailing/
├── rider-app/              # Rider application
├── driver-app/             # Driver application
└── core/
    ├── domain/            # Business logic and use cases
    ├── data/              # Repository implementations
    ├── network/           # API clients and WebSocket
    ├── database/          # Room database
    └── common/            # Shared utilities
```

### Technology Stack

- **Language**: Kotlin 1.9.20
- **UI**: Jetpack Compose with Material Design 3
- **Architecture**: MVVM (Model-View-ViewModel) + Clean Architecture
- **Dependency Injection**: Hilt (Dagger)
- **Networking**: Retrofit 2.9 + OkHttp 4.12
- **Database**: Room 2.6
- **Maps**: Google Maps SDK + Places API
- **Real-time**: OkHttp WebSocket
- **Push Notifications**: Firebase Cloud Messaging
- **Image Loading**: Coil
- **Async**: Kotlin Coroutines + Flow
- **Security**: EncryptedSharedPreferences + Biometric Auth

## 🚀 Getting Started

### Prerequisites

1. **Android Studio** Hedgehog (2023.1.1) or later
2. **JDK** 17 or later
3. **Android SDK** with API 34 (Android 14)
4. **Backend Server** running at `http://localhost:8000`

### Setup Instructions

1. **Clone the repository**
   ```bash
   cd android-ride-hailing
   ```

2. **Open in Android Studio**
   - Open Android Studio
   - Select "Open an Existing Project"
   - Navigate to `android-ride-hailing` folder
   - Wait for Gradle sync to complete

3. **Configure API Keys**

   Create `local.properties` file in the root directory:
   ```properties
   sdk.dir=/path/to/Android/sdk
   MAPS_API_KEY=your_google_maps_api_key_here
   ```

4. **Configure Firebase**
   - Download `google-services.json` from Firebase Console
   - Place in `rider-app/` directory
   - Place another copy in `driver-app/` directory

5. **Update Backend URL** (if needed)
   
   Edit `build.gradle.kts` in each app module:
   ```kotlin
   buildConfigField("String", "BASE_URL", "\"http://YOUR_IP:8000/api/\"")
   buildConfigField("String", "WS_URL", "\"ws://YOUR_IP:8000/ws\"")
   ```

   **Note**: Use `10.0.2.2` for Android Emulator to access localhost

6. **Build the project**
   ```bash
   ./gradlew build
   ```

7. **Run the apps**
   - Select `rider-app` or `driver-app` from the run configuration
   - Click Run or press Shift+F10

## 📱 Features

### Rider App Features

- ✅ Phone number authentication with OTP
- ✅ Biometric login (fingerprint/face)
- ✅ Request immediate rides
- ✅ Schedule rides up to 7 days in advance
- ✅ Request parcel delivery
- ✅ Real-time driver tracking on map
- ✅ Fare estimation and breakdown
- ✅ In-app payment (Razorpay/Paytm)
- ✅ Ride history with receipts
- ✅ Rate and review drivers
- ✅ Emergency SOS button
- ✅ Share ride with emergency contacts
- ✅ In-app chat with driver
- ✅ Push notifications
- ✅ Offline mode
- ✅ Dark mode
- ✅ Multi-language (English/Hindi)

### Driver App Features

- ✅ Toggle online/offline availability
- ✅ Receive ride requests with countdown timer
- ✅ Accept/reject ride requests
- ✅ Turn-by-turn navigation
- ✅ Real-time location sharing
- ✅ Start/complete rides
- ✅ Earnings tracking (daily/weekly/monthly)
- ✅ Vehicle registration
- ✅ Accept parcel deliveries
- ✅ Set preferences (extended area, parcels)
- ✅ Rating history and performance metrics
- ✅ In-app chat with rider
- ✅ Push notifications
- ✅ Dark mode
- ✅ Multi-language (English/Hindi)

## 🔧 Development

### Project Structure

```
rider-app/
├── src/main/
│   ├── kotlin/com/rideconnect/rider/
│   │   ├── ui/              # Compose UI screens
│   │   ├── viewmodel/       # ViewModels
│   │   ├── navigation/      # Navigation graph
│   │   └── RiderApp.kt      # Application class
│   ├── res/                 # Resources
│   └── AndroidManifest.xml
└── build.gradle.kts

core/
├── domain/                  # Business logic
│   ├── model/              # Domain models
│   ├── repository/         # Repository interfaces
│   └── usecase/            # Use cases
├── data/                    # Data layer
│   ├── repository/         # Repository implementations
│   ├── local/              # Local data sources
│   └── remote/             # Remote data sources
├── network/                 # Networking
│   ├── api/                # Retrofit API interfaces
│   ├── dto/                # Data transfer objects
│   └── websocket/          # WebSocket manager
├── database/                # Room database
│   ├── entity/             # Database entities
│   ├── dao/                # Data access objects
│   └── AppDatabase.kt
└── common/                  # Utilities
    ├── util/               # Helper functions
    ├── extension/          # Kotlin extensions
    └── Constants.kt
```

### Building for Release

1. **Generate signing key**
   ```bash
   keytool -genkey -v -keystore rideconnect.keystore -alias rideconnect -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Configure signing in `build.gradle.kts`**
   ```kotlin
   signingConfigs {
       create("release") {
           storeFile = file("path/to/rideconnect.keystore")
           storePassword = "your_password"
           keyAlias = "rideconnect"
           keyPassword = "your_password"
       }
   }
   ```

3. **Build release APK**
   ```bash
   ./gradlew assembleRelease
   ```

4. **Build release AAB (for Play Store)**
   ```bash
   ./gradlew bundleRelease
   ```

## 🧪 Testing

### Run Unit Tests
```bash
./gradlew test
```

### Run Instrumented Tests
```bash
./gradlew connectedAndroidTest
```

### Run Specific Test
```bash
./gradlew :rider-app:testDebugUnitTest --tests "AuthViewModelTest"
```

### Generate Coverage Report
```bash
./gradlew jacocoTestReport
```

## 📊 Code Quality

### Run Lint
```bash
./gradlew lint
```

### Run Detekt (Static Analysis)
```bash
./gradlew detekt
```

## 🔐 Security

- JWT tokens stored in EncryptedSharedPreferences
- SSL certificate pinning for API calls
- Secure WebSocket connections (WSS)
- ProGuard obfuscation for release builds
- Biometric authentication using Android Keystore
- No sensitive data logged in production

## 🌍 Localization

Supported languages:
- English (default)
- Hindi (हिन्दी)

Add new translations in `res/values-{language}/strings.xml`

## 🎨 Theming

The app supports:
- Light mode
- Dark mode
- System default (follows device setting)

Theme configuration in `ui/theme/` directory.

## 📝 API Integration

### Backend Endpoints

The apps integrate with these backend endpoints:

**Authentication**
- `POST /api/auth/register` - User registration
- `POST /api/auth/verify/send` - Send OTP
- `POST /api/auth/verify/confirm` - Verify OTP
- `POST /api/auth/login` - Login

**Rides**
- `POST /api/rides/request` - Request ride
- `POST /api/rides/schedule` - Schedule ride
- `GET /api/rides/history` - Ride history
- `POST /api/rides/{id}/cancel` - Cancel ride

**Drivers**
- `POST /api/drivers/availability` - Set availability
- `POST /api/drivers/vehicle` - Register vehicle
- `GET /api/drivers/earnings` - Get earnings

**Payments**
- `POST /api/payments/process` - Process payment
- `GET /api/payments/history` - Payment history

**WebSocket**
- `ws://backend/ws` - Real-time updates

Full API documentation: `http://localhost:8000/docs`

## 🐛 Troubleshooting

### Common Issues

**1. Gradle sync failed**
- Ensure you have JDK 17 installed
- Check internet connection for dependency downloads
- Try: File → Invalidate Caches → Restart

**2. Cannot connect to backend**
- Use `10.0.2.2` instead of `localhost` for emulator
- Check backend server is running
- Verify firewall settings

**3. Google Maps not showing**
- Ensure `MAPS_API_KEY` is set in `local.properties`
- Enable Maps SDK in Google Cloud Console
- Check API key restrictions

**4. Firebase notifications not working**
- Verify `google-services.json` is in app directory
- Check Firebase project configuration
- Ensure FCM is enabled in Firebase Console

**5. Build errors**
- Clean project: Build → Clean Project
- Rebuild: Build → Rebuild Project
- Delete `.gradle` folder and sync again

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the [API documentation](http://localhost:8000/docs)
- Review the spec documents in `.kiro/specs/android-ride-hailing-app/`
- Open an issue on GitHub

---

**Status**: 🚧 In Development

**Version**: 1.0.0

**Last Updated**: February 19, 2026
