# Rider App

## Overview

The Rider App is a native Android application for passengers to request rides, track drivers in real-time, make payments, and manage their ride history. Built with Kotlin and Jetpack Compose.

## Features

### Core Features
- **Authentication**: Phone number + OTP verification, biometric login
- **Ride Request**: Select pickup/dropoff, view fare estimate, request ride
- **Real-Time Tracking**: Track driver location on map with ETA
- **Scheduled Rides**: Schedule rides up to 7 days in advance
- **Parcel Delivery**: Request parcel delivery service
- **Payment**: Process payments with fare breakdown
- **Rating & Review**: Rate drivers and view rating history
- **In-Ride Chat**: Message driver during ride
- **Emergency Features**: SOS button, emergency contacts, ride sharing
- **Ride History**: View past rides with receipts
- **Profile Management**: Update profile, add emergency contacts
- **Multi-Language**: English and Hindi support
- **Dark Mode**: Light and dark theme support
- **Offline Mode**: View cached data when offline

### User Interface

#### Bottom Navigation
- **Home**: Request rides, view active ride
- **History**: Past rides and receipts
- **Profile**: User profile and settings

#### Key Screens
- `LoginScreen`: Phone number and OTP verification
- `HomeScreen`: Main screen with map and ride request
- `RideRequestScreen`: Location selection and fare estimation
- `RideTrackingScreen`: Real-time driver tracking
- `ScheduleRideScreen`: Schedule future rides
- `ParcelDeliveryScreen`: Request parcel delivery
- `PaymentScreen`: Payment processing
- `RatingDialog`: Rate driver after ride
- `ChatScreen`: In-ride messaging
- `RideHistoryScreen`: Past ride history
- `ProfileScreen`: User profile management
- `SettingsScreen`: App settings

## Architecture

### Clean Architecture with MVVM

```
Presentation Layer (UI)
    ├─ Screens (Composables)
    └─ ViewModels
        ↓
Domain Layer
    ├─ Models
    ├─ Repository Interfaces
    └─ Use Cases
        ↓
Data Layer
    ├─ Repository Implementations
    ├─ Network (Retrofit)
    ├─ Database (Room)
    └─ Device (Location, Biometric)
```

### Module Structure

```
rider-app/
├── src/main/kotlin/com/rideconnect/rider/
│   ├── MainActivity.kt
│   ├── RiderApplication.kt
│   ├── ui/
│   │   ├── auth/          # Login screens
│   │   ├── home/          # Home screen
│   │   ├── ride/          # Ride request screens
│   │   ├── payment/       # Payment screens
│   │   ├── rating/        # Rating screens
│   │   ├── profile/       # Profile screens
│   │   ├── settings/      # Settings screens
│   │   ├── main/          # Main screen with navigation
│   │   ├── navigation/    # Bottom navigation
│   │   └── theme/         # App theme
│   └── navigation/        # Navigation graph
└── src/androidTest/       # UI tests
```

## Getting Started

### Prerequisites

- Android Studio Hedgehog or later
- JDK 17
- Android SDK 34
- Google Maps API key
- Firebase project (for FCM)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd android-ride-hailing
   ```

2. **Add Google Maps API key**
   
   Create `local.properties` in project root:
   ```properties
   MAPS_API_KEY=your_google_maps_api_key
   ```

3. **Add Firebase configuration**
   
   Download `google-services.json` from Firebase Console and place in `rider-app/` directory.

4. **Configure backend URL**
   
   Update in `rider-app/build.gradle.kts`:
   ```kotlin
   buildConfigField("String", "BASE_URL", "\"http://10.0.2.2:8000/api/\"")
   buildConfigField("String", "WS_URL", "\"ws://10.0.2.2:8000/ws\"")
   ```

5. **Build and run**
   ```bash
   ./gradlew :rider-app:assembleDebug
   ./gradlew :rider-app:installDebug
   ```

## Configuration

### Backend API

The app connects to the FastAPI backend:
- API Base URL: `http://10.0.2.2:8000/api/` (emulator)
- WebSocket URL: `ws://10.0.2.2:8000/ws` (emulator)

