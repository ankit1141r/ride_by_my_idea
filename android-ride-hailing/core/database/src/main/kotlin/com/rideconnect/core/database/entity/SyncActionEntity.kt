package com.rideconnect.core.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entity representing a sync action to be performed when network is available
 */
@Entity(tableName = "sync_actions")
data class SyncActionEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val type: String, // SyncActionType enum value
    val data: String, // JSON serialized action data
    val timestamp: Long,
    val retryCount: Int = 0,
    val status: String // SyncStatus enum value
)
