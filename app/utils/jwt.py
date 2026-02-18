"""
JWT token generation and validation utilities.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import jwt, JWTError
from app.config import settings


def create_access_token(
    user_id: str,
    user_type: str,
    phone_verified: bool,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token with user claims.
    
    Args:
        user_id: The user's unique identifier
        user_type: The user type ('rider' or 'driver')
        phone_verified: Whether the user's phone is verified
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "user_type": user_type,
        "phone_verified": phone_verified,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: The JWT token string to decode
    
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None



def get_current_user(token: str) -> Dict:
    """
    Dependency function to get current user from JWT token.
    
    This is a placeholder that should be replaced with proper FastAPI dependency
    that extracts token from Authorization header.
    
    Args:
        token: JWT token string
        
    Returns:
        User data from token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    from fastapi import HTTPException, status
    
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "user_id": payload.get("user_id"),
        "user_type": payload.get("user_type"),
        "phone_verified": payload.get("phone_verified")
    }


# FastAPI dependency for extracting current user from request
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    FastAPI dependency to extract and validate current user from Authorization header.
    
    Args:
        credentials: HTTP Bearer credentials from request header
        
    Returns:
        User data from token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    return get_current_user(token)
