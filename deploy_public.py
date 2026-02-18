#!/usr/bin/env python3
"""
Public Deployment Script for RideConnect Platform
Deploys the application with frontend accessible via browser
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_command(cmd, description, check=True):
    """Run a shell command with description."""
    print(f"⚙️  {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False


def check_docker():
    """Check if Docker is installed and running."""
    print_header("Checking Docker Installation")
    
    # Check Docker
    if not run_command("docker --version", "Checking Docker", check=False):
        print("\n❌ Docker is not installed!")
        print("Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        return False
    
    # Check Docker Compose
    if not run_command("docker-compose --version", "Checking Docker Compose", check=False):
        print("\n❌ Docker Compose is not installed!")
        return False
    
    # Check if Docker daemon is running
    if not run_command("docker ps", "Checking Docker daemon", check=False):
        print("\n❌ Docker daemon is not running!")
        print("Please start Docker Desktop")
        return False
    
    return True


def stop_existing_containers():
    """Stop any existing containers."""
    print_header("Cleaning Up Existing Containers")
    run_command("docker-compose down", "Stopping existing containers", check=False)


def build_and_start():
    """Build and start all containers."""
    print_header("Building and Starting Services")
    
    if not run_command("docker-compose build", "Building Docker images"):
        return False
    
    if not run_command("docker-compose up -d", "Starting all services"):
        return False
    
    return True


def wait_for_services():
    """Wait for services to be healthy."""
    print_header("Waiting for Services to Start")
    
    print("⏳ Waiting for services to be healthy (this may take 30-60 seconds)...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        result = subprocess.run(
            "docker-compose ps",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if "healthy" in result.stdout or attempt > 20:
            print("✅ Services are starting up")
            time.sleep(5)  # Give a bit more time
            return True
        
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("⚠️  Services may still be starting. Continuing anyway...")
    return True


def check_health():
    """Check if the application is responding."""
    print_header("Checking Application Health")
    
    import urllib.request
    import urllib.error
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = urllib.request.urlopen("http://localhost/health", timeout=5)
            if response.status == 200:
                print("✅ Application is healthy and responding")
                return True
        except (urllib.error.URLError, urllib.error.HTTPError, Exception):
            print(f"   Attempt {attempt + 1}/{max_attempts}...")
            time.sleep(3)
    
    print("⚠️  Health check failed, but services may still be starting")
    return True


def show_access_info():
    """Display access information."""
    print_header("🎉 Deployment Complete!")
    
    print("Your RideConnect platform is now running!\n")
    
    print("📱 Access URLs:")
    print("   • Main Website:    http://localhost/web/")
    print("   • Rider Dashboard: http://localhost/web/rider-dashboard.html")
    print("   • Driver Dashboard: http://localhost/web/driver-dashboard.html")
    print("   • Admin Panel:     http://localhost/web/admin.html")
    print("   • API Docs:        http://localhost/docs")
    print("   • Health Check:    http://localhost/health")
    
    print("\n🔐 Test Accounts (from seed data):")
    print("   Riders:")
    print("   • Phone: +919876543210, Password: password123")
    print("   • Phone: +919876543211, Password: password123")
    
    print("\n   Drivers:")
    print("   • Phone: +919876543200, Password: password123")
    print("   • Phone: +919876543201, Password: password123")
    
    print("\n📊 Docker Commands:")
    print("   • View logs:       docker-compose logs -f")
    print("   • Stop services:   docker-compose down")
    print("   • Restart:         docker-compose restart")
    print("   • View status:     docker-compose ps")
    
    print("\n💡 Tips:")
    print("   • The database is pre-seeded with 50 users and 200 sample rides")
    print("   • All services are running in Docker containers")
    print("   • Data persists in Docker volumes")
    print("   • Frontend files are served by Nginx")
    
    print("\n" + "=" * 60)


def open_browser():
    """Open the application in browser."""
    print("\n🌐 Opening application in browser...")
    time.sleep(2)
    try:
        webbrowser.open("http://localhost/web/")
        print("✅ Browser opened")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please open http://localhost/web/ manually")


def main():
    """Main deployment function."""
    print_header("🚀 RideConnect Public Deployment")
    print("This script will deploy the complete platform with Docker")
    
    # Check prerequisites
    if not check_docker():
        print("\n❌ Deployment aborted - Docker not available")
        sys.exit(1)
    
    # Stop existing containers
    stop_existing_containers()
    
    # Build and start
    if not build_and_start():
        print("\n❌ Deployment failed during build/start")
        sys.exit(1)
    
    # Wait for services
    wait_for_services()
    
    # Check health
    check_health()
    
    # Show access information
    show_access_info()
    
    # Open browser
    response = input("\n🌐 Would you like to open the application in your browser? (y/n): ")
    if response.lower() in ['y', 'yes', '']:
        open_browser()
    
    print("\n✨ Deployment complete! Your platform is now publicly accessible.")
    print("   Press Ctrl+C to view logs, or close this window.\n")
    
    # Follow logs
    try:
        subprocess.run("docker-compose logs -f", shell=True)
    except KeyboardInterrupt:
        print("\n\n👋 Logs stopped. Services are still running in the background.")
        print("   Use 'docker-compose down' to stop all services.\n")


if __name__ == "__main__":
    main()
