"""
Simple server startup script without database checks.
Use this if databases are not yet configured.
"""
import sys

def main():
    """Start the FastAPI application."""
    try:
        import uvicorn
        from app.config import settings
        
        print("="*60)
        print("🚀 Starting Ride-Hailing Platform")
        print("="*60)
        print(f"Environment: {settings.app_env}")
        print(f"Debug Mode: {settings.debug}")
        print(f"Server: http://{settings.host}:{settings.port}")
        print(f"API Docs: http://{settings.host}:{settings.port}/docs")
        print(f"Health Check: http://{settings.host}:{settings.port}/health")
        print(f"Metrics: http://{settings.host}:{settings.port}/metrics")
        print("="*60)
        print("\n⚠️  Note: Database connections will be established on first request")
        print("Press CTRL+C to stop the server\n")
        
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
