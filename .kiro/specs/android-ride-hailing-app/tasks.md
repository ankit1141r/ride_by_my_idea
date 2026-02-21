# Implementation Plan: Android Ride-Hailing Application

## Overview

This implementation plan breaks down the development of two native Android applications (Rider App and Driver App) into discrete, manageable tasks. The plan follows an incremental approach where each task builds on previous work, with testing integrated throughout. The implementation uses Kotlin, Jetpack Compose, MVVM architecture, and integrates with the existing FastAPI backend.

## Tasks

- [x] 1. Project Setup and Core Infrastructure
  - Create multi-module Android project structure (rider-app, driver-app, core modules)
  - Configure Gradle build files with all dependencies (Compose, Hilt, Retrofit, Room, etc.)
  - Set up Hilt dependency injection framework
  - Configure ProGuard rules for release builds
  - Set up Firebase project and integrate FCM
  - _Requirements: 30.1, 19.1_

- [-] 2. Implement Authentication Module
  - [x] 2.1 Create authentication data models and API interfaces
    - Define AuthToken, User data classes
    - Create AuthApi interface with Retrofit annotations for OTP endpoints
    - Implement EncryptedSharedPreferences wrapper for secure token storage
    - _Requirements: 1.1, 1.2, 1.8_

  - [x]* 2.2 Write property test for phone number validation
    - **Property 1: Phone Number Validation**
    - **Validates: Requirements 1.6**

  - [x] 2.3 Implement AuthRepository with token management
    - Create AuthRepositoryImpl with OTP send/verify methods
    - Implement token storage and retrieval using EncryptedSharedPreferences
    - Add token refresh logic with automatic retry
    - _Requirements: 1.2, 1.4, 1.5_

  - [ ]* 2.4 Write property test for token refresh on expiration
    - **Property 2: Token Refresh on Expiration**
    - **Validates: Requirements 1.4**

  - [ ]* 2.5 Write property test for token storage round-trip
    - **Property 3: Token Storage Round-Trip**
    - **Validates: Requirements 1.2**

  - [x] 2.6 Create AuthViewModel with login/logout flows
    - Implement phone number input validation
    - Handle OTP verification state management
    - Manage authentication state with StateFlow
    - _Requirements: 1.1, 1.2, 1.5, 1.6_

  - [x] 2.7 Build authentication UI screens with Jetpack Compose
    - Create LoginScreen with phone number input
    - Create OTPVerificationScreen with code input
    - Add loading states and error handling UI
    - _Requirements: 1.1, 1.2, 1.6, 1.7_

  - [ ]* 2.8 Write unit tests for AuthViewModel
    - Test successful login flow
    - Test OTP verification with invalid code
    - Test network error handling
    - _Requirements: 1.1, 1.2, 1.7_

- [ ] 3. Implement Biometric Authentication
  - [x] 3.1 Create BiometricAuthManager
    - Check biometric availability on device
    - Implement biometric prompt using BiometricPrompt API
    - Store biometric preference in EncryptedSharedPreferences
    - _Requirements: 1.3, 24.8_

  - [x] 3.2 Integrate biometric auth into login flow
    - Add biometric option to LoginScreen
    - Handle biometric authentication success/failure
    - Fall back to OTP if biometric fails
    - _Requirements: 1.3_

  - [ ]* 3.3 Write unit tests for biometric authentication
    - Test biometric availability check
    - Test successful biometric authentication
    - Test fallback to OTP on failure
    - _Requirements: 1.3_


- [ ] 4. Implement Network Layer with Retrofit and OkHttp
  - [x] 4.1 Create OkHttp interceptors
    - Implement AuthInterceptor to add JWT token to requests
    - Implement ErrorInterceptor for HTTP status code handling
    - Configure timeout values (30s for API, 60s for uploads)
    - _Requirements: 30.2, 30.3, 30.6_

  - [ ]* 4.2 Write property test for HTTP status code handling
    - **Property 31: HTTP Status Code Handling**
    - **Validates: Requirements 30.3**

  - [ ]* 4.3 Write property test for token refresh on 401
    - **Property 32: Token Refresh on 401**
    - **Validates: Requirements 30.4**

  - [x] 4.4 Create Retrofit API service interfaces
    - Define RideApi, DriverApi, LocationApi, PaymentApi, RatingApi, ParcelApi, EmergencyApi
    - Add all endpoint methods with proper annotations
    - Configure Gson/Moshi for JSON parsing
    - _Requirements: 30.1, 30.7_

  - [x] 4.5 Implement retry logic with exponential backoff
    - Create retryWithExponentialBackoff utility function
    - Configure max attempts and delay parameters
    - _Requirements: 30.8_

  - [ ]* 4.6 Write property test for network retry with exponential backoff
    - **Property 33: Network Retry with Exponential Backoff**
    - **Validates: Requirements 30.8**

  - [ ]* 4.7 Write integration tests for API clients
    - Test API calls with mock server
    - Test error handling and retry logic
    - Test token refresh flow
    - _Requirements: 30.1, 30.3, 30.4, 30.8_

- [ ] 5. Implement Room Database for Local Storage
  - [x] 5.1 Define Room entities
    - Create UserEntity, RideEntity, ScheduledRideEntity, TransactionEntity
    - Create ChatMessageEntity, EmergencyContactEntity, ParcelDeliveryEntity
    - Add proper indices and foreign key relationships
    - _Requirements: 20.1, 20.2, 20.3_

  - [x] 5.2 Create DAO interfaces
    - Implement RideDao with CRUD operations and queries
    - Implement TransactionDao, ChatMessageDao, EmergencyContactDao
    - Use Flow for reactive queries
    - _Requirements: 20.1, 20.2, 28.1, 28.7_

  - [x] 5.3 Build AppDatabase class
    - Configure Room database with all entities and DAOs
    - Set up database migrations strategy
    - _Requirements: 20.1_

  - [ ]* 5.4 Write integration tests for database operations
    - Test CRUD operations for all entities
    - Test Flow queries for reactive updates
    - Test database migrations
    - _Requirements: 20.1, 20.2_

