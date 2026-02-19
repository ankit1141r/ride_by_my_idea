# Implementation Plan: Ride-Hailing Platform

## Overview

This implementation plan breaks down the ride-hailing platform into incremental development steps using Python. The platform will be built as a web application with REST APIs and WebSocket support for real-time features. We'll use FastAPI for the web framework, PostgreSQL for primary data storage, Redis for caching and real-time state, and MongoDB for location data.

The implementation follows a layered approach: data models → core services → API endpoints → real-time features → integration with external services. Each task builds on previous work, with property-based tests integrated throughout to validate correctness.

## Technology Stack

- **Backend Framework**: FastAPI (Python)
- **Databases**: PostgreSQL (primary), Redis (cache/sessions), MongoDB (location data)
- **Real-time**: WebSockets via FastAPI
- **Testing**: pytest, hypothesis (property-based testing)
- **External Services**: Razorpay/Paytm SDKs, Twilio (SMS), Google Maps API

## Tasks

- [x] 1. Project setup and infrastructure
  - Create Python project structure with virtual environment
  - Set up FastAPI application with basic configuration
  - Configure database connections (PostgreSQL, Redis, MongoDB)
  - Set up pytest with hypothesis for property-based testing
  - Create environment configuration management
  - _Requirements: All (foundational)_

leta
- [-] 2. Data models and database schemas
  - [x] 2.1 Create User model with SQLAlchemy ORM
    - Define User table with fields: userId, phoneNumber, name, email, userType, createdAt
    - Define DriverProfile table with vehicle and status fields
    - Define EmergencyContact table
    - Implement database migrations using Alembic
    - _Requirements: 1.1, 1.5, 10.1, 11.5_
  
  - [ ]* 2.2 Write property test for User model
    - **Property 1: Registration data completeness**
    - **Validates: Requirements 1.1, 10.1**
  
  - [x] 2.3 Create Ride model with status tracking
    - Define Ride table with all ride lifecycle fields
    - Define RideStatus enum with valid state transitions
    - Include location, timing, fare, and rating fields
    - _Requirements: 2.1, 3.3, 5.1, 7.1_
  
  - [ ]* 2.4 Write property test for Ride model state transitions
    - **Property 23: Automatic status transitions**
    - **Validates: Requirements 3.6, 12.4, 12.5**
  
  - [x] 2.5 Create Transaction and Payment models
    - Define Transaction table for payment records
    - Define DriverPayout table for payout scheduling
    - Include gateway integration fields
    - _Requirements: 6.1, 6.5, 6.6, 6.7_
  
  - [x] 2.6 Create VerificationSession model
    - Define table for phone verification sessions
    - Include expiry and attempt tracking
    - _Requirements: 1.2, 1.3, 1.4_
  
  - [x] 2.7 Create Rating model
    - Define Rating table with stars and review text
    - Link to rides and users
    - _Requirements: 7.1, 7.2, 7.3_

- [ ] 3. Authentication Service implementation
  - [x] 3.1 Implement user registration endpoint
    - Create POST /api/auth/register endpoint
    - Validate required fields based on user type
    - Hash passwords using bcrypt
    - Store user in database
    - _Requirements: 1.1, 1.5, 1.7_
  
  - [ ]* 3.2 Write property tests for registration
    - **Property 1: Registration data completeness**
    - **Property 4: Driver ID requirement enforcement**
    - **Property 5: Credential encryption**
    - **Validates: Requirements 1.1, 1.5, 1.7, 10.1**
  
  - [x] 3.3 Implement phone verification flow
    - Create POST /api/auth/verify/send endpoint to send OTP
    - Integrate with SMS gateway (Twilio)
    - Generate 6-digit verification code
    - Store in VerificationSession with 10-minute expiry
    - Create POST /api/auth/verify/confirm endpoint
    - Implement attempt limiting (3 attempts, 30-minute block)
    - _Requirements: 1.2, 1.3, 1.4_
  
  - [ ]* 3.4 Write property tests for verification
    - **Property 2: Verification code round-trip**
    - **Property 3: Verification attempt limiting**
    - **Validates: Requirements 1.2, 1.3, 1.4**
  
  - [x] 3.5 Implement login and JWT token generation
    - Create POST /api/auth/login endpoint
    - Validate credentials against hashed passwords
    - Generate JWT tokens with user claims
    - Store session in Redis
    - _Requirements: 1.8_
  
  - [ ]* 3.6 Write property test for authentication
    - **Property 6: Authentication session creation**
    - **Validates: Requirements 1.8**
  
  - [x] 3.7 Implement ID document verification for drivers
    - Create POST /api/auth/driver/verify-id endpoint
    - Accept document upload (image file)
    - Store document metadata
    - Implement basic validation checks
    - _Requirements: 1.6_

- [x] 4. Checkpoint - Authentication complete
  - Ensure all authentication tests pass, ask the user if questions arise.


