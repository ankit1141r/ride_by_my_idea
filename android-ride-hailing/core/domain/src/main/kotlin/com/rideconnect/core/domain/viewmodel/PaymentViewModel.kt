package com.rideconnect.core.domain.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.PaymentMethod
import com.rideconnect.core.domain.model.PaymentRequest
import com.rideconnect.core.domain.model.Receipt
import com.rideconnect.core.domain.model.Transaction
import com.rideconnect.core.domain.repository.PaymentRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for payment operations.
 * Requirements: 7.2, 7.3, 7.4, 7.5
 */
@HiltViewModel
class PaymentViewModel @Inject constructor(
    private val paymentRepository: PaymentRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(PaymentUiState())
    val uiState: StateFlow<PaymentUiState> = _uiState.asStateFlow()
    
    init {
        loadPaymentHistory()
        observePaymentHistory()
    }
    
    /**
     * Process a payment for a ride.
     * Requirements: 7.2
     */
    fun processPayment(rideId: String, amount: Double, paymentMethod: PaymentMethod = PaymentMethod.RAZORPAY) {
        viewModelScope.launch {
            _uiState.update { it.copy(isProcessing = true, error = null) }
            
            val request = PaymentRequest(
                rideId = rideId,
                amount = amount,
                paymentMethod = paymentMethod
            )
            
            when (val result = paymentRepository.processPayment(request)) {
                is Result.Success -> {
                    _uiState.update { 
                        it.copy(
                            isProcessing = false,
                            currentTransaction = result.data,
                            paymentSuccess = true,
                            error = null
                        )
                    }
                }
                is Result.Error -> {
                    _uiState.update { 
                        it.copy(
                            isProcessing = false,
                            paymentSuccess = false,
                            error = result.exception.message ?: "Payment failed"
                        )
                    }
                }
            }
        }
    }
    
    /**
     * Get receipt for a transaction.
     * Requirements: 7.3, 7.6
     */
    fun getReceipt(transactionId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingReceipt = true, error = null) }
            
            when (val result = paymentRepository.getReceipt(transactionId)) {
                is Result.Success -> {
                    _uiState.update { 
                        it.copy(
                            isLoadingReceipt = false,
                            currentReceipt = result.data,
                            error = null
                        )
                    }
                }
                is Result.Error -> {
                    _uiState.update { 
                        it.copy(
                            isLoadingReceipt = false,
                            error = result.exception.message ?: "Failed to load receipt"
                        )
                    }
                }
            }
        }
    }
    
    /**
     * Load payment history with pagination.
     * Requirements: 7.5
     */
    fun loadPaymentHistory(page: Int = 0, pageSize: Int = 20) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoadingHistory = true, error = null) }
            
            when (val result = paymentRepository.getPaymentHistory(page, pageSize)) {
                is Result.Success -> {
                    _uiState.update { 
                        it.copy(
                            isLoadingHistory = false,
                            paymentHistory = result.data,
                            error = null
                        )
                    }
                }
                is Result.Error -> {
                    _uiState.update { 
                        it.copy(
                            isLoadingHistory = false,
                            error = result.exception.message ?: "Failed to load payment history"
                        )
                    }
                }
            }
        }
    }
    
    /**
     * Observe payment history from local database.
     * Requirements: 7.5
     */
    private fun observePaymentHistory() {
        viewModelScope.launch {
            paymentRepository.observePaymentHistory().collect { transactions ->
                _uiState.update { it.copy(paymentHistory = transactions) }
            }
        }
    }
    
    /**
     * Clear payment success state.
     */
    fun clearPaymentSuccess() {
        _uiState.update { it.copy(paymentSuccess = false) }
    }
    
    /**
     * Clear error state.
     */
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}

/**
 * UI state for payment operations.
 */
data class PaymentUiState(
    val isProcessing: Boolean = false,
    val isLoadingReceipt: Boolean = false,
    val isLoadingHistory: Boolean = false,
    val currentTransaction: Transaction? = null,
    val currentReceipt: Receipt? = null,
    val paymentHistory: List<Transaction> = emptyList(),
    val paymentSuccess: Boolean = false,
    val error: String? = null
)
