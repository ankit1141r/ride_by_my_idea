package com.rideconnect.core.database.dao

import androidx.room.*
import com.rideconnect.core.database.entity.TransactionEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface TransactionDao {
    @Query("SELECT * FROM transactions WHERE ride_id IN (SELECT id FROM rides WHERE rider_id = :userId) ORDER BY created_at DESC")
    fun getTransactionHistory(userId: String): Flow<List<TransactionEntity>>
    
    @Query("SELECT * FROM transactions WHERE id = :transactionId")
    suspend fun getTransactionById(transactionId: String): TransactionEntity?
    
    @Query("SELECT * FROM transactions WHERE ride_id = :rideId")
    suspend fun getTransactionByRideId(rideId: String): TransactionEntity?
    
    @Query("SELECT * FROM transactions WHERE ride_id = :rideId")
    fun observeTransactionByRideId(rideId: String): Flow<TransactionEntity?>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTransaction(transaction: TransactionEntity)
    
    @Update
    suspend fun updateTransaction(transaction: TransactionEntity)
    
    @Query("DELETE FROM transactions WHERE id = :transactionId")
    suspend fun deleteTransaction(transactionId: String)
    
    @Query("DELETE FROM transactions")
    suspend fun deleteAllTransactions()
}