- [ ] 5. Location Service implementation
  - [x] 5.1 Create Location data model for MongoDB
    - Define Location schema with latitude, longitude, address
    - Create indexes for geospatial queries
    - _Requirements: 2.1, 8.1, 13.5_
  
  - [x] 5.2 Implement address validation and boundary checking
    - Create function to validate Indore city boundaries
    - Define boundary coordinates (lat: 22.6-22.8, lon: 75.7-75.9)
    - Implement isWithinServiceArea function
    - _Requirements: 2.4, 13.6_
  
  - [ ]* 5.3 Write property tests for boundary validation
    - **Property 8: Boundary validation**
    - **Property 57: Address validation**
    - **Validates: Requirements 2.4, 13.6**
  
  - [x] 5.4 Implement distance calculation
    - Create calculateDistance function using Haversine formula
    - Return distance in kilometers
    - _Requirements: 5.1, 5.2_
  
  - [x] 5.5 Integrate with Google Maps API
    - Set up Google Maps client
    - Implement address search functionality
    - Implement route calculation with polyline
    - _Requirements: 2.6, 8.3, 8.6_
  
  - [ ]* 5.6 Write property test for address search filtering
    - **Property 56: Address search boundary filtering**
    - **Validates: Requirements 13.5**
  
  - [x] 5.7 Implement driver location tracking
    - Create updateDriverLocation function to store in MongoDB
    - Create getDriverLocation function to retrieve latest location
    - Implement location update endpoint POST /api/location/driver
    - _Requirements: 4.4, 8.1, 8.2_
  
  - [x] 5.8 Implement route deviation detection
    - Create detectRouteDeviation function
    - Calculate distance from current location to expected route
    - Return alert if deviation exceeds threshold (500m)
    - _Requirements: 11.4_
  
  - [ ]* 5.9 Write property test for route deviation
    - **Property 53: Route deviation alert**
    - **Validates: Requirements 11.4**

- [ ] 6. Fare Calculation Service implementation
  - [x] 6.1 Implement fare calculation logic
    - Create calculateEstimatedFare function
    - Apply formula: (₹20 + distance_km * ₹8) * surge_multiplier
    - Return FareCalculation with breakdown
    - Create calculateFinalFare function for completed rides
    - Implement fare protection (20% cap)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [ ]* 6.2 Write property tests for fare calculation
    - **Property 25: Fare calculation formula**
    - **Property 26: Final fare calculation**
    - **Property 27: Fare protection cap**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6**
  
  - [ ]* 6.3 Write unit tests for specific fare examples
    - Test exact fare for 5km ride: ₹90
    - Test surge pricing with 2x multiplier
    - Test fare protection at 20% threshold
    - _Requirements: 5.1, 5.2, 5.5_

- [ ] 7. Ride Management Service implementation
  - [x] 7.1 Implement ride request creation
    - Create POST /api/rides/request endpoint
    - Validate pickup and destination within boundaries
    - Calculate estimated fare
    - Create RideRequest record
    - Return request ID and fare details
    - _Requirements: 2.1, 2.2, 2.4, 2.5_
  
  - [ ]* 7.2 Write property tests for ride request
    - **Property 7: Valid ride request creation**
    - **Property 8: Boundary validation**
    - **Property 9: Ride request completeness**
    - **Validates: Requirements 2.1, 2.2, 2.4, 2.5**
  
  - [x] 7.3 Implement ride lifecycle management
    - Create functions for status transitions: matched → in_progress → completed
    - Implement startRide function
    - Implement completeRide function with final fare calculation
    - Update ride status in database
    - _Requirements: 3.3, 5.4_
  
  - [x] 7.4 Implement ride history endpoints
    - Create GET /api/rides/history endpoint
    - Implement filtering by date range
    - Sort rides in reverse chronological order
    - Return rides with all required fields
    - Create GET /api/rides/{rideId} for detailed view
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 7.5 Write property tests for ride history
    - **Property 42: Complete history retention**
    - **Property 43: Chronological ordering**
    - **Property 44: History data completeness**
    - **Property 45: Date range filtering**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**
  
  - [x] 7.6 Implement cancellation logic
    - Create POST /api/rides/{rideId}/cancel endpoint
    - Check ride status to determine if cancellation allowed
    - Calculate cancellation fee based on ride status
    - Update ride status to cancelled
    - Record cancellation details
    - _Requirements: 15.1, 15.2, 15.3, 15.7_
  
  - [ ]* 7.7 Write property tests for cancellation
    - **Property 65: Pre-match cancellation**
    - **Property 66: Post-match cancellation fee**
    - **Property 70: In-progress cancellation restriction**
    - **Validates: Requirements 15.1, 15.2, 15.7**

- [x] 8. Checkpoint - Core ride management complete
  - Ensure all tests pass, ask the user if questions arise.


