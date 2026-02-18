"""
Startup script for the Ride-Hailing Platform.
Performs pre-flight checks and starts the application.
"""
import sys
import os
from pathlib import Path

def check_environment():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ Error: .env file not found!")
        print("Please create a .env file based on .env.example")
        return False
    
    # Check for critical environment variables
    required_vars = ["SECRET_KEY", "JWT_SECRET_KEY"]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configuration loaded")
    return True


def check_dependencies():
    """Check if required Python packages are installed."""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import redis
        import pymongo
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Error: Missing dependency - {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def check_database_connections():
    """Check if database services are accessible."""
    from app.config import settings
    
    # Check PostgreSQL
    try:
        from sqlalchemy import create_engine
        engine = create_engine(settings.postgres_url)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ PostgreSQL connection successful")
    except Exception as e:
        print(f"⚠️  Warning: PostgreSQL connection failed - {e}")
        print("   Make sure PostgreSQL is running on localhost:5432")
        print("   You can continue, but database operations will fail")
    
    # Check Redis
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"⚠️  Warning: Redis connection failed - {e}")
        print("   Make sure Redis is running on localhost:6379")
        print("   You can continue, but caching/sessions will fail")
    
    # Check MongoDB
    try:
        from pymongo import MongoClient
        client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"⚠️  Warning: MongoDB connection failed - {e}")
        print("   Make sure MongoDB is running on localhost:27017")
        print("   You can continue, but location services will fail")


def run_migrations():
    """Run database migrations."""
    print("\n📦 Running database migrations...")
    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Database migrations completed")
        else:
            print(f"⚠️  Warning: Migration failed - {result.stderr}")
    except Exception as e:
        print(f"⚠️  Warning: Could not run migrations - {e}")


def start_application():
    """Start the FastAPI application."""
    from app.config import settings
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Starting Ride-Hailing Platform")
    print("="*60)
    print(f"Environment: {settings.app_env}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Server: http://{settings.host}:{settings.port}")
    print(f"API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"Health Check: http://{settings.host}:{settings.port}/health")
    print(f"Metrics: http://{settings.host}:{settings.port}/metrics")
    print("="*60)
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )


def main():
    """Main startup function."""
    print("🔍 Performing pre-flight checks...\n")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database connections
    print("\n🔌 Checking database connections...")
    check_database_connections()
    
    # Run migrations
    run_migrations()
    
    # Start application
    try:
        start_application()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
