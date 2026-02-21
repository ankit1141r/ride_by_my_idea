# Google Maps Autocomplete Setup Guide

## Overview
The rider dashboard now includes Google Maps Places Autocomplete for location input fields. This provides real-time location suggestions as users type, making it easier to select accurate pickup and destination addresses.

## Features Added
- ✅ Google Maps Places Autocomplete on pickup location input
- ✅ Google Maps Places Autocomplete on destination input
- ✅ Real-time fare estimation based on actual coordinates
- ✅ Distance calculation using Haversine formula
- ✅ Reverse geocoding for "Use Current Location" button
- ✅ Styled autocomplete dropdown matching app design
- ✅ Restricted to Indian locations (can be customized)

## Setup Instructions

### 1. Get a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - **Maps JavaScript API**
   - **Places API**
   - **Geocoding API** (for reverse geocoding)
4. Go to "Credentials" and create an API key
5. (Optional but recommended) Restrict the API key:
   - Set application restrictions (HTTP referrers)
   - Set API restrictions (only enable the APIs listed above)

### 2. Add API Key to Configuration

Open `web/js/config.js` and add your API key:

```javascript
const APP_CONFIG = {
    NAME: 'RideConnect',
    VERSION: '1.0.0',
    GOOGLE_MAPS_API_KEY: 'YOUR_API_KEY_HERE', // Add your key here
    // ... rest of config
};
```

### 3. Test the Integration

1. Start the web server:
   ```bash
   python simple_app.py
   ```

2. Open the rider dashboard: http://localhost:8001/web/rider-dashboard.html

3. Try typing in the pickup or destination fields - you should see location suggestions

## How It Works

### Autocomplete Initialization
When the page loads, the Google Maps API is loaded dynamically with the Places library. The autocomplete is initialized on both location input fields with the following configuration:

```javascript
{
    componentRestrictions: { country: 'in' },  // Restrict to India
    fields: ['formatted_address', 'geometry', 'name', 'place_id'],
    types: ['establishment', 'geocode']
}
```

### Place Selection
When a user selects a place from the autocomplete suggestions:
1. The formatted address is displayed in the input field
2. Coordinates (latitude/longitude) are extracted
3. Fare estimation is automatically calculated using the Haversine formula
4. Distance between pickup and destination is displayed

### Fare Calculation
The fare is calculated using:
- Base fare: ₹30
- Per km rate: ₹12
- Formula: `Base Fare + (Distance × Per Km Rate)`

### Current Location Button
The "Use Current Location" button:
1. Gets the user's current GPS coordinates
2. Uses reverse geocoding to convert coordinates to an address
3. Sets the address in the input field
4. Stores coordinates for fare calculation

## Customization

### Change Location Restrictions
To change the country restriction, modify the autocomplete options in `web/js/rider-dashboard.js`:

```javascript
const autocompleteOptions = {
    componentRestrictions: { country: 'us' },  // Change to your country code
    // ... other options
};
```

### Adjust Fare Configuration
Modify fare settings in `web/js/config.js`:

```javascript
FARE_CONFIG: {
    BASE_FARE: 30,      // Change base fare
    PER_KM_RATE: 12,    // Change per km rate
    CURRENCY: '₹'       // Change currency symbol
}
```

## Troubleshooting

### Autocomplete Not Working
1. Check browser console for errors
2. Verify API key is correctly added to `config.js`
3. Ensure Maps JavaScript API and Places API are enabled in Google Cloud Console
4. Check if API key has proper restrictions (not too restrictive)

### "Failed to load Google Maps API" Error
- Verify your API key is valid
- Check if you have billing enabled on your Google Cloud account
- Ensure the API key has access to the required APIs

### No Location Suggestions Appearing
- Check if the API key has Places API enabled
- Verify network connectivity
- Check browser console for API errors

## API Usage and Billing

Google Maps Platform offers a free tier with $200 monthly credit, which covers:
- ~28,000 autocomplete requests per month
- ~40,000 geocoding requests per month

For production use, monitor your usage in the Google Cloud Console and set up billing alerts.

## Security Best Practices

1. **Restrict API Key**: Always restrict your API key to specific domains in production
2. **Use Environment Variables**: Store API keys in environment variables, not in code
3. **Monitor Usage**: Set up usage alerts to prevent unexpected charges
4. **Rotate Keys**: Regularly rotate API keys for security

## Next Steps

- Add map visualization showing pickup and destination markers
- Implement route display on the map
- Add real-time driver location tracking
- Integrate with backend API for actual ride requests

## Support

For issues or questions:
- Check the [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- Review the browser console for error messages
- Verify API key configuration and restrictions
