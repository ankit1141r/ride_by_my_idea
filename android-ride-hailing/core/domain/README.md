# Core Domain Module

## Overview

The Domain module contains the business logic layer of the application. It defines domain models, repository interfaces, use cases, and ViewModels that orchestrate the application's business rules.

## Architecture

This module follows Clean Architecture principles:
- **Domain Models**: Pure Kotlin data classes representing business entities
- **Repository Interfaces**: Contracts for data operations (implemented in the Data module)
- **ViewModels**: Presentation layer logic using MVVM pattern
- **Use Cases**: Optional layer for complex business logic (currently integrated into ViewModels)

## Key Components

### Models (`model/`)
- `User.kt`: User entity with authentication and profile data
- `Ride.kt`: Ride entity with status, locations, and fare information
- `Driver.kt`: Driver-specific entity with vehicle and availability data
- `Payment.kt`: Payment transaction entity
- `Rating.kt`: Rating and review entity
- `ScheduledRide.kt`: Scheduled ride entity
- `ParcelDelivery.kt`: Parcel delivery entity
- `Emergency.kt`: Emergency SOS entity

### Repository Interfaces (`repository/`)
Define contracts for data operations:
- `AuthRepository`: Authentication and token management
- `RideRepository`: Ride request and tracking
- `DriverRideRepository`: Driver-specific ride operations
- `ProfileRepository`: User profile management
- `PaymentRepository`: Payment processing
- `RatingRepository`: Rating and review operations
- `ChatRepository`: In-ride messaging
- `EmergencyRepository`: Emergency features
- `ParcelRepository`: Parcel delivery operations
- `ScheduledRideRepository`: Scheduled ride management

### ViewModels (`viewmodel/`)
Manage UI state and business logic:
- `AuthViewModel`: Login, OTP verification, biometric auth
- `RideViewModel`: Ride request, tracking, cancellation
- `DriverViewModel`: Driver availability, ride acceptance
- `ProfileViewModel`: Profile updates, emergency contacts
- `PaymentViewModel`: Payment processing, history
- `RatingViewModel`: Rating submission, history
- `ChatViewModel`: In-ride messaging
- `EmergencyViewModel`: SOS activation, emergency contacts
- `ParcelViewModel`: Parcel delivery requests
- `ScheduledRideViewModel`: Scheduled ride management
- `EarningsViewModel`: Driver earnings tracking
- `SettingsViewModel`: App settings and preferences
- `LocationSearchViewModel`: Location search and autocomplete

### WebSocket (`websocket/`)
- `WebSocketManager`: Interface for real-time communication
- `WebSocketMessage`: Sealed class hierarchy for message types

### Validation (`validation/`)
- `PhoneNumberValidator`: Phone number format validation

## Dependencies

- Kotlin Coroutines & Flow for asynchronous operations
- Hilt for dependency injection
- AndroidX Lifecycle for ViewModel support

## Usage Example

```kotlin
@HiltViewModel
class MyViewModel @Inject constructor(
    private val repository: MyRepository
) : ViewModel() {
    
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()
    
    fun performAction() {
        viewModelScope.launch {
            repository.getData()
                .collect { result ->
                    _state.value = when (result) {
                        is Result.Success -> UiState.Success(result.data)
                        is Result.Error -> UiState.Error(result.message)
                    }
                }
        }
    }
}
```

## Testing

Unit tests are located in `src/test/kotlin/` and focus on:
- ViewModel business logic
- Validation logic
- Domain model transformations

Property-based tests validate universal correctness properties using appropriate testing frameworks.