For physical devices, use your computer's IP address:
```kotlin
buildConfigField("String", "BASE_URL", "\"http://192.168.1.100:8000/api/\"")
```

### Build Variants

- **Debug**: Development build with logging enabled
- **Release**: Production build with ProGuard obfuscation

### ProGuard

ProGuard rules in `proguard-rules.pro` protect:
- Retrofit models
- Room entities
- Hilt components
- Firebase classes

## Testing

### Unit Tests

Run unit tests:
```bash
./gradlew :rider-app:testDebugUnitTest
```

### UI Tests

Run instrumented tests:
```bash
./gradlew :rider-app:connectedDebugAndroidTest
```

### Code Coverage

Generate coverage report:
```bash
./gradlew :rider-app:testDebugUnitTest
./gradlew jacocoTestReport
```

View report at: `build/reports/jacoco/jacocoTestReport/html/index.html`

### Static Analysis

Run Detekt:
```bash
./gradlew detekt
```

## Permissions

Required permissions in `AndroidManifest.xml`:

- `ACCESS_FINE_LOCATION`: Real-time location tracking
- `ACCESS_COARSE_LOCATION`: Approximate location
- `INTERNET`: Network communication
- `POST_NOTIFICATIONS`: Push notifications (Android 13+)
- `USE_BIOMETRIC`: Fingerprint/face authentication
- `VIBRATE`: Haptic feedback

## Dependencies

### Core
- Kotlin 1.9.20
- AndroidX Core KTX 1.12.0
- Jetpack Compose (BOM 2023.10.01)
- Material Design 3

### Architecture
- Hilt 2.48 (Dependency Injection)
- Lifecycle ViewModel 2.6.2
- Navigation Compose 2.7.5

### Networking
- Retrofit 2.9.0
- OkHttp 4.12.0
- Gson (JSON parsing)

### Database
- Room 2.6.1

### Maps & Location
- Google Maps SDK 18.2.0
- Google Places API 3.3.0
- Play Services Location 21.0.1
- Maps Compose 4.3.0

### Firebase
- Firebase BOM 32.7.0
- Firebase Cloud Messaging
- Firebase Analytics

### Other
- Coil 2.5.0 (Image loading)
- Biometric 1.1.0
- Security Crypto 1.1.0-alpha06
- WorkManager 2.9.0
- DataStore 1.0.0
- Accompanist 0.32.0

## Troubleshooting

### Common Issues

1. **Maps not showing**
   - Verify Google Maps API key in `local.properties`
   - Enable Maps SDK for Android in Google Cloud Console

2. **Backend connection failed**
   - Check backend is running at configured URL
   - For emulator, use `10.0.2.2` instead of `localhost`
   - For physical device, use computer's IP address

3. **Push notifications not working**
   - Verify `google-services.json` is in `rider-app/` directory
   - Check FCM is enabled in Firebase Console
   - Register device token with backend

4. **Build errors**
   - Clean and rebuild: `./gradlew clean build`
   - Invalidate caches: Android Studio → File → Invalidate Caches

## Release Build

### Generate signed APK

1. Create keystore:
   ```bash
   keytool -genkey -v -keystore rider-release.keystore -alias rider -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Configure signing in `build.gradle.kts`:
   ```kotlin
   signingConfigs {
       create("release") {
           storeFile = file("rider-release.keystore")
           storePassword = "your_password"
           keyAlias = "rider"
           keyPassword = "your_password"
       }
   }
   ```

3. Build release APK:
   ```bash
   ./gradlew :rider-app:assembleRelease
   ```

APK location: `rider-app/build/outputs/apk/release/rider-app-release.apk`

## Contributing

1. Follow Kotlin coding conventions
2. Write unit tests for new features
3. Run Detekt before committing
4. Update documentation for API changes

## License

[Your License Here]
