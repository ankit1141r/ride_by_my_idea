#!/usr/bin/env python3
"""
Mobile-Accessible Deployment
Starts server accessible from mobile devices on the same network
"""
import os
import sys
import socket
import webbrowser
import time
import qrcode
from io import BytesIO


def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Create a socket to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"


def print_banner():
    """Print mobile deployment banner."""
    print("\n" + "=" * 70)
    print("  📱 RideConnect - Mobile-Accessible Deployment")
    print("=" * 70 + "\n")


def generate_qr_code(url):
    """Generate QR code for easy mobile access."""
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        # Print QR code to terminal
        qr.print_ascii(invert=True)
        return True
    except ImportError:
        print("⚠️  QR code generation requires 'qrcode' package")
        print("   Install with: pip install qrcode[pil]")
        return False


def setup_env():
    """Setup environment file."""
    if not os.path.exists(".env"):
        print("📝 Creating .env file...")
        
        env_content = """# RideConnect Configuration
DATABASE_URL=sqlite:///./rideconnect.db
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017

JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production-12345
SECRET_KEY=dev-app-secret-key-change-in-production-67890

APP_ENV=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
"""
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ Environment configured\n")


def show_mobile_instructions(local_ip, port=8000):
    """Show instructions for mobile access."""
    print_banner()
    
    print("🌐 Server Information:")
    print(f"   • Local IP: {local_ip}")
    print(f"   • Port: {port}")
    print()
    
    # URLs
    computer_url = f"http://localhost:{port}/web/"
    mobile_url = f"http://{local_ip}:{port}/web/"
    
    print("📱 Access URLs:")
    print(f"   • From Computer: {computer_url}")
    print(f"   • From Mobile:   {mobile_url}")
    print()
    
    print("=" * 70)
    print("  📱 HOW TO ACCESS FROM YOUR MOBILE")
    print("=" * 70)
    print()
    
    print("Step 1: Make sure your mobile is on the SAME WiFi network")
    print("        as your computer")
    print()
    
    print("Step 2: Open your mobile browser (Chrome, Safari, etc.)")
    print()
    
    print("Step 3: Type this URL in your mobile browser:")
    print()
    print(f"        {mobile_url}")
    print()
    
    print("=" * 70)
    print()
    
    # Try to generate QR code
    print("📷 QR Code for Easy Access:")
    print()
    if generate_qr_code(mobile_url):
        print()
        print("   Scan this QR code with your mobile camera!")
    else:
        print("   (QR code not available - type URL manually)")
    
    print()
    print("=" * 70)
    print()
    
    print("🔐 Test Login Credentials:")
    print("   Rider:  +919876543210 / password123")
    print("   Driver: +919876543200 / password123")
    print()
    
    print("💡 Troubleshooting:")
    print("   • Make sure both devices are on the same WiFi")
    print("   • Check if firewall is blocking port 8000")
    print("   • Try disabling Windows Firewall temporarily")
    print("   • On Windows: Allow Python through firewall")
    print()
    
    print("🔥 Windows Firewall Fix:")
    print("   1. Search 'Windows Defender Firewall'")
    print("   2. Click 'Allow an app through firewall'")
    print("   3. Click 'Change settings'")
    print("   4. Find 'Python' and check both Private and Public")
    print("   5. Click OK")
    print()
    
    print("=" * 70)
    print()


def start_server(port=8000):
    """Start the FastAPI server accessible from network."""
    print("🚀 Starting server accessible from mobile devices...")
    print()
    print("⏳ Server starting in 3 seconds...")
    print()
    print("💡 Press Ctrl+C to stop the server")
    print()
    print("=" * 70)
    print("  📊 SERVER LOGS")
    print("=" * 70)
    print()
    
    time.sleep(3)
    
    try:
        import subprocess
        # Start server on 0.0.0.0 to accept connections from any IP
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",  # Important: Listen on all interfaces
            "--port", str(port),
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("  👋 Server Stopped")
        print("=" * 70)
        print("\n✨ Thank you for using RideConnect!\n")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n💡 Make sure uvicorn is installed:")
        print("   pip install uvicorn")
        return False
    
    return True


def main():
    """Main function."""
    # Get local IP
    local_ip = get_local_ip()
    
    # Setup environment
    setup_env()
    
    # Show instructions
    show_mobile_instructions(local_ip)
    
    # Ask for confirmation
    response = input("🚀 Ready to start server? (y/n): ").lower()
    if response not in ['y', 'yes', '']:
        print("\n📖 Deployment cancelled.")
        sys.exit(0)
    
    print()
    
    # Start server
    start_server()


if __name__ == "__main__":
    main()
