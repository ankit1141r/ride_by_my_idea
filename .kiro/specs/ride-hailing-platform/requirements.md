# Requirements Document: Ride-Hailing Platform

## Introduction

This document specifies the requirements for a web-first ride-hailing platform focused on intra-city transportation within Indore. The platform connects riders seeking immediate transportation with drivers who provide ride services. This represents Phase 1 of a larger multi-purpose transportation platform, establishing the foundation for future features including planned trip sharing and peer-to-peer parcel delivery.

## Glossary

- **Rider**: A user who requests and receives transportation services
- **Driver**: A verified user who provides transportation services using their vehicle
- **Ride_Request**: A rider's request for immediate transportation from a pickup location to a destination
- **Ride_Match**: The system's assignment of a driver to a ride request
- **Fare**: The calculated cost for a ride based on distance and other factors
- **Payment_Gateway**: External service (Razorpay, Paytm) that processes financial transactions
- **Verification_System**: The subsystem that validates user identity through phone and ID verification
- **Ride_Session**: An active ride from acceptance through completion
- **Platform**: The ride-hailing web application system

## Requirements

### Requirement 1: User Registration and Authentication

**User Story:** As a new user, I want to register and verify my identity, so that I can safely use the platform as either a rider or driver.

#### Acceptance Criteria

1. WHEN a user initiates registration, THE Platform SHALL collect phone number, name, and email address
2. WHEN a phone number is provided, THE Verification_System SHALL send a verification code via SMS
3. WHEN a user enters the verification code within 10 minutes, THE Verification_System SHALL validate the code and mark the phone as verified
4. IF the verification code is incorrect after 3 attempts, THEN THE Verification_System SHALL block further attempts for 30 minutes
5. WHERE a user registers as a driver, THE Verification_System SHALL require government-issued ID verification
6. WHEN ID documents are uploaded, THE Verification_System SHALL validate document authenticity and match with provided user details
7. THE Platform SHALL store user credentials securely using industry-standard encryption
8. WHEN a registered user logs in with valid credentials, THE Platform SHALL create an authenticated session

### Requirement 2: Ride Request Creation

**User Story:** As a rider, I want to request an immediate ride with my pickup and destination locations, so that I can get transportation when I need it.

#### Acceptance Criteria

1. WHEN a verified rider specifies a pickup location and destination within Indore, THE Platform SHALL create a ride request
2. WHEN creating a ride request, THE Platform SHALL calculate and display the estimated fare before confirmation
3. WHEN a rider confirms the ride request, THE Platform SHALL broadcast the request to available drivers in the pickup area
4. IF either pickup or destination is outside Indore city limits, THEN THE Platform SHALL reject the ride request with a clear error message
5. WHEN a ride request is created, THE Platform SHALL estimate arrival time based on available drivers
6. THE Platform SHALL allow riders to specify pickup location using map selection or address search

### Requirement 3: Driver Ride Management

**User Story:** As a driver, I want to receive and respond to ride requests, so that I can choose which rides to accept based on my availability and preferences.

#### Acceptance Criteria

1. WHEN a ride request is broadcast, THE Platform SHALL notify all available drivers within 5 km of the pickup location
2. WHEN a driver receives a ride request notification, THE Platform SHALL display pickup location, destination, and estimated fare
3. WHEN a driver accepts a ride request, THE Platform SHALL create a ride match and notify the rider
4. WHEN a driver rejects a ride request, THE Platform SHALL continue broadcasting to other available drivers
5. IF no driver accepts within 2 minutes, THEN THE Platform SHALL expand the search radius by 2 km and re-broadcast
6. WHEN a driver is matched with a ride, THE Platform SHALL mark the driver as unavailable for new requests
7. THE Platform SHALL allow drivers to toggle their availability status between available and unavailable

### Requirement 4: Real-Time Ride Matching

**User Story:** As the system, I want to efficiently match riders with nearby available drivers, so that rides are fulfilled quickly and fairly.

#### Acceptance Criteria

1. WHEN multiple drivers accept the same ride request, THE Platform SHALL assign the ride to the driver closest to the pickup location
2. WHEN a ride match is created, THE Platform SHALL cancel notifications to all other drivers who received the request
3. THE Platform SHALL prioritize drivers based on proximity to pickup location, with closer drivers receiving notifications first
4. WHEN calculating driver proximity, THE Platform SHALL use real-time driver location data
5. IF a matched driver cancels before pickup, THEN THE Platform SHALL re-broadcast the ride request to available drivers

