# Core Network Module

## Overview

The Network module handles all HTTP and WebSocket communication with the backend API. It provides Retrofit service interfaces, OkHttp interceptors, and data transfer objects (DTOs).

## Architecture

- **API Services**: Retrofit interfaces defining HTTP endpoints
- **DTOs**: Data transfer objects for JSON serialization
- **Interceptors**: OkHttp interceptors for authentication and error handling
- **WebSocket Config**: WebSocket connection configuration

## Key Components

### API Services (`api/`)

Retrofit interfaces for backend communication:

- `RideApi`: Ride request, tracking, cancellation endpoints
- `DriverApi`: Driver availability, ride acceptance, earnings endpoints
- `LocationApi`: Location updates and search endpoints
- `PaymentApi`: Payment processing and history endpoints
- `RatingApi`: Rating submission and retrieval endpoints
- `ParcelApi`: Parcel delivery endpoints
- `EmergencyApi`: Emergency SOS endpoints

### DTOs (`dto/`)

Data transfer objects matching backend API contracts:

- `AuthDto`: Authentication request/response
- `RideDto`: Ride data structures
- `DriverDto`: Driver-specific data
- `PaymentDto`: Payment transaction data
- `RatingDto`: Rating and review data
- `ScheduledRideDto`: Scheduled ride data
- `ParcelDto`: Parcel delivery data
- `EmergencyDto`: Emergency data
- `ProfileDto`: User profile data

### Interceptors (`interceptor/`)

- `AuthInterceptor`: Adds JWT token to all authenticated requests
- `ErrorInterceptor`: Handles HTTP error responses and token refresh

### Security (`security/`)

- `CertificatePinner`: SSL certificate pinning for secure connections

### Configuration (`config/`)

- `WebSocketConfig`: WebSocket connection settings

## Dependency Injection (`di/`)

`NetworkModule` provides:
- OkHttpClient with interceptors and timeouts
- Retrofit instance with Gson converter
- All API service interfaces

## API Configuration

### Base URLs

```kotlin
// Rider & Driver Apps
BASE_URL = "http://10.0.2.2:8000/api/"  // Android Emulator
WS_URL = "ws://10.0.2.2:8000/ws"        // WebSocket

// Production (update in build.gradle.kts)
BASE_URL = "https://api.rideconnect.com/api/"
WS_URL = "wss://api.rideconnect.com/ws"
```

### Timeouts

- Connect timeout: 30 seconds
- Read timeout: 30 seconds
- Write timeout: 30 seconds
- Upload timeout: 60 seconds

### Authentication

All authenticated endpoints require JWT token in header:
```
Authorization: Bearer <jwt_token>
```

Token is automatically added by `AuthInterceptor`.

### Error Handling

HTTP status codes are handled by `ErrorInterceptor`:
- 401 Unauthorized → Trigger token refresh
- 403 Forbidden → Clear session and redirect to login
- 404 Not Found → Return error message
- 500+ Server Error → Return generic error message

### Retry Logic

Network requests use exponential backoff retry:
- Max attempts: 3
- Initial delay: 1 second
- Backoff multiplier: 2x
- Max delay: 30 seconds

## Usage Example

```kotlin
interface RideApi {
    @POST("rides/request")
    suspend fun requestRide(
        @Body request: RideRequestDto
    ): Response<RideDto>
    
    @GET("rides/{rideId}")
    suspend fun getRideDetails(
        @Path("rideId") rideId: String
    ): Response<RideDto>
    
    @POST("rides/{rideId}/cancel")
    suspend fun cancelRide(
        @Path("rideId") rideId: String,
        @Body reason: CancelReasonDto
    ): Response<Unit>
}
```

## WebSocket Communication

WebSocket connection for real-time updates:

### Connection
```kotlin
val webSocket = okHttpClient.newWebSocket(
    request = Request.Builder()
        .url(WS_URL)
        .addHeader("Authorization", "Bearer $token")
        .build(),
    listener = webSocketListener
)
```

### Message Types
- `LocationUpdate`: Real-time driver location
- `RideStatusUpdate`: Ride status changes
- `RideRequest`: New ride request for drivers
- `ChatMessage`: In-ride messages

### Reconnection
- Automatic reconnection on connection loss
- Exponential backoff: 1s, 2s, 4s, 8s, max 30s
- Heartbeat/ping every 30 seconds

## Testing

Mock API responses for testing:
```kotlin
@Test
fun `test ride request success`() = runTest {
    val mockResponse = RideDto(...)
    coEvery { rideApi.requestRide(any()) } returns Response.success(mockResponse)
    
    val result = repository.requestRide(request)
    
    assertTrue(result is Result.Success)
}
```

## Dependencies

- Retrofit 2.9.0
- OkHttp 4.12.0
- Gson for JSON serialization
- Hilt for dependency injection
