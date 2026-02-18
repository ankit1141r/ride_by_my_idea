#!/usr/bin/env python3
"""
Quick script to open the RideConnect website
"""
import webbrowser
import time
import urllib.request
import urllib.error


def check_server(url, max_attempts=5):
    """Check if server is running."""
    print(f"🔍 Checking if server is running at {url}...")
    
    for attempt in range(max_attempts):
        try:
            response = urllib.request.urlopen(url, timeout=2)
            if response.status == 200:
                print(f"✅ Server is running!")
                return True
        except (urllib.error.URLError, urllib.error.HTTPError, Exception):
            if attempt < max_attempts - 1:
                print(f"   Attempt {attempt + 1}/{max_attempts}... waiting...")
                time.sleep(1)
    
    return False


def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("  🚀 RideConnect - Opening Website")
    print("=" * 60 + "\n")
    
    # Try different URLs
    urls = [
        ("http://localhost/web/", "Docker deployment"),
        ("http://localhost:8000/web/", "Simple/Local deployment"),
    ]
    
    server_found = False
    for url, deployment_type in urls:
        print(f"\n📡 Trying {deployment_type}...")
        if check_server(url.replace("/web/", "/health")):
            print(f"✅ Found server at {url}")
            print(f"🌐 Opening browser...")
            time.sleep(1)
            webbrowser.open(url)
            server_found = True
            break
    
    if not server_found:
        print("\n❌ Server is not running!")
        print("\n💡 To start the server, run one of these commands:")
        print("   • python deploy_simple.py")
        print("   • python deploy_public.py")
        print("   • docker-compose up -d")
        print("\n   Then run this script again to open the website.")
    else:
        print("\n✨ Website opened in your browser!")
        print("\n📱 Available pages:")
        print("   • Main Page: /web/")
        print("   • Rider Dashboard: /web/rider-dashboard.html")
        print("   • Driver Dashboard: /web/driver-dashboard.html")
        print("   • Admin Panel: /web/admin.html")
        print("   • API Docs: /docs")
        
        print("\n🔐 Test Login:")
        print("   Rider:  +919876543210 / password123")
        print("   Driver: +919876543200 / password123")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
