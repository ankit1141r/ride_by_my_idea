# Core Data Module

## Overview

The Data module implements the repository interfaces defined in the Domain module. It handles data operations from multiple sources including network APIs, local database, and device sensors.

## Architecture

This module follows the Repository pattern:
- **Repository Implementations**: Concrete implementations of domain repository interfaces
- **Data Mappers**: Convert between DTOs (network) and domain models
- **Local Data Sources**: Room database DAOs
- **Remote Data Sources**: Retrofit API services
- **Device Data Sources**: Location services, biometric authentication

## Key Components

### Repository Implementations (`repository/`)
- `AuthRepositoryImpl`: Authentication with token management
- `RideRepositoryImpl`: Ride operations with WebSocket integration
- `DriverRideRepositoryImpl`: Driver-specific ride operations
- `ProfileRepositoryImpl`: Profile management with image compression
- `PaymentRepositoryImpl`: Payment processing with local caching
- `RatingRepositoryImpl`: Rating operations with offline queueing
- `ChatRepositoryImpl`: Chat with offline message queueing
- `EmergencyRepositoryImpl`: Emergency features
- `ParcelRepositoryImpl`: Parcel delivery operations
- `ScheduledRideRepositoryImpl`: Scheduled ride management
- `EarningsRepositoryImpl`: Driver earnings tracking
- `SettingsRepositoryImpl`: App settings persistence
- `LocationRepositoryImpl`: Location tracking and search

### Data Mappers (`mapper/`)
Convert between data transfer objects and domain models:
- `AuthMapper`: Auth DTOs ↔ User models
- `RideMapper`: Ride DTOs ↔ Ride models
- `PaymentMapper`: Payment DTOs ↔ Payment models
- `RatingMapper`: Rating DTOs ↔ Rating models
- `EarningsMapper`: Earnings DTOs ↔ Earnings models

### Location Services (`location/`)
- `LocationServiceImpl`: FusedLocationProviderClient wrapper
- `LocationForegroundService`: Background location tracking for drivers
- `LocationRepositoryImpl`: Location operations and Google Places integration

### WebSocket (`websocket/`)
- `WebSocketManagerImpl`: OkHttp WebSocket implementation with reconnection logic
- `MessageSizeOptimizer`: Optimize WebSocket message payloads

### Biometric (`biometric/`)
- `BiometricAuthManagerImpl`: BiometricPrompt wrapper for fingerprint/face authentication

### Notification (`notification/`)
- `RideConnectFirebaseMessagingService`: FCM message handling
- `NotificationManagerImpl`: Local notification management
- `NotificationHandler`: Notification type routing

### Sync (`sync/`)
- `SyncManager`: Offline action queueing and synchronization
- `SyncScheduler`: WorkManager scheduling for periodic sync

### Workers (`worker/`)
- `SyncWorker`: Background sync worker
- `ScheduledRideReminderWorker`: Scheduled ride reminder notifications
- `ScheduledRideReminderManager`: Reminder scheduling

### Local Storage (`local/`)
- `TokenManager`: Secure token storage using EncryptedSharedPreferences

## Dependency Injection (`di/`)

Hilt modules provide dependencies:
- `RepositoryModule`: Repository implementations
- Additional modules in Network and Database modules

## Data Flow

```
UI Layer (ViewModels)
    ↓
Domain Layer (Repository Interfaces)
    ↓
Data Layer (Repository Implementations)
    ↓
    ├─→ Network (Retrofit APIs)
    ├─→ Database (Room DAOs)
    └─→ Device (Location, Biometric)
```

## Error Handling

All repository methods return `Result<T>` or `Flow<Result<T>>`:
- `Result.Success<T>`: Operation succeeded with data
- `Result.Error`: Operation failed with error message

## Offline Support

- Actions performed offline are queued in `SyncManager`
- Queued actions sync automatically when network is restored
- Local database caches data for offline access

## Testing

Tests are located in `src/test/kotlin/` and include:
- Repository unit tests with mocked dependencies
- Mapper tests for data transformations
- Integration tests for complex flows

## Dependencies

- Retrofit & OkHttp for networking
- Room for local database
- Google Play Services for location and maps
- Firebase Cloud Messaging for push notifications
- WorkManager for background tasks
- Hilt for dependency injection
