package com.rideconnect.core.data.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.data.mapper.RideMapper
import com.rideconnect.core.data.network.safeApiCall
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.Ride
import com.rideconnect.core.domain.repository.DriverRideRepository
import com.rideconnect.core.domain.websocket.WebSocketManager
import com.rideconnect.core.domain.websocket.WebSocketMessage
import com.rideconnect.core.network.api.DriverApi
import com.rideconnect.core.network.dto.AvailabilityRequestDto
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.filterIsInstance
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Implementation of DriverRideRepository.
 * Requirements: 11.1, 11.2, 12.4, 12.5, 13.3, 13.5, 13.6
 */
@Singleton
class DriverRideRepositoryImpl @Inject constructor(
    private val driverApi: DriverApi,
    private val webSocketManager: WebSocketManager
) : DriverRideRepository {
    
    private val _activeRide = MutableStateFlow<Ride?>(null)
    private val _rideRequests = MutableStateFlow<Ride?>(null)
    
    /**
     * Set driver availability status.
     * Requirements: 11.1, 11.2
     */
    override suspend fun setAvailability(isAvailable: Boolean): Result<Unit> {
        return safeApiCall {
            val request = AvailabilityRequestDto(
                isAvailable = isAvailable,
                latitude = null,
                longitude = null
            )
            driverApi.setAvailability(request)
        }
    }
    
    /**
     * Accept a ride request.
     * Requirements: 12.4
     */
    override suspend fun acceptRide(rideId: String): Result<Ride> {
        return when (val result = safeApiCall { driverApi.acceptRide(rideId) }) {
            is Result.Success -> {
                val ride = RideMapper.toRide(result.data)
                _activeRide.value = ride
                _rideRequests.value = null
                Result.Success(ride)
            }
            is Result.Error -> Result.Error(result.exception)
        }
    }
    
    /**
     * Reject a ride request.
     * Requirements: 12.5
     */
    override suspend fun rejectRide(rideId: String, reason: String): Result<Unit> {
        return when (val result = safeApiCall { driverApi.rejectRide(rideId, mapOf("reason" to reason)) }) {
            is Result.Success -> {
                _rideRequests.value = null
                Result.Success(Unit)
            }
            is Result.Error -> Result.Error(result.exception)
        }
    }
    
    /**
     * Start a ride.
     * Requirements: 13.3
     */
    override suspend fun startRide(rideId: String): Result<Unit> {
        return safeApiCall {
            driverApi.startRide(rideId)
        }
    }
    
    /**
     * Complete a ride.
     * Requirements: 13.6
     */
    override suspend fun completeRide(rideId: String): Result<Unit> {
        return when (val result = safeApiCall { driverApi.completeRide(rideId) }) {
            is Result.Success -> {
                _activeRide.value = null
                Result.Success(Unit)
            }
            is Result.Error -> Result.Error(result.exception)
        }
    }
    
    /**
     * Cancel a ride.
     * Requirements: 13.8
     */
    override suspend fun cancelRide(rideId: String, reason: String): Result<Unit> {
        return when (val result = safeApiCall { driverApi.cancelRide(rideId, mapOf("reason" to reason)) }) {
            is Result.Success -> {
                _activeRide.value = null
                Result.Success(Unit)
            }
            is Result.Error -> Result.Error(result.exception)
        }
    }
    
    /**
     * Observe ride requests via WebSocket.
     * Requirements: 12.1, 12.2
     */
    override fun observeRideRequests(): Flow<Ride?> {
        // Listen to WebSocket messages for ride requests
        return webSocketManager.messages
            .filterIsInstance<WebSocketMessage.RideRequest>()
            .map { message ->
                // Convert WebSocketMessage.RideRequest to Ride domain model
                val ride = Ride(
                    id = message.rideId,
                    riderId = message.riderId,
                    driverId = null,
                    pickupLocation = Location(
                        latitude = message.pickupLatitude,
                        longitude = message.pickupLongitude,
                        address = message.pickupAddress
                    ),
                    dropoffLocation = Location(
                        latitude = message.dropoffLatitude,
                        longitude = message.dropoffLongitude,
                        address = message.dropoffAddress
                    ),
                    status = com.rideconnect.core.domain.model.RideStatus.REQUESTED,
                    fare = message.estimatedFare,
                    distance = message.distance,
                    duration = null,
                    requestedAt = System.currentTimeMillis(),
                    acceptedAt = null,
                    startedAt = null,
                    completedAt = null,
                    cancelledAt = null,
                    cancellationReason = null,
                    driverDetails = null
                )
                _rideRequests.value = ride
                ride
            }
    }
    
    /**
     * Observe active ride via WebSocket.
     * Requirements: 13.3, 13.5, 13.6
     */
    override fun observeActiveRide(): Flow<Ride?> {
        // Listen to WebSocket messages for ride status updates
        webSocketManager.messages
            .filterIsInstance<WebSocketMessage.RideStatusUpdate>()
            .map { message ->
                val currentRide = _activeRide.value
                if (currentRide?.id == message.rideId) {
                    val newStatus = parseRideStatus(message.status)
                    _activeRide.value = currentRide.copy(status = newStatus)
                }
            }
        
        return _activeRide.asStateFlow()
    }
    
    private fun parseRideStatus(status: String): com.rideconnect.core.domain.model.RideStatus {
        return when (status.uppercase()) {
            "REQUESTED" -> com.rideconnect.core.domain.model.RideStatus.REQUESTED
            "SEARCHING" -> com.rideconnect.core.domain.model.RideStatus.SEARCHING
            "ACCEPTED" -> com.rideconnect.core.domain.model.RideStatus.ACCEPTED
            "DRIVER_ARRIVING" -> com.rideconnect.core.domain.model.RideStatus.DRIVER_ARRIVING
            "ARRIVED" -> com.rideconnect.core.domain.model.RideStatus.ARRIVED
            "IN_PROGRESS" -> com.rideconnect.core.domain.model.RideStatus.IN_PROGRESS
            "COMPLETED" -> com.rideconnect.core.domain.model.RideStatus.COMPLETED
            "CANCELLED" -> com.rideconnect.core.domain.model.RideStatus.CANCELLED
            else -> com.rideconnect.core.domain.model.RideStatus.REQUESTED
        }
    }
}
