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
  
  - [ ] 3.3 Implement phone verification flow
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
  
  - [ ] 3.5 Implement login and JWT token generation
    - Create POST /api/auth/login endpoint
    - Validate credentials against hashed passwords
    - Generate JWT tokens with user claims
    - Store session in Redis
    - _Requirements: 1.8_
  
  - [ ]* 3.6 Write property test for authentication
    - **Property 6: Authentication session creation**
    - **Validates: Requirements 1.8**
  
  - [ ] 3.7 Implement ID document verification for drivers
    - Create POST /api/auth/driver/verify-id endpoint
    - Accept document upload (image file)
    - Store document metadata
    - Implement basic validation checks
    - _Requirements: 1.6_

- [ ] 4. Checkpoint - Authentication complete
  - Ensure all authentication tests pass, ask the user if questions arise.


- [ ] 5. Location Service implementation
  - [ ] 5.1 Create Location data model for MongoDB
    - Define Location schema with latitude, longitude, address
    - Create indexes for geospatial queries
    - _Requirements: 2.1, 8.1, 13.5_
  
  - [ ] 5.2 Implement address validation and boundary checking
    - Create function to validate Indore city boundaries
    - Define boundary coordinates (lat: 22.6-22.8, lon: 75.7-75.9)
    - Implement isWithinServiceArea function
    - _Requirements: 2.4, 13.6_
  
  - [ ]* 5.3 Write property tests for boundary validation
    - **Property 8: Boundary validation**
    - **Property 57: Address validation**
    - **Validates: Requirements 2.4, 13.6**
  
  - [ ] 5.4 Implement distance calculation
    - Create calculateDistance function using Haversine formula
    - Return distance in kilometers
    - _Requirements: 5.1, 5.2_
  
  - [ ] 5.5 Integrate with Google Maps API
    - Set up Google Maps client
    - Implement address search functionality
    - Implement route calculation with polyline
    - _Requirements: 2.6, 8.3, 8.6_
  
  - [ ]* 5.6 Write property test for address search filtering
    - **Property 56: Address search boundary filtering**
    - **Validates: Requirements 13.5**
  
  - [ ] 5.7 Implement driver location tracking
    - Create updateDriverLocation function to store in MongoDB
    - Create getDriverLocation function to retrieve latest location
    - Implement location update endpoint POST /api/location/driver
    - _Requirements: 4.4, 8.1, 8.2_
  
  - [ ] 5.8 Implement route deviation detection
    - Create detectRouteDeviation function
    - Calculate distance from current location to expected route
    - Return alert if deviation exceeds threshold (500m)
    - _Requirements: 11.4_
  
  - [ ]* 5.9 Write property test for route deviation
    - **Property 53: Route deviation alert**
    - **Validates: Requirements 11.4**

- [ ] 6. Fare Calculation Service implementation
  - [ ] 6.1 Implement fare calculation logic
    - Create calculateEstimatedFare function
    - Apply formula: (₹30 + distance_km * ₹12) * surge_multiplier
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
  - [ ] 7.1 Implement ride request creation
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
  
  - [ ] 7.3 Implement ride lifecycle management
    - Create functions for status transitions: matched → in_progress → completed
    - Implement startRide function
    - Implement completeRide function with final fare calculation
    - Update ride status in database
    - _Requirements: 3.3, 5.4_
  
  - [ ] 7.4 Implement ride history endpoints
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
  
  - [ ] 7.6 Implement cancellation logic
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

- [ ] 8. Checkpoint - Core ride management complete
  - Ensure all tests pass, ask the user if questions arise.


