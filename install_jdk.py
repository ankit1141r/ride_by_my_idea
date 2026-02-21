"""
Automatic JDK Installation Script for Windows
Downloads and installs JDK 17, then configures JAVA_HOME
"""

import os
import sys
import urllib.request
import subprocess
import zipfile
import shutil
from pathlib import Path

def download_file(url, destination):
    """Download file with progress indicator"""
    print(f"Downloading from {url}...")
    print("This may take a few minutes...")
    
    try:
        urllib.request.urlretrieve(url, destination)
        print(f"✓ Downloaded to {destination}")
        return True
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """Extract zip file"""
    print(f"Extracting {zip_path}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"✓ Extracted to {extract_to}")
        return True
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        return False

def find_jdk_folder(base_path):
    """Find the JDK folder after extraction"""
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path) and 'jdk' in item.lower():
            return item_path
    return None

def set_environment_variable(name, value):
    """Set environment variable for current session"""
    os.environ[name] = value
    print(f"✓ Set {name}={value} for current session")

def main():
    print("=" * 60)
    print("JDK 17 Automatic Installation Script")
    print("=" * 60)
    print()
    
    # Check if Java is already installed
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("✓ Java is already installed!")
            print(result.stderr)
            
            # Try to find JAVA_HOME
            java_exe = shutil.which('java')
            if java_exe:
                java_home = str(Path(java_exe).parent.parent)
                print(f"\nDetected JAVA_HOME: {java_home}")
                set_environment_variable('JAVA_HOME', java_home)
                set_environment_variable('PATH', f"{java_home}\\bin;{os.environ.get('PATH', '')}")
                print("\n✓ Environment configured for current session!")
                return
    except:
        pass
    
    print("Java not found. Installing JDK 17...")
    print()
    
    # Download URL for JDK 17 (Adoptium/Eclipse Temurin) - MSI installer
    jdk_url = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.17+10/OpenJDK17U-jdk_x64_windows_hotspot_17.0.17_10.msi"
    
    # Paths
    download_dir = os.path.join(os.getcwd(), "jdk_download")
    msi_file = os.path.join(download_dir, "jdk17.msi")
    install_dir = "C:\\Program Files\\Eclipse Adoptium\\jdk-17.0.17.10-hotspot"
    
    # Create directories
    os.makedirs(download_dir, exist_ok=True)
    
    # Download JDK
    if not os.path.exists(msi_file):
        print("Step 1: Downloading JDK 17 MSI installer...")
        if not download_file(jdk_url, msi_file):
            print("\n✗ Failed to download JDK")
            print("\nTrying alternative method with winget...")
            try:
                result = subprocess.run(['winget', 'install', 'EclipseAdoptium.Temurin.17.JDK'],
                                      capture_output=True,
                                      text=True,
                                      timeout=300)
                if result.returncode == 0:
                    print("✓ JDK installed via winget!")
                    # Find installation
                    if os.path.exists(install_dir):
                        jdk_home = install_dir
                        set_environment_variable('JAVA_HOME', jdk_home)
                        set_environment_variable('PATH', f"{jdk_home}\\bin;{os.environ.get('PATH', '')}")
                        print(f"\n✓ JAVA_HOME set to: {jdk_home}")
                        return
                else:
                    print("✗ winget installation failed")
            except:
                pass
            
            print("\nManual installation:")
            print("1. Visit: https://adoptium.net/temurin/releases/")
            print("2. Download JDK 17 for Windows x64")
            print("3. Install and add to PATH")
            return
    else:
        print("✓ JDK MSI file already downloaded")
    
    # Install JDK using MSI
    print("\nStep 2: Installing JDK (this may require administrator privileges)...")
    try:
        # Silent install with ADDLOCAL=FeatureMain,FeatureEnvironment,FeatureJarFileRunWith,FeatureJavaHome
        result = subprocess.run(['msiexec', '/i', msi_file, '/quiet', '/norestart',
                               'ADDLOCAL=FeatureMain,FeatureEnvironment,FeatureJarFileRunWith,FeatureJavaHome',
                               'INSTALLDIR=' + install_dir],
                              capture_output=True,
                              text=True,
                              timeout=180)
        
        if result.returncode == 0:
            print("✓ JDK installed successfully")
        else:
            print(f"Installation may have completed with warnings (code: {result.returncode})")
    except Exception as e:
        print(f"Installation note: {e}")
        print("Checking if installation succeeded...")
    
    # Wait a moment for installation to complete
    import time
    time.sleep(2)
    
    # Find JDK folder
    if os.path.exists(install_dir):
        jdk_home = install_dir
    else:
        # Try to find in common locations
        possible_locations = [
            "C:\\Program Files\\Eclipse Adoptium",
            "C:\\Program Files\\Java",
            "C:\\Program Files (x86)\\Eclipse Adoptium"
        ]
        jdk_home = None
        for loc in possible_locations:
            if os.path.exists(loc):
                for item in os.listdir(loc):
                    if 'jdk' in item.lower() and '17' in item:
                        jdk_home = os.path.join(loc, item)
                        break
            if jdk_home:
                break
        
        if not jdk_home:
            print("\n✗ Could not find JDK installation")
            return
    
    print(f"\n✓ JDK installed at: {jdk_home}")
    
    # Set environment variables for current session
    print("\nStep 3: Configuring environment...")
    set_environment_variable('JAVA_HOME', jdk_home)
    set_environment_variable('PATH', f"{jdk_home}\\bin;{os.environ.get('PATH', '')}")
    
    # Verify installation
    print("\nStep 4: Verifying installation...")
    try:
        result = subprocess.run([os.path.join(jdk_home, 'bin', 'java.exe'), '-version'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            print("✓ Java verification successful!")
            print(result.stderr)
        else:
            print("✗ Java verification failed")
    except Exception as e:
        print(f"✗ Verification error: {e}")
    
    # Create batch file for permanent configuration
    batch_file = "set_java_env.bat"
    with open(batch_file, 'w') as f:
        f.write(f'@echo off\n')
        f.write(f'set JAVA_HOME={jdk_home}\n')
        f.write(f'set PATH=%JAVA_HOME%\\bin;%PATH%\n')
        f.write(f'echo JAVA_HOME set to %JAVA_HOME%\n')
        f.write(f'echo.\n')
        f.write(f'java -version\n')
    
    print(f"\n✓ Created {batch_file} for future sessions")
    
    print("\n" + "=" * 60)
    print("INSTALLATION COMPLETE!")
    print("=" * 60)
    print(f"\nJAVA_HOME: {jdk_home}")
    print("\nFor CURRENT session: Environment is configured ✓")
    print(f"\nFor FUTURE sessions: Run '{batch_file}' before building")
    print("\nOr add to System Environment Variables:")
    print(f"  Variable: JAVA_HOME")
    print(f"  Value: {jdk_home}")
    print("=" * 60)
    
    # Cleanup
    try:
        shutil.rmtree(download_dir)
        print("\n✓ Cleaned up temporary files")
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
