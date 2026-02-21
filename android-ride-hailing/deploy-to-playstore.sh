#!/bin/bash

# RideConnect - Google Play Store Deployment Script
# This script automates the build process for Play Store submission

set -e  # Exit on error

echo "========================================="
echo "RideConnect Play Store Deployment"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if keystore.properties exists
if [ ! -f "keystore.properties" ]; then
    echo -e "${RED}Error: keystore.properties not found!${NC}"
    echo "Please create keystore.properties with your signing credentials."
    echo "See GOOGLE_PLAY_DEPLOYMENT_GUIDE.md for details."
    exit 1
fi

echo -e "${GREEN}✓${NC} Found keystore.properties"

# Check if keystores exist
if [ ! -f "rider-app/release-keystore.jks" ]; then
    echo -e "${YELLOW}Warning: rider-app/release-keystore.jks not found${NC}"
    echo "Please generate the keystore first. See Step 2 in deployment guide."
    exit 1
fi

if [ ! -f "driver-app/release-keystore.jks" ]; then
    echo -e "${YELLOW}Warning: driver-app/release-keystore.jks not found${NC}"
    echo "Please generate the keystore first. See Step 2 in deployment guide."
    exit 1
fi

echo -e "${GREEN}✓${NC} Found signing keystores"
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
./gradlew clean
echo -e "${GREEN}✓${NC} Clean complete"
echo ""

# Build Rider App
echo "========================================="
echo "Building Rider App Release AAB..."
echo "========================================="
./gradlew :rider-app:bundleRelease

if [ -f "rider-app/build/outputs/bundle/release/rider-app-release.aab" ]; then
    SIZE=$(du -h "rider-app/build/outputs/bundle/release/rider-app-release.aab" | cut -f1)
    echo -e "${GREEN}✓${NC} Rider App AAB built successfully"
    echo "  Location: rider-app/build/outputs/bundle/release/rider-app-release.aab"
    echo "  Size: $SIZE"
    
    # Verify signing
    echo "  Verifying signature..."
    jarsigner -verify -verbose -certs rider-app/build/outputs/bundle/release/rider-app-release.aab > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} Signature verified"
    else
        echo -e "  ${RED}✗${NC} Signature verification failed"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Rider App build failed"
    exit 1
fi
echo ""

# Build Driver App
echo "========================================="
echo "Building Driver App Release AAB..."
echo "========================================="
./gradlew :driver-app:bundleRelease

if [ -f "driver-app/build/outputs/bundle/release/driver-app-release.aab" ]; then
    SIZE=$(du -h "driver-app/build/outputs/bundle/release/driver-app-release.aab" | cut -f1)
    echo -e "${GREEN}✓${NC} Driver App AAB built successfully"
    echo "  Location: driver-app/build/outputs/bundle/release/driver-app-release.aab"
    echo "  Size: $SIZE"
    
    # Verify signing
    echo "  Verifying signature..."
    jarsigner -verify -verbose -certs driver-app/build/outputs/bundle/release/driver-app-release.aab > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} Signature verified"
    else
        echo -e "  ${RED}✗${NC} Signature verification failed"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Driver App build failed"
    exit 1
fi
echo ""

# Summary
echo "========================================="
echo "Build Summary"
echo "========================================="
echo -e "${GREEN}✓${NC} Both apps built successfully!"
echo ""
echo "Release files:"
echo "  1. rider-app/build/outputs/bundle/release/rider-app-release.aab"
echo "  2. driver-app/build/outputs/bundle/release/driver-app-release.aab"
echo ""
echo "Next steps:"
echo "  1. Go to Google Play Console: https://play.google.com/console"
echo "  2. Create new releases for both apps"
echo "  3. Upload the AAB files"
echo "  4. Add release notes"
echo "  5. Submit for review"
echo ""
echo "See GOOGLE_PLAY_DEPLOYMENT_GUIDE.md for detailed instructions."
echo ""
echo -e "${GREEN}Deployment build complete!${NC}"