- [ ] 6. Implement Location Services Module
  - [x] 6.1 Create LocationService with FusedLocationProviderClient
    - Implement startLocationUpdates and stopLocationUpdates
    - Configure location request with balanced power mode
    - Expose location updates as Flow
    - _Requirements: 29.2, 29.3, 23.2_

  - [x] 6.2 Create LocationForegroundService for background tracking
    - Implement foreground service with notification
    - Start/stop location updates based on driver availability
    - Send location updates to backend every 10 seconds
    - _Requirements: 11.1, 11.2, 11.3, 29.5_

  - [ ]* 6.3 Write property test for location update frequency
    - **Property 6: Location Update Frequency**
    - **Validates: Requirements 11.3**

  - [ ]* 6.4 Write property test for GPS accuracy warning
    - **Property 7: GPS Accuracy Warning**
    - **Validates: Requirements 29.4**

  - [x] 6.5 Implement LocationRepository
    - Create methods for updateLocation, searchPlaces, getPlaceDetails, calculateRoute
    - Integrate Google Places API for location search
    - _Requirements: 18.3, 18.4_

  - [x] 6.6 Handle location permissions
    - Request location permissions with rationale
    - Handle permission denial gracefully
    - Request background location permission for Driver App
    - _Requirements: 29.1, 29.5, 29.7_

  - [ ]* 6.7 Write unit tests for location services
    - Test location permission handling
    - Test location update flow
    - Test GPS accuracy warnings
    - _Requirements: 29.1, 29.2, 29.4, 29.7_


- [ ] 7. Implement Google Maps Integration
  - [x] 7.1 Set up Google Maps SDK
    - Add Google Maps dependency and API key configuration
    - Create MapView composable wrapper
    - Implement map initialization and lifecycle handling
    - _Requirements: 18.1, 18.2_

  - [x] 7.2 Implement map features
    - Add marker placement and updates
    - Implement polyline drawing for routes
    - Add map gesture support (pan, zoom, rotate)
    - Display traffic information overlay
    - _Requirements: 18.2, 18.5, 18.6, 18.8_

  - [x] 7.3 Implement camera control
    - Auto-adjust camera bounds to show all markers
    - Smooth camera animations for location updates
    - _Requirements: 6.8, 18.7_

  - [ ]* 7.4 Write property test for map camera bounds
    - **Property 23: Map Camera Bounds for Multiple Markers**
    - **Validates: Requirements 18.7**

  - [x] 7.5 Integrate location search with Google Places
    - Create LocationSearchBar composable
    - Implement autocomplete with Places API
    - Display search results and handle selection
    - _Requirements: 18.3, 18.4_

  - [ ]* 7.6 Write unit tests for map functionality
    - Test marker placement and updates
    - Test camera bounds calculation
    - Test location search integration
    - _Requirements: 18.2, 18.3, 18.7_

- [ ] 8. Implement WebSocket Module for Real-Time Communication
  - [x] 8.1 Create WebSocketManager with OkHttp WebSocket
    - Implement connect/disconnect methods
    - Handle WebSocket authentication with JWT token
    - Implement message sending and receiving
    - _Requirements: 17.1, 17.2, 17.3_

  - [x] 8.2 Implement reconnection logic with exponential backoff
    - Auto-reconnect on connection loss
    - Use exponential backoff (1s, 2s, 4s, 8s, max 30s)
    - Maintain connection state with StateFlow
    - _Requirements: 17.4, 17.7_

  - [ ]* 8.3 Write property test for WebSocket reconnection backoff
    - **Property 14: WebSocket Reconnection with Exponential Backoff**
    - **Validates: Requirements 17.4**

  - [x] 8.4 Define WebSocket message types
    - Create sealed class hierarchy for message types
    - Implement JSON serialization/deserialization
    - Handle LocationUpdate, RideStatusUpdate, RideRequest, ChatMessage types
    - _Requirements: 17.5, 17.6_

  - [ ]* 8.5 Write property test for WebSocket update latency
    - **Property 13: WebSocket Update Latency**
    - **Validates: Requirements 6.6, 17.6**

  - [x] 8.6 Implement heartbeat/ping mechanism
    - Send ping every 30 seconds to keep connection alive
    - Handle pong responses
    - _Requirements: 17.3_

  - [ ]* 8.7 Write integration tests for WebSocket
    - Test connection establishment and authentication
    - Test message sending and receiving
    - Test reconnection on connection loss
    - _Requirements: 17.1, 17.2, 17.4_

- [x] 9. Checkpoint - Core Infrastructure Complete
  - Ensure all tests pass for authentication, networking, database, location, and WebSocket modules
  - Verify integration between modules
  - Ask the user if questions arise