- [ ] 9. Ride Matching Engine implementation
  - [x] 9.1 Implement driver availability management
    - Create POST /api/drivers/availability endpoint
    - Implement setDriverAvailable function (stores in Redis)
    - Implement setDriverUnavailable function
    - Store driver status and current location
    - _Requirements: 3.7, 12.1, 12.2, 12.3_
  
  - [ ]* 9.2 Write property tests for driver availability
    - **Property 21: Status toggling**
    - **Property 22: Availability-based matching inclusion**
    - **Validates: Requirements 3.7, 12.1, 12.2, 12.3**
  
  - [x] 9.3 Implement driver search by proximity
    - Create getAvailableDrivers function
    - Query MongoDB for drivers within radius of pickup location
    - Filter by availability status from Redis
    - Sort by distance from pickup
    - _Requirements: 3.1, 4.3_
  
  - [ ]* 9.4 Write property tests for proximity-based search
    - **Property 11: Proximity-based notification**
    - **Property 18: Distance-based prioritization**
    - **Validates: Requirements 3.1, 4.3**
  
  - [x] 9.5 Implement ride broadcasting logic
    - Create broadcastRideRequest function
    - Find available drivers within initial 5km radius
    - Store broadcast details in Redis
    - Return list of notified drivers
    - _Requirements: 2.3, 3.1_
  
  - [x] 9.6 Write property test for broadcasting
    - **Property 10: Ride request broadcasting**
    - **Validates: Requirements 2.3**
  
  - [x] 9.7 Implement ride matching algorithm
    - Create matchRide function
    - Handle concurrent acceptances using Redis locks
    - Select closest driver when multiple accept
    - Create RideMatch record
    - Update driver status to "Busy"
    - _Requirements: 3.3, 3.6, 4.1_
  
  - [ ]* 9.8 Write property tests for matching
    - **Property 13: Ride match creation**
    - **Property 16: Closest driver selection**
    - **Property 23: Automatic status transitions** (driver to busy)
    - **Validates: Requirements 3.3, 3.6, 4.1**
  
  - [x] 9.9 Implement search radius expansion
    - Create expandSearchRadius function
    - Trigger after 2-minute timeout
    - Increase radius by 2km
    - Re-broadcast to newly included drivers
    - _Requirements: 3.5_
  
  - [ ]* 9.10 Write property test for radius expansion
    - **Property 15: Search radius expansion**
    - **Validates: Requirements 3.5**
  
  - [x] 9.11 Implement driver rejection handling
    - Create rejectRide function
    - Keep ride request active for other drivers
    - Continue broadcasting
    - _Requirements: 3.4_
  
  - [ ]* 9.12 Write property test for rejection handling
    - **Property 14: Continued broadcasting after rejection**
    - **Validates: Requirements 3.4**
  
  - [x] 9.13 Implement driver cancellation handling
    - Create handleDriverCancellation function
    - Track cancellation count in driver profile
    - Suspend driver if count exceeds 3 in a day
    - Re-broadcast ride request to other drivers
    - _Requirements: 4.5, 15.3, 15.4, 15.5_
  
  - [ ]* 9.14 Write property tests for driver cancellation
    - **Property 20: Re-broadcast after driver cancellation**
    - **Property 67: Driver cancellation capability**
    - **Property 68: Driver cancellation logging**
    - **Property 69: Driver cancellation limit enforcement**
    - **Validates: Requirements 4.5, 15.3, 15.4, 15.5**

- [ ] 10. WebSocket implementation for real-time features
  - [x] 10.1 Set up WebSocket connection management
    - Create WebSocket endpoint /ws
    - Implement connection authentication via JWT
    - Maintain active connections in memory (connection pool)
    - Handle connection lifecycle (connect, disconnect, reconnect)
    - _Requirements: 8.1, 8.2_
  
  - [x] 10.2 Implement ride request broadcasting via WebSocket
    - Send ride request notifications to connected drivers
    - Include pickup, destination, estimated fare
    - _Requirements: 2.3, 3.2_
  
  - [ ]* 10.3 Write property test for notification content
    - **Property 12: Notification content completeness**
    - **Validates: Requirements 3.2**
  
  - [x] 10.4 Implement driver acceptance/rejection via WebSocket
    - Handle driver accept/reject messages
    - Call matching engine functions
    - Broadcast match confirmation to rider
    - Cancel notifications to other drivers
    - _Requirements: 3.3, 4.2_
  
  - [ ]* 10.5 Write property test for notification cancellation
    - **Property 17: Notification cancellation after match**
    - **Validates: Requirements 4.2**
  
  - [x] 10.6 Implement real-time location updates
    - Accept location updates from drivers every 10 seconds
    - Store in MongoDB
    - Broadcast to matched rider
    - _Requirements: 8.1, 8.2_
  
  - [ ]* 10.7 Write property tests for location tracking
    - **Property 19: Real-time location usage**
    - **Property 38: Location sharing on match**
    - **Validates: Requirements 4.4, 8.1**
  
  - [x] 10.8 Implement proximity notifications
    - Monitor driver location during driver_arriving status
    - Send notification when within 500m of pickup
    - _Requirements: 8.4_
  
  - [ ]* 10.9 Write property test for proximity notification
    - **Property 40: Proximity notification**
    - **Validates: Requirements 8.4**

- [x] 11. Checkpoint - Real-time features complete
  - Ensure all WebSocket tests pass, ask the user if questions arise.


