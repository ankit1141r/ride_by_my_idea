#!/bin/bash
# One-Click Deployment for Mac/Linux
# This script deploys the RideConnect platform with Docker

echo "========================================"
echo "  RideConnect - One-Click Deployment"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed!"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

echo "[1/3] Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed!"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "[2/3] Running deployment script..."
python3 deploy_public.py

echo ""
echo "[3/3] Deployment complete!"
echo ""
