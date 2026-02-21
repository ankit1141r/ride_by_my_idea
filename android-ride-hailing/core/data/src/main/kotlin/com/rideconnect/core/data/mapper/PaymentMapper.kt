package com.rideconnect.core.data.mapper

import com.rideconnect.core.domain.model.*
import com.rideconnect.core.network.dto.*
import com.rideconnect.core.database.entity.TransactionEntity
import java.time.Instant
import java.time.format.DateTimeFormatter

object PaymentMapper {
    
    fun toDto(request: PaymentRequest): PaymentRequestDto {
        return PaymentRequestDto(
            rideId = request.rideId,
            amount = request.amount,
            paymentMethod = request.paymentMethod.name.lowercase()
        )
    }
    
    fun toTransaction(dto: TransactionResponseDto): Transaction {
        return Transaction(
            id = dto.id,
            rideId = dto.rideId,
            amount = dto.amount,
            paymentMethod = PaymentMethod.fromString(dto.paymentMethod),
            status = TransactionStatus.fromString(dto.status),
            transactionId = dto.transactionId,
            createdAt = parseTimestamp(dto.createdAt),
            completedAt = dto.completedAt?.let { parseTimestamp(it) }
        )
    }
    
    fun toEntity(transaction: Transaction): TransactionEntity {
        return TransactionEntity(
            id = transaction.id,
            rideId = transaction.rideId,
            amount = transaction.amount,
            paymentMethod = transaction.paymentMethod.name,
            status = transaction.status.name,
            transactionId = transaction.transactionId,
            createdAt = transaction.createdAt,
            completedAt = transaction.completedAt
        )
    }
    
    fun toReceipt(dto: ReceiptResponseDto): Receipt {
        return Receipt(
            transaction = toTransaction(dto.transaction),
            ride = RideMapper.toRide(dto.ride),
            fareBreakdown = FareBreakdown(
                baseFare = dto.fareBreakdown.baseFare,
                distanceFare = dto.fareBreakdown.distanceFare,
                timeFare = dto.fareBreakdown.timeFare,
                total = dto.fareBreakdown.total
            )
        )
    }
    
    private fun parseTimestamp(timestamp: String): Long {
        return try {
            Instant.from(DateTimeFormatter.ISO_INSTANT.parse(timestamp)).toEpochMilli()
        } catch (e: Exception) {
            System.currentTimeMillis()
        }
    }
}