- [ ] 12. Payment Service implementation
  - [x] 12.1 Set up payment gateway integrations
    - Install Razorpay and Paytm Python SDKs
    - Configure API keys and credentials
    - Create PaymentGateway abstraction interface
    - Implement RazorpayGateway class
    - Implement PaytmGateway class
    - _Requirements: 6.2_
  
  - [x] 12.2 Implement payment processing
    - Create processPayment function
    - Trigger payment on ride completion
    - Implement retry logic (up to 2 retries with exponential backoff)
    - Store transaction records
    - Update ride payment status
    - _Requirements: 6.1, 6.3, 6.4, 6.5, 6.7_
  
  - [ ]* 12.3 Write property tests for payment processing
    - **Property 28: Payment initiation on completion**
    - **Property 29: Payment retry logic**
    - **Property 30: Payment success handling**
    - **Validates: Requirements 6.1, 6.4, 6.5, 6.7**
  
  - [ ]* 12.4 Write unit tests for payment scenarios
    - Test payment success on first attempt
    - Test payment failure and retry
    - Test payment failure after all retries
    - Test transaction logging
    - _Requirements: 6.3, 6.4, 6.7_
  
  - [x] 12.5 Implement driver payout scheduling
    - Create scheduleDriverPayout function
    - Schedule payouts within 24 hours of ride completion
    - Store payout records with status
    - Create background job to process scheduled payouts
    - _Requirements: 6.6_
  
  - [ ]* 12.6 Write property test for payout scheduling
    - **Property 31: Driver payout scheduling**
    - **Validates: Requirements 6.6**
  
  - [x] 12.7 Create payment endpoints
    - Create POST /api/payments/process endpoint
    - Create GET /api/payments/history endpoint
    - Create POST /api/payments/retry endpoint for failed payments
    - _Requirements: 6.1, 6.4_

- [ ] 13. Rating and Review System implementation
  - [x] 13.1 Implement rating submission
    - Create POST /api/ratings endpoint
    - Validate rating is between 1-5 stars
    - Validate review text is max 500 characters
    - Store rating linked to ride
    - Trigger rating prompt after payment completion
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [ ]* 13.2 Write property tests for rating validation
    - **Property 32: Rating prompt trigger**
    - **Property 33: Rating validation**
    - **Property 34: Review length validation**
    - **Validates: Requirements 7.1, 7.2, 7.3**
  
  - [x] 13.3 Implement average rating calculation
    - Create calculateAverageRating function
    - Calculate from last 100 rides (or all if fewer)
    - Update user's averageRating field
    - Trigger after each new rating
    - _Requirements: 7.4_
  
  - [ ]* 13.4 Write property test for average calculation
    - **Property 35: Average rating calculation**
    - **Validates: Requirements 7.4**
  
  - [x] 13.5 Implement low rating flagging
    - Create checkDriverRating function
    - Flag driver account if average falls below 3.5
    - Store flag in driver profile
    - _Requirements: 7.5_
  
  - [ ]* 13.6 Write property test for rating flagging
    - **Property 36: Low rating flagging**
    - **Validates: Requirements 7.5**
  
  - [x] 13.7 Implement rating display
    - Include driver rating in ride request response
    - Include rating and total rides in driver profile
    - _Requirements: 7.6, 7.7_
  
  - [ ]* 13.8 Write property test for rating display
    - **Property 37: Rating display completeness**
    - **Validates: Requirements 7.6, 7.7**

- [ ] 14. Vehicle Management implementation
  - [x] 14.1 Implement vehicle registration
    - Create POST /api/drivers/vehicle endpoint
    - Validate required fields: registration number, make, model, color
    - Validate insurance expiry is at least 30 days in future
    - Store vehicle info in driver profile
    - _Requirements: 10.1, 10.3_
  
  - [ ]* 14.2 Write property tests for vehicle validation
    - **Property 47: Insurance validity requirement**
    - **Validates: Requirements 10.3**
  
  - [x] 14.3 Implement vehicle details in notifications
    - Include vehicle info in ride match notifications
    - _Requirements: 10.4_
  
  - [ ]* 14.4 Write property test for vehicle details display
    - **Property 48: Vehicle details in match notification**
    - **Validates: Requirements 10.4**
  
  - [x] 14.5 Implement insurance expiry monitoring
    - Create background job to check insurance expiry daily
    - Suspend drivers with expired insurance
    - _Requirements: 10.5_
  
  - [ ]* 14.6 Write property test for insurance suspension
    - **Property 49: Insurance expiry suspension**
    - **Validates: Requirements 10.5**
  
  - [x] 14.7 Implement vehicle update with re-verification
    - Create PUT /api/drivers/vehicle endpoint
    - Mark vehicle as unverified on update
    - Require re-verification process
    - _Requirements: 10.6_
  
  - [ ]* 14.8 Write property test for vehicle update
    - **Property 50: Vehicle update re-verification**
    - **Validates: Requirements 10.6**

- [ ] 15. Checkpoint - Payment and vehicle management complete
  - Ensure all tests pass, ask the user if questions arise.


