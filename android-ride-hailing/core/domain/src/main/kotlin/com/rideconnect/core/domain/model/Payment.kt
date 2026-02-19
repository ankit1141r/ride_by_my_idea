package com.rideconnect.core.domain.model

data class Transaction(
    val id: String,
    val rideId: String,
    val amount: Double,
    val paymentMethod: PaymentMethod,
    val status: TransactionStatus,
    val transactionId: String?,
    val createdAt: Long,
    val completedAt: Long?
)

enum class PaymentMethod {
    RAZORPAY,
    PAYTM,
    CASH,
    UNKNOWN;
    
    companion object {
        fun fromString(value: String): PaymentMethod {
            return when (value.uppercase()) {
                "RAZORPAY" -> RAZORPAY
                "PAYTM" -> PAYTM
                "CASH" -> CASH
                else -> UNKNOWN
            }
        }
    }
}

enum class TransactionStatus {
    PENDING,
    PROCESSING,
    COMPLETED,
    FAILED,
    REFUNDED,
    UNKNOWN;
    
    companion object {
        fun fromString(value: String): TransactionStatus {
            return when (value.uppercase()) {
                "PENDING" -> PENDING
                "PROCESSING" -> PROCESSING
                "COMPLETED" -> COMPLETED
                "FAILED" -> FAILED
                "REFUNDED" -> REFUNDED
                else -> UNKNOWN
            }
        }
    }
}

data class Receipt(
    val transaction: Transaction,
    val ride: Ride,
    val fareBreakdown: FareBreakdown
)

data class FareBreakdown(
    val baseFare: Double,
    val distanceFare: Double,
    val timeFare: Double,
    val total: Double
)

data class PaymentRequest(
    val rideId: String,
    val amount: Double,
    val paymentMethod: PaymentMethod
)