- [ ] 9. Ride Matching Engine implementation
  - [ ] 9.1 Implement driver availability management
    - Create POST /api/drivers/availability endpoint
    - Implement setDriverAvailable function (stores in Redis)
    - Implement setDriverUnavailable function
    - Store driver status and current location
    - _Requirements: 3.7, 12.1, 12.2, 12.3_
  
  - [ ]* 9.2 Write property tests for driver availability
    - **Property 21: Status toggling**
    - **Property 22: Availability-based matching inclusion**
    - **Validates: Requirements 3.7, 12.1, 12.2, 12.3**
  
  - [ ] 9.3 Implement driver search by proximity
    - Create getAvailableDrivers function
    - Query MongoDB for drivers within radius of pickup location
    - Filter by availability status from Redis
    - Sort by distance from pickup
    - _Requirements: 3.1, 4.3_
  
  - [ ]* 9.4 Write property tests for proximity-based search
    - **Property 11: Proximity-based notification**
    - **Property 18: Distance-based prioritization**
    - **Validates: Requirements 3.1, 4.3**
  
  - [ ] 9.5 Implement ride broadcasting logic
    - Create broadcastRideRequest function
    - Find available drivers within initial 5km radius
    - Store broadcast details in Redis
    - Return list of notified drivers
    - _Requirements: 2.3, 3.1_
  
  - [ ]* 9.6 Write property test for broadcasting
    - **Property 10: Ride request broadcasting**
    - **Validates: Requirements 2.3**
  
  - [ ] 9.7 Implement ride matching algorithm
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
  
  - [ ] 9.9 Implement search radius expansion
    - Create expandSearchRadius function
    - Trigger after 2-minute timeout
    - Increase radius by 2km
    - Re-broadcast to newly included drivers
    - _Requirements: 3.5_
  
  - [ ]* 9.10 Write property test for radius expansion
    - **Property 15: Search radius expansion**
    - **Validates: Requirements 3.5**
  
  - [ ] 9.11 Implement driver rejection handling
    - Create rejectRide function
    - Keep ride request active for other drivers
    - Continue broadcasting
    - _Requirements: 3.4_
  
  - [ ]* 9.12 Write property test for rejection handling
    - **Property 14: Continued broadcasting after rejection**
    - **Validates: Requirements 3.4**
  
  - [ ] 9.13 Implement driver cancellation handling
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
  - [ ] 10.1 Set up WebSocket connection management
    - Create WebSocket endpoint /ws
    - Implement connection authentication via JWT
    - Maintain active connections in memory (connection pool)
    - Handle connection lifecycle (connect, disconnect, reconnect)
    - _Requirements: 8.1, 8.2_
  
  - [ ] 10.2 Implement ride request broadcasting via WebSocket
    - Send ride request notifications to connected drivers
    - Include pickup, destination, estimated fare
    - _Requirements: 2.3, 3.2_
  
  - [ ]* 10.3 Write property test for notification content
    - **Property 12: Notification content completeness**
    - **Validates: Requirements 3.2**
  
  - [ ] 10.4 Implement driver acceptance/rejection via WebSocket
    - Handle driver accept/reject messages
    - Call matching engine functions
    - Broadcast match confirmation to rider
    - Cancel notifications to other drivers
    - _Requirements: 3.3, 4.2_
  
  - [ ]* 10.5 Write property test for notification cancellation
    - **Property 17: Notification cancellation after match**
    - **Validates: Requirements 4.2**
  
  - [ ] 10.6 Implement real-time location updates
    - Accept location updates from drivers every 10 seconds
    - Store in MongoDB
    - Broadcast to matched rider
    - _Requirements: 8.1, 8.2_
  
  - [ ]* 10.7 Write property tests for location tracking
    - **Property 19: Real-time location usage**
    - **Property 38: Location sharing on match**
    - **Validates: Requirements 4.4, 8.1**
  
  - [ ] 10.8 Implement proximity notifications
    - Monitor driver location during driver_arriving status
    - Send notification when within 500m of pickup
    - _Requirements: 8.4_
  
  - [ ]* 10.9 Write property test for proximity notification
    - **Property 40: Proximity notification**
    - **Validates: Requirements 8.4**

- [ ] 11. Checkpoint - Real-time features complete
  - Ensure all WebSocket tests pass, ask the user if questions arise.


- [ ] 12. Payment Service implementation
  - [ ] 12.1 Set up payment gateway integrations
    - Install Razorpay and Paytm Python SDKs
    - Configure API keys and credentials
    - Create PaymentGateway abstraction interface
    - Implement RazorpayGateway class
    - Implement PaytmGateway class
    - _Requirements: 6.2_
  
  - [ ] 12.2 Implement payment processing
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
  
  - [ ] 12.5 Implement driver payout scheduling
    - Create scheduleDriverPayout function
    - Schedule payouts within 24 hours of ride completion
    - Store payout records with status
    - Create background job to process scheduled payouts
    - _Requirements: 6.6_
  
  - [ ]* 12.6 Write property test for payout scheduling
    - **Property 31: Driver payout scheduling**
    - **Validates: Requirements 6.6**
  
  - [ ] 12.7 Create payment endpoints
    - Create POST /api/payments/process endpoint
    - Create GET /api/payments/history endpoint
    - Create POST /api/payments/retry endpoint for failed payments
    - _Requirements: 6.1, 6.4_

- [ ] 13. Rating and Review System implementation
  - [ ] 13.1 Implement rating submission
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
  
  - [ ] 13.3 Implement average rating calculation
    - Create calculateAverageRating function
    - Calculate from last 100 rides (or all if fewer)
    - Update user's averageRating field
    - Trigger after each new rating
    - _Requirements: 7.4_
  
  - [ ]* 13.4 Write property test for average calculation
    - **Property 35: Average rating calculation**
    - **Validates: Requirements 7.4**
  
  - [ ] 13.5 Implement low rating flagging
    - Create checkDriverRating function
    - Flag driver account if average falls below 3.5
    - Store flag in driver profile
    - _Requirements: 7.5_
  
  - [ ]* 13.6 Write property test for rating flagging
    - **Property 36: Low rating flagging**
    - **Validates: Requirements 7.5**
  
  - [ ] 13.7 Implement rating display
    - Include driver rating in ride request response
    - Include rating and total rides in driver profile
    - _Requirements: 7.6, 7.7_
  
  - [ ]* 13.8 Write property test for rating display
    - **Property 37: Rating display completeness**
    - **Validates: Requirements 7.6, 7.7**

