"""
Fix Gradle Wrapper - Download missing gradle-wrapper.jar
"""

import os
import urllib.request

def download_gradle_wrapper():
    """Download gradle-wrapper.jar"""
    
    wrapper_dir = os.path.join("gradle", "wrapper")
    wrapper_jar = os.path.join(wrapper_dir, "gradle-wrapper.jar")
    
    # Create directory if it doesn't exist
    os.makedirs(wrapper_dir, exist_ok=True)
    
    if os.path.exists(wrapper_jar):
        print(f"✓ gradle-wrapper.jar already exists")
        return True
    
    print("Downloading gradle-wrapper.jar...")
    
    # URL for gradle wrapper jar
    url = "https://raw.githubusercontent.com/gradle/gradle/master/gradle/wrapper/gradle-wrapper.jar"
    
    try:
        urllib.request.urlretrieve(url, wrapper_jar)
        print(f"✓ Downloaded gradle-wrapper.jar to {wrapper_jar}")
        return True
    except Exception as e:
        print(f"✗ Download failed: {e}")
        
        # Try alternative URL
        print("Trying alternative download...")
        alt_url = "https://github.com/gradle/gradle/raw/master/gradle/wrapper/gradle-wrapper.jar"
        try:
            urllib.request.urlretrieve(alt_url, wrapper_jar)
            print(f"✓ Downloaded gradle-wrapper.jar from alternative source")
            return True
        except Exception as e2:
            print(f"✗ Alternative download failed: {e2}")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("Gradle Wrapper Fix")
    print("=" * 60)
    print()
    
    if download_gradle_wrapper():
        print("\n✓ Gradle wrapper is ready!")
        print("\nNow you can build the Android apps:")
        print("  1. Run: setup_java.bat")
        print("  2. Then: cd android-ride-hailing")
        print("  3. Then: gradlew.bat assembleDebug")
    else:
        print("\n✗ Failed to download gradle wrapper")
        print("\nManual fix:")
        print("  1. Download from: https://services.gradle.org/distributions/gradle-8.2-bin.zip")
        print("  2. Extract and copy gradle-wrapper.jar to android-ride-hailing/gradle/wrapper/")
