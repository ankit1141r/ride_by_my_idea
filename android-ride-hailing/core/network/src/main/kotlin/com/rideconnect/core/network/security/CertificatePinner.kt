package com.rideconnect.core.network.security

import okhttp3.CertificatePinner
import timber.log.Timber

/**
 * SSL Certificate Pinning configuration
 * Requirements: 24.2
 */
object CertificatePinnerConfig {
    
    // Backend API hostname
    private const val API_HOSTNAME = "api.rideconnect.com"
    
    // Certificate pins (SHA-256 hashes of public keys)
    // These should be replaced with actual certificate pins from your backend
    private val CERTIFICATE_PINS = arrayOf(
        // Primary certificate pin
        "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        // Backup certificate pin (for certificate rotation)
        "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
    )
    
    /**
     * Create certificate pinner for OkHttp
     * Requirements: 24.2
     */
    fun createCertificatePinner(): CertificatePinner {
        val builder = CertificatePinner.Builder()
        
        // Add pins for API hostname
        CERTIFICATE_PINS.forEach { pin ->
            builder.add(API_HOSTNAME, pin)
        }
        
        val pinner = builder.build()
        Timber.d("Certificate pinner created for $API_HOSTNAME")
        
        return pinner
    }
    
    /**
     * Create certificate pinner for development (disabled pinning)
     * Use only in debug builds
     */
    fun createDevelopmentPinner(): CertificatePinner {
        Timber.w("Using development certificate pinner (pinning disabled)")
        return CertificatePinner.Builder().build()
    }
    
    /**
     * Instructions for generating certificate pins:
     * 
     * 1. Get the certificate from your server:
     *    openssl s_client -connect api.rideconnect.com:443 < /dev/null | openssl x509 -outform DER > cert.der
     * 
     * 2. Extract the public key:
     *    openssl x509 -in cert.der -inform DER -pubkey -noout > pubkey.pem
     * 
     * 3. Generate SHA-256 hash:
     *    openssl pkey -pubin -in pubkey.pem -outform DER | openssl dgst -sha256 -binary | openssl enc -base64
     * 
     * 4. Add the pin with "sha256/" prefix:
     *    sha256/[base64-encoded-hash]
     * 
     * Best practices:
     * - Always pin at least 2 certificates (primary + backup)
     * - Update pins before certificate expiration
     * - Test certificate pinning in staging environment first
     * - Have a backup plan for pin updates (remote config, app update)
     */
}

/**
 * Certificate pinning error handler
 */
class CertificatePinningException(
    message: String,
    cause: Throwable? = null
) : SecurityException(message, cause) {
    
    companion object {
        fun create(hostname: String, cause: Throwable): CertificatePinningException {
            return CertificatePinningException(
                "Certificate pinning failed for $hostname. " +
                "This could indicate a man-in-the-middle attack or certificate mismatch.",
                cause
            )
        }
    }
}