- [ ] 10. Implement Profile Management Module
  - [x] 10.1 Create profile data models and API
    - Define ProfileUpdateRequest, VehicleDetails data classes
    - Add profile endpoints to API interfaces
    - _Requirements: 2.1, 2.5, 2.6_

  - [x] 10.2 Implement ProfileRepository
    - Create methods for updateProfile, uploadPhoto, addEmergencyContact
    - Implement image compression before upload
    - Handle offline queueing for profile updates
    - _Requirements: 2.1, 2.2, 2.3, 2.7_

  - [ ]* 10.3 Write property test for profile update validation
    - **Property 12: Profile Update Validation**
    - **Validates: Requirements 2.1**

  - [ ]* 10.4 Write property test for image compression ratio
    - **Property 10: Image Compression Ratio**
    - **Validates: Requirements 2.3, 23.3**

  - [ ]* 10.5 Write property test for local cache update on success
    - **Property 34: Local Cache Update on Success**
    - **Validates: Requirements 2.2**

  - [x] 10.6 Create ProfileViewModel
    - Manage profile state with StateFlow
    - Handle profile updates and photo uploads
    - Manage emergency contacts list
    - _Requirements: 2.1, 2.2, 2.3, 9.7_

  - [x] 10.7 Build profile UI screens
    - Create ProfileScreen with editable fields
    - Create EmergencyContactsScreen with add/remove functionality
    - Add photo picker and upload UI
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 2.6, 9.7_

  - [ ]* 10.8 Write unit tests for profile management
    - Test profile update validation
    - Test image compression
    - Test emergency contact management
    - _Requirements: 2.1, 2.3, 9.7_


- [ ] 11. Implement Ride Request Module (Rider App)
  - [x] 11.1 Create ride data models and API interfaces
    - Define RideRequest, Ride, FareEstimate data classes
    - Add ride endpoints to RideApi interface
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 11.2 Implement RideRepository
    - Create methods for requestRide, cancelRide, getRideDetails, getRideHistory
    - Implement WebSocket subscription for active ride updates
    - Handle ride state transitions
    - _Requirements: 3.3, 3.4, 3.5, 28.1_

  - [ ]* 11.3 Write property test for service radius validation
    - **Property 5: Service Radius Validation**
    - **Validates: Requirements 3.7, 5.8**

  - [ ]* 11.4 Write property test for fare breakdown completeness
    - **Property 18: Fare Breakdown Completeness**
    - **Validates: Requirements 7.1**

  - [x] 11.5 Create RideViewModel for Rider App
    - Manage ride request state with StateFlow
    - Handle fare estimation
    - Track active ride status and driver location
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 6.1, 6.2_

  - [x] 11.6 Build ride request UI screens
    - Create RideRequestScreen with location selection
    - Display fare estimate before confirmation
    - Show ride status and driver details after acceptance
    - _Requirements: 3.1, 3.2, 3.3, 3.5_

  - [x] 11.7 Implement real-time ride tracking UI
    - Display driver location on map with smooth animations
    - Show ETA and route polyline
    - Update UI based on WebSocket messages
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.6, 6.8_

  - [ ]* 11.8 Write unit tests for ride request flow
    - Test ride request validation
    - Test fare estimation
    - Test ride cancellation
    - _Requirements: 3.3, 3.7_

- [ ] 12. Implement Scheduled Rides Module
  - [x] 12.1 Create scheduled ride data models and API
    - Define ScheduledRideRequest, ScheduledRide data classes
    - Add scheduled ride endpoints to API
    - _Requirements: 4.1, 4.4_

  - [x] 12.2 Implement ScheduledRideRepository
    - Create methods for scheduleRide, cancelScheduledRide, getScheduledRides
    - Store scheduled rides in Room database
    - _Requirements: 4.4, 4.6, 4.7_

  - [ ]* 12.3 Write property test for maximum advance scheduling
    - **Property 8: Maximum Advance Scheduling**
    - **Validates: Requirements 4.2**

  - [ ]* 12.4 Write property test for minimum advance scheduling
    - **Property 9: Minimum Advance Scheduling**
    - **Validates: Requirements 4.3**

  - [x] 12.5 Create ScheduledRideViewModel
    - Manage scheduled rides list
    - Handle scheduling validation (1 hour min, 7 days max)
    - _Requirements: 4.1, 4.2, 4.3, 4.7_

  - [x] 12.6 Build scheduled rides UI
    - Create ScheduleRideScreen with date-time picker
    - Display list of scheduled rides
    - Add cancel functionality
    - _Requirements: 4.1, 4.2, 4.3, 4.6, 4.7_

  - [x] 12.7 Implement scheduled ride reminders
    - Schedule WorkManager job for 30 minutes before ride
    - Send push notification reminder
    - _Requirements: 4.5_

  - [ ]* 12.8 Write unit tests for scheduled rides
    - Test scheduling validation
    - Test scheduled ride creation and cancellation
    - Test reminder scheduling
    - _Requirements: 4.2, 4.3, 4.5_

- [ ] 13. Implement Parcel Delivery Module
  - [x] 13.1 Create parcel delivery data models and API
    - Define ParcelDeliveryRequest, ParcelDelivery, ParcelSize enum
    - Add parcel endpoints to ParcelApi interface
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 13.2 Implement ParcelRepository
    - Create methods for requestParcelDelivery, confirmPickup, confirmDelivery
    - Handle parcel status updates via WebSocket
    - _Requirements: 5.3, 5.6, 5.7, 15.3, 15.5, 15.7_

  - [x] 13.3 Create ParcelViewModel for Rider App
    - Manage parcel delivery request state
    - Handle sender/recipient information
    - Track parcel status
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 13.4 Build parcel delivery UI for Rider App
    - Create ParcelDeliveryScreen with size selection
    - Add sender/recipient contact forms
    - Display parcel tracking information
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 13.5 Implement parcel delivery handling for Driver App
    - Add parcel acceptance preference in driver settings
    - Display parcel details in ride request
    - Add confirm pickup/delivery buttons
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_

  - [ ]* 13.6 Write unit tests for parcel delivery
    - Test parcel request validation
    - Test parcel status transitions
    - Test driver parcel preferences
    - _Requirements: 5.1, 5.8, 15.1_


