package com.rideconnect.core.data.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.data.mapper.PaymentMapper
import com.rideconnect.core.data.network.safeApiCall
import com.rideconnect.core.database.dao.TransactionDao
import com.rideconnect.core.database.entity.TransactionEntity
import com.rideconnect.core.domain.model.PaymentRequest
import com.rideconnect.core.domain.model.Receipt
import com.rideconnect.core.domain.model.Transaction
import com.rideconnect.core.domain.repository.PaymentRepository
import com.rideconnect.core.network.api.PaymentApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Implementation of PaymentRepository.
 * Requirements: 7.2, 7.3, 7.5, 7.6
 */
@Singleton
class PaymentRepositoryImpl @Inject constructor(
    private val paymentApi: PaymentApi,
    private val transactionDao: TransactionDao
) : PaymentRepository {
    
    /**
     * Process a payment for a ride.
     * Requirements: 7.2
     */
    override suspend fun processPayment(request: PaymentRequest): Result<Transaction> {
        return when (val result = safeApiCall { paymentApi.processPayment(PaymentMapper.toDto(request)) }) {
            is Result.Success -> {
                val transaction = PaymentMapper.toTransaction(result.data)
                // Store transaction in local database
                transactionDao.insertTransaction(PaymentMapper.toEntity(transaction))
                Result.Success(transaction)
            }
            is Result.Error -> Result.Error(result.exception)
        }
    }
    
    /**
     * Get payment history with pagination.
     * Requirements: 7.5
     */
    override suspend fun getPaymentHistory(page: Int, pageSize: Int): Result<List<Transaction>> {
        return when (val result = safeApiCall { paymentApi.getPaymentHistory(page, pageSize) }) {
            is Result.Success -> {
                val transactions = result.data.map { PaymentMapper.toTransaction(it) }
                // Store transactions in local database
                transactions.forEach { transaction ->
                    transactionDao.insertTransaction(PaymentMapper.toEntity(transaction))
                }
                Result.Success(transactions)
            }
            is Result.Error -> Result.Error(result.exception)
        }
    }
    
    /**
     * Get receipt for a transaction.
     * Requirements: 7.3, 7.6
     */
    override suspend fun getReceipt(transactionId: String): Result<Receipt> {
        return when (val result = safeApiCall { paymentApi.getReceipt(transactionId) }) {
            is Result.Success -> Result.Success(PaymentMapper.toReceipt(result.data))
            is Result.Error -> Result.Error(result.exception)
        }
    }
    
    /**
     * Observe payment history from local database.
     * Requirements: 7.5
     */
    override fun observePaymentHistory(): Flow<List<Transaction>> {
        // Get current user ID (would come from auth repository)
        val userId = "current_user_id" // TODO: Get from AuthRepository
        
        return transactionDao.getTransactionHistory(userId)
            .map { entities ->
                entities.map { it.toTransaction() }
            }
    }
}

/**
 * Extension function to convert Transaction to TransactionEntity
 */
private fun Transaction.toEntity(): TransactionEntity {
    return TransactionEntity(
        id = id,
        rideId = rideId,
        amount = amount,
        paymentMethod = paymentMethod.name,
        status = status.name,
        transactionId = transactionId,
        createdAt = createdAt,
        completedAt = completedAt
    )
}

/**
 * Extension function to convert TransactionEntity to Transaction
 */
private fun TransactionEntity.toTransaction(): Transaction {
    return Transaction(
        id = id,
        rideId = rideId,
        amount = amount,
        paymentMethod = com.rideconnect.core.domain.model.PaymentMethod.fromString(paymentMethod),
        status = com.rideconnect.core.domain.model.TransactionStatus.fromString(status),
        transactionId = transactionId,
        createdAt = createdAt,
        completedAt = completedAt
    )
}
