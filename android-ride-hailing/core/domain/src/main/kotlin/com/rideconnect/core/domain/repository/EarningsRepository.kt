package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.EarningsData
import com.rideconnect.core.domain.model.EarningsPeriod
import com.rideconnect.core.domain.model.EarningsRequest
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for earnings data operations.
 * Requirements: 14.2, 14.5, 14.6, 14.7
 */
interface EarningsRepository {
    
    /**
     * Get earnings data for a specific date range.
     * Fetches from backend and caches locally.
     * Requirements: 14.2, 14.5
     */
    suspend fun getEarnings(request: EarningsRequest): Result<EarningsData>
    
    /**
     * Observe earnings data from local database.
     * Requirements: 14.6
     */
    fun observeEarnings(driverId: String, period: EarningsPeriod): Flow<EarningsData>
    
    /**
     * Sync earnings data with backend.
     * Requirements: 14.7
     */
    suspend fun syncEarnings(driverId: String): Result<Unit>
    
    /**
     * Get pending earnings from local database.
     * Requirements: 14.6
     */
    fun observePendingEarnings(driverId: String): Flow<Double>
}
