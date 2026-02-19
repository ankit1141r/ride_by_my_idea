package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.AverageRating
import com.rideconnect.core.domain.model.Rating
import com.rideconnect.core.domain.model.RatingRequest
import com.rideconnect.core.domain.repository.RatingRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for rating operations.
 * Requirements: 8.1, 8.3, 8.6, 8.7
 */
@HiltViewModel
class RatingViewModel @Inject constructor(
    private val ratingRepository: RatingRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(RatingUiState())
    val uiState: StateFlow<RatingUiState> = _uiState.asStateFlow()
    
    init {
        loadAverageRating()
    }
    
    /**
     * Submit a rating for a ride.
     * Requirements: 8.1, 8.3
     */
    fun submitRating(rideId: String, rating: Int, review: String? = null) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSubmitting = true, error = null) }
            
            try {
                val request = RatingRequest(
                    rideId = rideId,
                    rating = rating,
                    review = review
                )
                
                when (val result = ratingRepository.submitRating(request)) {
                    is Result.Success -> {
                        _uiState.update { 
                            it.copy(
                                isSubmitting = false,
                                submitSuccess = true,
                                error = null
                            )
                        }
                        // Reload average rating after submission
                        loadAverageRating()
                    }
                    is Result.Error -> {
                        // Queue for offline sync if network error
                        queueRatingForSync(request)
                        _uiState.update { 
                            it.copy(
                                isSubmitting = false,
                                submitSuccess = false,
                                error = result.exception.message ?: "Failed to submit rating"
                            )
                        }
                    }
                }
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        isSubmitting = false,
                        submitSuccess = false,
                        error = e.message ?: "Invalid rating data"
                    )
                }
            }
        }
    }
    
    /**
     * Load ratings for a user.
     * Requirements: 8.5, 8.6
     */
    fun loadRatings(userId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingRatings = true, error = null) }
            
            when (val result = ratingRepository.getRatings(userId)) {
                is Result.Success -> {
                    _uiState.update { 
                        it.copy(
                            isLoadingRatings = false,
                            ratings = result.data,
                            error = null
                        )
                    }
                }
                is Result.Error -> {
                    _uiState.update { 
                        it.copy(
                            isLoadingRatings = false,
                            error = result.exception.message ?: "Failed to load ratings"
                        )
                    }
                }
            }
        }
    }
    
    /**
     * Load average rating for current user.
     * Requirements: 8.5, 8.6
     */
    fun loadAverageRating(userId: String = "current_user_id") {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingAverage = true) }
            
            when (val result = ratingRepository.getAverageRating(userId)) {
                is Result.Success -> {
                    _uiState.update { 
                        it.copy(
                            isLoadingAverage = false,
                            averageRating = result.data,
                            error = null
                        )
                    }
                }
                is Result.Error -> {
                    _uiState.update { 
                        it.copy(
                            isLoadingAverage = false,
                            error = result.exception.message ?: "Failed to load average rating"
                        )
                    }
                }
            }
        }
    }
    
    /**
     * Observe ratings from local database.
     * Requirements: 8.6
     */
    fun observeRatings(userId: String) {
        viewModelScope.launch {
            ratingRepository.observeRatings(userId).collect { ratings ->
                _uiState.update { it.copy(ratings = ratings) }
            }
        }
    }
    
    /**
     * Queue rating for offline sync.
     * Requirements: 8.7
     */
    private fun queueRatingForSync(request: RatingRequest) {
        viewModelScope.launch {
            ratingRepository.queueRatingForSync(request)
            _uiState.update { 
                it.copy(
                    submitSuccess = true,
                    error = "Rating queued for sync when online"
                )
            }
        }
    }
    
    /**
     * Sync pending ratings.
     * Requirements: 8.7
     */
    fun syncPendingRatings() {
        viewModelScope.launch {
            val pendingRatings = ratingRepository.getPendingRatings()
            pendingRatings.forEach { request ->
                ratingRepository.submitRating(request)
            }
        }
    }
    
    /**
     * Clear submit success state.
     */
    fun clearSubmitSuccess() {
        _uiState.update { it.copy(submitSuccess = false) }
    }
    
    /**
     * Clear error state.
     */
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}

/**
 * UI state for rating operations.
 */
data class RatingUiState(
    val isSubmitting: Boolean = false,
    val isLoadingRatings: Boolean = false,
    val isLoadingAverage: Boolean = false,
    val submitSuccess: Boolean = false,
    val ratings: List<Rating> = emptyList(),
    val averageRating: AverageRating? = null,
    val error: String? = null
)
