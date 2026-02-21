package com.rideconnect.core.domain.model

import java.time.LocalDate

/**
 * Earnings period filter.
 * Requirements: 14.2, 14.3, 14.4
 */
enum class EarningsPeriod {
    DAY,
    WEEK,
    MONTH,
    CUSTOM
}

/**
 * Request for earnings data with date range.
 * Requirements: 14.2
 */
data class EarningsRequest(
    val startDate: LocalDate,
    val endDate: LocalDate,
    val period: EarningsPeriod = EarningsPeriod.CUSTOM
) {
    init {
        require(!endDate.isBefore(startDate)) { "End date must be after or equal to start date" }
    }
}
