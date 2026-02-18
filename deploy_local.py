#!/usr/bin/env python3
"""
Local Deployment Script (Without Docker)
Deploys the application locally with all services
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_python():
    """Check Python version."""
    print_header("Checking Python Installation")
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    return True


def check_env_file():
    """Check if .env file exists."""
    print_header("Checking Environment Configuration")
    
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Creating from .env.example...")
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file exists")
    
    return True


def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Dependencies")
    
    print("📦 Installing Python packages...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Dependencies installed")
        return True
    else:
        print("❌ Failed to install dependencies")
        print(result.stderr)
        return False


def check_databases():
    """Check database connections."""
    print_header("Checking Database Connections")
    
    print("⚠️  Note: This deployment requires:")
    print("   • PostgreSQL running on localhost:5432")
    print("   • Redis running on localhost:6379")
    print("   • MongoDB running on localhost:27017 (optional)")
    
    print("\n💡 If you don't have these installed, use Docker deployment:")
    print("   python deploy_public.py")
    
    response = input("\n✅ Are your databases running? (y/n): ")
    return response.lower() in ['y', 'yes']


def run_migrations():
    """Run database migrations."""
    print_header("Running Database Migrations")
    
    print("🔄 Running Alembic migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Migrations completed")
        return True
    else:
        print("⚠️  Migration warning (may be okay if already migrated)")
        return True


def seed_database():
    """Seed database with test data."""
    print_header("Seeding Database")
    
    response = input("Would you like to seed the database with test data? (y/n): ")
    if response.lower() not in ['y', 'yes']:
        print("⏭️  Skipping database seeding")
        return True
    
    print("🌱 Seeding database...")
    result = subprocess.run(
        [sys.executable, "seed_database.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Database seeded with test data")
        return True
    else:
        print("⚠️  Seeding failed (database may already be seeded)")
        return True


def start_server():
    """Start the FastAPI server."""
    print_header("Starting Application Server")
    
    print("🚀 Starting FastAPI server on http://localhost:8000")
    print("   Frontend will be available at http://localhost:8000/web/")
    print("\n   Press Ctrl+C to stop the server\n")
    
    time.sleep(2)
    
    try:
        # Start server
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app.main:app", 
             "--host", "0.0.0.0", "--port", "8000", "--reload"],
            check=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return False
    
    return True


def show_access_info():
    """Display access information."""
    print_header("🎉 Server Starting!")
    
    print("📱 Access URLs:")
    print("   • Main Website:    http://localhost:8000/web/")
    print("   • Rider Dashboard: http://localhost:8000/web/rider-dashboard.html")
    print("   • Driver Dashboard: http://localhost:8000/web/driver-dashboard.html")
    print("   • Admin Panel:     http://localhost:8000/web/admin.html")
    print("   • API Docs:        http://localhost:8000/docs")
    print("   • Health Check:    http://localhost:8000/health")
    
    print("\n🔐 Test Accounts (if database was seeded):")
    print("   Riders:")
    print("   • Phone: +919876543210, Password: password123")
    
    print("\n   Drivers:")
    print("   • Phone: +919876543200, Password: password123")
    
    print("\n" + "=" * 60 + "\n")


def open_browser():
    """Open the application in browser."""
    print("🌐 Opening application in browser...")
    time.sleep(3)
    try:
        webbrowser.open("http://localhost:8000/web/")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")


def main():
    """Main deployment function."""
    print_header("🚀 RideConnect Local Deployment")
    print("This script will deploy the platform locally (without Docker)")
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check databases
    if not check_databases():
        print("\n❌ Deployment aborted - databases not available")
        print("   Use Docker deployment instead: python deploy_public.py")
        sys.exit(1)
    
    # Run migrations
    run_migrations()
    
    # Seed database
    seed_database()
    
    # Show access info
    show_access_info()
    
    # Open browser
    response = input("🌐 Would you like to open the application in your browser? (y/n): ")
    if response.lower() in ['y', 'yes', '']:
        open_browser()
    
    # Start server
    start_server()


if __name__ == "__main__":
    main()
