# Manual Testing Checklist

## Overview

This document provides a comprehensive manual testing checklist for the Android Ride-Hailing Application. Use this checklist to verify all features work correctly across different devices, Android versions, and network conditions.

## Testing Environment

### Devices to Test

**Minimum Requirements:**
- [ ] Android 8.0 (API 26) device
- [ ] Android 10 (API 29) device
- [ ] Android 12 (API 31) device
- [ ] Android 14 (API 34) device

**Screen Sizes:**
- [ ] Small phone (< 5.5")
- [ ] Medium phone (5.5" - 6.5")
- [ ] Large phone (> 6.5")
- [ ] Tablet (7"+)

**Manufacturers:**
- [ ] Samsung device
- [ ] Google Pixel device
- [ ] One other manufacturer (Xiaomi, OnePlus, etc.)

### Network Conditions

Test under various network conditions:
- [ ] WiFi (good connection)
- [ ] 4G/LTE (good connection)
- [ ] 3G (slow connection)
- [ ] Poor connection (airplane mode toggle)
- [ ] Offline mode

## Rider App Testing

### 1. Authentication Flow

**Login with OTP:**
- [ ] Enter valid phone number
- [ ] Receive OTP code
- [ ] Enter correct OTP
- [ ] Successfully logged in
- [ ] Enter incorrect OTP → Error shown
- [ ] Request OTP resend → New code received

**Biometric Authentication:**
- [ ] Enable biometric login in settings
- [ ] Logout and return to login
- [ ] Biometric prompt appears
- [ ] Authenticate with fingerprint/face → Success
- [ ] Cancel biometric → Fall back to OTP
- [ ] Biometric fails → Fall back to OTP

**Edge Cases:**
- [ ] Invalid phone number format → Error shown
- [ ] Network error during OTP send → Error shown
- [ ] Network error during OTP verify → Error shown

### 2. Ride Request Flow

**Basic Ride Request:**
- [ ] Open app → Map loads with current location
- [ ] Tap pickup location → Location search opens
- [ ] Search for pickup address → Results shown
- [ ] Select pickup location → Marker placed on map
- [ ] Tap dropoff location → Location search opens
- [ ] Search for dropoff address → Results shown
- [ ] Select dropoff location → Marker placed on map
- [ ] Fare estimate displayed
- [ ] Tap "Request Ride" → Ride requested
- [ ] Searching for driver animation shown
- [ ] Driver accepts → Driver details shown
- [ ] Driver location updates in real-time
- [ ] ETA updates as driver approaches
- [ ] Driver arrives → Notification received
- [ ] Ride starts → Route shown on map
- [ ] Ride completes → Payment screen shown

**Edge Cases:**
- [ ] Request ride with same pickup/dropoff → Error shown
- [ ] Request ride outside service area → Error shown
- [ ] Cancel ride before driver accepts → Cancellation confirmed
- [ ] Cancel ride after driver accepts → Cancellation fee shown
- [ ] No drivers available → Appropriate message shown
- [ ] Network error during request → Error shown and retry option

### 3. Scheduled Rides

**Schedule a Ride:**
- [ ] Tap "Schedule Ride"
- [ ] Select pickup and dropoff locations
- [ ] Select date and time (1 hour minimum)
- [ ] Fare estimate shown
- [ ] Confirm schedule → Ride scheduled
- [ ] Scheduled ride appears in list
- [ ] Receive reminder 30 minutes before ride
- [ ] Cancel scheduled ride → Cancellation confirmed

**Edge Cases:**
- [ ] Try to schedule < 1 hour ahead → Error shown
- [ ] Try to schedule > 7 days ahead → Error shown
- [ ] Schedule ride then go offline → Ride still in list

### 4. Parcel Delivery

**Request Parcel Delivery:**
- [ ] Tap "Parcel Delivery"
- [ ] Select parcel size (Small/Medium/Large)
- [ ] Enter sender details
- [ ] Enter recipient details
- [ ] Select pickup and dropoff locations
- [ ] Fare estimate shown
- [ ] Confirm request → Parcel delivery requested
- [ ] Driver accepts → Driver details shown
- [ ] Driver picks up parcel → Confirmation shown
- [ ] Driver delivers parcel → Delivery confirmed

**Edge Cases:**
- [ ] Missing sender/recipient details → Error shown
- [ ] Invalid phone numbers → Error shown

### 5. Payment

**Process Payment:**
- [ ] Ride completes → Payment screen shown
- [ ] Fare breakdown displayed (base fare, distance, time, surge)
- [ ] Confirm payment → Payment processed
- [ ] Receipt generated
- [ ] Receipt can be shared (PDF/image)

**Payment History:**
- [ ] View payment history
- [ ] Filter by date range
- [ ] View individual receipt
- [ ] Share receipt

**Edge Cases:**
- [ ] Payment fails → Error shown and retry option
- [ ] Network error during payment → Queued for retry

### 6. Rating and Review

**Rate Driver:**
- [ ] Payment completes → Rating dialog shown
- [ ] Select star rating (1-5)
- [ ] Enter review text (optional)
- [ ] Submit rating → Rating submitted
- [ ] Rating appears in history

**View Ratings:**
- [ ] View own average rating
- [ ] View rating history
- [ ] View individual ratings with reviews

**Edge Cases:**
- [ ] Submit rating offline → Queued for sync
- [ ] Review text > 500 characters → Error shown

### 7. In-Ride Chat

**Chat with Driver:**
- [ ] Active ride → Chat button visible
- [ ] Tap chat → Chat screen opens
- [ ] Send message → Message sent
- [ ] Receive message from driver → Notification shown
- [ ] Message status updates (sent, delivered, read)
- [ ] Ride completes → Chat archived

**Edge Cases:**
- [ ] Send message offline → Queued for sending
- [ ] Receive message when app in background → Notification shown

### 8. Emergency Features

**SOS Button:**
- [ ] Active ride → SOS button visible
- [ ] Tap SOS → Confirmation dialog shown
- [ ] Confirm SOS → Alert sent to backend
- [ ] Emergency contacts notified via SMS
- [ ] Location update frequency increased

**Emergency Contacts:**
- [ ] Add emergency contact
- [ ] Edit emergency contact
- [ ] Remove emergency contact
- [ ] Share ride with emergency contact → Link sent

**Edge Cases:**
- [ ] Trigger SOS offline → Queued for sending when online

### 9. Profile Management

**Update Profile:**
- [ ] View profile
- [ ] Edit name → Saved successfully
- [ ] Edit email → Saved successfully
- [ ] Upload profile photo → Photo uploaded and compressed
- [ ] View profile photo

**Emergency Contacts:**
- [ ] Add emergency contact with name and phone
- [ ] Edit emergency contact
- [ ] Remove emergency contact
- [ ] Call emergency contact

**Edge Cases:**
- [ ] Upload large photo → Compressed to < 500KB
- [ ] Update profile offline → Queued for sync

### 10. Ride History

**View Ride History:**
- [ ] View list of past rides
- [ ] Rides sorted by date (newest first)
- [ ] Filter by date range
- [ ] Search by location or driver name
- [ ] Tap ride → View ride details
- [ ] View route on map
- [ ] View receipt

**Edge Cases:**
- [ ] Load ride history offline → Cached rides shown
- [ ] Pagination works for > 20 rides

### 11. Settings

**App Settings:**
- [ ] Change language (English/Hindi) → UI updates
- [ ] Change theme (Light/Dark/System) → Theme updates
- [ ] Toggle notification preferences → Saved
- [ ] View app version and build info
- [ ] Logout → Redirected to login

**Edge Cases:**
- [ ] Change settings offline → Saved locally

### 12. Offline Mode

**Offline Functionality:**
- [ ] Go offline → Offline indicator shown
- [ ] View ride history → Cached rides shown
- [ ] View profile → Cached data shown
- [ ] Try to request ride → Blocked with message
- [ ] Rate ride offline → Queued for sync
- [ ] Send chat message offline → Queued for sending
- [ ] Go online → Queued actions sync automatically

## Driver App Testing

### 1. Authentication Flow

Same as Rider App (see above)

### 2. Availability Management

**Go Online:**
- [ ] Tap "Go Online" toggle
- [ ] Location permission granted
- [ ] Foreground service starts
- [ ] Location updates every 10 seconds
- [ ] Status shows "Online"

**Go Offline:**
- [ ] Tap "Go Offline" toggle
- [ ] Foreground service stops
- [ ] Status shows "Offline"

**Edge Cases:**
- [ ] Battery < 15% → Warning shown
- [ ] GPS disabled → Prompt to enable
- [ ] Location permission denied → Cannot go online

### 3. Ride Request Handling

**Receive Ride Request:**
- [ ] Driver online → Ride request received
- [ ] Push notification shown
- [ ] Sound plays
- [ ] Request dialog shown with details
- [ ] Countdown timer starts (30 seconds)
- [ ] Accept ride → Navigate to pickup
- [ ] Reject ride → Request dismissed

**Multiple Requests:**
- [ ] Receive multiple requests → Queued
- [ ] One request shown at a time
- [ ] Accept/reject → Next request shown

**Edge Cases:**
- [ ] Timer expires → Auto-rejected
- [ ] Network error during accept → Error shown and retry

### 4. Navigation and Ride Execution

**Navigate to Pickup:**
- [ ] Accept ride → Navigation starts
- [ ] Turn-by-turn directions shown
- [ ] ETA updates
- [ ] Arrive at pickup → "Start Ride" button enabled
- [ ] Tap "Start Ride" → Ride started

**Navigate to Dropoff:**
- [ ] Ride started → Navigation to dropoff
- [ ] Turn-by-turn directions shown
- [ ] Arrive at dropoff → "Complete Ride" button enabled
- [ ] Tap "Complete Ride" → Ride completed

**Cancel Ride:**
- [ ] Tap cancel button
- [ ] Select cancellation reason
- [ ] Confirm cancellation → Ride cancelled

**Edge Cases:**
- [ ] GPS signal lost → Warning shown
- [ ] Network error during status update → Queued for retry

### 5. Parcel Delivery (Driver)

**Accept Parcel Delivery:**
- [ ] Receive parcel delivery request
- [ ] Parcel details shown (size, sender, recipient)
- [ ] Accept request → Navigate to pickup
- [ ] Arrive at pickup → "Confirm Pickup" button shown
- [ ] Tap "Confirm Pickup" → Pickup confirmed
- [ ] Navigate to dropoff
- [ ] Arrive at dropoff → "Confirm Delivery" button shown
- [ ] Tap "Confirm Delivery" → Delivery confirmed

**Edge Cases:**
- [ ] Parcel acceptance disabled in settings → No parcel requests received

### 6. Earnings Tracking

**View Earnings:**
- [ ] View today's earnings
- [ ] View this week's earnings
- [ ] View this month's earnings
- [ ] View earnings breakdown (total rides, average fare)
- [ ] View pending earnings
- [ ] View ride list with individual fares

**Edge Cases:**
- [ ] Earnings update after each ride completion
- [ ] View earnings offline → Cached data shown

### 7. Rating and Performance

**View Ratings:**
- [ ] View average rating
- [ ] View rating breakdown (5 star, 4 star, etc.)
- [ ] View acceptance rate
- [ ] View cancellation rate
- [ ] View improvement suggestions for low ratings

**Rate Rider:**
- [ ] Ride completes → Rate rider dialog shown
- [ ] Select star rating
- [ ] Submit rating → Rating submitted

**Edge Cases:**
- [ ] Submit rating offline → Queued for sync

### 8. Driver Settings

**Driver-Specific Settings:**
- [ ] Toggle parcel delivery acceptance
- [ ] Toggle extended service area preference
- [ ] Update vehicle details
- [ ] View driver profile

## Cross-App Testing

### 1. End-to-End Ride Flow

**Complete Ride Flow:**
- [ ] Rider requests ride
- [ ] Driver receives request
- [ ] Driver accepts ride
- [ ] Rider sees driver details and location
- [ ] Driver navigates to pickup
- [ ] Rider sees driver approaching
- [ ] Driver arrives at pickup
- [ ] Driver starts ride
- [ ] Rider sees ride in progress
- [ ] Driver navigates to dropoff
- [ ] Rider sees route and ETA
- [ ] Driver completes ride
- [ ] Rider processes payment
- [ ] Both rate each other

### 2. Real-Time Updates

**Location Updates:**
- [ ] Driver location updates on rider's map
- [ ] Updates smooth (no jumping)
- [ ] ETA updates as driver moves

**Status Updates:**
- [ ] Ride status changes reflect on both apps
- [ ] WebSocket connection stable
- [ ] Reconnects automatically if disconnected

### 3. Chat Communication

**Bidirectional Chat:**
- [ ] Rider sends message → Driver receives
- [ ] Driver sends message → Rider receives
- [ ] Messages show correct timestamps
- [ ] Message status updates correctly
- [ ] Notifications work when app in background

## Performance Testing

### App Startup

- [ ] Cold start < 3 seconds
- [ ] Warm start < 1 second
- [ ] Splash screen shows briefly

### Map Performance

- [ ] Map loads quickly
- [ ] Smooth panning and zooming
- [ ] Markers update without lag
- [ ] Polylines draw smoothly

### Animation Performance

- [ ] All animations smooth (60 FPS)
- [ ] No frame drops during transitions
- [ ] Loading indicators smooth

### Memory Usage

- [ ] App uses < 200MB RAM during normal use
- [ ] No memory leaks during extended use
- [ ] App doesn't crash after hours of use

### Battery Usage

- [ ] Rider app: Minimal battery drain
- [ ] Driver app (online): Moderate battery drain
- [ ] Driver app (offline): Minimal battery drain
- [ ] Location tracking optimized

## Accessibility Testing

### Screen Reader (TalkBack)

- [ ] Enable TalkBack
- [ ] Navigate through all screens
- [ ] All interactive elements have content descriptions
- [ ] All text is readable
- [ ] Navigation is logical

### Text Scaling

- [ ] Set text size to 200%
- [ ] All text visible (no truncation)
- [ ] Layouts don't break
- [ ] Buttons still accessible

### Color Contrast

- [ ] All text meets WCAG 2.1 Level AA
- [ ] Test in light mode
- [ ] Test in dark mode
- [ ] Color is not the only indicator

### Touch Targets

- [ ] All interactive elements ≥ 48dp × 48dp
- [ ] Adequate spacing between elements
- [ ] Easy to tap without mistakes

## Security Testing

### Authentication

- [ ] JWT tokens stored securely (EncryptedSharedPreferences)
- [ ] Tokens not visible in logs
- [ ] Tokens refresh automatically
- [ ] Logout clears all tokens

### Data Security

- [ ] Sensitive data encrypted at rest
- [ ] HTTPS used for all API calls
- [ ] WSS used for WebSocket
- [ ] Certificate pinning works

### Input Validation

- [ ] SQL injection attempts blocked
- [ ] XSS attempts blocked
- [ ] Invalid inputs rejected
- [ ] Error messages don't leak sensitive info

## Edge Cases and Error Scenarios

### Network Errors

- [ ] API timeout → Error shown and retry option
- [ ] Server error (500) → Generic error shown
- [ ] No internet → Offline mode activated
- [ ] Intermittent connection → Retry logic works

### Permission Denials

- [ ] Location permission denied → Cannot request/accept rides
- [ ] Notification permission denied → No push notifications
- [ ] Camera permission denied → Cannot upload photo

### Low Resources

- [ ] Low battery → Warning shown (driver app)
- [ ] Low storage → App still functions
- [ ] Low memory → App doesn't crash

### Concurrent Actions

- [ ] Multiple rapid taps → No duplicate actions
- [ ] Rapid navigation → No crashes
- [ ] Background/foreground transitions → State preserved

## Regression Testing

After any bug fixes or changes, retest:

- [ ] Authentication flow
- [ ] Ride request flow
- [ ] Payment flow
- [ ] Real-time updates
- [ ] Offline mode

## Sign-Off

**Tester Name:** _______________
**Date:** _______________
**Device:** _______________
**Android Version:** _______________
**App Version:** _______________

**Overall Status:**
- [ ] All critical features working
- [ ] All major features working
- [ ] Minor issues documented
- [ ] Ready for release

**Issues Found:** (List any issues discovered during testing)

1. 
2. 
3. 

**Notes:**
