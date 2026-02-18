"""
Authentication and authorization middleware.
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from app.utils.jwt import decode_access_token

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials
) -> dict:
    """
    Validate JWT token and extract user information.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        payload = decode_access_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return payload
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


def require_user_type(*allowed_types: str):
    """
    Decorator to require specific user types for endpoints.
    
    Args:
        *allowed_types: Allowed user types (e.g., "rider", "driver")
        
    Returns:
        Dependency function
    """
    async def check_user_type(
        credentials: HTTPAuthorizationCredentials = security
    ) -> dict:
        user = await get_current_user(credentials)
        
        if user.get("user_type") not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required user type: {', '.join(allowed_types)}"
            )
        
        return user
    
    return check_user_type


def require_verified_phone():
    """
    Decorator to require phone verification for endpoints.
    
    Returns:
        Dependency function
    """
    async def check_phone_verified(
        credentials: HTTPAuthorizationCredentials = security
    ) -> dict:
        user = await get_current_user(credentials)
        
        if not user.get("phone_verified"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Phone verification required"
            )
        
        return user
    
    return check_phone_verified


async def get_current_user_optional(
    request: Request
) -> Optional[dict]:
    """
    Get current user from token if present, otherwise return None.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User dict if authenticated, None otherwise
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        payload = decode_access_token(token)
        return payload
    except Exception:
        return None