- [ ] 14. Implement Driver Availability and Ride Request Handling (Driver App)
  - [x] 14.1 Create driver-specific data models and API
    - Define AvailabilityRequest, RideRequest notification data classes
    - Add driver endpoints to DriverApi interface
    - _Requirements: 11.1, 11.2, 12.1_

  - [x] 14.2 Implement DriverRideRepository
    - Create methods for setAvailability, acceptRide, rejectRide, startRide, completeRide
    - Subscribe to ride request notifications via WebSocket
    - _Requirements: 11.1, 11.2, 12.4, 12.5, 13.3, 13.5, 13.6_

  - [x] 14.3 Create DriverViewModel
    - Manage online/offline status with StateFlow
    - Handle incoming ride requests with countdown timer
    - Track active ride state
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 12.1, 12.2, 12.3_

  - [ ]* 14.4 Write property test for ride request countdown timer
    - **Property 16: Ride Request Countdown Timer**
    - **Validates: Requirements 12.3**

  - [ ]* 14.5 Write property test for auto-reject on timer expiration
    - **Property 17: Auto-Reject on Timer Expiration**
    - **Validates: Requirements 12.6**

  - [x] 14.6 Build driver home screen UI
    - Create DriverHomeScreen with online/offline toggle
    - Display current status and earnings summary
    - Show battery warning when below 15%
    - _Requirements: 11.1, 11.2, 11.4, 11.6, 14.1_

  - [x] 14.7 Implement ride request notification UI
    - Create RideRequestDialog with countdown timer
    - Display pickup, dropoff, and fare information
    - Add accept/reject buttons with sound notification
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.7_

  - [x] 14.8 Handle multiple ride requests
    - Queue incoming requests
    - Display one request at a time
    - _Requirements: 12.8_

  - [ ]* 14.9 Write unit tests for driver availability
    - Test online/offline toggle
    - Test ride request handling
    - Test countdown timer logic
    - _Requirements: 11.1, 11.2, 12.3, 12.6_

- [ ] 15. Implement Navigation and Ride Execution (Driver App)
  - [x] 15.1 Integrate Google Maps navigation
    - Display turn-by-turn navigation to pickup location
    - Switch to dropoff navigation after ride starts
    - _Requirements: 13.1, 13.4_

  - [x] 15.2 Create ActiveRideScreen for Driver App
    - Display navigation map with route
    - Show "Start Ride" button at pickup location
    - Show "Complete Ride" button at dropoff location
    - Display rider contact options (call/chat)
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_

  - [x] 15.3 Implement ride cancellation for drivers
    - Add cancel button with reason selection
    - Send cancellation to backend
    - _Requirements: 13.8_

  - [x] 15.4 Handle ride status transitions
    - Update ride status via API on each action
    - Sync status changes with WebSocket
    - _Requirements: 13.3, 13.5, 13.6_

  - [ ]* 15.5 Write unit tests for ride execution
    - Test ride status transitions
    - Test navigation flow
    - Test ride cancellation
    - _Requirements: 13.3, 13.5, 13.6, 13.8_

- [ ] 16. Checkpoint - Ride Management Complete
  - Ensure all tests pass for ride request, scheduled rides, parcel delivery, and driver modules
  - Verify end-to-end ride flow from request to completion
  - Ask the user if questions arise

- [ ] 17. Implement Payment Module
  - [x] 17.1 Create payment data models and API
    - Define PaymentRequest, Transaction, Receipt data classes
    - Add payment endpoints to PaymentApi interface
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 17.2 Implement PaymentRepository
    - Create methods for processPayment, getPaymentHistory, getReceipt
    - Store transactions in Room database
    - _Requirements: 7.2, 7.3, 7.5, 7.6_

  - [x] 17.3 Create PaymentViewModel
    - Manage payment state with StateFlow
    - Handle payment success/failure
    - Load payment history
    - _Requirements: 7.2, 7.3, 7.4, 7.5_

  - [x] 17.4 Build payment UI screens
    - Create PaymentScreen with fare breakdown
    - Display payment confirmation and receipt
    - Show payment history list
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.6, 7.7_

  - [x] 17.5 Implement receipt generation and sharing
    - Generate receipt with all ride details
    - Add share functionality (PDF/image export)
    - _Requirements: 7.3, 7.6, 7.7, 28.6_

  - [ ]* 17.6 Write unit tests for payment processing
    - Test payment flow
    - Test error handling
    - Test receipt generation
    - _Requirements: 7.2, 7.3, 7.4_


- [ ] 18. Implement Rating and Review System
  - [x] 18.1 Create rating data models and API
    - Define RatingRequest, Rating data classes
    - Add rating endpoints to RatingApi interface
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 18.2 Implement RatingRepository
    - Create methods for submitRating, getRatings, getAverageRating
    - Store ratings in Room database for offline access
    - Queue ratings for sync when offline
    - _Requirements: 8.3, 8.5, 8.6, 8.7_

  - [ ]* 18.3 Write property test for review character limit
    - **Property 11: Review Character Limit**
    - **Validates: Requirements 8.2**

  - [x] 18.4 Create RatingViewModel
    - Manage rating submission state
    - Load user's average rating
    - Handle offline queueing
    - _Requirements: 8.1, 8.3, 8.6, 8.7_

  - [x] 18.5 Build rating UI components
    - Create RatingDialog with star selection and review text
    - Display average rating on profile
    - Show rating history list
    - _Requirements: 8.1, 8.2, 8.4, 8.5, 8.6_

  - [x] 18.6 Implement driver rating features
    - Display driver's average rating on dashboard
    - Show performance metrics (acceptance rate, cancellation rate)
    - Display rating breakdown by star count
    - Show improvement suggestions for low ratings
    - _Requirements: 16.1, 16.2, 16.3, 16.5, 16.7_

  - [x] 18.7 Add rider rating for drivers
    - Prompt driver to rate rider after ride completion
    - _Requirements: 16.4_

  - [ ]* 18.8 Write unit tests for rating system
    - Test rating submission validation
    - Test offline queueing
    - Test rating sync
    - _Requirements: 8.3, 8.4, 8.7_

