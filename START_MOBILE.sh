#!/bin/bash
# Start server for mobile access

echo "========================================"
echo "  RideConnect - Mobile Access"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed!"
    exit 1
fi

echo "Starting mobile-accessible server..."
echo ""

python3 start_mobile.py