### Requirement 5: Fare Calculation

**User Story:** As a rider, I want to know the fare before confirming my ride, so that I can make informed decisions about my transportation costs.

#### Acceptance Criteria

1. WHEN a ride request is created, THE Platform SHALL calculate fare based on straight-line distance between pickup and destination
2. THE Platform SHALL apply a base fare of ₹30 plus ₹12 per kilometer
3. WHEN displaying estimated fare, THE Platform SHALL show the breakdown of base fare and distance charges
4. THE Platform SHALL calculate the final fare after ride completion based on actual distance traveled
5. IF the actual fare differs from estimated fare by more than 20%, THEN THE Platform SHALL charge the estimated fare
6. WHERE surge pricing is active, THE Platform SHALL apply a multiplier to the base fare calculation and display it clearly to the rider

### Requirement 6: Payment Processing

**User Story:** As a rider, I want to pay for my ride securely through integrated payment gateways, so that I can complete transactions conveniently.

#### Acceptance Criteria

1. WHEN a ride is completed, THE Platform SHALL initiate payment processing through the Payment_Gateway
2. THE Platform SHALL support payment through Razorpay and Paytm gateways
3. WHEN payment is initiated, THE Payment_Gateway SHALL process the transaction and return a success or failure status
4. IF payment fails, THEN THE Platform SHALL retry payment up to 2 additional times
5. WHEN payment succeeds, THE Platform SHALL record the transaction and mark the ride as paid
6. THE Platform SHALL transfer driver earnings to their registered bank account within 24 hours of ride completion
7. WHEN a payment transaction occurs, THE Platform SHALL store transaction details for audit purposes

### Requirement 7: Rating and Review System

**User Story:** As a user, I want to rate and review my ride experience, so that the platform maintains quality and helps other users make informed decisions.

#### Acceptance Criteria

1. WHEN a ride is completed and paid, THE Platform SHALL prompt both rider and driver to provide ratings
2. THE Platform SHALL accept ratings on a scale of 1 to 5 stars
3. WHEN a user submits a rating, THE Platform SHALL optionally allow a text review up to 500 characters
4. THE Platform SHALL calculate and display average ratings for drivers based on their last 100 rides
5. WHEN a driver's average rating falls below 3.5 stars, THE Platform SHALL flag the account for review
6. THE Platform SHALL display driver ratings to riders before they confirm ride requests
7. WHEN ratings are displayed, THE Platform SHALL show both the average rating and total number of rides completed

### Requirement 8: Basic Ride Tracking

**User Story:** As a rider, I want to track my driver's location and ride progress in real-time, so that I know when to expect pickup and can monitor my journey.

#### Acceptance Criteria

1. WHEN a ride is matched, THE Platform SHALL display the driver's real-time location to the rider
2. WHEN a driver is en route to pickup, THE Platform SHALL update the driver's location every 10 seconds
3. WHEN the ride is in progress, THE Platform SHALL display the current route and estimated time to destination
4. THE Platform SHALL notify the rider when the driver is within 500 meters of the pickup location
5. WHEN a ride is completed, THE Platform SHALL display the complete route taken during the ride
6. THE Platform SHALL calculate and display estimated time of arrival based on current traffic conditions

### Requirement 9: Ride History

**User Story:** As a user, I want to view my past rides with details, so that I can track my usage and access receipts for completed trips.

#### Acceptance Criteria

1. THE Platform SHALL maintain a complete history of all rides for each user
2. WHEN a user accesses ride history, THE Platform SHALL display rides in reverse chronological order
3. WHEN displaying ride history, THE Platform SHALL show date, time, pickup location, destination, fare, and driver rating for each ride
4. THE Platform SHALL allow users to filter ride history by date range
5. WHEN a user selects a past ride, THE Platform SHALL display complete ride details including route map and payment receipt
6. THE Platform SHALL allow users to download receipts for past rides in PDF format
7. THE Platform SHALL retain ride history for a minimum of 2 years

### Requirement 10: Driver Vehicle Management

**User Story:** As a driver, I want to register my vehicle details, so that riders can see what vehicle to expect and the platform can verify my eligibility.

#### Acceptance Criteria

