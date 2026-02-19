package com.rideconnect.core.database.dao

import androidx.room.*
import com.rideconnect.core.database.entity.ChatMessageEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ChatMessageDao {
    @Query("SELECT * FROM chat_messages WHERE ride_id = :rideId ORDER BY timestamp ASC")
    fun getMessages(rideId: String): Flow<List<ChatMessageEntity>>
    
    @Query("SELECT * FROM chat_messages WHERE id = :messageId")
    suspend fun getMessageById(messageId: String): ChatMessageEntity?
    
    @Query("SELECT COUNT(*) FROM chat_messages WHERE ride_id = :rideId AND status != 'READ' AND sender_id != :currentUserId")
    fun getUnreadMessageCount(rideId: String, currentUserId: String): Flow<Int>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMessage(message: ChatMessageEntity)
    
    @Update
    suspend fun updateMessage(message: ChatMessageEntity)
    
    @Query("UPDATE chat_messages SET status = :status WHERE id = :messageId")
    suspend fun updateMessageStatus(messageId: String, status: String)
    
    @Query("UPDATE chat_messages SET status = :status WHERE ride_id = :rideId AND sender_id != :currentUserId")
    suspend fun markAllMessagesAsRead(rideId: String, currentUserId: String, status: String = "READ")
    
    @Query("DELETE FROM chat_messages WHERE ride_id = :rideId")
    suspend fun deleteMessagesByRideId(rideId: String)
    
    @Query("DELETE FROM chat_messages")
    suspend fun deleteAllMessages()
}