- [ ] 16. Safety and Emergency Features implementation
  - [x] 16.1 Implement emergency contact management
    - Create POST /api/users/emergency-contacts endpoint
    - Validate maximum 3 contacts per user
    - Store emergency contacts linked to user
    - Create GET and DELETE endpoints for contact management
    - _Requirements: 11.5_
  
  - [ ]* 16.2 Write property test for contact limit
    - **Property 54: Emergency contact limit**
    - **Validates: Requirements 11.5**
  
  - [x] 16.3 Implement emergency alert system
    - Create POST /api/rides/{rideId}/emergency endpoint
    - Notify platform administrators immediately
    - Include ride details and current location
    - Log incident with timestamp
    - _Requirements: 11.2, 11.6_
  
  - [ ]* 16.4 Write property tests for emergency alerts
    - **Property 51: Emergency notification**
    - **Property 55: Emergency incident logging**
    - **Validates: Requirements 11.2, 11.6**
  
  - [x] 16.5 Implement ride sharing with emergency contacts
    - Create POST /api/rides/{rideId}/share endpoint
    - Generate shareable link with ride details
    - Send link to emergency contacts via SMS
    - Include live location tracking
    - _Requirements: 11.3_
  
  - [ ]* 16.6 Write property test for ride sharing
    - **Property 52: Ride sharing capability**
    - **Validates: Requirements 11.3**
  
  - [x] 16.7 Implement route deviation monitoring
    - Create background job to check route deviation
    - Run every 30 seconds for in-progress rides
    - Call detectRouteDeviation from Location Service
    - Send alert if deviation exceeds threshold
    - _Requirements: 11.4_

- [ ] 17. Notification Service implementation
  - [x] 17.1 Set up SMS gateway integration
    - Install Twilio Python SDK
    - Configure Twilio credentials
    - Create sendSMS function
    - _Requirements: 1.2, 14.6_
  
  - [x] 17.2 Implement notification functions
    - Create sendInAppNotification function (via WebSocket)
    - Create sendSMSNotification function
    - Create sendDualNotification for critical events
    - _Requirements: 14.6_
  
  - [ ]* 17.3 Write property test for dual notifications
    - **Property 63: Dual notification channels**
    - **Validates: Requirements 14.6**
  
  - [x] 17.4 Implement ride event notifications
    - Send match notification with driver details and ETA
    - Send acceptance notification with pickup details
    - Send arrival notification
    - Send completion notification with rating prompt
    - Send payment receipt notification
    - Send cancellation notification
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.7_
  
  - [ ]* 17.5 Write property tests for notification content
    - **Property 58: Match notification content**
    - **Property 59: Acceptance notification content**
    - **Property 60: Arrival notification**
    - **Property 61: Completion notification**
    - **Property 62: Payment receipt notification**
    - **Property 64: Cancellation notification**
    - **Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5, 14.7, 15.6**

- [ ] 18. Ride tracking and route display implementation
  - [x] 18.1 Implement route display for in-progress rides
    - Create GET /api/rides/{rideId}/route endpoint
    - Return current route with polyline
    - Include estimated time to destination
    - _Requirements: 8.3_
  
  - [ ]* 18.2 Write property test for route display
    - **Property 39: In-progress route display**
    - **Validates: Requirements 8.3**
  
  - [x] 18.3 Implement completed ride route storage
    - Store complete route in Ride model on completion
    - Include all location points from ride
    - _Requirements: 8.5_
  
  - [ ]* 18.4 Write property test for route storage
    - **Property 41: Completed ride route storage**
    - **Validates: Requirements 8.5**

- [ ] 19. Receipt generation implementation
  - [x] 19.1 Implement PDF receipt generation
    - Install reportlab or similar PDF library
    - Create generateReceipt function
    - Include ride details, fare breakdown, payment info
    - Create GET /api/rides/{rideId}/receipt endpoint
    - Return PDF file
    - _Requirements: 9.6_
  
  - [ ]* 19.2 Write property test for receipt generation
    - **Property 46: Receipt generation**
    - **Validates: Requirements 9.6**

- [ ] 20. Driver availability time tracking
  - [x] 20.1 Implement availability time tracking
    - Track time when driver sets status to "Available"
    - Track time when driver sets status to "Unavailable" or "Busy"
    - Calculate and accumulate daily availability hours
    - Store in driver profile
    - Reset daily at midnight
    - _Requirements: 12.6_
  
  - [ ]* 20.2 Write property test for time tracking
    - **Property 24: Availability time tracking**
    - **Validates: Requirements 12.6**

- [ ] 21. API endpoint integration and error handling
  - [x] 21.1 Implement comprehensive error handling
    - Add global exception handlers for FastAPI
    - Implement retry logic with exponential backoff for external services
    - Implement circuit breaker for payment gateways
    - Add proper error responses with status codes
    - _Requirements: All (cross-cutting)_
  
  - [x] 21.2 Add request validation middleware
    - Validate JWT tokens on protected endpoints
    - Validate request body schemas
    - Validate user permissions (rider vs driver actions)
    - _Requirements: 1.8_
  
  - [x] 21.3 Add logging and monitoring
    - Configure structured logging
    - Log all API requests and responses
    - Log errors with context (userId, rideId, etc.)
    - Add performance metrics
    - _Requirements: All (cross-cutting)_