- [ ] 19. Implement Chat Module
  - [x] 19.1 Create chat data models
    - Define ChatMessage, MessageStatus enum
    - Add chat message entity to Room database
    - _Requirements: 10.1, 10.4, 10.5, 10.7_

  - [x] 19.2 Implement ChatRepository
    - Create methods for sendMessage, observeMessages, markAsRead
    - Send messages via WebSocket
    - Store messages in Room database
    - Queue messages when offline
    - _Requirements: 10.2, 10.5, 10.6, 10.8_

  - [ ]* 19.3 Write property test for message delivery status progression
    - **Property 15: Message Delivery Status Progression**
    - **Validates: Requirements 10.7**

  - [x] 19.4 Create ChatViewModel
    - Manage chat messages with StateFlow
    - Handle message sending and receiving
    - Track unread message count
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.7_

  - [x] 19.5 Build chat UI screen
    - Create ChatScreen with message list
    - Add message input field
    - Display message timestamps and status
    - Show push notification for new messages when in background
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.7_

  - [x] 19.6 Implement chat archiving
    - Archive chat messages when ride completes
    - Disable chat functionality after ride ends
    - _Requirements: 10.6_

  - [ ]* 19.7 Write unit tests for chat functionality
    - Test message sending
    - Test message status updates
    - Test offline queueing
    - _Requirements: 10.2, 10.7, 10.8_

- [ ] 20. Implement Emergency Features
  - [x] 20.1 Create emergency data models and API
    - Define SOSRequest, EmergencyContact data classes
    - Add emergency endpoints to EmergencyApi interface
    - _Requirements: 9.1, 9.2, 9.7_

  - [x] 20.2 Implement EmergencyRepository
    - Create methods for triggerSOS, addEmergencyContact, removeEmergencyContact, shareRideWithContacts
    - Store emergency contacts in Room database
    - _Requirements: 9.1, 9.2, 9.4, 9.7_

  - [x] 20.3 Create EmergencyViewModel
    - Manage emergency contacts list
    - Handle SOS activation
    - Track SOS active state
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.7_

  - [x] 20.4 Build emergency UI components
    - Create prominent SOS button on active ride screen
    - Add confirmation dialog for SOS activation
    - Display emergency contact list with call buttons
    - _Requirements: 9.1, 9.3, 9.5_

  - [x] 20.5 Implement SOS functionality
    - Send SOS alert to backend with current location
    - Send SMS to emergency contacts
    - Record timestamp and location
    - Increase location update frequency to 5 seconds
    - _Requirements: 9.1, 9.2, 9.6_

  - [x] 20.6 Implement ride sharing feature
    - Generate shareable ride tracking link
    - Send link to emergency contacts
    - _Requirements: 9.4_

  - [ ]* 20.7 Write unit tests for emergency features
    - Test SOS activation
    - Test emergency contact management
    - Test ride sharing
    - _Requirements: 9.1, 9.2, 9.4, 9.7_


- [ ] 21. Implement Earnings Tracking (Driver App)
  - [x] 21.1 Create earnings data models and API
    - Define EarningsData, EarningsResponse data classes
    - Add earnings endpoint to DriverApi interface
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

  - [x] 21.2 Implement EarningsRepository
    - Create methods for getEarnings with date range filtering
    - Store earnings data in Room database
    - Sync with backend when online
    - _Requirements: 14.2, 14.5, 14.6, 14.7_

  - [x] 21.3 Create EarningsViewModel
    - Manage earnings state with StateFlow
    - Calculate statistics (total rides, average fare)
    - Handle day/week/month filtering
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.6_

  - [x] 21.4 Build earnings UI screens
    - Display total earnings on driver dashboard
    - Create EarningsScreen with breakdown by period
    - Show earnings statistics and ride list
    - Display pending earnings
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.6, 14.8_

  - [x] 21.5 Update earnings on ride completion
    - Automatically update earnings display after each ride
    - _Requirements: 14.3_

  - [ ]* 21.6 Write unit tests for earnings tracking
    - Test earnings calculation
    - Test date range filtering
    - Test earnings sync
    - _Requirements: 14.2, 14.3, 14.7_

- [ ] 22. Implement Push Notifications with Firebase Cloud Messaging
  - [x] 22.1 Set up FCM integration
    - Configure Firebase project and add google-services.json
    - Implement FirebaseMessagingService
    - _Requirements: 19.1_

  - [x] 22.2 Implement NotificationManager
    - Create methods for registerDeviceToken, handleNotification, showLocalNotification
    - Register device token with backend on app launch
    - _Requirements: 19.1, 19.2_

  - [x] 22.3 Define notification types and channels
    - Create NotificationType enum
    - Set up notification channels for Android 8.0+
    - _Requirements: 19.3, 19.4, 19.5, 19.6_

  - [x] 22.4 Implement notification handling
    - Handle different notification types
    - Implement deep linking to relevant screens
    - Display notifications based on user preferences
    - _Requirements: 19.3, 19.4, 19.5, 19.6, 19.7, 19.8_

  - [ ]* 22.5 Write property test for push notification navigation
    - **Property 25: Push Notification Navigation**
    - **Validates: Requirements 19.8**

  - [x] 22.6 Add notification preferences to settings
    - Allow users to enable/disable specific notification types
    - Store preferences and respect them when showing notifications
    - _Requirements: 19.7, 27.2_

  - [ ]* 22.7 Write unit tests for notification handling
    - Test notification type handling
    - Test deep linking
    - Test notification preferences
    - _Requirements: 19.2, 19.7, 19.8_

