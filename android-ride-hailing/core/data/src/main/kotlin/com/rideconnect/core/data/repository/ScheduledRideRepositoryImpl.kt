package com.rideconnect.core.data.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.database.dao.ScheduledRideDao
import com.rideconnect.core.database.entity.ScheduledRideEntity
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.ScheduledRide
import com.rideconnect.core.domain.model.ScheduledRideRequest
import com.rideconnect.core.domain.model.ScheduledRideStatus
import com.rideconnect.core.domain.repository.ScheduledRideRepository
import com.rideconnect.core.data.worker.ScheduledRideReminderManager
import com.rideconnect.core.network.api.ScheduledRideApi
import com.rideconnect.core.network.dto.CancelScheduledRideRequestDto
import com.rideconnect.core.network.dto.LocationDto
import com.rideconnect.core.network.dto.ScheduledRideRequestDto
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject

/**
 * Implementation of ScheduledRideRepository.
 * 
 * Requirements: 4.4, 4.5, 4.6, 4.7
 */
class ScheduledRideRepositoryImpl @Inject constructor(
    private val scheduledRideApi: ScheduledRideApi,
    private val scheduledRideDao: ScheduledRideDao,
    private val reminderManager: ScheduledRideReminderManager
) : ScheduledRideRepository {
    
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply {
        timeZone = TimeZone.getTimeZone("UTC")
    }
    
    override suspend fun scheduleRide(request: ScheduledRideRequest): Result<ScheduledRide> {
        return try {
            val requestDto = ScheduledRideRequestDto(
                pickupLocation = request.pickupLocation.toDto(),
                dropoffLocation = request.dropoffLocation.toDto(),
                scheduledTime = dateFormat.format(Date(request.scheduledTime))
            )
            
            val response = scheduledRideApi.scheduleRide(requestDto)
            
            if (response.isSuccessful && response.body() != null) {
                val scheduledRide = response.body()!!.toDomain()
                
                // Store in local database
                scheduledRideDao.insertScheduledRide(scheduledRide.toEntity())
                
                // Schedule reminder notification (Requirement 4.5)
                reminderManager.scheduleReminder(scheduledRide)
                
                Result.Success(scheduledRide)
            } else {
                Result.Error(Exception("Failed to schedule ride: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun cancelScheduledRide(rideId: String, reason: String): Result<Unit> {
        return try {
            val requestDto = CancelScheduledRideRequestDto(reason = reason)
            val response = scheduledRideApi.cancelScheduledRide(rideId, requestDto)
            
            if (response.isSuccessful) {
                // Cancel reminder notification (Requirement 4.6)
                reminderManager.cancelReminder(rideId)
                
                // Update local database
                scheduledRideDao.deleteScheduledRide(rideId)
                Result.Success(Unit)
            } else {
                Result.Error(Exception("Failed to cancel scheduled ride: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun getScheduledRides(page: Int, pageSize: Int): Result<List<ScheduledRide>> {
        return try {
            val response = scheduledRideApi.getScheduledRides(page, pageSize)
            
            if (response.isSuccessful && response.body() != null) {
                val scheduledRides = response.body()!!.map { it.toDomain() }
                
                // Update local database
                scheduledRides.forEach { ride ->
                    scheduledRideDao.insertScheduledRide(ride.toEntity())
                }
                
                Result.Success(scheduledRides)
            } else {
                // Return cached data if API fails
                val cachedRides = scheduledRideDao.getAllScheduledRides()
                    .map { it.toDomain() }
                Result.Success(cachedRides)
            }
        } catch (e: Exception) {
            // Return cached data on error
            try {
                val cachedRides = scheduledRideDao.getAllScheduledRides()
                    .map { it.toDomain() }
                Result.Success(cachedRides)
            } catch (dbError: Exception) {
                Result.Error(e)
            }
        }
    }
    
    override suspend fun getScheduledRideDetails(rideId: String): Result<ScheduledRide> {
        return try {
            val response = scheduledRideApi.getScheduledRideDetails(rideId)
            
            if (response.isSuccessful && response.body() != null) {
                val scheduledRide = response.body()!!.toDomain()
                
                // Update local database
                scheduledRideDao.insertScheduledRide(scheduledRide.toEntity())
                
                Result.Success(scheduledRide)
            } else {
                // Try to get from local database
                val cachedRide = scheduledRideDao.getScheduledRideById(rideId)
                if (cachedRide != null) {
                    Result.Success(cachedRide.toDomain())
                } else {
                    Result.Error(Exception("Scheduled ride not found"))
                }
            }
        } catch (e: Exception) {
            // Try to get from local database
            try {
                val cachedRide = scheduledRideDao.getScheduledRideById(rideId)
                if (cachedRide != null) {
                    Result.Success(cachedRide.toDomain())
                } else {
                    Result.Error(e)
                }
            } catch (dbError: Exception) {
                Result.Error(e)
            }
        }
    }
    
    override fun observeScheduledRides(): Flow<List<ScheduledRide>> {
        return scheduledRideDao.observeScheduledRides().map { entities ->
            entities.map { it.toDomain() }
        }
    }
    
    // Extension functions for mapping
    private fun Location.toDto(): LocationDto {
        return LocationDto(
            latitude = this.latitude,
            longitude = this.longitude,
            address = this.address
        )
    }
    
    private fun com.rideconnect.core.network.dto.ScheduledRideResponseDto.toDomain(): ScheduledRide {
        return ScheduledRide(
            id = this.id,
            riderId = this.riderId,
            pickupLocation = Location(
                latitude = this.pickupLocation.latitude,
                longitude = this.pickupLocation.longitude,
                address = this.pickupLocation.address,
                accuracy = 0f,
                timestamp = System.currentTimeMillis()
            ),
            dropoffLocation = Location(
                latitude = this.dropoffLocation.latitude,
                longitude = this.dropoffLocation.longitude,
                address = this.dropoffLocation.address,
                accuracy = 0f,
                timestamp = System.currentTimeMillis()
            ),
            scheduledTime = try {
                dateFormat.parse(this.scheduledTime)?.time ?: System.currentTimeMillis()
            } catch (e: Exception) {
                System.currentTimeMillis()
            },
            status = when (this.status.uppercase()) {
                "SCHEDULED" -> ScheduledRideStatus.SCHEDULED
                "CONFIRMED" -> ScheduledRideStatus.CONFIRMED
                "IN_PROGRESS" -> ScheduledRideStatus.IN_PROGRESS
                "COMPLETED" -> ScheduledRideStatus.COMPLETED
                "CANCELLED" -> ScheduledRideStatus.CANCELLED
                else -> ScheduledRideStatus.SCHEDULED
            },
            fare = this.fare,
            distance = this.distance,
            createdAt = try {
                dateFormat.parse(this.createdAt)?.time ?: System.currentTimeMillis()
            } catch (e: Exception) {
                System.currentTimeMillis()
            }
        )
    }
    
    private fun ScheduledRide.toEntity(): ScheduledRideEntity {
        return ScheduledRideEntity(
            id = this.id,
            riderId = this.riderId,
            pickupLatitude = this.pickupLocation.latitude,
            pickupLongitude = this.pickupLocation.longitude,
            pickupAddress = this.pickupLocation.address,
            dropoffLatitude = this.dropoffLocation.latitude,
            dropoffLongitude = this.dropoffLocation.longitude,
            dropoffAddress = this.dropoffLocation.address,
            scheduledTime = this.scheduledTime,
            status = this.status.name,
            createdAt = this.createdAt
        )
    }
    
    private fun ScheduledRideEntity.toDomain(): ScheduledRide {
        return ScheduledRide(
            id = this.id,
            riderId = this.riderId,
            pickupLocation = Location(
                latitude = this.pickupLatitude,
                longitude = this.pickupLongitude,
                address = this.pickupAddress,
                accuracy = 0f,
                timestamp = System.currentTimeMillis()
            ),
            dropoffLocation = Location(
                latitude = this.dropoffLatitude,
                longitude = this.dropoffLongitude,
                address = this.dropoffAddress,
                accuracy = 0f,
                timestamp = System.currentTimeMillis()
            ),
            scheduledTime = this.scheduledTime,
            status = ScheduledRideStatus.valueOf(this.status),
            fare = null,
            distance = null,
            createdAt = this.createdAt
        )
    }
}
