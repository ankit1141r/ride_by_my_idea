# Driver App

## Overview

The Driver App is a native Android application for drivers to receive ride requests, navigate to pickup/dropoff locations, track earnings, and manage their availability. Built with Kotlin and Jetpack Compose.

## Features

### Core Features
- **Authentication**: Phone number + OTP verification, biometric login
- **Availability Management**: Toggle online/offline status
- **Ride Requests**: Receive and accept/reject ride requests with countdown timer
- **Navigation**: Turn-by-turn navigation to pickup and dropoff
- **Ride Execution**: Start and complete rides
- **Parcel Delivery**: Accept parcel delivery requests
- **Earnings Tracking**: View daily, weekly, and monthly earnings
- **Rating & Review**: View ratings and rate riders
- **In-Ride Chat**: Message rider during ride
- **Emergency Features**: SOS button, emergency contacts
- **Profile Management**: Update profile and vehicle details
- **Multi-Language**: English and Hindi support
- **Dark Mode**: Light and dark theme support
- **Offline Mode**: View cached data when offline

### User Interface

#### Drawer Navigation
- **Home**: Online/offline toggle, active ride
- **Earnings**: Earnings summary and breakdown
- **Ratings**: Driver ratings and performance metrics
- **Settings**: App settings and preferences

#### Key Screens
- `LoginScreen`: Phone number and OTP verification
- `DriverHomeScreen`: Main screen with online toggle
- `RideRequestDialog`: Incoming ride request with countdown
- `ActiveRideScreen`: Navigation and ride controls
- `EarningsScreen`: Earnings breakdown by period
- `DriverRatingsScreen`: Rating history and metrics
- `RateRiderDialog`: Rate rider after ride
- `ChatScreen`: In-ride messaging
- `DriverSettingsScreen`: Driver-specific settings
- `ProfileScreen`: Driver profile and vehicle details

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
driver-app/
├── src/main/kotlin/com/rideconnect/driver/
│   ├── MainActivity.kt
│   ├── DriverApplication.kt
│   ├── ui/
│   │   ├── auth/          # Login screens
│   │   ├── home/          # Home screen
│   │   ├── ride/          # Ride request and execution
│   │   ├── earnings/      # Earnings screens
│   │   ├── ratings/       # Rating screens
│   │   ├── parcel/        # Parcel delivery screens
│   │   ├── settings/      # Settings screens
│   │   ├── main/          # Main screen with navigation
│   │   └── navigation/    # Drawer navigation
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
   
   Download `google-services.json` from Firebase Console and place in `driver-app/` directory.

4. **Configure backend URL**
   
   Update in `driver-app/build.gradle.kts`:
   ```kotlin
   buildConfigField("String", "BASE_URL", "\"http://10.0.2.2:8000/api/\"")
   buildConfigField("String", "WS_URL", "\"ws://10.0.2.2:8000/ws\"")
   ```

5. **Build and run**
   ```bash
   ./gradlew :driver-app:assembleDebug
   ./gradlew :driver-app:installDebug
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

## Background Location Tracking

The Driver App uses a foreground service for continuous location tracking when online:

### LocationForegroundService

- Starts when driver goes online
- Updates location every 10 seconds
- Shows persistent notification
- Stops when driver goes offline

### Battery Optimization

- Uses balanced power mode for location requests
- Reduces update frequency when app in background
- Shows battery warning when below 15%

## Testing

### Unit Tests

Run unit tests:
```bash
./gradlew :driver-app:testDebugUnitTest
```

### UI Tests

Run instrumented tests:
```bash
./gradlew :driver-app:connectedDebugAndroidTest
```

### Code Coverage

Generate coverage report:
```bash
./gradlew :driver-app:testDebugUnitTest
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
- `ACCESS_BACKGROUND_LOCATION`: Background location (Android 10+)
- `FOREGROUND_SERVICE`: Foreground service for location tracking
- `FOREGROUND_SERVICE_LOCATION`: Location foreground service (Android 14+)
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
- Lifecycle Service 2.6.2
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

## Driver-Specific Features

### Ride Request Handling

1. **Receive Request**: Push notification + in-app dialog
2. **Countdown Timer**: 30 seconds to accept/reject
3. **Auto-Reject**: Automatically rejected if timer expires
4. **Queue**: Multiple requests queued, shown one at a time

### Earnings Tracking

- **Real-time Updates**: Earnings updated after each ride
- **Period Filtering**: View by day, week, or month
- **Statistics**: Total rides, average fare, total earnings
- **Pending Earnings**: Track unpaid earnings

### Performance Metrics

- **Acceptance Rate**: Percentage of accepted ride requests
- **Cancellation Rate**: Percentage of cancelled rides
- **Average Rating**: Overall driver rating
- **Rating Breakdown**: Distribution by star count

## Troubleshooting

### Common Issues

1. **Location not updating**
   - Check location permissions granted
   - Verify GPS is enabled
   - Check battery optimization settings

2. **Not receiving ride requests**
   - Verify driver is online
   - Check WebSocket connection status
   - Verify FCM token registered with backend

3. **Background location not working**
   - Grant background location permission
   - Disable battery optimization for app
   - Check foreground service is running

4. **Maps not showing**
   - Verify Google Maps API key in `local.properties`
   - Enable Maps SDK for Android in Google Cloud Console

## Release Build

### Generate signed APK

1. Create keystore:
   ```bash
   keytool -genkey -v -keystore driver-release.keystore -alias driver -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Configure signing in `build.gradle.kts`:
   ```kotlin
   signingConfigs {
       create("release") {
           storeFile = file("driver-release.keystore")
           storePassword = "your_password"
           keyAlias = "driver"
           keyPassword = "your_password"
       }
   }
   ```

3. Build release APK:
   ```bash
   ./gradlew :driver-app:assembleRelease
   ```

APK location: `driver-app/build/outputs/apk/release/driver-app-release.apk`

## Contributing

1. Follow Kotlin coding conventions
2. Write unit tests for new features
3. Run Detekt before committing
4. Update documentation for API changes

## License

[Your License Here]
