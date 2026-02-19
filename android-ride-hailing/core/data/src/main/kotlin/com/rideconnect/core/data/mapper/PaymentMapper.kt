package com.rideconnect.core.data.mapper

import com.rideconnect.core.domain.model.*
import com.rideconnect.core.network.dto.*
import java.time.Instant

fun TransactionResponseDto.toTransaction(): Transaction {
    return Transaction(
        id = id,
        rideId = rideId,
        amount = amount,
        paymentMethod = PaymentMethod.fromString(paymentMethod),
        status = TransactionStatus.fromString(status),
        transactionId = transactionId,
        createdAt = parseTimestamp(createdAt),
        completedAt = completedAt?.let { parseTimestamp(it) }
    )
}

fun ReceiptResponseDto.toReceipt(): Receipt {
    return Receipt(
        transaction = transaction.toTransaction(),
        ride = ride.toRide(),
        fareBreakdown = fareBreakdown.toFareBreakdown()
    )
}

fun FareBreakdownDto.toFareBreakdown(): FareBreakdown {
    return FareBreakdown(
        baseFare = baseFare,
        distanceFare = distanceFare,
        timeFare = timeFare,
        total = total
    )
}

fun PaymentRequest.toDto(): PaymentRequestDto {
    return PaymentRequestDto(
        rideId = rideId,
        amount = amount,
        paymentMethod = paymentMethod.name.lowercase()
    )
}

private fun parseTimestamp(timestamp: String): Long {
    return try {
        Instant.parse(timestamp).toEpochMilli()
    } catch (e: Exception) {
        System.currentTimeMillis()
    }
}
