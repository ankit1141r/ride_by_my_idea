package com.rideconnect.core.common.result

/**
 * A sealed class representing the result of an operation that can either succeed or fail.
 * This is used throughout the app for consistent error handling.
 */
sealed class Result<out T> {
    /**
     * Represents a successful result with data
     */
    data class Success<T>(val data: T) : Result<T>()
    
    /**
     * Represents a failed result with an error
     */
    data class Error(val exception: Exception, val message: String? = null) : Result<Nothing>()
    
    /**
     * Returns true if this is a Success result
     */
    val isSuccess: Boolean
        get() = this is Success
    
    /**
     * Returns true if this is an Error result
     */
    val isError: Boolean
        get() = this is Error
    
    /**
     * Returns the data if Success, or null if Error
     */
    fun getOrNull(): T? = when (this) {
        is Success -> data
        is Error -> null
    }
    
    /**
     * Returns the data if Success, or throws the exception if Error
     */
    fun getOrThrow(): T = when (this) {
        is Success -> data
        is Error -> throw exception
    }
    
    /**
     * Returns the data if Success, or the default value if Error
     */
    fun getOrDefault(default: T): T = when (this) {
        is Success -> data
        is Error -> default
    }
    
    /**
     * Maps the success value using the provided transform function
     */
    inline fun <R> map(transform: (T) -> R): Result<R> = when (this) {
        is Success -> Success(transform(data))
        is Error -> this
    }
    
    /**
     * Flat maps the success value using the provided transform function
     */
    inline fun <R> flatMap(transform: (T) -> Result<R>): Result<R> = when (this) {
        is Success -> transform(data)
        is Error -> this
    }
    
    /**
     * Executes the given action if this is a Success
     */
    inline fun onSuccess(action: (T) -> Unit): Result<T> {
        if (this is Success) {
            action(data)
        }
        return this
    }
    
    /**
     * Executes the given action if this is an Error
     */
    inline fun onError(action: (Exception) -> Unit): Result<T> {
        if (this is Error) {
            action(exception)
        }
        return this
    }
}

/**
 * Creates a Success result
 */
fun <T> success(data: T): Result<T> = Result.Success(data)

/**
 * Creates an Error result
 */
fun error(exception: Exception, message: String? = null): Result<Nothing> = 
    Result.Error(exception, message)

/**
 * Wraps a block in a try-catch and returns a Result
 */
inline fun <T> resultOf(block: () -> T): Result<T> = try {
    Result.Success(block())
} catch (e: Exception) {
    Result.Error(e)
}

/**
 * Wraps a suspending block in a try-catch and returns a Result
 */
suspend inline fun <T> suspendResultOf(crossinline block: suspend () -> T): Result<T> = try {
    Result.Success(block())
} catch (e: Exception) {
    Result.Error(e)
}
