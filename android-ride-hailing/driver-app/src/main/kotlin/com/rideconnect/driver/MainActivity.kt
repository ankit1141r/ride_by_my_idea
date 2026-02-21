package com.rideconnect.driver

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.rememberNavController
import com.rideconnect.core.common.navigation.Screen
import com.rideconnect.core.common.theme.RideConnectTheme
import com.rideconnect.core.domain.viewmodel.AuthViewModel
import com.rideconnect.driver.navigation.DriverNavGraph
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.delay

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Install splash screen before calling super.onCreate()
        val splashScreen = installSplashScreen()
        
        super.onCreate(savedInstanceState)
        
        // Keep splash screen visible while checking authentication
        var keepSplashScreen = true
        splashScreen.setKeepOnScreenCondition { keepSplashScreen }
        
        setContent {
            val authViewModel: AuthViewModel = hiltViewModel()
            val authState by authViewModel.authState.collectAsState()
            
            // Determine start destination based on auth state
            var startDestination by remember { mutableStateOf<String?>(null) }
            
            LaunchedEffect(authState) {
                // Simulate minimum splash screen duration
                delay(500)
                
                startDestination = if (authState.isAuthenticated) {
                    Screen.DriverHome.route
                } else {
                    Screen.Login.route
                }
                
                keepSplashScreen = false
            }
            
            RideConnectTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    // Only show navigation when start destination is determined
                    startDestination?.let { destination ->
                        val navController = rememberNavController()
                        
                        // Handle deep links from intent
                        LaunchedEffect(Unit) {
                            intent?.data?.let { uri ->
                                navController.navigate(uri)
                            }
                        }
                        
                        DriverNavGraph(
                            navController = navController,
                            startDestination = destination
                        )
                    }
                }
            }
        }
    }
}

