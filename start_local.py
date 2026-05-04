#!/usr/bin/env python3
"""
Local deployment script for Ride-Hailing Platform
Starts the application on localhost without Docker
"""

import os
import sys
import subprocess
import time

def check_port(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def main():
    print("=" * 60)
    print("🚀 Ride-Hailing Platform - Local Deployment")
    print("=" * 60)
    print()
    
    # Check if port 8000 is available
    if not check_port(8000):
        print("❌ Port 8000 is already in use!")
        print("   Please stop the other application or use a different port.")
        sys.exit(1)
    
    print("✅ Port 8000 is available")
    print()
    
    # Set minimal environment variables for local development
    os.environ.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')
    os.environ.setdefault('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')
    os.environ.setdefault('APP_ENV', 'development')
    os.environ.setdefault('DEBUG', 'true')
    
    print("📝 Starting application...")
    print()
    print("🌐 Application will be available at:")
    print("   - Web Interface: http://localhost:8000/web/")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Admin Panel: http://localhost:8000/web/admin.html")
    print("   - Health Check: http://localhost:8000/health")
    print()
    print("⚠️  Note: Database features require PostgreSQL, Redis, and MongoDB")
    print("   For full functionality, use Docker Compose deployment")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        # Start uvicorn server
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
        print("Thank you for using Ride-Hailing Platform!")

if __name__ == '__main__':
    main()
