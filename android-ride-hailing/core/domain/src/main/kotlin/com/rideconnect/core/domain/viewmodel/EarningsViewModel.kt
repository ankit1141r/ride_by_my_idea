package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.EarningsData
import com.rideconnect.core.domain.model.EarningsPeriod
import com.rideconnect.core.domain.model.EarningsRequest
import com.rideconnect.core.domain.repository.EarningsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.time.LocalDate
import javax.inject.Inject

/**
 * ViewModel for earnings tracking.
 * Requirements: 14.1, 14.2, 14.3, 14.4, 14.6
 */
@HiltViewModel
class EarningsViewModel @Inject constructor(
    private val earningsRepository: EarningsRepository
) : ViewModel() {
    
    private val _selectedPeriod = MutableStateFlow(EarningsPeriod.DAY)
    val selectedPeriod: StateFlow<EarningsPeriod> = _selectedPeriod.asStateFlow()
    
    private val _earningsState = MutableStateFlow<EarningsUiState>(EarningsUiState.Loading)
    val earningsState: StateFlow<EarningsUiState> = _earningsState.asStateFlow()
    
    private val _pendingEarnings = MutableStateFlow(0.0)
    val pendingEarnings: StateFlow<Double> = _pendingEarnings.asStateFlow()
    
    private val driverId = "current_driver_id" // TODO: Get from auth state
    
    init {
        observePendingEarnings()
        loadEarnings(EarningsPeriod.DAY)
    }
    
    /**
     * Load earnings for the selected period.
     * Requirements: 14.2, 14.3, 14.4
     */
    fun loadEarnings(period: EarningsPeriod) {
        viewModelScope.launch {
            _selectedPeriod.value = period
            _earningsState.value = EarningsUiState.Loading
            
            val (startDate, endDate) = getDateRangeForPeriod(period)
            val request = EarningsRequest(startDate, endDate, period)
            
            when (val result = earningsRepository.getEarnings(request)) {
                is Result.Success -> {
                    _earningsState.value = EarningsUiState.Success(result.data)
                }
                is Result.Error -> {
                    // Try to load from local cache
                    earningsRepository.observeEarnings(driverId, period)
                        .catch { e ->
                            _earningsState.value = EarningsUiState.Error(
                                result.message ?: "Failed to load earnings"
                            )
                        }
                        .collect { data ->
                            _earningsState.value = EarningsUiState.Success(data)
                        }
                }
            }
        }
    }
    
    /**
     * Load earnings for a custom date range.
     * Requirements: 14.2
     */
    fun loadEarningsForDateRange(startDate: LocalDate, endDate: LocalDate) {
        viewModelScope.launch {
            _selectedPeriod.value = EarningsPeriod.CUSTOM
            _earningsState.value = EarningsUiState.Loading
            
            val request = EarningsRequest(startDate, endDate, EarningsPeriod.CUSTOM)
            
            when (val result = earningsRepository.getEarnings(request)) {
                is Result.Success -> {
                    _earningsState.value = EarningsUiState.Success(result.data)
                }
                is Result.Error -> {
                    _earningsState.value = EarningsUiState.Error(
                        result.message ?: "Failed to load earnings"
                    )
                }
            }
        }
    }
    
    /**
     * Refresh earnings data from backend.
     * Requirements: 14.7
     */
    fun refreshEarnings() {
        loadEarnings(_selectedPeriod.value)
    }
    
    /**
     * Sync earnings with backend.
     * Requirements: 14.7
     */
    fun syncEarnings() {
        viewModelScope.launch {
            earningsRepository.syncEarnings(driverId)
        }
    }
    
    /**
     * Observe pending earnings.
     * Requirements: 14.6
     */
    private fun observePendingEarnings() {
        viewModelScope.launch {
            earningsRepository.observePendingEarnings(driverId)
                .collect { pending ->
                    _pendingEarnings.value = pending
                }
        }
    }
    
    /**
     * Calculate statistics from earnings data.
     * Requirements: 14.3, 14.4
     */
    fun getStatistics(): EarningsStatistics? {
        val state = _earningsState.value
        if (state !is EarningsUiState.Success) return null
        
        val data = state.data
        return EarningsStatistics(
            totalEarnings = data.totalEarnings,
            totalRides = data.totalRides,
            averageFare = data.averageFare,
            pendingEarnings = data.pendingEarnings,
            highestFare = data.rides.maxOfOrNull { it.fare } ?: 0.0,
            lowestFare = data.rides.minOfOrNull { it.fare } ?: 0.0
        )
    }
    
    private fun getDateRangeForPeriod(period: EarningsPeriod): Pair<LocalDate, LocalDate> {
        val today = LocalDate.now()
        return when (period) {
            EarningsPeriod.DAY -> today to today
            EarningsPeriod.WEEK -> today.minusDays(6) to today
            EarningsPeriod.MONTH -> today.minusDays(29) to today
            EarningsPeriod.CUSTOM -> today to today
        }
    }
}

/**
 * UI state for earnings screen.
 */
sealed class EarningsUiState {
    object Loading : EarningsUiState()
    data class Success(val data: EarningsData) : EarningsUiState()
    data class Error(val message: String) : EarningsUiState()
}

/**
 * Statistics calculated from earnings data.
 * Requirements: 14.3, 14.4
 */
data class EarningsStatistics(
    val totalEarnings: Double,
    val totalRides: Int,
    val averageFare: Double,
    val pendingEarnings: Double,
    val highestFare: Double,
    val lowestFare: Double
)
