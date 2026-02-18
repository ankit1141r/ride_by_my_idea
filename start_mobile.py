#!/usr/bin/env python3
"""
Simple Mobile Access Script
Starts server and shows mobile access URL
"""
import socket
import sys
import subprocess
import time


def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to detect"


def main():
    """Main function."""
    print("\n" + "=" * 70)
    print("  📱 RideConnect - Mobile Access")
    print("=" * 70 + "\n")
    
    # Get IP
    local_ip = get_local_ip()
    mobile_url = f"http://{local_ip}:8000/web/"
    
    print("🌐 Your Mobile Access URL:")
    print()
    print(f"   {mobile_url}")
    print()
    print("=" * 70)
    print()
    print("📱 Steps to Access from Mobile:")
    print()
    print("1. Connect your mobile to the SAME WiFi as this computer")
    print()
    print("2. Open browser on your mobile")
    print()
    print("3. Type this URL:")
    print(f"   {mobile_url}")
    print()
    print("4. Login with:")
    print("   Phone: +919876543210")
    print("   Password: password123")
    print()
    print("=" * 70)
    print()
    print("🔥 If it doesn't work:")
    print()
    print("Windows Users:")
    print("  • Open Windows Defender Firewall")
    print("  • Click 'Allow an app through firewall'")
    print("  • Find Python and check both boxes")
    print()
    print("Mac Users:")
    print("  • Go to System Preferences > Security")
    print("  • Allow Python to accept incoming connections")
    print()
    print("=" * 70)
    print()
    
    input("Press Enter to start server...")
    
    print("\n🚀 Starting server...\n")
    print(f"📱 Mobile URL: {mobile_url}")
    print("💻 Computer URL: http://localhost:8000/web/")
    print()
    print("Press Ctrl+C to stop\n")
    print("=" * 70 + "\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped\n")


if __name__ == "__main__":
    main()
