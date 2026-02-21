package com.rideconnect.core.data.mapper

import com.rideconnect.core.database.entity.EarningsEntity
import com.rideconnect.core.domain.model.EarningsData
import com.rideconnect.core.domain.model.EarningsRide
import com.rideconnect.core.network.dto.EarningsResponseDto
import com.rideconnect.core.network.dto.EarningsRideDto
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneId

/**
 * Mapper for earnings data between layers.
 * Requirements: 14.1, 14.2, 14.5, 14.6
 */
object EarningsMapper {
    
    fun toDomain(dto: EarningsResponseDto): EarningsData {
        val rides = dto.rides.map { it.toDomain() }
        
        // Calculate period-specific earnings
        val today = LocalDate.now()
        val todayEarnings = rides.filter { it.date.toLocalDate() == today }.sumOf { it.fare }
        val weekStart = today.minusDays(6)
        val weekEarnings = rides.filter { it.date.toLocalDate() >= weekStart }.sumOf { it.fare }
        val monthStart = today.minusDays(29)
        val monthEarnings = rides.filter { it.date.toLocalDate() >= monthStart }.sumOf { it.fare }
        
        return EarningsData(
            totalEarnings = dto.totalEarnings,
            todayEarnings = todayEarnings,
            weekEarnings = weekEarnings,
            monthEarnings = monthEarnings,
            totalRides = dto.totalRides,
            averageFare = dto.averageFare,
            pendingEarnings = dto.pendingEarnings,
            rides = rides
        )
    }
    
    fun EarningsRideDto.toDomain(): EarningsRide {
        val localDate = LocalDate.parse(date)
        val localDateTime = localDate.atStartOfDay()
        
        return EarningsRide(
            rideId = rideId,
            date = localDateTime,
            fare = fare,
            pickupAddress = pickupAddress,
            dropoffAddress = dropoffAddress,
            distance = distance,
            duration = duration
        )
    }
    
    fun EarningsEntity.toDomain(): EarningsRide {
        return EarningsRide(
            rideId = rideId,
            date = Instant.ofEpochMilli(date).atZone(ZoneId.systemDefault()).toLocalDateTime(),
            fare = fare,
            pickupAddress = pickupAddress,
            dropoffAddress = dropoffAddress,
            distance = distance,
            duration = duration
        )
    }
    
    fun EarningsRideDto.toEntity(driverId: String, isPending: Boolean = true): EarningsEntity {
        val localDate = LocalDate.parse(date)
        val timestamp = localDate.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
        
        return EarningsEntity(
            id = rideId,
            driverId = driverId,
            rideId = rideId,
            date = timestamp,
            fare = fare,
            pickupAddress = pickupAddress,
            dropoffAddress = dropoffAddress,
            distance = distance,
            duration = duration,
            isPending = isPending,
            synced = true
        )
    }
    
    fun List<EarningsEntity>.toDomainData(): EarningsData {
        val rides = this.map { it.toDomain() }
        val totalEarnings = this.sumOf { it.fare }
        val totalRides = this.size
        val averageFare = if (totalRides > 0) totalEarnings / totalRides else 0.0
        val pendingEarnings = this.filter { it.isPending }.sumOf { it.fare }
        
        // Calculate period-specific earnings
        val today = LocalDate.now()
        val todayEarnings = rides.filter { it.date.toLocalDate() == today }.sumOf { it.fare }
        val weekStart = today.minusDays(6)
        val weekEarnings = rides.filter { it.date.toLocalDate() >= weekStart }.sumOf { it.fare }
        val monthStart = today.minusDays(29)
        val monthEarnings = rides.filter { it.date.toLocalDate() >= monthStart }.sumOf { it.fare }
        
        return EarningsData(
            totalEarnings = totalEarnings,
            todayEarnings = todayEarnings,
            weekEarnings = weekEarnings,
            monthEarnings = monthEarnings,
            totalRides = totalRides,
            averageFare = averageFare,
            pendingEarnings = pendingEarnings,
            rides = rides
        )
    }
}
