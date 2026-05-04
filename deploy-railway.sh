#!/bin/bash

# Railway Deployment Script for Ride-Hailing Platform
# This script helps you deploy to Railway quickly

echo "🚀 Ride-Hailing Platform - Railway Deployment"
echo "=============================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo ""
    echo "Please install it first:"
    echo "  npm install -g @railway/cli"
    echo ""
    echo "Or visit: https://docs.railway.app/develop/cli"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Login to Railway
echo "📝 Logging in to Railway..."
railway login

# Initialize project
echo ""
echo "🎯 Initializing Railway project..."
railway init

# Link to project (if already exists)
echo ""
echo "🔗 Linking to Railway project..."
railway link

# Add PostgreSQL
echo ""
echo "🗄️  Adding PostgreSQL database..."
railway add --database postgresql

# Add Redis
echo ""
echo "📦 Adding Redis cache..."
railway add --database redis

# Set environment variables
echo ""
echo "⚙️  Setting environment variables..."
echo ""
echo "Please provide the following information:"
echo ""

read -p "Google Maps API Key: " GOOGLE_MAPS_KEY
read -p "Twilio Account SID (optional, press Enter to skip): " TWILIO_SID
read -p "Twilio Auth Token (optional, press Enter to skip): " TWILIO_TOKEN
read -p "Twilio Phone Number (optional, press Enter to skip): " TWILIO_PHONE

# Generate random secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

echo ""
echo "🔐 Setting secrets..."

railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set JWT_SECRET_KEY="$JWT_SECRET_KEY"
railway variables set APP_ENV="production"
railway variables set DEBUG="false"

if [ ! -z "$GOOGLE_MAPS_KEY" ]; then
    railway variables set GOOGLE_MAPS_API_KEY="$GOOGLE_MAPS_KEY"
fi

if [ ! -z "$TWILIO_SID" ]; then
    railway variables set TWILIO_ACCOUNT_SID="$TWILIO_SID"
    railway variables set TWILIO_AUTH_TOKEN="$TWILIO_TOKEN"
    railway variables set TWILIO_PHONE_NUMBER="$TWILIO_PHONE"
fi

# Set default configuration
railway variables set INDORE_LAT_MIN="22.6"
railway variables set INDORE_LAT_MAX="22.8"
railway variables set INDORE_LON_MIN="75.7"
railway variables set INDORE_LON_MAX="75.9"
railway variables set INITIAL_SEARCH_RADIUS_KM="5"
railway variables set SEARCH_RADIUS_EXPANSION_KM="2"
railway variables set MATCH_TIMEOUT_SECONDS="120"
railway variables set BASE_FARE="30"
railway variables set PER_KM_RATE="12"
railway variables set FARE_PROTECTION_THRESHOLD="0.20"

# Deploy
echo ""
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📊 Check deployment status:"
echo "   railway status"
echo ""
echo "📝 View logs:"
echo "   railway logs"
echo ""
echo "🌐 Open in browser:"
echo "   railway open"
echo ""
echo "🎉 Deployment complete!"
