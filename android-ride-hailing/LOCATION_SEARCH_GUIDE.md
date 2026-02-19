# Location Search with Google Places API - Implementation Guide

## Overview

Task 7.5 implements location search functionality using Google Places API. This allows users to search for locations with autocomplete suggestions and select places to use as pickup or dropoff locations.

## Components Implemented

### 1. GooglePlacesClient
**Location**: `core/data/src/main/kotlin/com/rideconnect/core/data/location/LocationRepositoryImpl.kt`

Implements the `PlacesClient` interface with actual Google Places API integration:
- `searchPlaces()`: Uses FindAutocompletePredictionsRequest for location autocomplete
- `getPlaceDetails()`: Fetches full place details including coordinates using FetchPlaceRequest
- `calculateRoute()`: Calculates route distance and duration (uses Haversine formula for now)

Features:
- Biases search results to user's current location
- Restricts results to India (configurable)
- Returns place predictions with name and address
- Fetches coordinates when place is selected

### 2. LocationSearchBar Composable
**Location**: `core/common/src/main/kotlin/com/rideconnect/core/common/ui/LocationSearchBar.kt`

A reusable Compose UI component for location search:
- Search input field with clear button
- Animated dropdown showing search results
- Loading indicator during search
- Keyboard actions (search on enter)
- Automatic search when query length >= 3 characters

### 3. LocationSearchViewModel
**Location**: `core/domain/src/main/kotlin/com/rideconnect/core/domain/viewmodel/LocationSearchViewModel.kt`

Manages location search state and business logic:
- Debounced search (300ms) to reduce API calls
- Minimum 3 characters before searching
- Handles place selection and fetches full details
- Manages loading and error states
- Supports location biasing for better results

### 4. LocationSearchScreen (Example)
**Location**: `core/common/src/main/kotlin/com/rideconnect/core/common/ui/LocationSearchScreen.kt`

Example screen demonstrating how to use LocationSearchBar in your app.

### 5. PlacesInitializer
**Location**: `core/data/src/main/kotlin/com/rideconnect/core/data/location/PlacesInitializer.kt`

Helper class to initialize Google Places SDK during app startup.

## Setup Instructions

### 1. Get Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable the following APIs:
   - Places API
   - Maps SDK for Android
4. Create an API key:
   - Go to "Credentials"
   - Click "Create Credentials" → "API Key"
   - Restrict the key to Android apps
   - Add your app's package name and SHA-1 certificate fingerprint

### 2. Add API Key to Project

**Option A: Using local.properties (Recommended)**

Add to `local.properties` (not committed to git):
```properties
GOOGLE_PLACES_API_KEY=your_api_key_here
```

Then in `build.gradle.kts`:
```kotlin
android {
    defaultConfig {
        val properties = Properties()
        properties.load(project.rootProject.file("local.properties").inputStream())
        buildConfigField("String", "GOOGLE_PLACES_API_KEY", 
            "\"${properties.getProperty("GOOGLE_PLACES_API_KEY")}\"")
    }
}
```

**Option B: Using AndroidManifest.xml**

Add to `AndroidManifest.xml`:
```xml
<application>
    <meta-data
        android:name="com.google.android.geo.API_KEY"
        android:value="YOUR_API_KEY_HERE" />
</application>
```

### 3. Initialize Places SDK

In your Application class:

```kotlin
@HiltAndroidApp
class RideConnectApp : Application() {
    
    @Inject
    lateinit var placesInitializer: PlacesInitializer
    
    override fun onCreate() {
        super.onCreate()
        
        // Initialize Google Places SDK
        val apiKey = BuildConfig.GOOGLE_PLACES_API_KEY
        placesInitializer.initialize(apiKey)
    }
}
```

## Usage Examples

### Basic Usage in a Screen

```kotlin
@Composable
fun RideRequestScreen(
    viewModel: LocationSearchViewModel = hiltViewModel()
) {
    val searchQuery by viewModel.searchQuery.collectAsState()
    val searchResults by viewModel.searchResults.collectAsState()
    val selectedPlace by viewModel.selectedPlace.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    
    Column(modifier = Modifier.padding(16.dp)) {
        LocationSearchBar(
            query = searchQuery,
            onQueryChange = { viewModel.updateSearchQuery(it) },
            searchResults = searchResults,
            onPlaceSelected = { viewModel.selectPlace(it) },
            onSearch = { viewModel.search(it) },
            isLoading = isLoading,
            placeholder = "Enter pickup location"
        )
        
        // Use selectedPlace for your ride request
        selectedPlace?.let { place ->
            Text("Selected: ${place.name}")
            Text("Coordinates: ${place.latitude}, ${place.longitude}")
        }
    }
}
```

