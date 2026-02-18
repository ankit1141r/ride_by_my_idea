#!/usr/bin/env python3
"""
Deploy with Public URL using ngrok or localtunnel
Works from anywhere - no WiFi setup needed!
"""
import os
import sys
import subprocess
import time
import webbrowser


def print_banner():
    """Print banner."""
    print("\n" + "=" * 70)
    print("  🌐 RideConnect - Public URL Deployment")
    print("=" * 70 + "\n")


def check_ngrok():
    """Check if ngrok is installed."""
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  ngrok is not installed")
    return False


def install_ngrok_instructions():
    """Show ngrok installation instructions."""
    print("\n📥 How to Install ngrok:\n")
    print("1. Go to: https://ngrok.com/download")
    print("2. Download ngrok for your system")
    print("3. Extract the file")
    print("4. Move ngrok to a folder in your PATH")
    print("\n   Windows: Move to C:\\Windows\\System32\\")
    print("   Mac: Move to /usr/local/bin/")
    print("   Linux: Move to /usr/local/bin/")
    print("\n5. Run this script again")
    print()


def start_server_background():
    """Start FastAPI server in background."""
    print("🚀 Starting FastAPI server...")
    
    # Start server in background
    if sys.platform == "win32":
        # Windows
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # Mac/Linux
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    print("✅ Server started\n")


def start_ngrok():
    """Start ngrok tunnel."""
    print("🌐 Creating public URL with ngrok...\n")
    print("=" * 70)
    print("  YOUR PUBLIC URL WILL APPEAR BELOW")
    print("=" * 70)
    print()
    print("💡 Copy the 'Forwarding' URL (https://xxxxx.ngrok.io)")
    print("   Share this URL with anyone to access your platform!")
    print()
    print("🔐 Test Login:")
    print("   Phone: +919876543210")
    print("   Password: password123")
    print()
    print("⚠️  Press Ctrl+C to stop ngrok (server will keep running)")
    print()
    print("=" * 70)
    print()
    
    try:
        subprocess.run(["ngrok", "http", "8000"])
    except KeyboardInterrupt:
        print("\n\n✅ ngrok stopped (server still running)")
        print("   To stop server, close the other terminal window")


def use_localtunnel():
    """Use localtunnel as alternative."""
    print("\n🌐 Using localtunnel (alternative to ngrok)...\n")
    
    # Check if npm is installed
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ Node.js/npm is not installed")
        print("\n📥 Install Node.js from: https://nodejs.org/")
        return False
    
    # Install localtunnel
    print("📦 Installing localtunnel...")
    subprocess.run(["npm", "install", "-g", "localtunnel"], capture_output=True)
    
    print("🌐 Creating public URL...\n")
    print("=" * 70)
    print("  YOUR PUBLIC URL")
    print("=" * 70)
    print()
    
    try:
        subprocess.run(["lt", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n\n✅ Tunnel stopped")
    
    return True


def deploy_to_cloud():
    """Show cloud deployment options."""
    print("\n☁️  Cloud Deployment Options:\n")
    
    print("1. Render (Easiest - Free Tier)")
    print("   • Go to: https://render.com")
    print("   • Click 'New Web Service'")
    print("   • Connect your GitHub repo")
    print("   • Deploy automatically!")
    print()
    
    print("2. Railway (Modern - Free Tier)")
    print("   • Go to: https://railway.app")
    print("   • Click 'Deploy from GitHub'")
    print("   • Select your repo")
    print("   • Done!")
    print()
    
    print("3. Heroku (Popular)")
    print("   • Install Heroku CLI")
    print("   • Run: heroku create")
    print("   • Run: git push heroku main")
    print()


def main():
    """Main function."""
    print_banner()
    
    print("This will create a PUBLIC URL that works from anywhere!")
    print("No WiFi setup needed - works on mobile data too!\n")
    
    print("Choose deployment method:\n")
    print("1. ngrok (Recommended - Instant public URL)")
    print("2. localtunnel (Alternative)")
    print("3. Cloud deployment (Permanent URL)")
    print("4. Exit")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        if not check_ngrok():
            install_ngrok_instructions()
            
            response = input("\n✅ Have you installed ngrok? (y/n): ").lower()
            if response not in ['y', 'yes']:
                print("\n📖 Install ngrok first, then run this script again")
                return
        
        start_server_background()
        start_ngrok()
    
    elif choice == "2":
        start_server_background()
        use_localtunnel()
    
    elif choice == "3":
        deploy_to_cloud()
    
    else:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