- [ ] 23. Implement Offline Mode and Data Synchronization
  - [x] 23.1 Create SyncManager
    - Track network connectivity state
    - Queue actions performed in offline mode
    - Implement sync logic for queued actions
    - _Requirements: 20.1, 20.4, 20.5, 20.6_

  - [ ]* 23.2 Write property test for offline action queueing
    - **Property 19: Offline Action Queueing**
    - **Validates: Requirements 20.4**

  - [ ]* 23.3 Write property test for automatic sync on reconnection
    - **Property 20: Automatic Sync on Reconnection**
    - **Validates: Requirements 20.5**

  - [ ]* 23.4 Write property test for sync retry with exponential backoff
    - **Property 21: Sync Retry with Exponential Backoff**
    - **Validates: Requirements 20.8**

  - [x] 23.2 Implement SyncWorker with WorkManager
    - Create background worker for periodic sync
    - Sync pending ratings, messages, profile updates
    - Retry failed syncs with exponential backoff
    - _Requirements: 20.5, 20.8_

  - [x] 23.6 Add offline mode indicators
    - Display offline indicator in UI when network unavailable
    - Show cached data with offline badge
    - Prevent ride requests in offline mode
    - _Requirements: 20.1, 20.2, 20.3, 20.6, 20.7_

  - [ ]* 23.7 Write integration tests for offline sync
    - Test action queueing in offline mode
    - Test automatic sync on reconnection
    - Test retry logic
    - _Requirements: 20.4, 20.5, 20.8_

- [ ] 24. Checkpoint - Core Features Complete
  - Ensure all tests pass for payment, rating, chat, emergency, earnings, notifications, and offline sync
  - Verify end-to-end flows for both Rider and Driver apps
  - Ask the user if questions arise


- [ ] 25. Implement Ride History and Receipts
  - [x] 25.1 Create ride history UI components
    - Build RideHistoryScreen with list of past rides
    - Display ride status, date, and locations
    - Implement date range filtering
    - Add search functionality by location or driver/rider name
    - _Requirements: 28.1, 28.2, 28.3, 28.4, 28.5_

  - [ ]* 25.2 Write property test for ride history sorting
    - **Property 24: Ride History Sorting**
    - **Validates: Requirements 28.1**

  - [ ]* 25.3 Write property test for ride sync to local database
    - **Property 35: Ride Sync to Local Database**
    - **Validates: Requirements 28.8**

  - [x] 25.4 Implement receipt detail view
    - Create RideReceiptScreen with complete ride details
    - Display fare breakdown, route, driver/rider info
    - _Requirements: 28.2, 7.7_

  - [x] 25.5 Add receipt sharing functionality
    - Generate receipt as PDF or image
    - Implement share via email or messaging apps
    - _Requirements: 28.6_

  - [x] 25.6 Ensure offline access to ride history
    - Load ride history from Room database
    - Sync new rides when online
    - _Requirements: 28.7, 28.8_

  - [ ]* 25.7 Write unit tests for ride history
    - Test sorting and filtering
    - Test search functionality
    - Test receipt generation
    - _Requirements: 28.1, 28.3, 28.4_

- [ ] 26. Implement Settings and Preferences
  - [x] 26.1 Create settings data models
    - Define NotificationPreferences, AppSettings data classes
    - Store preferences in SharedPreferences
    - _Requirements: 27.1, 27.2, 27.3, 27.4_

  - [x] 26.2 Implement SettingsRepository
    - Create methods for saving and loading preferences
    - Handle language and theme changes
    - _Requirements: 21.2, 21.3, 22.2, 22.3, 27.2, 27.3, 27.4_

  - [ ]* 26.3 Write property test for settings persistence round-trip
    - **Property 22: Settings Persistence Round-Trip**
    - **Validates: Requirements 21.3, 22.3**

  - [x] 26.4 Create SettingsViewModel
    - Manage settings state with StateFlow
    - Handle preference updates
    - _Requirements: 27.2, 27.3, 27.4, 27.5, 27.6_

  - [x] 26.5 Build settings UI screen
    - Create SettingsScreen with all preference options
    - Add notification preferences toggles
    - Add language selector (English/Hindi)
    - Add theme selector (light/dark/system)
    - Display app version and build info
    - Add logout button
    - _Requirements: 27.1, 27.2, 27.3, 27.4, 27.5, 27.6, 27.7, 27.8_

  - [x] 26.6 Implement driver-specific settings
    - Add parcel delivery acceptance toggle
    - Add extended service area preference
    - _Requirements: 27.5, 27.6_

  - [ ]* 26.7 Write unit tests for settings
    - Test preference persistence
    - Test language change
    - Test theme change
    - _Requirements: 21.2, 21.3, 22.2, 22.3_

- [ ] 27. Implement Multi-Language Support
  - [x] 27.1 Set up string resources
    - Create strings.xml for English
    - Create strings.xml for Hindi (values-hi)
    - Translate all UI strings
    - _Requirements: 21.1, 21.6_

  - [x] 27.2 Implement language switching
    - Apply selected language to app context
    - Restart activities to apply language change
    - _Requirements: 21.2, 21.3_

  - [x] 27.3 Handle device language
    - Use device default language if no preference set
    - Update when device language changes
    - _Requirements: 21.4, 21.5_

  - [x] 27.4 Preserve dynamic content language
    - Don't translate addresses, names, or user-generated content
    - _Requirements: 21.7_

  - [ ]* 27.5 Write unit tests for language support
    - Test language switching
    - Test default language selection
    - _Requirements: 21.2, 21.3, 21.4_

