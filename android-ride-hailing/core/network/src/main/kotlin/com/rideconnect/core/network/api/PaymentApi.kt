package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.PaymentRequestDto
import com.rideconnect.core.network.dto.ReceiptResponseDto
import com.rideconnect.core.network.dto.TransactionResponseDto
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface PaymentApi {
    
    @POST("payments/process")
    suspend fun processPayment(@Body request: PaymentRequestDto): Response<TransactionResponseDto>
    
    @GET("payments/history")
    suspend fun getPaymentHistory(
        @Query("page") page: Int,
        @Query("page_size") pageSize: Int
    ): Response<List<TransactionResponseDto>>
    
    @GET("payments/receipt/{transactionId}")
    suspend fun getReceipt(@Path("transactionId") transactionId: String): Response<ReceiptResponseDto>
}
