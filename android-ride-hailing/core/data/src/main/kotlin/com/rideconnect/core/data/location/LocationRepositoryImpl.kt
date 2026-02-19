package com.rideconnect.core.data.location

import android.content.Context
import com.google.android.gms.maps.model.LatLng
import com.google.android.libraries.places.api.model.RectangularBounds
import com.google.android.libraries.places.api.net.FetchPlaceRequest
import com.google.android.libraries.places.api.net.FindAutocompletePredictionsRequest
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.location.LocationRepository
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.Place
import com.rideconnect.core.domain.model.Route
import com.rideconnect.core.domain.model.RouteBounds
import com.rideconnect.core.network.api.LocationApi
import com.rideconnect.core.network.dto.LocationUpdateRequest
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext
import timber.log.Timber
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Implementation of LocationRepository.
 * Integrates with backend API and Google Places API.
 * 
 * Requirements: 18.3, 18.4
 */
@Singleton
class LocationRepositoryImpl @Inject constructor(
    private val locationApi: LocationApi,
    private val placesClient: PlacesClient
) : LocationRepository {
    
    override suspend fun updateLocation(location: Location): Result<Unit> {
        return withContext(Dispatchers.IO) {
            try {
                val request = LocationUpdateRequest(
                    latitude = location.latitude,
                    longitude = location.longitude,
                    accuracy = location.accuracy,
                    timestamp = location.timestamp
                )
                locationApi.updateDriverLocation(request)
                Result.Success(Unit)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }
    
    override suspend fun searchPlaces(query: String, location: Location?): Result<List<Place>> {
        return withContext(Dispatchers.IO) {
            try {
                val places = placesClient.searchPlaces(query, location)
                Result.Success(places)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }
    
    override suspend fun getPlaceDetails(placeId: String): Result<Place> {
        return withContext(Dispatchers.IO) {
            try {
                val place = placesClient.getPlaceDetails(placeId)
                Result.Success(place)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }
    
    override suspend fun calculateRoute(origin: Location, destination: Location): Result<Route> {
        return withContext(Dispatchers.IO) {
            try {
                val route = placesClient.calculateRoute(origin, destination)
                Result.Success(route)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }
}

/**
 * Client for Google Places API and Directions API.
 * Wraps Google Play Services libraries for location search and routing.
 */
interface PlacesClient {
    suspend fun searchPlaces(query: String, location: Location?): List<Place>
    suspend fun getPlaceDetails(placeId: String): Place
    suspend fun calculateRoute(origin: Location, destination: Location): Route
}

/**
 * Implementation of PlacesClient using Google Play Services.
 */
@Singleton
class GooglePlacesClient @Inject constructor(
    @ApplicationContext private val context: Context
) : PlacesClient {
    
    private val placesClient: com.google.android.libraries.places.api.net.PlacesClient by lazy {
        com.google.android.libraries.places.api.Places.createClient(context)
    }
    
    override suspend fun searchPlaces(query: String, location: Location?): List<Place> {
        return withContext(Dispatchers.IO) {
            try {
                val request = FindAutocompletePredictionsRequest.builder()
                    .setQuery(query)
                    .apply {
                        // Bias results to user's location if available
                        location?.let {
                            setLocationBias(
                                RectangularBounds.newInstance(
                                    LatLng(it.latitude - 0.1, it.longitude - 0.1),
                                    LatLng(it.latitude + 0.1, it.longitude + 0.1)
                                )
                            )
                        }
                    }
                    .setCountries(listOf("IN")) // Restrict to India
                    .build()
                
                val response = placesClient.findAutocompletePredictions(request).await()
                
                response.autocompletePredictions.map { prediction ->
                    Place(
                        placeId = prediction.placeId,
                        name = prediction.getPrimaryText(null).toString(),
                        address = prediction.getFullText(null).toString(),
                        latitude = 0.0, // Will be fetched when place is selected
                        longitude = 0.0
                    )
                }
            } catch (e: Exception) {
                Timber.e(e, "Error searching places")
                emptyList()
            }
        }
    }
    
    override suspend fun getPlaceDetails(placeId: String): Place {
        return withContext(Dispatchers.IO) {
            try {
                val placeFields = listOf(
                    com.google.android.libraries.places.api.model.Place.Field.ID,
                    com.google.android.libraries.places.api.model.Place.Field.NAME,
                    com.google.android.libraries.places.api.model.Place.Field.ADDRESS,
                    com.google.android.libraries.places.api.model.Place.Field.LAT_LNG
                )
                
                val request = FetchPlaceRequest.builder(placeId, placeFields).build()
                val response = placesClient.fetchPlace(request).await()
                
                val place = response.place
                val latLng = place.latLng ?: throw IllegalStateException("Place has no coordinates")
                
                Place(
                    placeId = place.id ?: placeId,
                    name = place.name ?: "",
                    address = place.address ?: "",
                    latitude = latLng.latitude,
                    longitude = latLng.longitude
                )
            } catch (e: Exception) {
                Timber.e(e, "Error fetching place details")
                throw e
            }
        }
    }
    
    override suspend fun calculateRoute(origin: Location, destination: Location): Route {
        // Note: Google Directions API requires a separate API key and is typically called via backend
        // For now, we'll return a simple route with straight-line distance
        return withContext(Dispatchers.IO) {
            try {
                // Calculate straight-line distance using Haversine formula
                val distanceMeters = calculateDistance(
                    origin.latitude, origin.longitude,
                    destination.latitude, destination.longitude
                )
                
                // Estimate duration (assuming average speed of 30 km/h in city)
                val durationSeconds = (distanceMeters / 30000.0 * 3600).toInt()
                
                Route(
                    polyline = "", // Polyline would come from Directions API
                    distanceMeters = distanceMeters.toInt(),
                    durationSeconds = durationSeconds,
                    bounds = RouteBounds(
                        northeast = Location(
                            latitude = maxOf(origin.latitude, destination.latitude),
                            longitude = maxOf(origin.longitude, destination.longitude),
                            accuracy = 0f,
                            timestamp = System.currentTimeMillis()
                        ),
                        southwest = Location(
                            latitude = minOf(origin.latitude, destination.latitude),
                            longitude = minOf(origin.longitude, destination.longitude),
                            accuracy = 0f,
                            timestamp = System.currentTimeMillis()
                        )
                    )
                )
            } catch (e: Exception) {
                Timber.e(e, "Error calculating route")
                throw e
            }
        }
    }
    
    /**
     * Calculate distance between two coordinates using Haversine formula.
     * Returns distance in meters.
     */
    private fun calculateDistance(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val earthRadius = 6371000.0 // meters
        val dLat = Math.toRadians(lat2 - lat1)
        val dLon = Math.toRadians(lon2 - lon1)
        val a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2)
        val c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
        return earthRadius * c
    }
}
