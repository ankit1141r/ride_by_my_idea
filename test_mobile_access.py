import requests

def test_mobile_access():
    print("📱 Testing Mobile Access URLs")
    print("=" * 40)
    
    mobile_ip = "192.168.1.3"
    port = "8001"
    
    urls_to_test = [
        f"http://{mobile_ip}:{port}/health",
        f"http://{mobile_ip}:{port}/web/navigation.html",
        f"http://{mobile_ip}:{port}/web/index.html",
        f"http://{mobile_ip}:{port}/web/mobile-access.html"
    ]
    
    for url in urls_to_test:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} - Working!")
            else:
                print(f"⚠️ {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    
    print(f"\n📱 MOBILE ACCESS URL:")
    print(f"🔗 http://{mobile_ip}:{port}/web/navigation.html")
    print(f"\n💡 Copy this URL to your mobile browser!")

if __name__ == "__main__":
    test_mobile_access()