- [ ] 22. Integration testing
  - [ ]* 22.1 Write integration tests for complete ride flow
    - Test: rider request → driver match → ride start → ride complete → payment → rating
    - Test: rider request → no drivers available → timeout
    - Test: rider request → driver cancels → re-match
    - _Requirements: 2.1, 3.3, 6.1, 7.1_
  
  - [ ]* 22.2 Write integration tests for cancellation flows
    - Test: rider cancels before match (no fee)
    - Test: rider cancels after match (₹20 fee)
    - Test: driver cancels before pickup (re-broadcast)
    - Test: cannot cancel in-progress ride
    - _Requirements: 15.1, 15.2, 15.3, 15.7_
  
  - [ ]* 22.3 Write integration tests for emergency flow
    - Test: emergency activation → admin notification → incident log
    - Test: ride sharing with emergency contacts
    - _Requirements: 11.2, 11.3, 11.6_

- [x] 23. Final checkpoint - Complete system integration
  - Ensure all integration tests pass
  - Verify all property-based tests pass with 100+ iterations
  - Verify all API endpoints are functional
  - Ask the user if questions arise.

## New Feature Implementation Tasks

- [-] 24. Geographical scope expansion implementation
  - [x] 24.1 Update location service boundaries
    - Update isWithinServiceArea to check 20km radius from city center
    - Implement isInExtendedArea function to distinguish extended area from city center
    - Update boundary coordinates to support circular 20km radius
    - Add visual boundary indicator data for map display
    - _Requirements: 18.1, 18.2, 18.3_
  
  - [ ]* 24.2 Write property tests for boundary validation
    - **Property 96: Extended service area boundary validation**
    - **Property 97: Extended area location classification**
    - **Validates: Requirements 18.1, 18.2, 18.3**
  
  - [x] 24.3 Update fare calculation for tiered pricing
    - Modify calculateEstimatedFare to apply ₹12/km for first 25km
    - Apply ₹10/km for distance beyond 25km
    - Update fare breakdown to show tiered calculation
    - _Requirements: 18.4, 18.9_
  
  - [ ]* 24.4 Write property tests for tiered fare calculation
    - **Property 98: Extended area fare calculation with tiered pricing**
    - **Validates: Requirements 18.4, 18.9**
  
  - [x] 24.5 Update matching engine for extended area
    - Modify getInitialSearchRadius to return 8km for extended area, 5km for city center
    - Update timeout logic: 3 minutes for extended area, 2 minutes for city center
    - Update radius expansion: +3km for extended area, +2km for city center
    - _Requirements: 18.5, 18.6_
  
  - [ ]* 24.6 Write property tests for extended area matching
    - **Property 99: Extended area initial search radius**
    - **Property 100: Extended area timeout and expansion**
    - **Validates: Requirements 18.5, 18.6**
  
  - [x] 24.7 Implement driver extended area preferences
    - Add acceptExtendedArea field to DriverProfile
    - Create PUT /api/drivers/preferences endpoint
    - Store and retrieve driver preferences
    - _Requirements: 18.10_
  
  - [x] 24.8 Update matching to respect extended area preferences
    - Filter drivers by extended area preference when matching extended area rides
    - Exclude drivers with disabled preference from extended area notifications
    - _Requirements: 18.11_
  
  - [ ]* 24.9 Write property tests for preference enforcement
    - **Property 102: Driver extended area preference**
    - **Property 103: Extended area preference enforcement**
    - **Validates: Requirements 18.10, 18.11**
  
  - [x] 24.10 Implement extended area statistics tracking
    - Track extended area rides in driver profile
    - Calculate percentage of extended area rides
    - Display in driver dashboard
    - _Requirements: 18.12_
  
  - [ ]* 24.11 Write property test for statistics tracking
    - **Property 104: Extended area ride percentage tracking**
    - **Validates: Requirements 18.12**
  
  - [x] 24.12 Update location validation error messages
    - Return clear error for locations beyond 20km service area
    - Include distance from service area in error message
    - _Requirements: 18.8_
  
  - [ ]* 24.13 Write property test for out-of-area rejection
    - **Property 101: Out-of-service-area rejection**
    - **Validates: Requirements 18.8**

- [ ] 25. Checkpoint - Geographical expansion complete
  - Ensure all extended area tests pass, ask the user if questions arise.

