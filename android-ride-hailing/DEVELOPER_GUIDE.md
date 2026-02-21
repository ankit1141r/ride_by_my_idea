# Developer Guide

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Setup and Installation](#setup-and-installation)
5. [Build and Run](#build-and-run)
6. [Testing Strategy](#testing-strategy)
7. [Code Quality](#code-quality)
8. [API Integration](#api-integration)
9. [Development Workflow](#development-workflow)
10. [Troubleshooting](#troubleshooting)

## Project Overview

The Android Ride-Hailing Application consists of two native Android apps:
- **Rider App**: For passengers to request and track rides
- **Driver App**: For drivers to receive requests and complete rides

Both apps share common core modules and follow Clean Architecture with MVVM pattern.

### Technology Stack

- **Language**: Kotlin 1.9.20
- **UI Framework**: Jetpack Compose with Material Design 3
- **Architecture**: Clean Architecture + MVVM
- **Dependency Injection**: Hilt
- **Networking**: Retrofit + OkHttp
- **Database**: Room
- **Async**: Kotlin Coroutines + Flow
- **Maps**: Google Maps SDK
- **Push Notifications**: Firebase Cloud Messaging
- **Image Loading**: Coil
- **Testing**: JUnit, Mockito, Compose Testing

## Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (UI Screens, ViewModels, Compose)      │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│           Domain Layer                  │
│  (Models, Repository Interfaces,        │
│   Business Logic)                       │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│            Data Layer                   │
│  (Repository Implementations,           │
│   Network, Database, Device)            │
└─────────────────────────────────────────┘
```

### MVVM Pattern

```
View (Composable)
    ↓ User Actions
ViewModel
    ↓ Business Logic
Repository
    ↓ Data Operations
Data Sources (API, DB, Device)
```

### Data Flow

```
UI → ViewModel → Repository → Data Source
                      ↓
                   Result<T>
                      ↓
                  StateFlow
                      ↓
                     UI
```

## Project Structure

```
android-ride-hailing/
├── rider-app/                 # Rider application module
│   ├── src/main/
│   │   ├── kotlin/com/rideconnect/rider/
│   │   │   ├── MainActivity.kt
│   │   │   ├── RiderApplication.kt
│   │   │   ├── ui/            # UI screens
│   │   │   └── navigation/    # Navigation graph
│   │   ├── res/               # Resources
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
│
├── driver-app/                # Driver application module
│   ├── src/main/
│   │   ├── kotlin/com/rideconnect/driver/
│   │   │   ├── MainActivity.kt
│   │   │   ├── DriverApplication.kt
│   │   │   ├── ui/            # UI screens
│   │   │   └── navigation/    # Navigation graph
│   │   ├── res/               # Resources
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
│
├── core/                      # Shared core modules
│   ├── domain/                # Business logic layer
│   │   ├── model/             # Domain models
│   │   ├── repository/        # Repository interfaces
│   │   ├── viewmodel/         # ViewModels
│   │   ├── websocket/         # WebSocket interfaces
│   │   └── validation/        # Validation logic
│   │
│   ├── data/                  # Data layer
│   │   ├── repository/        # Repository implementations
│   │   ├── mapper/            # Data mappers
│   │   ├── location/          # Location services
│   │   ├── websocket/         # WebSocket implementation
│   │   ├── biometric/         # Biometric auth
│   │   ├── notification/      # Push notifications
│   │   ├── sync/              # Offline sync
│   │   ├── worker/            # Background workers
│   │   └── local/             # Local storage
│   │
│   ├── network/               # Network layer
│   │   ├── api/               # Retrofit API interfaces
│   │   ├── dto/               # Data transfer objects
│   │   ├── interceptor/       # OkHttp interceptors
│   │   ├── security/          # Certificate pinning
│   │   └── di/                # Network DI module
│   │
│   ├── database/              # Database layer
│   │   ├── entity/            # Room entities
│   │   ├── dao/               # Data access objects
│   │   └── AppDatabase.kt     # Database configuration
│   │
│   └── common/                # Shared utilities
│       ├── ui/                # Reusable UI components
│       ├── theme/             # App theme
│       ├── util/              # Utility functions
│       ├── navigation/        # Navigation helpers
│       ├── security/          # Security utilities
│       ├── map/               # Map utilities
│       └── res/               # Shared resources
│
├── config/                    # Configuration files
│   └── detekt/                # Detekt configuration
│
├── build.gradle.kts           # Root build file
├── settings.gradle.kts        # Project settings
└── gradle.properties          # Gradle properties
```

## Setup and Installation

### Prerequisites

1. **Android Studio**: Hedgehog (2023.1.1) or later
2. **JDK**: Version 17
3. **Android SDK**: API 34 (Android 14)
4. **Google Maps API Key**: From Google Cloud Console
5. **Firebase Project**: For push notifications

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd android-ride-hailing
   ```

2. **Configure Google Maps API**
   
   Create `local.properties` in project root:
   ```properties
   sdk.dir=/path/to/Android/sdk
   MAPS_API_KEY=your_google_maps_api_key_here
   ```

3. **Add Firebase Configuration**
   
   Download `google-services.json` from Firebase Console:
   - Place in `rider-app/` directory
   - Place in `driver-app/` directory

4. **Sync Gradle**
   ```bash
   ./gradlew --refresh-dependencies
   ```

### Backend Configuration

The apps connect to a FastAPI backend. Configure URLs in build files:

**For Android Emulator:**
```kotlin
buildConfigField("String", "BASE_URL", "\"http://10.0.2.2:8000/api/\"")
buildConfigField("String", "WS_URL", "\"ws://10.0.2.2:8000/ws\"")
```

**For Physical Device:**
```kotlin
buildConfigField("String", "BASE_URL", "\"http://192.168.1.100:8000/api/\"")
buildConfigField("String", "WS_URL", "\"ws://192.168.1.100:8000/ws\"")
```

Replace `192.168.1.100` with your computer's IP address.

## Build and Run

### Build Variants

The project uses product flavors for different environments:

- **dev**: Development environment (local backend)
- **staging**: Staging environment (staging server)
- **prod**: Production environment (production server)

Combined with build types (debug/release), you get:
- `devDebug`, `devRelease`
- `stagingDebug`, `stagingRelease`
- `prodDebug`, `prodRelease`

### Build Commands

**Build Debug APK:**
```bash
# Rider App
./gradlew :rider-app:assembleDevDebug

# Driver App
./gradlew :driver-app:assembleDevDebug
```

**Build Release APK:**
```bash
# Rider App
./gradlew :rider-app:assembleProdRelease

# Driver App
./gradlew :driver-app:assembleProdRelease
```

**Install on Device:**
```bash
# Rider App
./gradlew :rider-app:installDevDebug

# Driver App
./gradlew :driver-app:installDevDebug
```

### Run from Android Studio

1. Select run configuration (rider-app or driver-app)
2. Select build variant (Build → Select Build Variant)
3. Select device/emulator
4. Click Run (Shift+F10)

## Testing Strategy

### Test Types

1. **Unit Tests**: Test business logic in isolation
2. **Integration Tests**: Test component interactions
3. **UI Tests**: Test user interface with Compose Testing
4. **Property-Based Tests**: Test universal properties (optional)

### Running Tests

**Unit Tests:**
```bash
# All modules
./gradlew test

# Specific module
./gradlew :core:domain:testDebugUnitTest
./gradlew :rider-app:testDevDebugUnitTest
```

**UI Tests:**
```bash
# All UI tests
./gradlew connectedAndroidTest

# Specific app
./gradlew :rider-app:connectedDevDebugAndroidTest
```

**Code Coverage:**
```bash
# Run tests with coverage
./gradlew testDebugUnitTest

# Generate coverage report
./gradlew jacocoTestReport

# Verify coverage threshold (70%)
./gradlew jacocoTestCoverageVerification
```

View coverage report: `build/reports/jacoco/jacocoTestReport/html/index.html`

### Writing Tests

**Unit Test Example:**
```kotlin
@Test
fun `test ride request validation`() = runTest {
    // Given
    val request = RideRequest(
        pickupLat = 0.0,
        pickupLng = 0.0,
        dropoffLat = 0.0,
        dropoffLng = 0.0
    )
    
    // When
    val result = viewModel.requestRide(request)
    
    // Then
    assertTrue(result is Result.Error)
    assertEquals("Invalid location", result.message)
}
```

**UI Test Example:**
```kotlin
@Test
fun testLoginFlow() {
    composeTestRule.setContent {
        LoginScreen(onLoginSuccess = {})
    }
    
    // Enter phone number
    composeTestRule
        .onNodeWithTag("phone_input")
        .performTextInput("1234567890")
    
    // Click send OTP
    composeTestRule
        .onNodeWithTag("send_otp_button")
        .performClick()
    
    // Verify OTP screen shown
    composeTestRule
        .onNodeWithTag("otp_input")
        .assertIsDisplayed()
}
```

## Code Quality

### Static Analysis with Detekt

**Run Detekt:**
```bash
./gradlew detekt
```

View report: `build/reports/detekt/detekt.html`

**Configuration:** `config/detekt/detekt.yml`

### Code Style

Follow [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html):

- Use camelCase for variables and functions
- Use PascalCase for classes
- Use UPPER_SNAKE_CASE for constants
- Indent with 4 spaces
- Max line length: 120 characters

### Compose Best Practices

1. **State Hoisting**: Lift state to the appropriate level
2. **Recomposition**: Minimize unnecessary recompositions
3. **Side Effects**: Use LaunchedEffect, DisposableEffect appropriately
4. **Remember**: Use remember for expensive calculations
5. **Immutability**: Use immutable data classes for state

### Git Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -m "Add feature"`
3. Run tests: `./gradlew test`
4. Run Detekt: `./gradlew detekt`
5. Push and create PR: `git push origin feature/my-feature`

## API Integration

### Backend API

The apps integrate with a FastAPI backend providing REST and WebSocket APIs.

**Base URL:** `http://localhost:8000/api/`
**WebSocket URL:** `ws://localhost:8000/ws`

### API Documentation

Backend API documentation available at: `http://localhost:8000/docs`

### Authentication

All authenticated endpoints require JWT token:
```
Authorization: Bearer <jwt_token>
```

Token is automatically added by `AuthInterceptor`.

### WebSocket Communication

Real-time updates via WebSocket:

**Connection:**
```kotlin
webSocketManager.connect(token)
```

**Subscribe to messages:**
```kotlin
webSocketManager.messages
    .collect { message ->
        when (message) {
            is LocationUpdate -> handleLocationUpdate(message)
            is RideStatusUpdate -> handleStatusUpdate(message)
            // ...
        }
    }
```

### Error Handling

API errors are wrapped in `Result<T>`:

```kotlin
when (val result = repository.getData()) {
    is Result.Success -> {
        // Handle success
        val data = result.data
    }
    is Result.Error -> {
        // Handle error
        val message = result.message
    }
}
```

## Development Workflow

### Adding a New Feature

1. **Define Requirements**: Document in spec
2. **Create Models**: Add domain models in `core/domain/model/`
3. **Define Repository Interface**: Add in `core/domain/repository/`
4. **Implement Repository**: Add in `core/data/repository/`
5. **Create ViewModel**: Add in `core/domain/viewmodel/`
6. **Build UI**: Add screens in app module
7. **Write Tests**: Add unit and UI tests
8. **Update Navigation**: Add to navigation graph

### Adding a New API Endpoint

1. **Define DTO**: Add in `core/network/dto/`
2. **Add API Method**: Add to appropriate API interface in `core/network/api/`
3. **Update Repository**: Implement in repository
4. **Test**: Add integration test

### Adding a New Database Table

1. **Create Entity**: Add in `core/database/entity/`
2. **Create DAO**: Add in `core/database/dao/`
3. **Update Database**: Add entity to `AppDatabase`
4. **Create Migration**: Add migration if needed
5. **Test**: Add database test

## Troubleshooting

### Common Issues

**Build Errors:**
```bash
# Clean and rebuild
./gradlew clean build

# Invalidate caches (Android Studio)
File → Invalidate Caches → Invalidate and Restart
```

**Maps Not Showing:**
- Verify API key in `local.properties`
- Enable Maps SDK in Google Cloud Console
- Check API key restrictions

**Backend Connection Failed:**
- Verify backend is running
- Check URL configuration
- For emulator, use `10.0.2.2` instead of `localhost`
- For device, use computer's IP address

**Push Notifications Not Working:**
- Verify `google-services.json` is present
- Check FCM is enabled in Firebase Console
- Verify device token is registered with backend

**Location Not Updating:**
- Check location permissions granted
- Verify GPS is enabled
- Check battery optimization settings

### Debug Tools

**Logcat Filtering:**
```bash
# Filter by tag
adb logcat -s RideConnect

# Filter by package
adb logcat | grep com.rideconnect
```

**Network Inspection:**
- Use OkHttp logging interceptor (enabled in debug builds)
- Use Charles Proxy or similar tool

**Database Inspection:**
- Use Android Studio Database Inspector
- Or use `adb shell` to access database file

## Additional Resources

- [Android Developer Documentation](https://developer.android.com/)
- [Jetpack Compose Documentation](https://developer.android.com/jetpack/compose)
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [Hilt Documentation](https://dagger.dev/hilt/)
- [Room Documentation](https://developer.android.com/training/data-storage/room)
- [Retrofit Documentation](https://square.github.io/retrofit/)

## Support

For questions or issues:
1. Check this documentation
2. Review module README files
3. Check existing issues in repository
4. Contact the development team
