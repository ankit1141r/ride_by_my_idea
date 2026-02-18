# Ride-Hailing Platform

A web-first ride-hailing platform for intra-city transportation within Indore, built with FastAPI and Python.

## Features

- User registration and authentication (phone + ID verification)
- Real-time ride matching between riders and drivers
- Location-based services with Indore city boundary validation
- Fare calculation and payment processing (Razorpay, Paytm)
- Rating and review system
- Safety and emergency features
- Real-time ride tracking via WebSocket

## Tech Stack

- **Backend**: FastAPI (Python)
- **Databases**: 
  - PostgreSQL (primary data)
  - Redis (cache & sessions)
  - MongoDB (location data)
- **Testing**: pytest, hypothesis (property-based testing)
- **External Services**: Razorpay, Paytm, Twilio, Google Maps API

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- MongoDB

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and configure your environment variables:
   ```bash
   cp .env.example .env
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   python app/main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with pytest:
```bash
pytest
```

Run property-based tests:
```bash
pytest -k property
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration management
│   ├── database.py       # Database connections
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── routers/          # API endpoints
├── alembic/              # Database migrations
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

## License

Proprietary
