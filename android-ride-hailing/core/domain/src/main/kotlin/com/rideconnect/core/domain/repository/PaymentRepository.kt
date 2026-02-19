package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.PaymentRequest
import com.rideconnect.core.domain.model.Receipt
import com.rideconnect.core.domain.model.Transaction
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for payment operations.
 * Requirements: 7.2, 7.3, 7.5, 7.6
 */
interface PaymentRepository {
    
    /**
     * Process a payment for a ride.
     * Requirements: 7.2
     */
    suspend fun processPayment(request: PaymentRequest): Result<Transaction>
    
    /**
     * Get payment history with pagination.
     * Requirements: 7.5
     */
    suspend fun getPaymentHistory(page: Int, pageSize: Int): Result<List<Transaction>>
    
    /**
     * Get receipt for a transaction.
     * Requirements: 7.3, 7.6
     */
    suspend fun getReceipt(transactionId: String): Result<Receipt>
    
    /**
     * Observe payment history from local database.
     * Requirements: 7.5
     */
    fun observePaymentHistory(): Flow<List<Transaction>>
}