- [-] 26. Scheduled rides implementation
  - [x] 26.1 Create ScheduledRide data model
    - Define ScheduledRide table with SQLAlchemy ORM
    - Include fields: rideId, riderId, pickupLocation, destination, scheduledPickupTime, status, etc.
    - Define ScheduledRideStatus enum
    - Implement database migration
    - _Requirements: 16.1, 16.2, 16.4_
  
  - [x] 26.2 Implement scheduled ride creation endpoint
    - Create POST /api/rides/schedule endpoint
    - Validate scheduled time is within 7 days
    - Validate all required fields present
    - Calculate estimated fare
    - Store with status "scheduled"
    - _Requirements: 16.1, 16.2, 16.3, 16.4_
  
  - [ ]* 26.3 Write property tests for scheduled ride creation
    - **Property 71: Scheduled ride time window validation**
    - **Property 72: Scheduled ride data completeness**
    - **Property 73: Scheduled ride fare calculation**
    - **Property 74: Scheduled ride initial status**
    - **Validates: Requirements 16.1, 16.2, 16.3, 16.4**
  
  - [x] 26.4 Implement scheduled ride modification
    - Create PUT /api/rides/schedule/{rideId} endpoint
    - Check modification is >2 hours before pickup
    - Allow updates to pickup, destination, or scheduled time
    - Recalculate fare if locations change
    - _Requirements: 16.6_
  
  - [ ]* 26.5 Write property test for modification window
    - **Property 76: Scheduled ride modification window**
    - **Validates: Requirements 16.6**
  
  - [x] 26.6 Implement scheduled ride cancellation
    - Create DELETE /api/rides/schedule/{rideId} endpoint
    - Check cancellation time relative to pickup
    - Charge ₹30 fee if <1 hour before pickup
    - No fee if >1 hour before pickup
    - Update status to "cancelled"
    - _Requirements: 16.7, 16.8_
  
  - [ ]* 26.7 Write property test for cancellation fees
    - **Property 77: Scheduled ride cancellation fee logic**
    - **Validates: Requirements 16.7, 16.8**
  
  - [x] 26.8 Implement scheduled ride background job
    - Create background job that runs every minute
    - Find scheduled rides where scheduledTime - 30 minutes <= now
    - Change status to "matching"
    - Trigger matching engine for each eligible ride
    - _Requirements: 16.5_
  
  - [ ]* 26.9 Write property test for matching trigger
    - **Property 75: Scheduled ride matching trigger**
    - **Validates: Requirements 16.5**
  
  - [x] 26.10 Implement scheduled ride reminders
    - Add reminder logic to background job
    - Send rider reminder at 15 minutes before pickup
    - Send driver reminder at 15 minutes before pickup (if matched)
    - Mark reminder as sent to avoid duplicates
    - _Requirements: 16.9, 16.10_
  
  - [ ]* 26.11 Write property tests for reminders
    - **Property 78: Scheduled ride rider reminder**
    - **Property 79: Scheduled ride driver reminder**
    - **Validates: Requirements 16.9, 16.10**
  
  - [x] 26.12 Implement no-driver-found handling
    - Check scheduled rides at 15 minutes past scheduled time
    - If status still "matching", send notification to rider
    - Offer options to reschedule or cancel
    - Update status to "no_driver_found"
    - _Requirements: 16.11_
  
  - [ ]* 26.13 Write property test for no-driver notification
    - **Property 80: Scheduled ride no-driver notification**
    - **Validates: Requirements 16.11**
  
  - [x] 26.14 Implement scheduled rides dashboard endpoints
    - Create GET /api/rides/scheduled endpoint
    - Return scheduled rides separately from immediate rides
    - Include filtering by status
    - Sort by scheduled pickup time
    - _Requirements: 16.12_
  
  - [ ]* 26.15 Write property test for separate display
    - **Property 81: Scheduled rides separate display**
    - **Validates: Requirements 16.12**

- [x] 27. Checkpoint - Scheduled rides complete
  - Ensure all scheduled ride tests pass, ask the user if questions arise.

