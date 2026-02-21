package com.rideconnect.core.common.util

import android.app.Activity
import android.content.Context
import android.content.res.Configuration
import android.content.res.Resources
import android.os.Build
import com.rideconnect.core.domain.model.Language
import java.util.*

object LanguageUtil {
    
    /**
     * Apply language to the context
     * Requirements: 21.2, 21.3
     */
    fun applyLanguage(context: Context, language: Language): Context {
        val locale = when (language) {
            Language.ENGLISH -> Locale.ENGLISH
            Language.HINDI -> Locale("hi", "IN")
            Language.SYSTEM_DEFAULT -> getSystemLocale()
        }
        
        return updateResources(context, locale)
    }
    
    /**
     * Get system default locale
     * Requirements: 21.4
     */
    private fun getSystemLocale(): Locale {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            Resources.getSystem().configuration.locales[0]
        } else {
            @Suppress("DEPRECATION")
            Resources.getSystem().configuration.locale
        }
    }
    
    /**
     * Update context resources with new locale
     */
    private fun updateResources(context: Context, locale: Locale): Context {
        Locale.setDefault(locale)
        
        val configuration = Configuration(context.resources.configuration)
        configuration.setLocale(locale)
        
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            context.createConfigurationContext(configuration)
        } else {
            @Suppress("DEPRECATION")
            context.resources.updateConfiguration(configuration, context.resources.displayMetrics)
            context
        }
    }
    
    /**
     * Restart activity to apply language change
     * Requirements: 21.2
     */
    fun restartActivity(activity: Activity) {
        val intent = activity.intent
        activity.finish()
        activity.startActivity(intent)
        activity.overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
    }
    
    /**
     * Get locale code from Language enum
     */
    fun getLocaleCode(language: Language): String {
        return when (language) {
            Language.ENGLISH -> "en"
            Language.HINDI -> "hi"
            Language.SYSTEM_DEFAULT -> "system"
        }
    }
    
    /**
     * Get Language enum from locale code
     */
    fun getLanguageFromCode(code: String): Language {
        return when (code) {
            "en" -> Language.ENGLISH
            "hi" -> Language.HINDI
            else -> Language.SYSTEM_DEFAULT
        }
    }
}
