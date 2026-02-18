# RideConnect - Ride-Hailing Platform

A comprehensive ride-hailing platform built with FastAPI, featuring real-time matching, payments, and a complete web interface.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- MongoDB (optional, for location data)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd ride-hailing-platform
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your database credentials and API keys
```

### 3. Database Setup
```bash
# Run migrations
alembic upgrade head

# Seed with test data
python seed_database.py
```

### 4. Start the Application
```bash
# Simple startup (recommended for development)
python start_server.py

# Or with full database checks
python run.py
```

### 5. Access the Application
- **API Documentation**: http://localhost:8000/docs
- **Web Interface**: http://localhost:8000/web/
- **Admin Panel**: http://localhost:8000/web/admin.html
- **Health Check**: http://localhost:8000/health

## 🌐 Web Interface

### Landing Page
- User registration and login
- Role selection (Rider/Driver)
- Feature overview

### Rider Dashboard
- Book rides with pickup/dropoff selection
- Real-time ride tracking
- Ride history and receipts
- Emergency features

### Driver Dashboard
- Go online/offline
- Accept/reject ride requests
- Earnings tracking
- Vehicle management

### Admin Panel
- System overview and metrics
- User and driver management
- Ride monitoring
- Payment tracking
- Database seeding tools

## 🔧 Features

### Core Functionality
- ✅ User authentication with phone verification
- ✅ Real-time ride matching and tracking
- ✅ Payment processing (Razorpay/Paytm)
- ✅ Rating and review system
- ✅ Emergency features and ride sharing
- ✅ Driver vehicle management
- ✅ Comprehensive admin panel

### Technical Features
- ✅ WebSocket real-time updates
- ✅ Property-based testing
- ✅ Circuit breaker pattern
- ✅ Structured logging and metrics
- ✅ Background job processing
- ✅ Geospatial location handling

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/verify/send` - Send OTP
- `POST /api/auth/verify/confirm` - Confirm OTP

### Rides
- `POST /api/rides/request` - Request a ride
- `GET /api/rides/history` - Get ride history
- `POST /api/rides/{id}/start` - Start ride
- `POST /api/rides/{id}/complete` - Complete ride

### Drivers
- `POST /api/drivers/availability` - Set availability
- `POST /api/drivers/vehicle` - Register vehicle

### Payments
- `POST /api/payments/process` - Process payment
- `GET /api/payments/history` - Payment history

### Admin
- `POST /api/admin/seed` - Seed test data
- `GET /api/admin/stats` - System statistics

## 🗄️ Database Schema

### Core Models
- **Users**: Riders and drivers with profiles
- **Rides**: Complete ride lifecycle tracking
- **Transactions**: Payment processing records
- **Ratings**: User feedback system
- **Locations**: Geospatial data (MongoDB)

## 🔐 Security Features

- JWT-based authentication
- Phone number verification
- Password hashing with bcrypt
- Request validation middleware
- Rate limiting on sensitive endpoints

## 📊 Monitoring

- Health check endpoints
- Performance metrics collection
- Structured logging with request IDs
- Error tracking and alerting

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/

# Property-based tests
pytest tests/ -k "property"

# Coverage report
pytest --cov=app tests/
```

### Test Data
The system includes comprehensive test data:
- 50 users (17 drivers, 33 riders)
- 200 sample rides with various statuses
- Payment transactions and driver payouts
- Realistic Indian names and locations

## 🚀 Deployment

### Production Setup
1. **Environment Variables**
   - Set production API keys
   - Configure database URLs
   - Set CORS origins

2. **Database Optimization**
   - Add indexes for performance
   - Configure connection pooling
   - Set up read replicas

3. **Background Jobs**
   - Schedule insurance expiry checks
   - Route deviation monitoring
   - Daily statistics reset

4. **Monitoring**
   - Set up application monitoring
   - Configure error alerting
   - Log aggregation

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up -d
```

## 🛠️ Development

### Project Structure
```
app/
├── models/          # Database models
├── routers/         # API endpoints
├── services/        # Business logic
├── middleware/      # Request middleware
├── utils/           # Utility functions
└── config.py        # Configuration

web/
├── css/            # Stylesheets
├── js/             # JavaScript files
├── index.html      # Landing page
├── rider-dashboard.html
├── driver-dashboard.html
└── admin.html      # Admin panel

tests/              # Test suite
alembic/           # Database migrations
```

### Adding New Features
1. Create database models in `app/models/`
2. Add API endpoints in `app/routers/`
3. Implement business logic in `app/services/`
4. Write tests in `tests/`
5. Update web interface as needed

## 📝 Configuration

### Required Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/rideconnect
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017

# External Services
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
GOOGLE_MAPS_API_KEY=your_google_maps_key
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret

# Security
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the test suite for examples
- Use the admin panel for system monitoring

---

**Status**: ✅ Production Ready

The platform is fully functional with comprehensive features, testing, and monitoring capabilities.
