#!/usr/bin/env python3
"""
Simple web server for Ride-Hailing Platform frontend
Serves static files without requiring database connections
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Serve index.html for root path
        if self.path == '/':
            self.path = '/web/index.html'
        super().do_GET()

def main():
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    print("=" * 70)
    print("🚀 Ride-Hailing Platform - Static Web Server")
    print("=" * 70)
    print()
    print("✅ Starting web server on port", PORT)
    print()
    print("🌐 Access the application at:")
    print(f"   - Main Page: http://localhost:{PORT}/web/")
    print(f"   - Landing Page: http://localhost:{PORT}/web/index.html")
    print(f"   - Rider Dashboard: http://localhost:{PORT}/web/rider-dashboard.html")
    print(f"   - Driver Dashboard: http://localhost:{PORT}/web/driver-dashboard.html")
    print(f"   - Admin Panel: http://localhost:{PORT}/web/admin.html")
    print()
    print("⚠️  Note: This is a static file server only")
    print("   API endpoints require the full backend with databases")
    print("   For full functionality, install Docker and use docker-compose")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    # Start server
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✅ Server running at http://localhost:{PORT}/")
        print()
        
        # Open browser
        try:
            webbrowser.open(f'http://localhost:{PORT}/web/')
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Server stopped")
            print("Thank you for using Ride-Hailing Platform!")

if __name__ == '__main__':
    main()
