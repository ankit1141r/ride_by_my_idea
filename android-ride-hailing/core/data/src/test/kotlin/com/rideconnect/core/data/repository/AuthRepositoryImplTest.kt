package com.rideconnect.core.data.repository

import com.rideconnect.core.data.local.TokenManagerWrapper
import com.rideconnect.core.domain.model.AuthToken
import com.rideconnect.core.domain.model.User
import com.rideconnect.core.domain.model.UserType
import com.rideconnect.core.network.api.AuthApi
import com.rideconnect.core.network.dto.AuthResponse
import com.rideconnect.core.network.dto.RefreshTokenRequest
import com.rideconnect.core.network.dto.SendOtpRequest
import com.rideconnect.core.network.dto.UserDto
import com.rideconnect.core.network.dto.VerifyOtpRequest
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.test.runTest
import okhttp3.ResponseBody.Companion.toResponseBody
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import retrofit2.Response

class AuthRepositoryImplTest {
    
    private lateinit var authApi: AuthApi
    private lateinit var tokenManager: TokenManager
    private lateinit var authRepository: AuthRepositoryImpl
    
    @Before
    fun setup() {
        authApi = mockk()
        tokenManager = mockk(relaxed = true)
        authRepository = AuthRepositoryImpl(authApi, tokenManager)
    }
    
    @Test
    fun `sendOtp should return success when API call succeeds`() = runTest {
        // Given
        val phoneNumber = "+1234567890"
        coEvery { authApi.sendOtp(SendOtpRequest(phoneNumber)) } returns Response.success(Unit)
        
        // When
        val result = authRepository.sendOtp(phoneNumber)
        
        // Then
        assertTrue(result.isSuccess)
        coVerify { authApi.sendOtp(SendOtpRequest(phoneNumber)) }
    }
    
    @Test
    fun `sendOtp should return failure when API call fails`() = runTest {
        // Given
        val phoneNumber = "+1234567890"
        val errorBody = "Invalid phone number".toResponseBody()
        coEvery { authApi.sendOtp(SendOtpRequest(phoneNumber)) } returns 
            Response.error(400, errorBody)
        
        // When
        val result = authRepository.sendOtp(phoneNumber)
        
        // Then
        assertTrue(result.isFailure)
    }
    
    @Test
    fun `verifyOtp should return success and store token when API call succeeds`() = runTest {
        // Given
        val phoneNumber = "+1234567890"
        val otp = "123456"
        val authResponse = createMockAuthResponse()
        coEvery { authApi.verifyOtp(VerifyOtpRequest(phoneNumber, otp)) } returns 
            Response.success(authResponse)
        
        // When
        val result = authRepository.verifyOtp(phoneNumber, otp)
        
        // Then
        assertTrue(result.isSuccess)
        val (token, user) = result.getOrNull()!!
        assertEquals("access_token_123", token.accessToken)
        assertEquals("refresh_token_123", token.refreshToken)
        assertEquals("user_123", user.id)
        
        verify { tokenManager.saveToken(any()) }
        verify { tokenManager.saveUser(any()) }
    }
    
    @Test
    fun `verifyOtp should return failure when API call fails`() = runTest {
        // Given
        val phoneNumber = "+1234567890"
        val otp = "123456"
        val errorBody = "Invalid OTP".toResponseBody()
        coEvery { authApi.verifyOtp(VerifyOtpRequest(phoneNumber, otp)) } returns 
            Response.error(401, errorBody)
        
        // When
        val result = authRepository.verifyOtp(phoneNumber, otp)
        
        // Then
        assertTrue(result.isFailure)
    }
    
    @Test
    fun `refreshToken should return success and store new token when API call succeeds`() = runTest {
        // Given
        val refreshToken = "refresh_token_123"
        val authResponse = createMockAuthResponse()
        coEvery { authApi.refreshToken(RefreshTokenRequest(refreshToken)) } returns 
            Response.success(authResponse)
        
        // When
        val result = authRepository.refreshToken(refreshToken)
        
        // Then
        assertTrue(result.isSuccess)
        val (token, user) = result.getOrNull()!!
        assertEquals("access_token_123", token.accessToken)
        
        verify { tokenManager.saveToken(any()) }
        verify { tokenManager.saveUser(any()) }
    }
    
    @Test
    fun `refreshToken should retry on failure with exponential backoff`() = runTest {
        // Given
        val refreshToken = "refresh_token_123"
        val authResponse = createMockAuthResponse()
        
        // First two attempts fail, third succeeds
        coEvery { authApi.refreshToken(RefreshTokenRequest(refreshToken)) } returnsMany listOf(
            Response.error(500, "Server error".toResponseBody()),
            Response.error(500, "Server error".toResponseBody()),
            Response.success(authResponse)
        )
        
        // When
        val result = authRepository.refreshToken(refreshToken)
        
        // Then
        assertTrue(result.isSuccess)
        coVerify(exactly = 3) { authApi.refreshToken(RefreshTokenRequest(refreshToken)) }
    }
    
    @Test
    fun `refreshToken should fail after max retry attempts`() = runTest {
        // Given
        val refreshToken = "refresh_token_123"
        coEvery { authApi.refreshToken(RefreshTokenRequest(refreshToken)) } returns 
            Response.error(500, "Server error".toResponseBody())
        
        // When
        val result = authRepository.refreshToken(refreshToken)
        
        // Then
        assertTrue(result.isFailure)
        coVerify(exactly = 3) { authApi.refreshToken(RefreshTokenRequest(refreshToken)) }
    }
    
    @Test
    fun `logout should clear tokens when API call succeeds`() = runTest {
        // Given
        coEvery { authApi.logout() } returns Response.success(Unit)
        
        // When
        val result = authRepository.logout()
        
        // Then
        assertTrue(result.isSuccess)
        verify { tokenManager.clearAll() }
    }
    
    @Test
    fun `logout should clear tokens even when API call fails`() = runTest {
        // Given
        coEvery { authApi.logout() } returns Response.error(500, "Server error".toResponseBody())
        
        // When
        val result = authRepository.logout()
        
        // Then
        assertTrue(result.isFailure)
        verify { tokenManager.clearAll() }
    }
    
    @Test
    fun `getStoredToken should return token from TokenManager`() {
        // Given
        val expectedToken = AuthToken("access", "refresh")
        every { tokenManager.getToken() } returns expectedToken
        
        // When
        val token = authRepository.getStoredToken()
        
        // Then
        assertNotNull(token)
        assertEquals(expectedToken, token)
    }
    
    @Test
    fun `getStoredUser should return user from TokenManager`() {
        // Given
        val expectedUser = User(
            id = "user_123",
            phoneNumber = "+1234567890",
            name = "Test User",
            userType = UserType.RIDER,
            createdAt = System.currentTimeMillis()
        )
        every { tokenManager.getUser() } returns expectedUser
        
        // When
        val user = authRepository.getStoredUser()
        
        // Then
        assertNotNull(user)
        assertEquals(expectedUser, user)
    }
    
    private fun createMockAuthResponse(): AuthResponse {
        return AuthResponse(
            accessToken = "access_token_123",
            refreshToken = "refresh_token_123",
            tokenType = "Bearer",
            expiresIn = 3600L,
            user = UserDto(
                id = "user_123",
                phoneNumber = "+1234567890",
                name = "Test User",
                email = "test@example.com",
                profilePhotoUrl = null,
                userType = "rider",
                rating = 4.5,
                createdAt = "2024-01-01T00:00:00Z"
            )
        )
    }
}
