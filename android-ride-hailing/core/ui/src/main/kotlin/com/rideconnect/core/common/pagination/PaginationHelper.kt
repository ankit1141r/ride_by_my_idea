package com.rideconnect.core.common.pagination

import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.snapshotFlow
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.filter

/**
 * Helper for implementing pagination in lists
 * Requirements: 23.8
 */
object PaginationHelper {
    
    const val DEFAULT_PAGE_SIZE = 20
    const val LOAD_MORE_THRESHOLD = 5 // Load more when 5 items from end
    
    /**
     * Calculate page number from offset
     */
    fun calculatePage(offset: Int, pageSize: Int = DEFAULT_PAGE_SIZE): Int {
        return offset / pageSize
    }
    
    /**
     * Calculate offset from page number
     */
    fun calculateOffset(page: Int, pageSize: Int = DEFAULT_PAGE_SIZE): Int {
        return page * pageSize
    }
    
    /**
     * Check if should load more items
     */
    fun shouldLoadMore(
        currentItemCount: Int,
        lastVisibleItemIndex: Int,
        threshold: Int = LOAD_MORE_THRESHOLD
    ): Boolean {
        return lastVisibleItemIndex >= currentItemCount - threshold
    }
}

/**
 * State holder for paginated data
 */
data class PaginatedState<T>(
    val items: List<T> = emptyList(),
    val currentPage: Int = 0,
    val isLoading: Boolean = false,
    val isLoadingMore: Boolean = false,
    val hasMore: Boolean = true,
    val error: String? = null
) {
    val isEmpty: Boolean get() = items.isEmpty() && !isLoading
    val canLoadMore: Boolean get() = hasMore && !isLoading && !isLoadingMore
}

/**
 * Composable to detect when user scrolls near end of list
 * Requirements: 23.8
 */
@Composable
fun LazyListState.OnLoadMore(
    threshold: Int = PaginationHelper.LOAD_MORE_THRESHOLD,
    onLoadMore: () -> Unit
) {
    val shouldLoadMore by remember {
        derivedStateOf {
            val lastVisibleItem = layoutInfo.visibleItemsInfo.lastOrNull()
                ?: return@derivedStateOf false
            
            val lastVisibleItemIndex = lastVisibleItem.index
            val totalItemsCount = layoutInfo.totalItemsCount
            
            lastVisibleItemIndex >= totalItemsCount - threshold
        }
    }
    
    LaunchedEffect(shouldLoadMore) {
        snapshotFlow { shouldLoadMore }
            .distinctUntilChanged()
            .filter { it }
            .collect {
                onLoadMore()
            }
    }
}

/**
 * Pagination manager for handling page loading logic
 */
class PaginationManager<T>(
    private val pageSize: Int = PaginationHelper.DEFAULT_PAGE_SIZE,
    private val loadPage: suspend (page: Int, pageSize: Int) -> List<T>
) {
    private var currentPage = 0
    private var isLoading = false
    private var hasMore = true
    
    /**
     * Load next page of data
     */
    suspend fun loadNextPage(): List<T> {
        if (isLoading || !hasMore) {
            return emptyList()
        }
        
        isLoading = true
        return try {
            val items = loadPage(currentPage, pageSize)
            
            if (items.size < pageSize) {
                hasMore = false
            }
            
            currentPage++
            items
        } finally {
            isLoading = false
        }
    }
    
    /**
     * Reset pagination to start
     */
    fun reset() {
        currentPage = 0
        isLoading = false
        hasMore = true
    }
    
    /**
     * Check if can load more
     */
    fun canLoadMore(): Boolean = hasMore && !isLoading
    
    /**
     * Get current page number
     */
    fun getCurrentPage(): Int = currentPage
}
