# Quick Start Guide

## Prerequisites

Before running the application, ensure you have the following installed:

1. **Python 3.9+**
2. **PostgreSQL** (running on localhost:5432)
3. **Redis** (running on localhost:6379)
4. **MongoDB** (running on localhost:27017)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file is already configured with default values for local development. For production, update the following:

- `SECRET_KEY` - Change to a secure random string
- `JWT_SECRET_KEY` - Change to a secure random string
- `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` - Add your Razorpay credentials
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` - Add your Twilio credentials
- `GOOGLE_MAPS_API_KEY` - Add your Google Maps API key

### 3. Set Up Databases

#### PostgreSQL
```bash
# Create database
createdb ride_hailing

# Or using psql
psql -U postgres
CREATE DATABASE ride_hailing;
\q
```

#### Redis
```bash
# Start Redis (if not running)
redis-server
```

#### MongoDB
```bash
# Start MongoDB (if not running)
mongod
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start the Application

#### Option 1: Using the startup script (recommended)
```bash
python run.py
```

#### Option 2: Using uvicorn directly
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option 3: Using the main module
```bash
python -m app.main
```

## Accessing the Application

Once started, the application will be available at:

- **API Base URL**: http://localhost:8000
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## Testing the API

### 1. Register a Rider

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "user_type": "rider"
  }'
```

### 2. Register a Driver

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543211",
    "name": "Jane Driver",
    "email": "jane@example.com",
    "password": "password123",
    "user_type": "driver",
    "license_number": "DL1234567890",
    "vehicle_registration": "MP09AB1234",
    "vehicle_make": "Maruti",
    "vehicle_model": "Swift",
    "vehicle_color": "White",
    "insurance_expiry": "2025-12-31T00:00:00"
  }'
```

### 3. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "password": "password123"
  }'
```

Save the `access_token` from the response for authenticated requests.

### 4. Request a Ride

```bash
curl -X POST "http://localhost:8000/api/rides/request" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "pickup_location": {
      "latitude": 22.7196,
      "longitude": 75.8577,
      "address": "Rajwada, Indore"
    },
    "destination": {
      "latitude": 22.7532,
      "longitude": 75.8937,
      "address": "Treasure Island Mall, Indore"
    }
  }'
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth_registration.py

# Run with verbose output
pytest -v
```

## Background Jobs

The following background jobs should be scheduled using cron or a task scheduler:

```bash
# Daily at midnight - Reset cancellation counts
python -c "from app.services.background_jobs import BackgroundJobService; from app.database import SessionLocal; db = SessionLocal(); service = BackgroundJobService(db); service.reset_daily_cancellation_counts()"

# Daily at midnight - Reset availability hours
python -c "from app.services.background_jobs import BackgroundJobService; from app.database import SessionLocal; db = SessionLocal(); service = BackgroundJobService(db); service.reset_daily_availability_hours()"

# Daily at 6 AM - Check insurance expiry
python -c "from app.services.background_jobs import BackgroundJobService; from app.database import SessionLocal; db = SessionLocal(); service = BackgroundJobService(db); service.check_insurance_expiry()"

# Hourly - Unsuspend drivers
python -c "from app.services.background_jobs import BackgroundJobService; from app.database import SessionLocal; db = SessionLocal(); service = BackgroundJobService(db); service.unsuspend_drivers_after_24_hours()"
```

## Troubleshooting

### Database Connection Errors

If you see database connection errors:

1. Ensure PostgreSQL is running: `pg_isready`
2. Check credentials in `.env` file
3. Verify database exists: `psql -l | grep ride_hailing`

### Redis Connection Errors

1. Check if Redis is running: `redis-cli ping` (should return "PONG")
2. Verify Redis host/port in `.env` file

### MongoDB Connection Errors

1. Check if MongoDB is running: `mongosh --eval "db.version()"`
2. Verify MongoDB host/port in `.env` file

### Import Errors

If you see import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Development Tips

1. **Auto-reload**: The application runs with auto-reload in debug mode, so changes to code will automatically restart the server.

2. **API Documentation**: Use the Swagger UI at `/docs` to explore and test all endpoints interactively.

3. **Logging**: Check console output for detailed logs of all requests and errors.

4. **Metrics**: Monitor application performance at `/metrics` endpoint.

## Next Steps

- Configure external service API keys (Razorpay, Twilio, Google Maps)
- Set up background job scheduling
- Configure production database credentials
- Set up monitoring and alerting
- Deploy to production environment

For more details, see `SYSTEM_STATUS.md` for complete feature documentation.