- [ ] 28. Implement Dark Mode Support
  - [x] 28.1 Create Material Design 3 theme
    - Define light and dark color schemes
    - Create Theme.kt with Material3 theme configuration
    - _Requirements: 22.1_

  - [x] 28.2 Implement theme switching
    - Apply selected theme to app
    - Handle system theme changes
    - _Requirements: 22.2, 22.3, 22.4, 22.5_

  - [x] 28.3 Ensure readability in both themes
    - Test all screens in light and dark modes
    - Adjust colors for sufficient contrast
    - Update map markers and polylines for dark mode
    - _Requirements: 22.6, 22.7_

  - [ ]* 28.4 Write unit tests for theme support
    - Test theme switching
    - Test system theme following
    - _Requirements: 22.2, 22.3, 22.4, 22.5_


- [ ] 29. Implement Performance Optimizations
  - [x] 29.1 Optimize app startup time
    - Implement lazy initialization for non-critical components
    - Use App Startup library for initialization
    - Profile startup time and optimize bottlenecks
    - _Requirements: 23.1_

  - [ ]* 29.2 Write property test for app startup time
    - **Property 27: App Startup Time**
    - **Validates: Requirements 23.1**

  - [x] 29.3 Optimize location updates for battery efficiency
    - Use balanced power mode for location requests
    - Reduce update frequency when app in background
    - _Requirements: 23.2, 23.6_

  - [x] 29.4 Implement image caching and compression
    - Use Coil for efficient image loading
    - Compress images before upload (50% reduction)
    - _Requirements: 2.3, 23.3_

  - [x] 29.5 Optimize map performance
    - Cache map tiles locally
    - Limit marker updates to reduce rendering
    - _Requirements: 23.4_

  - [x] 29.6 Ensure smooth animations
    - Profile frame rate during animations
    - Optimize Compose recompositions
    - Target 60 FPS for all transitions
    - _Requirements: 23.5_

  - [ ]* 29.7 Write property test for animation frame rate
    - **Property 28: Animation Frame Rate**
    - **Validates: Requirements 23.5**

  - [x] 29.8 Implement pagination for ride history
    - Load rides in pages of 20 items
    - Implement infinite scroll
    - _Requirements: 23.8_

  - [x] 29.9 Optimize WebSocket message size
    - Limit message payload to 10KB
    - Use efficient JSON serialization
    - _Requirements: 23.7_

- [x] 30. Implement Security Features
  - [x] 30.1 Set up EncryptedSharedPreferences
    - Store JWT tokens securely
    - Store biometric keys in Android Keystore
    - _Requirements: 24.1, 24.8_

  - [x] 30.2 Implement SSL certificate pinning
    - Pin backend API certificates
    - Handle certificate validation errors
    - _Requirements: 24.2_

  - [x] 30.3 Implement input validation
    - Validate all user inputs for injection attacks
    - Sanitize inputs before sending to backend
    - _Requirements: 24.3_

  - [ ]* 30.4 Write property test for input injection prevention
    - **Property 4: Input Injection Prevention**
    - **Validates: Requirements 24.3**

  - [x] 30.5 Use secure WebSocket connections
    - Configure WSS protocol for WebSocket
    - _Requirements: 24.4_

  - [x] 30.6 Clear sensitive data on logout
    - Remove tokens from memory and storage
    - Clear cached user data
    - _Requirements: 24.5_

  - [x] 30.7 Configure ProGuard for release builds
    - Enable code obfuscation
    - Remove debug logging in production
    - _Requirements: 24.6, 24.7_

  - [ ]* 30.8 Write unit tests for security features
    - Test token encryption
    - Test input validation
    - Test data clearing on logout
    - _Requirements: 24.1, 24.3, 24.5_

- [x] 31. Implement Accessibility Features
  - [x] 31.1 Add content descriptions
    - Provide content descriptions for all interactive elements
    - Test with TalkBack screen reader
    - _Requirements: 25.1, 25.2_

  - [x] 31.2 Ensure minimum touch target sizes
    - Set minimum 48dp × 48dp for all interactive elements
    - _Requirements: 25.3_

  - [ ]* 31.3 Write property test for minimum touch target size
    - **Property 29: Minimum Touch Target Size**
    - **Validates: Requirements 25.3**

  - [x] 31.4 Ensure color contrast ratios
    - Verify WCAG 2.1 Level AA compliance for all text
    - Test with contrast checking tools
    - _Requirements: 25.4_

  - [ ]* 31.5 Write property test for color contrast ratio
    - **Property 30: Color Contrast Ratio**
    - **Validates: Requirements 25.4**

  - [x] 31.6 Support text scaling
    - Test layouts with text scaled to 200%
    - Ensure no text truncation or layout breaks
    - _Requirements: 25.5_

  - [x] 31.7 Add haptic feedback
    - Provide haptic feedback for important actions
    - Add vibration for notifications
    - _Requirements: 25.6_

  - [x] 31.8 Support keyboard and switch navigation
    - Test navigation with external keyboard
    - Ensure all features accessible via switch controls
    - _Requirements: 25.7_

  - [ ]* 31.9 Write accessibility tests
    - Test TalkBack compatibility
    - Test keyboard navigation
    - Test text scaling
    - _Requirements: 25.2, 25.5, 25.7_