- [-] 28. Parcel delivery service implementation
  - [x] 28.1 Create ParcelDelivery data model
    - Define ParcelDelivery table with SQLAlchemy ORM
    - Define ParcelDetails embedded model
    - Define ParcelStatus enum
    - Include fields for photos, signatures, confirmations
    - Implement database migration
    - _Requirements: 17.2, 17.3_
  
  - [x] 28.2 Implement parcel fare calculation
    - Create calculateParcelFare function
    - Apply base fare by size: small ₹40, medium ₹60, large ₹80
    - Apply per-km rate by size: small ₹8, medium ₹10, large ₹12
    - Return ParcelFareBreakdown
    - _Requirements: 17.4, 17.5, 17.6_
  
  - [ ]* 28.3 Write property tests for parcel fare calculation
    - **Property 84: Parcel size classification**
    - **Property 85: Parcel fare calculation**
    - **Validates: Requirements 17.3, 17.4, 17.5, 17.6**
  
  - [x] 28.4 Implement parcel delivery request endpoint
    - Create POST /api/parcels/request endpoint
    - Validate user is verified
    - Validate all required fields present
    - Validate weight does not exceed 30kg
    - Calculate estimated fare and delivery time
    - Store with status "requested"
    - _Requirements: 17.1, 17.2, 17.13, 17.14_
  
  - [ ]* 28.5 Write property tests for parcel request validation
    - **Property 82: Parcel delivery access control**
    - **Property 83: Parcel delivery data completeness**
    - **Property 93: Parcel weight limit enforcement**
    - **Validates: Requirements 17.1, 17.2, 17.14**
  
  - [x] 28.6 Implement parcel pickup confirmation
    - Create POST /api/parcels/{deliveryId}/confirm-pickup endpoint
    - Require photo upload (base64 or file)
    - Optionally require signature if specified
    - Update status to "in_transit"
    - Store pickup timestamp
    - _Requirements: 17.7, 17.8, 17.9_
  
  - [ ]* 28.7 Write property tests for pickup confirmation
    - **Property 86: Parcel pickup confirmation requirement**
    - **Property 87: Parcel signature requirement**
    - **Property 88: Parcel status transition on pickup**
    - **Validates: Requirements 17.7, 17.8, 17.9**
  
  - [x] 28.8 Implement parcel delivery confirmation
    - Create POST /api/parcels/{deliveryId}/confirm-delivery endpoint
    - Require signature or photo from recipient
    - Update status to "delivered"
    - Store delivery timestamp
    - Trigger payment processing
    - _Requirements: 17.10_
  
  - [ ]* 28.9 Write property test for delivery confirmation
    - **Property 89: Parcel delivery confirmation requirement**
    - **Validates: Requirements 17.10**
  
  - [x] 28.10 Implement parcel location tracking
    - Reuse driver location tracking from Location Service
    - Create GET /api/parcels/{deliveryId}/location endpoint
    - Return real-time driver location for in-transit parcels
    - _Requirements: 17.11_
  
  - [ ]* 28.11 Write property test for parcel tracking
    - **Property 90: Parcel location tracking**
    - **Validates: Requirements 17.11**
  
  - [x] 28.12 Implement parcel completion notifications
    - Send notification to sender on delivery completion
    - Send notification to recipient on delivery completion
    - Include delivery confirmation details
    - _Requirements: 17.12_
  
  - [ ]* 28.13 Write property test for completion notifications
    - **Property 91: Parcel completion notifications**
    - **Validates: Requirements 17.12**
  
  - [x] 28.14 Implement parcel special instructions
    - Store special instructions in ParcelDetails
    - Display instructions to driver in notification
    - Include fragile, urgent flags
    - _Requirements: 17.15, 17.16_
  
  - [ ]* 28.15 Write property test for special instructions
    - **Property 94: Parcel special instructions storage**
    - **Validates: Requirements 17.15, 17.16**
  
  - [x] 28.16 Implement parcel history endpoints
    - Create GET /api/parcels/history endpoint
    - Filter by role: sender or recipient
    - Return parcels separately from rides
    - Include all parcel details and status
    - _Requirements: 17.17_
  
  - [ ]* 28.17 Write property test for parcel history separation
    - **Property 95: Parcel history separation**
    - **Validates: Requirements 17.17**
  
  - [x] 28.18 Update matching engine for parcel deliveries
    - Implement broadcastParcelRequest function
    - Filter drivers by parcel delivery preference
    - Use same proximity-based matching algorithm
    - Create matchParcel function
    - _Requirements: 17.1_
  
  - [x] 28.19 Add parcel delivery preference to driver profile
    - Add acceptParcelDelivery field to DriverProfile
    - Update driver preferences endpoint
    - Filter drivers in matching based on preference
    - _Requirements: 17.1_
  
  - [x] 28.20 Implement parcel delivery time estimation
    - Calculate estimated delivery time based on distance
    - Account for traffic conditions
    - Display to sender and recipient
    - _Requirements: 17.13_
  
  - [ ]* 28.21 Write property test for time estimation
    - **Property 92: Parcel delivery time estimation**
    - **Validates: Requirements 17.13**

- [x] 29. Checkpoint - Parcel delivery complete
  - Ensure all parcel delivery tests pass, ask the user if questions arise.

- [ ] 30. Integration testing for new features
  - [ ]* 30.1 Write integration tests for scheduled ride flow
    - Test: schedule ride → wait for matching window → match → complete
    - Test: schedule ride → modify → match → complete
    - Test: schedule ride → cancel with fee
    - Test: schedule ride → no driver found → notification
    - _Requirements: 16.1-16.12_
  
  - [ ]* 30.2 Write integration tests for parcel delivery flow
    - Test: request parcel → match → pickup with photo → deliver with signature → payment
    - Test: request parcel → weight exceeds limit → rejection
    - Test: request parcel → special instructions → driver sees instructions
    - _Requirements: 17.1-17.17_
  
  - [ ]* 30.3 Write integration tests for extended area flow
    - Test: request ride in extended area → adjusted matching → tiered fare
    - Test: driver disables extended area → excluded from extended area rides
    - Test: location beyond 20km → rejection with error
    - _Requirements: 18.1-18.12_

- [ ] 31. Final checkpoint - All new features integrated
  - Ensure all new feature tests pass
  - Verify all property-based tests pass with 100+ iterations
  - Verify all new API endpoints are functional
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each property test should run minimum 100 iterations using hypothesis
- Use pytest fixtures for test data setup
- Mock external services (payment gateways, SMS, maps) in tests
- Property tests validate universal correctness across all inputs
- Unit tests validate specific examples and edge cases
- Integration tests validate component interactions
- All monetary values in Indian Rupees (₹)
- WebSocket connections should handle reconnection gracefully
- Use Redis for real-time state (driver availability, active rides)
- Use MongoDB for location data (optimized for geospatial queries)
- Use PostgreSQL for transactional data (users, rides, payments, scheduled rides, parcels)
- Background jobs for scheduled rides should use a job scheduler (e.g., APScheduler)
- Parcel photos and signatures should be stored securely (consider cloud storage like S3)
- Extended area rides may have longer wait times - set user expectations appropriately
