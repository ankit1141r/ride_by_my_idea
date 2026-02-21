# Core Common Module

## Overview

The Common module contains shared utilities, UI components, themes, and resources used across both Rider and Driver apps. It promotes code reuse and consistency.

## Architecture

- **UI Components**: Reusable Compose components
- **Theme**: Material Design 3 theme with light/dark mode
- **Utilities**: Helper functions and extensions
- **Navigation**: Shared navigation definitions
- **Resources**: Strings, colors, dimensions

## Key Components

### UI Components (`ui/`)

Reusable Compose components:

#### Ride Management
- `RideRequestScreen`: Location selection and fare estimation
- `RideTrackingScreen`: Real-time ride tracking with map
- `ScheduleRideScreen`: Schedule future rides
- `ScheduledRidesScreen`: View scheduled rides
- `RideHistoryScreen`: Past ride history
- `RideReceiptScreen`: Ride receipt details

#### Parcel Delivery
- `ParcelDeliveryScreen`: Request parcel delivery
- `ParcelTrackingScreen`: Track parcel delivery

#### Payment
- `PaymentScreen`: Payment processing
- `PaymentHistoryScreen`: Payment transaction history
- `ReceiptScreen`: Payment receipt

#### Rating & Review
- `RatingDialog`: Submit rating and review
- `RatingHistoryScreen`: View rating history

#### Chat & Emergency
- `ChatScreen`: In-ride messaging
- `EmergencySOSButton`: Emergency SOS button
- `EmergencyContactsScreen`: Manage emergency contacts
- `RideShareDialog`: Share ride with contacts

#### Profile & Settings
- `ProfileScreen`: User profile management
- `SettingsScreen`: App settings
- `NotificationPreferencesScreen`: Notification settings
- `NotificationPreferencesDialog`: Quick notification settings

#### Offline & Sync
- `OfflineModeIndicator`: Show offline status
- `OfflineBlocker`: Block actions when offline

#### Error Handling
- `ErrorComponents`: Error dialogs and snackbars

### Theme (`theme/`)

Material Design 3 theme with customization:

```kotlin
// Color.kt
val PrimaryLight = Color(0xFF6750A4)
val PrimaryDark = Color(0xFFD0BCFF)

// Theme.kt
@Composable
fun RideConnectTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) darkColorScheme else lightColorScheme
    
    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
```

#### Map Theme
- `MapTheme.kt`: Map styling for light/dark modes

### Utilities (`util/`)

Helper functions and utilities:

- `ImageCompressionUtil`: Compress images before upload
- `BatteryOptimizationUtil`: Battery usage optimization
- `StartupProfiler`: App startup time profiling
- `LanguageUtil`: Language switching
- `RideReceiptShareUtil`: Share ride receipts
- `ReceiptShareUtil`: Share payment receipts

### Navigation (`navigation/`)

- `Screen`: Sealed class defining all app screens
- `NavigationHelper`: Navigation utilities

### Compose Performance (`compose/`)

- `ComposePerformanceUtils`: Optimize Compose recompositions

### Animation (`animation/`)

- `AnimationOptimizer`: Optimize animations for performance

### Map Utilities (`map/`)

- `GoogleMapComposable`: Google Maps Compose wrapper
- `MapMarkers`: Custom map markers
- `MapCameraControl`: Camera control utilities
- `MapPerformanceOptimizer`: Map performance optimization
- `MapTileCacheConfig`: Map tile caching

### Image Loading (`image/`)

- `CoilConfiguration`: Coil image loading configuration

### Pagination (`pagination/`)

- `PaginationHelper`: Pagination utilities for lists

### Security (`security/`)

- `SecureStorageManager`: Secure data storage
- `InputValidator`: Input validation and sanitization
- `DataCleaner`: Clear sensitive data

### Error Handling (`error/`)

- `ErrorHandler`: Centralized error handling

### Network (`network/`)

- `SafeApiCall`: Safe API call wrapper
- `NetworkExtensions`: Network utility extensions

### Result (`result/`)

- `Result`: Sealed class for operation results

### Accessibility (`accessibility/`)

- `AccessibilityUtils`: Accessibility helper functions

### Permission (`permission/`)

- `LocationPermissionHandler`: Location permission handling
- `LocationPermissionComposable`: Permission UI

### Base (`base/`)

- `BaseApplication`: Base application class with initialization

### Startup (`startup/`)

- `AppInitializer`: App initialization logic
- `StartupOptimizationGuide.md`: Startup optimization guide

## Resources (`res/`)

### Strings (`values/strings.xml`, `values-hi/strings.xml`)
- English and Hindi translations
- All UI strings for localization

### Colors
- Defined in `theme/Color.kt`
- Material Design 3 color system

### Dimensions
- Consistent spacing and sizing

## Usage Example

### Using Reusable Components

```kotlin
@Composable
fun MyScreen() {
    RideConnectTheme {
        Scaffold(
            topBar = { /* App bar */ }
        ) { padding ->
            RideHistoryScreen(
                rides = rides,
                onRideClick = { ride -> /* Navigate */ },
                modifier = Modifier.padding(padding)
            )
        }
    }
}
```

### Using Utilities

```kotlin
// Image compression
val compressedImage = ImageCompressionUtil.compressImage(
    context = context,
    imageUri = uri,
    maxSizeKB = 500
)

// Language switching
LanguageUtil.setAppLanguage(context, "hi") // Switch to Hindi
```

### Using Theme

```kotlin
@Composable
fun App() {
    val darkTheme = remember { mutableStateOf(false) }
    
    RideConnectTheme(darkTheme = darkTheme.value) {
        // App content
    }
}
```

## Accessibility

All components follow accessibility best practices:
- Content descriptions for screen readers
- Minimum touch target size (48dp)
- Sufficient color contrast (WCAG 2.1 Level AA)
- Support for text scaling
- Keyboard and switch navigation

## Performance

Performance optimizations:
- Lazy loading for lists
- Image caching with Coil
- Compose recomposition optimization
- Map tile caching
- Animation frame rate optimization

## Testing

UI components can be tested with Compose testing:

```kotlin
@Test
fun testRatingDialog() {
    composeTestRule.setContent {
        RatingDialog(
            onDismiss = {},
            onSubmit = { rating, review -> }
        )
    }
    
    composeTestRule
        .onNodeWithTag("rating_star_5")
        .performClick()
    
    composeTestRule
        .onNodeWithTag("submit_button")
        .assertIsEnabled()
}
```

## Dependencies

- Jetpack Compose
- Material Design 3
- Coil for image loading
- Google Maps Compose
- Accompanist for permissions
- Hilt for dependency injection
