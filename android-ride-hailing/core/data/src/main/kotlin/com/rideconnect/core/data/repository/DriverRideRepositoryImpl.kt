package com.rideconnect.core.data.repository

import com.rideconnect.core.common.network.safeApiCall
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.data.mapper.toRide
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
        return safeApiCall {
            driverApi.acceptRide(rideId)
        }.map { rideDto ->
            val ride = rideDto.toRide()
            _activeRide.value = ride
            _rideRequests.value = null
            ride
        }
    }
    
    /**
     * Reject a ride request.
     * Requirements: 12.5
     */
    override suspend fun rejectRide(rideId: String, reason: String): Result<Unit> {
        return safeApiCall {
            driverApi.rejectRide(rideId, mapOf("reason" to reason))
        }.map {
            _rideRequests.value = null
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
        return safeApiCall {
            driverApi.completeRide(rideId)
        }.map {
            _activeRide.value = null
        }
    }
    
    /**
     * Cancel a ride.
     * Requirements: 13.8
     */
    override suspend fun cancelRide(rideId: String, reason: String): Result<Unit> {
        return safeApiCall {
            driverApi.cancelRide(rideId, mapOf("reason" to reason))
        }.map {
            _activeRide.value = null
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
                val ride = message.ride
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
                    _activeRide.value = currentRide.copy(status = message.status)
                }
            }
        
        return _activeRide.asStateFlow()
    }
}
