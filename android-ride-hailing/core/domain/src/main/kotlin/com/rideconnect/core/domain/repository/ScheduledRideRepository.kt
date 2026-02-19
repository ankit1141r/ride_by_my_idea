package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.ScheduledRide
import com.rideconnect.core.domain.model.ScheduledRideRequest
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for scheduled ride operations.
 * 
 * Requirements: 4.4, 4.6, 4.7
 */
interface ScheduledRideRepository {
    
    /**
     * Schedule a ride for a future time.
     * Requirements: 4.1, 4.4
     */
    suspend fun scheduleRide(request: ScheduledRideRequest): Result<ScheduledRide>
    
    /**
     * Cancel a scheduled ride.
     * Requirements: 4.6
     */
    suspend fun cancelScheduledRide(rideId: String, reason: String): Result<Unit>
    
    /**
     * Get all scheduled rides for the current user.
     * Requirements: 4.7
     */
    suspend fun getScheduledRides(page: Int = 0, pageSize: Int = 20): Result<List<ScheduledRide>>
    
    /**
     * Get details of a specific scheduled ride.
     * Requirements: 4.7
     */
    suspend fun getScheduledRideDetails(rideId: String): Result<ScheduledRide>
    
    /**
     * Observe scheduled rides from local database.
     * Requirements: 4.7
     */
    fun observeScheduledRides(): Flow<List<ScheduledRide>>
}