### With Current Location Biasing

```kotlin
@Composable
fun LocationSearchWithBias(
    viewModel: LocationSearchViewModel = hiltViewModel(),
    locationService: LocationService
) {
    val currentLocation by locationService.locationFlow.collectAsState(initial = null)
    
    // Update ViewModel with current location for biasing
    LaunchedEffect(currentLocation) {
        currentLocation?.let { viewModel.updateCurrentLocation(it) }
    }
    
    LocationSearchBar(
        query = viewModel.searchQuery.collectAsState().value,
        onQueryChange = { viewModel.updateSearchQuery(it) },
        searchResults = viewModel.searchResults.collectAsState().value,
        onPlaceSelected = { viewModel.selectPlace(it) },
        onSearch = { viewModel.search(it) },
        isLoading = viewModel.isLoading.collectAsState().value
    )
}
```

### Dual Location Selection (Pickup & Dropoff)

```kotlin
@Composable
fun DualLocationSearch() {
    val pickupViewModel: LocationSearchViewModel = hiltViewModel()
    val dropoffViewModel: LocationSearchViewModel = hiltViewModel()
    
    Column {
        Text("Pickup Location")
        LocationSearchBar(
            query = pickupViewModel.searchQuery.collectAsState().value,
            onQueryChange = { pickupViewModel.updateSearchQuery(it) },
            searchResults = pickupViewModel.searchResults.collectAsState().value,
            onPlaceSelected = { pickupViewModel.selectPlace(it) },
            onSearch = { pickupViewModel.search(it) },
            isLoading = pickupViewModel.isLoading.collectAsState().value,
            placeholder = "Enter pickup location"
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text("Dropoff Location")
        LocationSearchBar(
            query = dropoffViewModel.searchQuery.collectAsState().value,
            onQueryChange = { dropoffViewModel.updateSearchQuery(it) },
            searchResults = dropoffViewModel.searchResults.collectAsState().value,
            onPlaceSelected = { dropoffViewModel.selectPlace(it) },
            onSearch = { dropoffViewModel.search(it) },
            isLoading = dropoffViewModel.isLoading.collectAsState().value,
            placeholder = "Enter dropoff location"
        )
    }
}
```

## Features

### Automatic Debouncing
The ViewModel automatically debounces search queries by 300ms to reduce API calls. Users can type freely without triggering excessive searches.

### Minimum Query Length
Search only triggers when query is at least 3 characters long, following Google Places API best practices.

### Location Biasing
When current location is provided, search results are biased towards nearby places for better relevance.

### Error Handling
All API errors are caught and exposed via the ViewModel's error state for UI display.

### Loading States
Loading indicators are shown during API calls for better UX.

## API Costs

Google Places API has usage limits and costs:
- **Autocomplete (per session)**: $2.83 per 1000 sessions
- **Place Details**: $17 per 1000 requests
- **Free tier**: $200 credit per month

To optimize costs:
1. Use session tokens for autocomplete (not yet implemented)
2. Cache frequently searched places
3. Implement rate limiting
4. Use location biasing to reduce irrelevant results

## Testing

### Manual Testing
1. Run the app
2. Navigate to a screen with LocationSearchBar
3. Type at least 3 characters
4. Verify autocomplete suggestions appear
5. Select a place
6. Verify coordinates are fetched

### Unit Testing
Test the ViewModel:
```kotlin
@Test
fun `search triggers after debounce`() = runTest {
    val viewModel = LocationSearchViewModel(mockRepository)
    
    viewModel.updateSearchQuery("test")
    advanceTimeBy(300)
    
    verify(mockRepository).searchPlaces("test", null)
}
```

## Troubleshooting

### No search results
- Check API key is valid and not restricted
- Verify Places API is enabled in Google Cloud Console
- Check network connectivity
- Verify query is at least 3 characters

### API key errors
- Ensure API key is properly configured in BuildConfig or AndroidManifest
- Check API key restrictions (package name, SHA-1)
- Verify billing is enabled in Google Cloud Console

### Coordinates are (0.0, 0.0)
- This means place details haven't been fetched yet
- Call `viewModel.selectPlace()` to fetch full details
- Check for errors in the error state

## Requirements Validated

✅ **Requirement 18.3**: Location search using Google Places Autocomplete API
✅ **Requirement 18.4**: Display search results and handle selection

## Next Steps

1. Implement session tokens for cost optimization
2. Add place caching to reduce API calls
3. Implement recent searches feature
4. Add favorite locations
5. Integrate with Google Directions API for actual route polylines
