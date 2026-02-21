package com.rideconnect.core.data.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.database.dao.RideDao
import com.rideconnect.core.database.entity.RideEntity
import com.rideconnect.core.domain.model.*
import com.rideconnect.core.domain.repository.RideRepository
import com.rideconnect.core.domain.websocket.WebSocketManager
import com.rideconnect.core.domain.websocket.WebSocketMessage
import com.rideconnect.core.network.api.RideApi
import com.rideconnect.core.network.dto.CancelRideRequestDto
import com.rideconnect.core.network.dto.RideRequestDto
import kotlinx.coroutines.flow.*
import java.time.Instant
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class RideRepositoryImpl @Inject constructor(
    private val rideApi: RideApi,
    private val webSocketManager: WebSocketManager,
    private val rideDao: RideDao
) : RideRepository {
    
    private val _activeRide = MutableStateFlow<Ride?>(null)
    
    override suspend fun requestRide(request: RideRequest): Result<Ride> {
        return try {
            val requestDto = RideRequestDto(
                pickupLatitude = request.pickupLocation.latitude,
                pickupLongitude = request.pickupLocation.longitude,
                pickupAddress = request.pickupLocation.address,
                dropoffLatitude = request.dropoffLocation.latitude,
                dropoffLongitude = request.dropoffLocation.longitude,
                dropoffAddress = request.dropoffLocation.address
            )
            
            val response = rideApi.requestRide(requestDto)
            
            if (response.isSuccessful && response.body() != null) {
                val ride = mapRideResponseToRide(response.body()!!)
                _activeRide.value = ride
                Result.Success(ride)
            } else {
                Result.Error(Exception("Failed to request ride: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun getFareEstimate(request: RideRequest): Result<FareEstimate> {
        return try {
            val requestDto = RideRequestDto(
                pickupLatitude = request.pickupLocation.latitude,
                pickupLongitude = request.pickupLocation.longitude,
                pickupAddress = request.pickupLocation.address,
                dropoffLatitude = request.dropoffLocation.latitude,
                dropoffLongitude = request.dropoffLocation.longitude,
                dropoffAddress = request.dropoffLocation.address
            )
            
            val response = rideApi.getFareEstimate(requestDto)
            
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val fareEstimate = FareEstimate(
                    baseFare = dto.baseFare,
                    distanceFare = dto.distanceFare,
                    timeFare = dto.timeFare,
                    totalFare = dto.totalFare,
                    distance = dto.distance,
                    estimatedDuration = dto.estimatedDuration
                )
                Result.Success(fareEstimate)
            } else {
                Result.Error(Exception("Failed to get fare estimate: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun cancelRide(rideId: String, reason: String): Result<Unit> {
        return try {
            val requestDto = CancelRideRequestDto(reason = reason)
            val response = rideApi.cancelRide(rideId, requestDto)
            
            if (response.isSuccessful) {
                _activeRide.value = null
                Result.Success(Unit)
            } else {
                Result.Error(Exception("Failed to cancel ride: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun getRideDetails(rideId: String): Result<Ride> {
        return try {
            val response = rideApi.getRideDetails(rideId)
            
            if (response.isSuccessful && response.body() != null) {
                val ride = mapRideResponseToRide(response.body()!!)
                Result.Success(ride)
            } else {
                Result.Error(Exception("Failed to get ride details: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun getRideHistory(page: Int, pageSize: Int): Result<List<Ride>> {
        return try {
            // Try to fetch from API
            val response = rideApi.getRideHistory(page, pageSize)
            
            if (response.isSuccessful && response.body() != null) {
                val rides = response.body()!!.map { mapRideResponseToRide(it) }
                
                // Save to local database for offline access
                rides.forEach { ride ->
                    rideDao.insertRide(mapRideToEntity(ride))
                }
                
                Result.Success(rides)
            } else {
                // Fallback to local database if API fails
                val localRides = rideDao.getRideHistory("current_user_id") // TODO: Get actual user ID
                    .first()
                    .map { mapEntityToRide(it) }
                Result.Success(localRides)
            }
        } catch (e: Exception) {
            // Fallback to local database on network error
            try {
                val localRides = rideDao.getRideHistory("current_user_id") // TODO: Get actual user ID
                    .first()
                    .map { mapEntityToRide(it) }
                Result.Success(localRides)
            } catch (dbError: Exception) {
                Result.Error(e)
            }
        }
    }
    
    override fun observeActiveRide(): Flow<Ride?> {
        return merge(
            _activeRide,
            webSocketManager.messages
                .filterIsInstance<WebSocketMessage.RideStatusUpdate>()
                .mapNotNull { message ->
                    val currentRide = _activeRide.value
                    if (currentRide?.id == message.rideId) {
                        currentRide.copy(status = RideStatus.valueOf(message.status.uppercase()))
                    } else {
                        null
                    }
                }
                .onEach { updatedRide ->
                    _activeRide.value = updatedRide
                },
            webSocketManager.messages
                .filterIsInstance<WebSocketMessage.RideAccepted>()
                .mapNotNull { message ->
                    val currentRide = _activeRide.value
                    if (currentRide?.id == message.rideId) {
                        // Fetch updated ride details with driver info
                        when (val result = getRideDetails(message.rideId)) {
                            is Result.Success -> result.data
                            is Result.Error -> null
                        }
                    } else {
                        null
                    }
                }
                .onEach { updatedRide ->
                    _activeRide.value = updatedRide
                }
        ).distinctUntilChanged()
    }
    
    override suspend fun setActiveRide(ride: Ride?) {
        _activeRide.value = ride
    }
    
    private fun mapRideResponseToRide(dto: com.rideconnect.core.network.dto.RideResponseDto): Ride {
        return Ride(
            id = dto.id,
            riderId = dto.riderId,
            driverId = dto.driverId,
            pickupLocation = Location(
                latitude = dto.pickupLatitude,
                longitude = dto.pickupLongitude,
                address = dto.pickupAddress,
                placeId = null
            ),
            dropoffLocation = Location(
                latitude = dto.dropoffLatitude,
                longitude = dto.dropoffLongitude,
                address = dto.dropoffAddress,
                placeId = null
            ),
            status = RideStatus.valueOf(dto.status.uppercase()),
            fare = dto.fare,
            distance = dto.distance,
            duration = dto.duration,
            requestedAt = Instant.parse(dto.requestedAt).toEpochMilli(),
            acceptedAt = dto.acceptedAt?.let { Instant.parse(it).toEpochMilli() },
            startedAt = dto.startedAt?.let { Instant.parse(it).toEpochMilli() },
            completedAt = dto.completedAt?.let { Instant.parse(it).toEpochMilli() },
            cancelledAt = dto.cancelledAt?.let { Instant.parse(it).toEpochMilli() },
            cancellationReason = dto.cancellationReason,
            driverDetails = dto.driver?.let { driverDto ->
                DriverDetails(
                    id = driverDto.id,
                    name = "", // Name not provided in DriverDetailsDto
                    phoneNumber = "", // Phone not provided in DriverDetailsDto
                    profilePhotoUrl = null,
                    rating = driverDto.rating,
                    vehicleDetails = VehicleDetails(
                        make = driverDto.vehicleMake,
                        model = driverDto.vehicleModel,
                        year = driverDto.vehicleYear,
                        color = driverDto.vehicleColor,
                        licensePlate = driverDto.licensePlate,
                        vehicleType = VehicleType.valueOf(driverDto.vehicleType.uppercase())
                    )
                )
            }
        )
    }
    
    /**
     * Maps Ride domain model to RideEntity for database storage
     */
    private fun mapRideToEntity(ride: Ride): RideEntity {
        return RideEntity(
            id = ride.id,
            riderId = ride.riderId,
            driverId = ride.driverId,
            pickupLatitude = ride.pickupLocation.latitude,
            pickupLongitude = ride.pickupLocation.longitude,
            pickupAddress = ride.pickupLocation.address,
            dropoffLatitude = ride.dropoffLocation.latitude,
            dropoffLongitude = ride.dropoffLocation.longitude,
            dropoffAddress = ride.dropoffLocation.address,
            status = ride.status.name,
            fare = ride.fare,
            distance = ride.distance,
            duration = ride.duration,
            requestedAt = ride.requestedAt,
            acceptedAt = ride.acceptedAt,
            startedAt = ride.startedAt,
            completedAt = ride.completedAt,
            cancelledAt = ride.cancelledAt,
            cancellationReason = ride.cancellationReason
        )
    }
    
    /**
     * Maps RideEntity from database to Ride domain model
     */
    private fun mapEntityToRide(entity: RideEntity): Ride {
        return Ride(
            id = entity.id,
            riderId = entity.riderId,
            driverId = entity.driverId,
            pickupLocation = Location(
                latitude = entity.pickupLatitude,
                longitude = entity.pickupLongitude,
                address = entity.pickupAddress,
                placeId = null
            ),
            dropoffLocation = Location(
                latitude = entity.dropoffLatitude,
                longitude = entity.dropoffLongitude,
                address = entity.dropoffAddress,
                placeId = null
            ),
            status = RideStatus.valueOf(entity.status),
            fare = entity.fare,
            distance = entity.distance,
            duration = entity.duration,
            requestedAt = entity.requestedAt,
            acceptedAt = entity.acceptedAt,
            startedAt = entity.startedAt,
            completedAt = entity.completedAt,
            cancelledAt = entity.cancelledAt,
            cancellationReason = entity.cancellationReason,
            driverDetails = null // Driver details not stored in entity
        )
    }
}
