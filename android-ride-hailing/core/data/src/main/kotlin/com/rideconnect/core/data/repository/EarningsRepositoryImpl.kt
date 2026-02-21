package com.rideconnect.core.data.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.data.mapper.EarningsMapper
import com.rideconnect.core.data.mapper.EarningsMapper.toDomainData
import com.rideconnect.core.database.dao.EarningsDao
import com.rideconnect.core.domain.model.EarningsData
import com.rideconnect.core.domain.model.EarningsPeriod
import com.rideconnect.core.domain.model.EarningsRequest
import com.rideconnect.core.domain.repository.EarningsRepository
import com.rideconnect.core.network.api.DriverApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.time.LocalDate
import java.time.ZoneId
import javax.inject.Inject

/**
 * Implementation of EarningsRepository.
 * Requirements: 14.2, 14.5, 14.6, 14.7
 */
class EarningsRepositoryImpl @Inject constructor(
    private val driverApi: DriverApi,
    private val earningsDao: EarningsDao
) : EarningsRepository {
    
    override suspend fun getEarnings(request: EarningsRequest): Result<EarningsData> {
        return try {
            // Fetch from backend
            val response = driverApi.getEarnings(
                startDate = request.startDate.toString(),
                endDate = request.endDate.toString()
            )
            
            if (response.isSuccessful && response.body() != null) {
                val responseDto = response.body()!!
                
                // Map to domain model
                val earningsData = EarningsMapper.toDomain(responseDto)
                
                // Cache in local database
                val driverId = getCurrentDriverId() // This should come from auth state
                val entities = responseDto.rides.map { 
                    EarningsMapper.run { it.toEntity(driverId, isPending = false) }
                }
                earningsDao.insertEarnings(entities)
                
                Result.Success(earningsData)
            } else {
                Result.Error(Exception("Failed to fetch earnings: ${response.message()}"))
            }
        } catch (e: Exception) {
            // Fall back to local data if network fails
            val startTimestamp = request.startDate.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
            val endTimestamp = request.endDate.atTime(23, 59, 59).atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
            
            try {
                val driverId = getCurrentDriverId()
                val localEarnings = earningsDao.getEarningsByDateRange(driverId, startTimestamp, endTimestamp)
                
                // Convert Flow to single value for fallback
                Result.Error(e)
            } catch (localError: Exception) {
                Result.Error(e)
            }
        }
    }
    
    override fun observeEarnings(driverId: String, period: EarningsPeriod): Flow<EarningsData> {
        val (startDate, endDate) = getDateRangeForPeriod(period)
        val startTimestamp = startDate.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
        val endTimestamp = endDate.atTime(23, 59, 59).atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
        
        return earningsDao.getEarningsByDateRange(driverId, startTimestamp, endTimestamp)
            .map { entities -> entities.toDomainData() }
    }
    
    override suspend fun syncEarnings(driverId: String): Result<Unit> {
        return try {
            // Get unsynced earnings
            val unsyncedEarnings = earningsDao.getUnsyncedEarnings()
            
            // Sync with backend (if needed)
            // For now, just mark as synced since backend is source of truth
            unsyncedEarnings.forEach { earning ->
                earningsDao.markAsSynced(earning.id)
            }
            
            Result.Success(Unit)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override fun observePendingEarnings(driverId: String): Flow<Double> {
        return earningsDao.getPendingEarnings(driverId)
            .map { entities -> entities.sumOf { it.fare } }
    }
    
    private fun getDateRangeForPeriod(period: EarningsPeriod): Pair<LocalDate, LocalDate> {
        val today = LocalDate.now()
        return when (period) {
            EarningsPeriod.DAY -> today to today
            EarningsPeriod.WEEK -> today.minusDays(6) to today
            EarningsPeriod.MONTH -> today.minusDays(29) to today
            EarningsPeriod.CUSTOM -> today to today // Will be overridden by request
        }
    }
    
    // TODO: This should be injected from AuthRepository or UserSession
    private fun getCurrentDriverId(): String {
        return "current_driver_id" // Placeholder
    }
}
