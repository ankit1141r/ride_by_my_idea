#!/usr/bin/env python3
"""
Simple Deployment - No Docker Required
Serves both frontend and backend on the same server
"""
import os
import sys
import webbrowser
import time
from pathlib import Path


def print_banner():
    """Print deployment banner."""
    print("\n" + "=" * 70)
    print("  🚀 RideConnect - Simple Deployment (No Docker Required)")
    print("=" * 70 + "\n")


def check_requirements():
    """Check if required files exist."""
    print("📋 Checking requirements...")
    
    required_files = [
        "app/main.py",
        "web/index.html",
        ".env.example"
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"❌ Missing required files: {', '.join(missing)}")
        return False
    
    print("✅ All required files present")
    return True


def setup_env():
    """Setup environment file."""
    print("\n📝 Setting up environment...")
    
    if not os.path.exists(".env"):
        print("   Creating .env file with default settings...")
        
        env_content = """# RideConnect Configuration
# Database URLs (using SQLite for simplicity)
DATABASE_URL=sqlite:///./rideconnect.db
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017

# Security Keys
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production-12345
SECRET_KEY=dev-app-secret-key-change-in-production-67890

# Application Settings
APP_ENV=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# External Services (Optional - leave empty for demo)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
GOOGLE_MAPS_API_KEY=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
PAYTM_MERCHANT_ID=
PAYTM_MERCHANT_KEY=
"""
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ Environment file created")
    else:
        print("✅ Environment file already exists")
    
    return True


def show_instructions():
    """Show deployment instructions."""
    print_banner()
    
    print("📱 Your RideConnect platform is ready to deploy!\n")
    
    print("🎯 DEPLOYMENT OPTIONS:\n")
    
    print("Option 1: Quick Start (Recommended for Testing)")
    print("   This will start the backend server with frontend")
    print("   • No database setup needed (uses SQLite)")
    print("   • Perfect for testing and development")
    print("   • Access at: http://localhost:8000/web/\n")
    
    print("Option 2: Full Deployment with Docker")
    print("   Install Docker Desktop and run:")
    print("   • python deploy_public.py")
    print("   • Includes PostgreSQL, Redis, MongoDB")
    print("   • Production-ready setup\n")
    
    print("Option 3: Cloud Deployment")
    print("   Deploy to Heroku, Railway, or DigitalOcean")
    print("   • See PUBLIC_DEPLOYMENT_GUIDE.md for details\n")
    
    print("=" * 70)
    
    choice = input("\n🚀 Start Quick Deployment now? (y/n): ").lower()
    return choice in ['y', 'yes', '']


def start_server():
    """Start the FastAPI server."""
    print("\n" + "=" * 70)
    print("  🚀 Starting RideConnect Server")
    print("=" * 70 + "\n")
    
    print("📡 Server Information:")
    print("   • Backend API: http://localhost:8000")
    print("   • Frontend:    http://localhost:8000/web/")
    print("   • API Docs:    http://localhost:8000/docs")
    print("   • Health:      http://localhost:8000/health\n")
    
    print("🔐 Demo Login (after seeding database):")
    print("   Rider:  +919876543210 / password123")
    print("   Driver: +919876543200 / password123\n")
    
    print("💡 Tips:")
    print("   • Press Ctrl+C to stop the server")
    print("   • The server will auto-reload on code changes")
    print("   • Check logs below for any errors\n")
    
    print("=" * 70)
    print("\n⏳ Starting server in 3 seconds...\n")
    time.sleep(3)
    
    # Open browser
    try:
        webbrowser.open("http://localhost:8000/web/")
        print("🌐 Opening browser...\n")
    except:
        print("⚠️  Could not open browser automatically")
        print("   Please open: http://localhost:8000/web/\n")
    
    time.sleep(2)
    
    print("=" * 70)
    print("  📊 SERVER LOGS")
    print("=" * 70 + "\n")
    
    # Start uvicorn
    try:
        import subprocess
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("  👋 Server Stopped")
        print("=" * 70)
        print("\n✨ Thank you for using RideConnect!\n")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure port 8000 is not in use")
        print("   2. Install uvicorn: pip install uvicorn")
        print("   3. Check .env file configuration")
        return False
    
    return True


def main():
    """Main deployment function."""
    # Check requirements
    if not check_requirements():
        print("\n❌ Deployment aborted - missing required files")
        sys.exit(1)
    
    # Setup environment
    if not setup_env():
        print("\n❌ Deployment aborted - environment setup failed")
        sys.exit(1)
    
    # Show instructions and get confirmation
    if not show_instructions():
        print("\n📖 Deployment cancelled.")
        print("   Read PUBLIC_DEPLOYMENT_GUIDE.md for more options.")
        sys.exit(0)
    
    # Start server
    start_server()


if __name__ == "__main__":
    main()