- [ ] 14. Vehicle Management implementation
  - [ ] 14.1 Implement vehicle registration
    - Create POST /api/drivers/vehicle endpoint
    - Validate required fields: registration number, make, model, color
    - Validate insurance expiry is at least 30 days in future
    - Store vehicle info in driver profile
    - _Requirements: 10.1, 10.3_
  
  - [ ]* 14.2 Write property tests for vehicle validation
    - **Property 47: Insurance validity requirement**
    - **Validates: Requirements 10.3**
  
  - [ ] 14.3 Implement vehicle details in notifications
    - Include vehicle info in ride match notifications
    - _Requirements: 10.4_
  
  - [ ]* 14.4 Write property test for vehicle details display
    - **Property 48: Vehicle details in match notification**
    - **Validates: Requirements 10.4**
  
  - [ ] 14.5 Implement insurance expiry monitoring
    - Create background job to check insurance expiry daily
    - Suspend drivers with expired insurance
    - _Requirements: 10.5_
  
  - [ ]* 14.6 Write property test for insurance suspension
    - **Property 49: Insurance expiry suspension**
    - **Validates: Requirements 10.5**
  
  - [ ] 14.7 Implement vehicle update with re-verification
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
  - [ ] 16.1 Implement emergency contact management
    - Create POST /api/users/emergency-contacts endpoint
    - Validate maximum 3 contacts per user
    - Store emergency contacts linked to user
    - Create GET and DELETE endpoints for contact management
    - _Requirements: 11.5_
  
  - [ ]* 16.2 Write property test for contact limit
    - **Property 54: Emergency contact limit**
    - **Validates: Requirements 11.5**
  
  - [ ] 16.3 Implement emergency alert system
    - Create POST /api/rides/{rideId}/emergency endpoint
    - Notify platform administrators immediately
    - Include ride details and current location
    - Log incident with timestamp
    - _Requirements: 11.2, 11.6_
  
  - [ ]* 16.4 Write property tests for emergency alerts
    - **Property 51: Emergency notification**
    - **Property 55: Emergency incident logging**
    - **Validates: Requirements 11.2, 11.6**
  
  - [ ] 16.5 Implement ride sharing with emergency contacts
    - Create POST /api/rides/{rideId}/share endpoint
    - Generate shareable link with ride details
    - Send link to emergency contacts via SMS
    - Include live location tracking
    - _Requirements: 11.3_
  
  - [ ]* 16.6 Write property test for ride sharing
    - **Property 52: Ride sharing capability**
    - **Validates: Requirements 11.3**
  
  - [ ] 16.7 Implement route deviation monitoring
    - Create background job to check route deviation
    - Run every 30 seconds for in-progress rides
    - Call detectRouteDeviation from Location Service
    - Send alert if deviation exceeds threshold
    - _Requirements: 11.4_

- [ ] 17. Notification Service implementation
  - [ ] 17.1 Set up SMS gateway integration
    - Install Twilio Python SDK
    - Configure Twilio credentials
    - Create sendSMS function
    - _Requirements: 1.2, 14.6_
  
  - [ ] 17.2 Implement notification functions
    - Create sendInAppNotification function (via WebSocket)
    - Create sendSMSNotification function
    - Create sendDualNotification for critical events
    - _Requirements: 14.6_
  
  - [ ]* 17.3 Write property test for dual notifications
    - **Property 63: Dual notification channels**
    - **Validates: Requirements 14.6**
  
  - [ ] 17.4 Implement ride event notifications
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
  - [ ] 18.1 Implement route display for in-progress rides
    - Create GET /api/rides/{rideId}/route endpoint
    - Return current route with polyline
    - Include estimated time to destination
    - _Requirements: 8.3_
  
  - [ ]* 18.2 Write property test for route display
    - **Property 39: In-progress route display**
    - **Validates: Requirements 8.3**
  
  - [ ] 18.3 Implement completed ride route storage
    - Store complete route in Ride model on completion
    - Include all location points from ride
    - _Requirements: 8.5_
  
  - [ ]* 18.4 Write property test for route storage
    - **Property 41: Completed ride route storage**
    - **Validates: Requirements 8.5**

- [ ] 19. Receipt generation implementation
  - [ ] 19.1 Implement PDF receipt generation
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
  - [ ] 20.1 Implement availability time tracking
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
  - [ ] 21.1 Implement comprehensive error handling
    - Add global exception handlers for FastAPI
    - Implement retry logic with exponential backoff for external services
    - Implement circuit breaker for payment gateways
    - Add proper error responses with status codes
    - _Requirements: All (cross-cutting)_
  
  - [ ] 21.2 Add request validation middleware
    - Validate JWT tokens on protected endpoints
    - Validate request body schemas
    - Validate user permissions (rider vs driver actions)
    - _Requirements: 1.8_
  
  - [ ] 21.3 Add logging and monitoring
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

- [ ] 23. Final checkpoint - Complete system integration
  - Ensure all integration tests pass
  - Verify all property-based tests pass with 100+ iterations
  - Verify all API endpoints are functional
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
- Use PostgreSQL for transactional data (users, rides, payments)
