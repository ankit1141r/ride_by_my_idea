"""
Generate mobile access information and QR codes for RideConnect website.
"""
import socket
import webbrowser

def get_mobile_access_info():
    print("📱 RideConnect - Mobile Access Setup")
    print("=" * 60)
    
    # Get network information
    try:
        # Get local IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "192.168.1.3"  # Fallback to detected IP
    
    # URLs for mobile access
    mobile_urls = {
        "🏠 Landing Page": f"http://192.168.1.3:8001/web/index.html",
        "📋 Navigation": f"http://192.168.1.3:8001/web/navigation.html", 
        "👤 Rider Dashboard": f"http://192.168.1.3:8001/web/rider-dashboard.html",
        "🚗 Driver Dashboard": f"http://192.168.1.3:8001/web/driver-dashboard.html",
        "⚙️ Admin Panel": f"http://192.168.1.3:8001/web/admin.html",
        "📚 API Docs": f"http://192.168.1.3:8001/docs"
    }
    
    print("🌐 Mobile Access URLs:")
    print("Copy these URLs to your mobile browser:")
    print()
    
    for name, url in mobile_urls.items():
        print(f"{name}")
        print(f"   {url}")
        print()
    
    print("📋 Quick Access - Main URL:")
    print("=" * 40)
    main_url = "http://192.168.1.3:8001/web/navigation.html"
    print(f"🔗 {main_url}")
    print("=" * 40)
    
    print("\n✅ Setup Instructions:")
    print("1. Make sure your mobile is connected to the same WiFi network")
    print("2. Copy the URL above to your mobile browser")
    print("3. Bookmark it for easy access")
    print("4. The website is fully responsive and mobile-friendly")
    
    print("\n🔧 Troubleshooting:")
    print("• If it doesn't work, try these alternative IPs:")
    print(f"  - http://{local_ip}:8001/web/navigation.html")
    print("  - http://192.168.0.3:8001/web/navigation.html")
    print("  - http://10.0.0.3:8001/web/navigation.html")
    
    print("\n📱 Mobile Features:")
    print("• Touch-friendly interface")
    print("• Responsive design for all screen sizes") 
    print("• Swipe gestures and mobile navigation")
    print("• Optimized for mobile browsers")
    
    # Create a simple HTML page with QR code and mobile links
    create_mobile_access_page(mobile_urls, main_url)
    
    return main_url

def create_mobile_access_page(urls, main_url):
    """Create a mobile access page with QR codes and easy links."""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RideConnect - Mobile Access</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .logo {{
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .qr-section {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 15px;
        }}
        
        .qr-placeholder {{
            width: 200px;
            height: 200px;
            margin: 0 auto 20px;
            background: white;
            border: 2px dashed #667eea;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            font-size: 14px;
            color: #666;
            text-align: center;
            line-height: 1.4;
        }}
        
        .main-url {{
            background: #667eea;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            word-break: break-all;
            font-family: monospace;
            font-size: 14px;
        }}
        
        .url-list {{
            margin: 20px 0;
        }}
        
        .url-item {{
            background: #f0f2ff;
            margin: 10px 0;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .url-title {{
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
        }}
        
        .url-link {{
            color: #667eea;
            text-decoration: none;
            font-family: monospace;
            font-size: 13px;
            word-break: break-all;
        }}
        
        .instructions {{
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .instructions h3 {{
            color: #2e7d32;
            margin-bottom: 15px;
        }}
        
        .instructions ol {{
            margin-left: 20px;
        }}
        
        .instructions li {{
            margin-bottom: 8px;
            color: #333;
        }}
        
        .copy-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 10px;
        }}
        
        .copy-btn:hover {{
            background: #5a6fd8;
        }}
        
        @media (max-width: 480px) {{
            .container {{
                padding: 20px;
                margin: 10px;
            }}
            
            .qr-placeholder {{
                width: 150px;
                height: 150px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">📱 RideConnect Mobile Access</div>
            <p>Access the full website on your mobile device</p>
        </div>
        
        <div class="qr-section">
            <div class="qr-placeholder">
                QR Code<br>
                (Scan with your<br>mobile camera)
            </div>
            <p><strong>Main URL for Mobile:</strong></p>
            <div class="main-url">
                {main_url}
                <button class="copy-btn" onclick="copyToClipboard('{main_url}')">Copy</button>
            </div>
        </div>
        
        <div class="instructions">
            <h3>📋 How to Access on Mobile:</h3>
            <ol>
                <li>Make sure your mobile is on the same WiFi network</li>
                <li>Copy the URL above to your mobile browser</li>
                <li>Or scan the QR code with your camera</li>
                <li>Bookmark the page for easy access</li>
            </ol>
        </div>
        
        <div class="url-list">
            <h3>🌐 All Available Pages:</h3>"""
    
    for name, url in urls.items():
        html_content += f"""
            <div class="url-item">
                <div class="url-title">{name}</div>
                <a href="{url}" class="url-link" target="_blank">{url}</a>
                <button class="copy-btn" onclick="copyToClipboard('{url}')">Copy</button>
            </div>"""
    
    html_content += """
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>✅ Fully responsive design optimized for mobile devices</p>
        </div>
    </div>
    
    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                alert('URL copied to clipboard!');
            }).catch(function() {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('URL copied to clipboard!');
            });
        }
        
        // Auto-generate QR code using online service
        document.addEventListener('DOMContentLoaded', function() {
            const qrPlaceholder = document.querySelector('.qr-placeholder');
            const mainUrl = '""" + main_url + """';
            const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(mainUrl)}`;
            
            qrPlaceholder.innerHTML = `<img src="${qrUrl}" alt="QR Code" style="max-width: 100%; border-radius: 5px;">`;
        });
    </script>
</body>
</html>"""
    
    # Save the mobile access page
    with open('web/mobile-access.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n📄 Created mobile access page: web/mobile-access.html")

if __name__ == "__main__":
    main_url = get_mobile_access_info()
    
    print(f"\n🚀 Opening mobile access page...")
    webbrowser.open("web/mobile-access.html")
    
    print(f"\n📱 COPY THIS URL TO YOUR MOBILE:")
    print(f"🔗 {main_url}")
    print(f"\n💡 Or visit: http://192.168.1.3:8001/web/mobile-access.html")