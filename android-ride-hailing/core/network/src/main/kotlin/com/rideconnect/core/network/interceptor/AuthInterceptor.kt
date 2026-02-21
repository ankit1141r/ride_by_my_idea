package com.rideconnect.core.network.interceptor

import com.rideconnect.core.common.local.TokenManager
import okhttp3.Interceptor
import okhttp3.Response
import timber.log.Timber
import javax.inject.Inject

/**
 * Interceptor that adds JWT authentication token to all API requests.
 * Automatically includes the Bearer token in the Authorization header.
 */
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Get the stored access token
        val token = tokenManager.getAccessToken()
        
        // If no token, proceed without authentication header
        if (token == null) {
            Timber.d("No auth token available, proceeding without Authorization header")
            return chain.proceed(originalRequest)
        }
        
        // Add Authorization header with Bearer token
        val authenticatedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .build()
        
        Timber.d("Added Authorization header to request: ${originalRequest.url}")
        
        return chain.proceed(authenticatedRequest)
    }
}
