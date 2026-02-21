# Core Database Module

## Overview

The Database module provides local data persistence using Room. It stores user data, ride history, messages, and other information for offline access and caching.

## Architecture

- **Entities**: Room database tables
- **DAOs**: Data Access Objects for database operations
- **Database**: Room database configuration
- **Migrations**: Database schema migrations

## Key Components

### Database (`AppDatabase.kt`)

Room database with all entities and DAOs:

```kotlin
@Database(
    entities = [
        RideEntity::class,
        ScheduledRideEntity::class,
        ChatMessageEntity::class,
        ParcelDeliveryEntity::class,
        RatingEntity::class,
        // ... other entities
    ],
    version = 1,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun rideDao(): RideDao
    abstract fun chatMessageDao(): ChatMessageDao
    abstract fun ratingDao(): RatingDao
    abstract fun earningsDao(): EarningsDao
    abstract fun syncActionDao(): SyncActionDao
}
```

### Entities (`entity/`)

Room entities representing database tables:

- `RideEntity`: Ride information with status, locations, fare
- `ScheduledRideEntity`: Scheduled rides with pickup time
- `ChatMessageEntity`: In-ride chat messages
- `ParcelDeliveryEntity`: Parcel delivery details
- `RatingEntity`: Ratings and reviews
- `EarningsEntity`: Driver earnings records
- `SyncActionEntity`: Queued offline actions

### DAOs (`dao/`)

Data Access Objects for database operations:

- `RideDao`: CRUD operations for rides
- `ChatMessageDao`: Message storage and retrieval
- `RatingDao`: Rating operations
- `EarningsDao`: Earnings queries with date filtering
- `SyncActionDao`: Offline action queue management

## Database Schema

### RideEntity
```kotlin
@Entity(tableName = "rides")
data class RideEntity(
    @PrimaryKey val id: String,
    val status: String,
    val pickupLatitude: Double,
    val pickupLongitude: Double,
    val pickupAddress: String,
    val dropoffLatitude: Double,
    val dropoffLongitude: Double,
    val dropoffAddress: String,
    val fare: Double,
    val driverId: String?,
    val driverName: String?,
    val vehicleNumber: String?,
    val createdAt: Long,
    val updatedAt: Long
)
```

### Indices and Foreign Keys

Entities use indices for efficient queries:
```kotlin
@Entity(
    tableName = "chat_messages",
    indices = [Index(value = ["rideId", "timestamp"])]
)
```

## Usage Example

### Insert Data
```kotlin
@Dao
interface RideDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertRide(ride: RideEntity)
    
    @Query("SELECT * FROM rides WHERE id = :rideId")
    suspend fun getRideById(rideId: String): RideEntity?
    
    @Query("SELECT * FROM rides ORDER BY createdAt DESC")
    fun getAllRidesFlow(): Flow<List<RideEntity>>
}
```

### Query with Flow
```kotlin
// In Repository
override fun getRideHistory(): Flow<Result<List<Ride>>> = flow {
    rideDao.getAllRidesFlow()
        .map { entities -> entities.map { it.toDomainModel() } }
        .collect { rides ->
            emit(Result.Success(rides))
        }
}
```

## Migrations

Database migrations handle schema changes:

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL(
            "ALTER TABLE rides ADD COLUMN rating REAL DEFAULT 0.0 NOT NULL"
        )
    }
}
```

## Offline Support

The database enables offline functionality:

1. **Caching**: Store API responses for offline access
2. **Queueing**: Store actions to sync when online
3. **Reactive Updates**: Use Flow for real-time UI updates

### Sync Queue

`SyncActionEntity` stores offline actions:
```kotlin
@Entity(tableName = "sync_actions")
data class SyncActionEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val actionType: String,  // "RATE_RIDE", "SEND_MESSAGE", etc.
    val payload: String,     // JSON payload
    val timestamp: Long,
    val retryCount: Int = 0
)
```

## Testing

In-memory database for testing:
```kotlin
@Before
fun setup() {
    database = Room.inMemoryDatabaseBuilder(
        context,
        AppDatabase::class.java
    ).build()
    
    rideDao = database.rideDao()
}

@Test
fun `test insert and retrieve ride`() = runTest {
    val ride = RideEntity(...)
    rideDao.insertRide(ride)
    
    val retrieved = rideDao.getRideById(ride.id)
    assertEquals(ride, retrieved)
}
```

## Dependencies

- Room 2.6.1
- Kotlin Coroutines & Flow
- Hilt for dependency injection

## Best Practices

1. **Use Flow for reactive queries**: Automatically update UI when data changes
2. **Use suspend functions**: All database operations are asynchronous
3. **Handle conflicts**: Use `OnConflictStrategy.REPLACE` for upserts
4. **Index frequently queried columns**: Improve query performance
5. **Export schema**: Enable schema validation and migrations
