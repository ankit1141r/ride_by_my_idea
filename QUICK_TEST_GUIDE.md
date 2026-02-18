# Quick Test Guide - New Features

## Prerequisites

1. **Run Database Migrations**
   ```bash
   alembic upgrade head
   ```

2. **Start the Server**
   ```bash
   python run.py
   ```

3. **Get Authentication Token**
   - Register/login as a rider
   - Register/login as a driver
   - Save the JWT tokens

---

## Test 1: Geographical Expansion

### Update Driver Preferences

```bash
curl -X PUT http://localhost:8001/api/drivers/preferences \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_DRIVER_TOKEN" \
  -d '{
    "accept_extended_area": true,
    "accept_parcel_delivery": true
  }'
```

### Request Extended Area Ride

```bash
curl -X POST http://localhost:8001/api/rides/request \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_RIDER_TOKEN" \
  -d '{
    "pickup_location": {
      "latitude": 22.7196,
      "longitude": 75.8577,
      "address": "Vijay Nagar, Indore"
    },
    "destination": {
      "latitude": 22.8000,
      "longitude": 75.9000,
      "address": "Extended Area"
    }
  }'
```

**Expected:**
- Fare calculated with tiered pricing
- Extended area flag set to true
- Only drivers with `accept_extended_area=true` notified

---

## Test 2: Scheduled Rides

### Create Scheduled Ride

```bash
curl -X POST http://localhost:8001/api/rides/scheduled \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_RIDER_TOKEN" \
  -d '{
    "pickup_location": {
      "latitude": 22.7196,
      "longitude": 75.8577,
      "address": "Vijay Nagar, Indore"
    },
    "destination": {
      "latitude": 22.7532,
      "longitude": 75.8937,
      "address": "Palasia, Indore"
    },
    "scheduled_pickup_time": "2026-02-20T10:00:00Z"
  }'
```

**Expected:**
- Ride created with status "scheduled"
- Estimated fare calculated
- Ride ID returned

### List Scheduled Rides

```bash
curl -X GET "http://localhost:8001/api/rides/scheduled?rider_id=YOUR_RIDER_ID" \
  -H "Authorization: Bearer YOUR_RIDER_TOKEN"
```

### Modify Scheduled Ride

```bash
curl -X PUT http://localhost:8001/api/rides/scheduled/RIDE_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_RIDER_TOKEN" \
  -d '{
    "scheduled_pickup_time": "2026-02-20T11:00:00Z"
  }'
```

**Expected:**
- Only works if >2 hours before pickup
- Reminder flags reset

### Cancel Scheduled Ride

```bash
curl -X DELETE "http://localhost:8001/api/rides/scheduled/RIDE_ID?rider_id=YOUR_RIDER_ID" \
  -H "Authorization: Bearer YOUR_RIDER_TOKEN"
```

**Expected:**
- Free if >1 hour before pickup
- ₹30 fee if <1 hour before pickup

---

## Test 3: Parcel Delivery

### Request Parcel Delivery

```bash
curl -X POST http://localhost:8001/api/parcels/request \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SENDER_TOKEN" \
  -d '{
    "pickup_location": {
      "latitude": 22.7196,
      "longitude": 75.8577,
      "address": "Vijay Nagar, Indore"
    },
    "delivery_location": {
      "latitude": 22.7532,
      "longitude": 75.8937,
      "address": "Palasia, Indore"
    },
    "recipient_phone": "+919876543210",
    "recipient_name": "John Doe",
    "parcel_size": "medium",
    "weight_kg": 8.5,
    "description": "Electronics package",
    "is_fragile": true,
    "is_urgent": false,
    "special_instructions": "Handle with care"
  }'
```

**Expected:**
- Fare calculated based on size (medium: ₹60 + ₹10/km)
- Estimated delivery time calculated
- Delivery ID returned

### Confirm Pickup

```bash
curl -X POST http://localhost:8001/api/parcels/DELIVERY_ID/confirm-pickup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_DRIVER_TOKEN" \
  -d '{
    "pickup_photo": "base64_encoded_image_or_url",
    "pickup_signature": "optional_signature"
  }'
```

**Expected:**
- Status changes to "in_transit"
- Pickup timestamp recorded

