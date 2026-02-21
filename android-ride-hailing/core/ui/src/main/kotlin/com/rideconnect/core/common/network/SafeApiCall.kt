package com.rideconnect.core.common.network

import com.rideconnect.core.common.result.Result
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import retrofit2.HttpException
import retrofit2.Response
import java.io.IOException

/**
 * Safe API call wrapper that handles exceptions and converts them to Result
 * Requirements: 26.1, 26.4
 */
suspend fun <T> safeApiCall(
    apiCall: suspend () -> Response<T>
): Result<T> {
    return withContext(Dispatchers.IO) {
        try {
            val response = apiCall()
            if (response.isSuccessful) {
                val body = response.body()
                if (body != null) {
                    Result.Success(body)
                } else {
                    Result.Error(Exception("Response body is null"))
                }
            } else {
                Result.Error(Exception("HTTP ${response.code()}: ${response.message()}"))
            }
        } catch (e: HttpException) {
            Result.Error(Exception("HTTP error: ${e.message}", e))
        } catch (e: IOException) {
            Result.Error(Exception("Network error: ${e.message}", e))
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}

/**
 * Safe API call for endpoints that return Unit
 */
suspend fun safeApiCallUnit(
    apiCall: suspend () -> Response<Unit>
): Result<Unit> {
    return withContext(Dispatchers.IO) {
        try {
            val response = apiCall()
            if (response.isSuccessful) {
                Result.Success(Unit)
            } else {
                Result.Error(Exception("HTTP ${response.code()}: ${response.message()}"))
            }
        } catch (e: HttpException) {
            Result.Error(Exception("HTTP error: ${e.message}", e))
        } catch (e: IOException) {
            Result.Error(Exception("Network error: ${e.message}", e))
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}

/**
 * Safe API call with custom error mapping
 */
suspend fun <T> safeApiCallWithMapping(
    apiCall: suspend () -> Response<T>,
    errorMapper: (Exception) -> Exception = { it }
): Result<T> {
    return withContext(Dispatchers.IO) {
        try {
            val response = apiCall()
            if (response.isSuccessful) {
                val body = response.body()
                if (body != null) {
                    Result.Success(body)
                } else {
                    Result.Error(errorMapper(Exception("Response body is null")))
                }
            } else {
                Result.Error(errorMapper(Exception("HTTP ${response.code()}: ${response.message()}")))
            }
        } catch (e: Exception) {
            Result.Error(errorMapper(e))
        }
    }
}

/**
 * Extension function for Response to check success and extract body
 */
fun <T> Response<T>.toResult(): Result<T> {
    return if (isSuccessful) {
        val body = body()
        if (body != null) {
            Result.Success(body)
        } else {
            Result.Error(Exception("Response body is null"))
        }
    } else {
        Result.Error(Exception("HTTP ${code()}: ${message()}"))
    }
}
