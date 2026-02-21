package com.rideconnect.driver.ui.navigation

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.compose.currentBackStackEntryAsState
import com.rideconnect.core.common.navigation.Screen
import kotlinx.coroutines.launch

/**
 * Drawer navigation items for the Driver App.
 */
sealed class DrawerNavItem(
    val route: String,
    val title: String,
    val icon: ImageVector
) {
    object Home : DrawerNavItem(
        route = Screen.DriverHome.route,
        title = "Home",
        icon = Icons.Default.Home
    )
    
    object Earnings : DrawerNavItem(
        route = Screen.Earnings.route,
        title = "Earnings",
        icon = Icons.Default.AttachMoney
    )
    
    object Ratings : DrawerNavItem(
        route = Screen.DriverRatings.route,
        title = "Ratings",
        icon = Icons.Default.Star
    )
    
    object RideHistory : DrawerNavItem(
        route = Screen.RideHistory.route,
        title = "Ride History",
        icon = Icons.Default.History
    )
    
    object Profile : DrawerNavItem(
        route = Screen.Profile.route,
        title = "Profile",
        icon = Icons.Default.Person
    )
    
    object Settings : DrawerNavItem(
        route = Screen.DriverSettings.route,
        title = "Settings",
        icon = Icons.Default.Settings
    )
}

/**
 * Navigation drawer content for the Driver App.
 */
@Composable
fun DriverDrawerContent(
    navController: NavController,
    drawerState: DrawerState,
    modifier: Modifier = Modifier
) {
    val scope = rememberCoroutineScope()
    val navBackStackEntry = navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry.value?.destination
    
    val items = listOf(
        DrawerNavItem.Home,
        DrawerNavItem.Earnings,
        DrawerNavItem.Ratings,
        DrawerNavItem.RideHistory,
        DrawerNavItem.Profile,
        DrawerNavItem.Settings
    )
    
    ModalDrawerSheet(modifier = modifier) {
        // Drawer header
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 32.dp, horizontal = 16.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Default.DirectionsCar,
                    contentDescription = null,
                    modifier = Modifier.size(64.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "RideConnect Driver",
                    style = MaterialTheme.typography.titleLarge
                )
            }
        }
        
        Divider()
        
        // Navigation items
        items.forEach { item ->
            val selected = currentDestination?.hierarchy?.any {
                it.route == item.route
            } == true
            
            NavigationDrawerItem(
                icon = {
                    Icon(
                        imageVector = item.icon,
                        contentDescription = item.title
                    )
                },
                label = { Text(item.title) },
                selected = selected,
                onClick = {
                    scope.launch {
                        drawerState.close()
                    }
                    if (!selected) {
                        navController.navigate(item.route) {
                            // Pop up to the start destination to avoid building up a large stack
                            popUpTo(Screen.DriverHome.route) {
                                saveState = true
                            }
                            // Avoid multiple copies of the same destination
                            launchSingleTop = true
                            // Restore state when reselecting a previously selected item
                            restoreState = true
                        }
                    }
                },
                modifier = Modifier.padding(NavigationDrawerItemDefaults.ItemPadding)
            )
        }
    }
}
