"""
Browser launcher for RideConnect application.
Opens all the key pages in your default browser.
"""
import webbrowser
import time

def open_rideconnect():
    print("🌐 Opening RideConnect in your browser...")
    print("=" * 50)
    
    # Main URLs
    urls = {
        "🏠 Landing Page": "http://localhost:8001/web/",
        "📚 API Documentation": "http://localhost:8001/docs",
        "🔍 Health Check": "http://localhost:8001/health",
        "👥 Demo Users API": "http://localhost:8001/api/demo/users",
        "🚗 Demo Rides API": "http://localhost:8001/api/demo/rides",
        "📊 Demo Stats API": "http://localhost:8001/api/demo/stats"
    }
    
    # Open main web interface
    print("Opening main web interface...")
    webbrowser.open("http://localhost:8001/web/")
    time.sleep(2)
    
    # Open API documentation
    print("Opening API documentation...")
    webbrowser.open("http://localhost:8001/docs")
    
    print("\n🎉 RideConnect is now open in your browser!")
    print("\n📱 Available Pages:")
    for name, url in urls.items():
        print(f"   {name}: {url}")
    
    print("\n🔧 What you can explore:")
    print("   • Landing page with modern UI")
    print("   • Interactive API documentation")
    print("   • Sample data endpoints")
    print("   • Rider and Driver dashboards")
    print("   • Admin panel interface")
    
    print("\n💡 Note: The web interface includes:")
    print("   • User registration and login forms")
    print("   • Ride booking interface")
    print("   • Driver dashboard")
    print("   • Admin management panel")

if __name__ == "__main__":
    open_rideconnect()