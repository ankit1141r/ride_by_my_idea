#!/usr/bin/env python3
"""
Simple local web server for the RideConnect web interface.
Serves static files from the web directory.
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080
DIRECTORY = "web"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def main():
    # Check if web directory exists
    if not os.path.exists(DIRECTORY):
        print(f"❌ Error: '{DIRECTORY}' directory not found!")
        return
    
    print("=" * 60)
    print("🌐 RideConnect Web Interface - Local Server")
    print("=" * 60)
    print(f"📁 Serving files from: {os.path.abspath(DIRECTORY)}")
    print(f"🌍 Server running at: http://localhost:{PORT}")
    print("=" * 60)
    print("\n✨ Opening web browser...")
    print("\n⚠️  Note: Backend API is not running!")
    print("   To run the full application with backend:")
    print("   1. Start Docker Desktop")
    print("   2. Run: docker-compose up")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    print("=" * 60)
    
    # Open browser
    webbrowser.open(f'http://localhost:{PORT}/index.html')
    
    # Start server
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped.")
            print("=" * 60)

if __name__ == "__main__":
    main()