- [x] 32. Implement Error Handling and User Feedback
  - [x] 32.1 Create error handling utilities
    - Implement safeApiCall wrapper for network requests
    - Create error-to-message mapping functions
    - _Requirements: 26.1, 26.4_

  - [ ]* 32.2 Write property test for network error user feedback
    - **Property 36: Network Error User Feedback**
    - **Validates: Requirements 26.1**

  - [x] 32.3 Add loading indicators
    - Display loading states during network operations
    - Show progress indicators for long-running tasks
    - _Requirements: 26.5_

  - [ ]* 32.4 Write property test for loading indicator display
    - **Property 26: Loading Indicator Display**
    - **Validates: Requirements 26.5**

  - [x] 32.5 Implement error dialogs and snackbars
    - Show user-friendly error messages
    - Provide retry options for failed operations
    - _Requirements: 26.1, 26.4_

  - [x] 32.6 Add success feedback
    - Display confirmation messages for successful actions
    - Use visual feedback (animations, color changes)
    - _Requirements: 26.6_

  - [x] 32.7 Handle specific error scenarios
    - GPS disabled → prompt to enable location services
    - Payment failed → show specific error and corrective actions
    - API errors → parse and display meaningful messages
    - _Requirements: 26.2, 26.3, 26.4_

  - [x] 32.8 Integrate Firebase Crashlytics
    - Set up Crashlytics for crash reporting
    - Log non-fatal errors for debugging
    - _Requirements: 26.7_

  - [x] 32.9 Handle unexpected errors gracefully
    - Display generic error message for unknown errors
    - Log details for investigation
    - _Requirements: 26.8_

  - [ ]* 32.10 Write unit tests for error handling
    - Test error message generation
    - Test retry logic
    - Test error logging
    - _Requirements: 26.1, 26.4, 26.7_

- [x] 33. Implement Navigation and App Structure
  - [x] 33.1 Set up Jetpack Compose Navigation
    - Define navigation graph for Rider App
    - Define navigation graph for Driver App
    - Implement deep linking for notifications
    - _Requirements: 19.8_

  - [x] 33.2 Create main app structure
    - Build MainActivity with navigation host
    - Implement splash screen
    - Handle authentication state routing
    - _Requirements: 23.1_

  - [x] 33.3 Implement bottom navigation (Rider App)
    - Create bottom nav with Home, History, Profile tabs
    - Handle tab navigation and state preservation
    - _Requirements: 27.1_

  - [x] 33.4 Implement drawer navigation (Driver App)
    - Create navigation drawer with Home, Earnings, Ratings, Settings
    - _Requirements: 27.1_

  - [ ]* 33.5 Write UI tests for navigation
    - Test navigation between screens
    - Test deep linking
    - Test back navigation
    - _Requirements: 19.8_

- [x] 34. Checkpoint - UI and UX Complete
  - Ensure all tests pass for performance, security, accessibility, error handling, and navigation
  - Verify UI consistency across both apps
  - Test on multiple device sizes and Android versions
  - Ask the user if questions arise

- [x] 35. Implement End-to-End UI Tests
  - [x] 35.1 Write UI tests for Rider App critical flows
    - Test complete login flow
    - Test ride request flow from location selection to tracking
    - Test payment flow
    - Test rating submission
    - _Requirements: 1.1, 3.1, 7.2, 8.1_

  - [x] 35.2 Write UI tests for Driver App critical flows
    - Test login flow
    - Test going online and receiving ride request
    - Test accepting ride and completing it
    - Test earnings display
    - _Requirements: 1.1, 11.1, 12.4, 13.6, 14.3_

  - [x] 35.3 Write UI tests for shared features
    - Test profile management
    - Test settings changes
    - Test language switching
    - Test theme switching
    - _Requirements: 2.1, 21.2, 22.2, 27.2_

- [x] 36. Code Quality and Documentation
  - [x] 36.1 Run static code analysis
    - Configure Detekt with custom rules
    - Fix all critical and major issues
    - _Requirements: 31.8_

  - [x] 36.2 Ensure test coverage
    - Run Jacoco coverage report
    - Verify minimum 70% code coverage
    - Add tests for uncovered critical paths
    - _Requirements: 31.4_

  - [x] 36.3 Write code documentation
    - Add KDoc comments for public APIs
    - Document complex algorithms and business logic
    - Create README for each module

  - [x] 36.4 Optimize build configuration
    - Configure build variants (debug, release)
    - Set up signing configuration for release builds
    - Optimize ProGuard rules

  - [x] 36.5 Create developer documentation
    - Document project structure
    - Document build and run instructions
    - Document testing strategy
    - Document API integration details

- [x] 37. Final Testing and Polish
  - [x] 37.1 Perform manual testing
    - Test all features on physical devices
    - Test on different Android versions (8.0 to 14)
    - Test on different screen sizes
    - Test with poor network conditions

  - [x] 37.2 Performance testing
    - Profile app startup time
    - Monitor memory usage
    - Test battery consumption
    - Verify frame rates during animations

  - [x] 37.3 Security testing
    - Verify SSL certificate pinning
    - Test token security
    - Verify data encryption
    - Test input validation

  - [x] 37.4 Accessibility testing
    - Test with TalkBack enabled
    - Test with large text sizes
    - Verify color contrast
    - Test keyboard navigation

  - [x] 37.5 Fix bugs and polish UI
    - Address any issues found during testing
    - Polish animations and transitions
    - Ensure consistent styling across screens

- [x] 38. Final Checkpoint - Apps Ready for Deployment
  - Ensure all tests pass (unit, property, integration, UI)
  - Verify code coverage meets 70% minimum
  - Confirm all requirements are implemented
  - Verify both Rider App and Driver App are fully functional
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional test tasks that can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration tests validate component interactions
- UI tests validate critical user flows
- Checkpoints ensure incremental validation and provide opportunities for user feedback
- Both Rider App and Driver App share common core modules (authentication, networking, database)
- Implementation assumes existing FastAPI backend is running at http://localhost:8000/api/
- WebSocket endpoint is at ws://localhost:8000/ws
- All backend API documentation is available at /docs endpoint