1. WHERE a user registers as a driver, THE Platform SHALL require vehicle registration number, make, model, and color
2. WHEN vehicle details are provided, THE Verification_System SHALL validate the registration number against government records
3. THE Platform SHALL require vehicle insurance documentation that is valid for at least 30 days
4. WHEN a ride is matched, THE Platform SHALL display vehicle details to the rider
5. IF vehicle insurance expires, THEN THE Platform SHALL suspend the driver's account until updated documentation is provided
6. THE Platform SHALL allow drivers to update vehicle details with re-verification required

### Requirement 11: Safety and Emergency Features

**User Story:** As a user, I want access to safety features during my ride, so that I can get help quickly in case of emergencies.

#### Acceptance Criteria

1. WHEN a ride is in progress, THE Platform SHALL display an emergency button to both rider and driver
2. WHEN the emergency button is activated, THE Platform SHALL immediately notify platform administrators with ride details and current location
3. THE Platform SHALL provide a way to share live ride details with emergency contacts
4. WHEN a ride deviates significantly from the expected route, THE Platform SHALL alert the rider
5. THE Platform SHALL allow users to add up to 3 emergency contacts who can be notified during emergencies
6. WHEN an emergency is triggered, THE Platform SHALL log the incident with timestamp and location for investigation

### Requirement 12: Driver Availability and Status Management

**User Story:** As a driver, I want to control when I'm available for rides, so that I can manage my work schedule effectively.

#### Acceptance Criteria

1. THE Platform SHALL allow drivers to set their status to "Available" or "Unavailable"
2. WHEN a driver sets status to "Available", THE Platform SHALL include them in ride matching for new requests
3. WHEN a driver sets status to "Unavailable", THE Platform SHALL exclude them from receiving new ride requests
4. WHEN a driver has an active ride, THE Platform SHALL automatically set their status to "Busy"
5. WHEN a ride is completed, THE Platform SHALL automatically return the driver status to "Available"
6. THE Platform SHALL track total hours a driver has been available each day

### Requirement 13: Location Services Integration

**User Story:** As a user, I want the platform to accurately determine and use my location, so that I can easily set pickup points and the system can provide accurate navigation.

#### Acceptance Criteria

1. WHEN a user accesses the platform, THE Platform SHALL request permission to access device location
2. WHEN location permission is granted, THE Platform SHALL retrieve the user's current GPS coordinates
3. THE Platform SHALL display the user's location on an interactive map
4. THE Platform SHALL allow users to manually adjust their pickup location by dragging a map pin
5. THE Platform SHALL provide address search functionality that returns valid locations within Indore
6. WHEN a user searches for an address, THE Platform SHALL validate that the address exists and is within service boundaries
7. THE Platform SHALL update driver location continuously while they are available or on an active ride

### Requirement 14: Notification System

**User Story:** As a user, I want to receive timely notifications about my ride status, so that I stay informed throughout the ride lifecycle.

#### Acceptance Criteria

1. WHEN a ride is matched, THE Platform SHALL notify the rider with driver details and estimated arrival time
2. WHEN a driver accepts a ride, THE Platform SHALL notify the driver with pickup details
3. WHEN a driver arrives at pickup location, THE Platform SHALL notify the rider
4. WHEN a ride is completed, THE Platform SHALL notify both parties to provide ratings
5. WHEN payment is processed, THE Platform SHALL send a receipt notification to the rider
6. THE Platform SHALL support both in-app and SMS notifications for critical ride events
7. WHEN a driver cancels a matched ride, THE Platform SHALL immediately notify the rider

### Requirement 15: Cancellation Management

**User Story:** As a user, I want the ability to cancel rides when needed, so that I have flexibility if my plans change.

#### Acceptance Criteria

1. THE Platform SHALL allow riders to cancel ride requests before a driver is matched without penalty
2. WHEN a rider cancels after driver match but before pickup, THE Platform SHALL charge a cancellation fee of ₹20
3. THE Platform SHALL allow drivers to cancel accepted rides before pickup
4. WHEN a driver cancels a matched ride, THE Platform SHALL record the cancellation in their history
5. IF a driver cancels more than 3 rides in a day, THEN THE Platform SHALL temporarily suspend their account for 24 hours
6. WHEN a cancellation occurs, THE Platform SHALL notify the other party immediately
7. THE Platform SHALL not allow cancellations after the ride has started

## Notes

- All monetary values are in Indian Rupees (₹)
- Distance calculations should account for Indore's road network
- The system should be designed to scale beyond Indore in future phases
- Integration with payment gateways should follow PCI DSS compliance standards
- Location data should be handled in compliance with privacy regulations
