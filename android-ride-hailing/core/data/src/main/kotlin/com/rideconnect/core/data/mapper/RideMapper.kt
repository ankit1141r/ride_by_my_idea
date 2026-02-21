package com.rideconnect.core.data.mapper

import com.rideconnect.core.domain.model.DriverDetails
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.Ride
import com.rideconnect.core.domain.model.RideStatus
import com.rideconnect.core.domain.model.VehicleDetails
import com.rideconnect.core.network.dto.RideResponseDto
import java.time.Instant

object RideMapper {
    
    fun toRide(dto: RideResponseDto): Ride {
        return Ride(
            id = dto.id,
            riderId = dto.riderId,
            driverId = dto.driverId,
            pickupLocation = Location(
                latitude = dto.pickupLatitude,
                longitude = dto.pickupLongitude,
                address = dto.pickupAddress
            ),
            dropoffLocation = Location(
                latitude = dto.dropoffLatitude,
                longitude = dto.dropoffLongitude,
                address = dto.dropoffAddress
            ),
            status = parseRideStatus(dto.status),
            fare = dto.fare,
            distance = dto.distance,
            duration = dto.duration,
            requestedAt = parseTimestamp(dto.requestedAt),
            acceptedAt = dto.acceptedAt?.let { parseTimestamp(it) },
            startedAt = dto.startedAt?.let { parseTimestamp(it) },
            completedAt = dto.completedAt?.let { parseTimestamp(it) },
            cancelledAt = dto.cancelledAt?.let { parseTimestamp(it) },
            cancellationReason = dto.cancellationReason,
            driverDetails = dto.driver?.let {
                DriverDetails(
                    id = it.id,
                    name = "", // Not available in DriverDetailsDto
                    phoneNumber = "", // Not available in DriverDetailsDto
                    profilePhotoUrl = null, // Not available in DriverDetailsDto
                    rating = it.rating,
                    vehicleDetails = VehicleDetails(
                        make = it.vehicleMake,
                        model = it.vehicleModel,
                        year = it.vehicleYear,
                        color = it.vehicleColor,
                        licensePlate = it.licensePlate,
                        vehicleType = parseVehicleType(it.vehicleType)
                    )
                )
            }
        )
    }
    
    private fun parseVehicleType(type: String): com.rideconnect.core.domain.model.VehicleType {
        return when (type.uppercase()) {
            "SEDAN" -> com.rideconnect.core.domain.model.VehicleType.SEDAN
            "SUV" -> com.rideconnect.core.domain.model.VehicleType.SUV
            "HATCHBACK" -> com.rideconnect.core.domain.model.VehicleType.HATCHBACK
            "AUTO" -> com.rideconnect.core.domain.model.VehicleType.AUTO
            else -> com.rideconnect.core.domain.model.VehicleType.SEDAN
        }
    }
    
    private fun parseRideStatus(status: String): RideStatus {
        return when (status.uppercase()) {
            "REQUESTED" -> RideStatus.REQUESTED
            "SEARCHING" -> RideStatus.SEARCHING
            "ACCEPTED" -> RideStatus.ACCEPTED
            "DRIVER_ARRIVING" -> RideStatus.DRIVER_ARRIVING
            "ARRIVED" -> RideStatus.ARRIVED
            "IN_PROGRESS" -> RideStatus.IN_PROGRESS
            "COMPLETED" -> RideStatus.COMPLETED
            "CANCELLED" -> RideStatus.CANCELLED
            else -> RideStatus.REQUESTED
        }
    }
    
    private fun parseTimestamp(timestamp: String): Long {
        return try {
            Instant.parse(timestamp).toEpochMilli()
        } catch (e: Exception) {
            System.currentTimeMillis()
        }
    }
}