### Track Parcel Location

```bash
curl -X GET http://localhost:8001/api/parcels/DELIVERY_ID/location \
  -H "Authorization: Bearer YOUR_SENDER_TOKEN"
```

**Expected:**
- Real-time driver location returned
- Estimated delivery time included

### Confirm Delivery

```bash
curl -X POST http://localhost:8001/api/parcels/DELIVERY_ID/confirm-delivery \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_DRIVER_TOKEN" \
  -d '{
    "delivery_signature": "recipient_signature_required",
    "delivery_photo": "optional_photo"
  }'
```

**Expected:**
- Status changes to "delivered"
- Notifications sent to sender and recipient
- Final fare recorded

### Get Parcel History

```bash
curl -X GET "http://localhost:8001/api/parcels/history?user_id=YOUR_USER_ID&role=sender" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:**
- List of all parcels sent by user
- Sorted by creation date (newest first)

---

## Test 4: Background Jobs

### Scheduled Ride Processing

**Setup:**
1. Create a scheduled ride for 30 minutes from now
2. Wait for background job to run (runs every minute)

**Expected:**
- At 30 minutes before pickup: Status changes to "matching", drivers notified
- At 15 minutes before pickup: Reminders sent to rider (and driver if matched)
- At 15 minutes past scheduled time: If still "matching", status changes to "no_driver_found"

---

## Test 5: Fare Calculations

### Test Tiered Pricing

**10km ride:**
- Base: ₹30
- Distance: 10 × ₹12 = ₹120
- Total: ₹150

**30km ride:**
- Base: ₹30
- First 25km: 25 × ₹12 = ₹300
- Next 5km: 5 × ₹10 = ₹50
- Total: ₹380

### Test Parcel Fares

**Small parcel, 5km:**
- Base: ₹40
- Distance: 5 × ₹8 = ₹40
- Total: ₹80

**Medium parcel, 10km:**
- Base: ₹60
- Distance: 10 × ₹10 = ₹100
- Total: ₹160

**Large parcel, 15km:**
- Base: ₹80
- Distance: 15 × ₹12 = ₹180
- Total: ₹260

---

## Test 6: Driver Preferences

### Test Extended Area Filtering

1. Set driver A: `accept_extended_area = true`
2. Set driver B: `accept_extended_area = false`
3. Request ride in extended area

**Expected:**
- Only driver A receives notification
- Driver B is filtered out

### Test Parcel Delivery Filtering

1. Set driver A: `accept_parcel_delivery = true`
2. Set driver B: `accept_parcel_delivery = false`
3. Request parcel delivery

**Expected:**
- Only driver A receives notification
- Driver B is filtered out

---

## Test 7: Validation

### Test Scheduled Ride Validations

**Should Fail:**
- Scheduled time in the past
- Scheduled time >7 days in future
- Modification <2 hours before pickup
- Pickup/destination outside service area

### Test Parcel Validations

**Should Fail:**
- Weight >30kg
- Invalid parcel size (not small/medium/large)
- Unverified user requesting delivery
- Pickup/delivery outside service area

---

## Troubleshooting

### Background Job Not Running

Check if scheduler is configured in `app/main.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=background_job_service.process_scheduled_rides,
    trigger="interval",
    minutes=1
)
scheduler.start()
```

### Notifications Not Sending

1. Check notification service configuration
2. Verify SMS gateway credentials (Twilio)
3. Check WebSocket connections

### Matching Not Working

1. Verify drivers are available
2. Check driver locations are updated
3. Verify driver preferences
4. Check Redis connection

---

## Success Criteria

✅ All API endpoints return expected responses  
✅ Fare calculations are correct  
✅ Driver preferences are respected  
✅ Scheduled rides trigger matching at correct time  
✅ Reminders are sent at correct time  
✅ Parcel confirmations work with photos/signatures  
✅ Notifications are delivered  
✅ Database migrations applied successfully  

---

## Next Steps

1. Run all tests above
2. Monitor logs for errors
3. Test edge cases
4. Perform load testing
5. Deploy to staging
6. User acceptance testing
7. Deploy to production

---

**Happy Testing! 🚀**
