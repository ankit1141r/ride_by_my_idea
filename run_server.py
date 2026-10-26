"""
RideConnect India - Web & API Server Launcher
Starts the FastAPI application and serves the complete Pan-India web platform.
"""
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import uvicorn
from app.config import settings

def main():
    print("=" * 65)
    print("🚀 RIDECONNECT INDIA — PAN-INDIA RIDE-HAILING & LOGISTICS")
    print("=" * 65)
    print(f"Platform: {settings.app_name}")
    print(f"Coverage: All India (50+ Cities in 28 States & 8 Union Territories)")
    print(f"Web Portal: http://localhost:{settings.port}/web/index.html")
    print(f"Rider App:  http://localhost:{settings.port}/web/rider.html")
    print(f"Driver App: http://localhost:{settings.port}/web/driver.html")
    print(f"Admin Hub:  http://localhost:{settings.port}/web/admin.html")
    print(f"API Docs:   http://localhost:{settings.port}/docs")
    print("=" * 65)
    print("Press CTRL+C to stop the server\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=False
    )

if __name__ == "__main__":
    main()
