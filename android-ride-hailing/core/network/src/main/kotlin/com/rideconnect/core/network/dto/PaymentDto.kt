package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

data class PaymentRequestDto(
    @SerializedName("ride_id")
    val rideId: String,
    @SerializedName("amount")
    val amount: Double,
    @SerializedName("payment_method")
    val paymentMethod: String
)

data class TransactionResponseDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("ride_id")
    val rideId: String,
    @SerializedName("amount")
    val amount: Double,
    @SerializedName("payment_method")
    val paymentMethod: String,
    @SerializedName("status")
    val status: String,
    @SerializedName("transaction_id")
    val transactionId: String?,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("completed_at")
    val completedAt: String?
)

data class ReceiptResponseDto(
    @SerializedName("transaction")
    val transaction: TransactionResponseDto,
    @SerializedName("ride")
    val ride: RideResponseDto,
    @SerializedName("fare_breakdown")
    val fareBreakdown: FareBreakdownDto
)

data class FareBreakdownDto(
    @SerializedName("base_fare")
    val baseFare: Double,
    @SerializedName("distance_fare")
    val distanceFare: Double,
    @SerializedName("time_fare")
    val timeFare: Double,
    @SerializedName("total")
    val total: Double
)
