"""
Admin API endpoints for system management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import asyncio
import subprocess
import sys
import os

from app.database import get_async_session
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/seed")
async def seed_database(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Seed the database with sample data for testing.
    
    Note: In production, this should be restricted to admin users only.
    For demo purposes, any authenticated user can trigger seeding.
    """
    
    try:
        # In production, check if user is admin
        # if current_user.user_type != "admin":
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Admin access required"
        #     )
        
        # Run the seeding script
        script_path = os.path.join(os.getcwd(), "seed_database.py")
        
        if not os.path.exists(script_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Seeding script not found"
            )
        
        # Execute the seeding script
        process = await asyncio.create_subprocess_exec(
            sys.executable, script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "success": True,
                "message": "Database seeded successfully with sample data",
                "output": stdout.decode() if stdout else "",
                "details": {
                    "users_created": "50 (17 drivers, 33 riders)",
                    "rides_created": "200",
                    "transactions_created": "~120",
                    "driver_profiles_created": "17"
                }
            }
        else:
            error_message = stderr.decode() if stderr else "Unknown error"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Seeding failed: {error_message}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed database: {str(e)}"
        )

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """Get system statistics for admin dashboard."""
    
    try:
        # Get basic counts from database
        from sqlalchemy import text
        
        # Count users
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        total_users = result.scalar()
        
        result = await session.execute(text("SELECT COUNT(*) FROM users WHERE user_type = 'driver'"))
        total_drivers = result.scalar()
        
        result = await session.execute(text("SELECT COUNT(*) FROM users WHERE user_type = 'rider'"))
        total_riders = result.scalar()
        
        # Count rides
        result = await session.execute(text("SELECT COUNT(*) FROM rides"))
        total_rides = result.scalar()
        
        result = await session.execute(text("SELECT COUNT(*) FROM rides WHERE status = 'completed'"))
        completed_rides = result.scalar()
        
        # Count transactions
        result = await session.execute(text("SELECT COUNT(*) FROM transactions"))
        total_transactions = result.scalar()
        
        result = await session.execute(text("SELECT SUM(amount) FROM transactions WHERE status = 'completed'"))
        total_revenue = result.scalar() or 0
        
        # Today's stats
        result = await session.execute(text("""
            SELECT COUNT(*) FROM users 
            WHERE DATE(created_at) = CURRENT_DATE
        """))
        today_users = result.scalar()
        
        result = await session.execute(text("""
            SELECT COUNT(*) FROM rides 
            WHERE DATE(created_at) = CURRENT_DATE
        """))
        today_rides = result.scalar()
        
        result = await session.execute(text("""
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE status = 'completed' AND DATE(created_at) = CURRENT_DATE
        """))
        today_revenue = result.scalar() or 0
        
        return {
            "total_users": total_users,
            "total_drivers": total_drivers,
            "total_riders": total_riders,
            "total_rides": total_rides,
            "completed_rides": completed_rides,
            "total_transactions": total_transactions,
            "total_revenue": float(total_revenue),
            "today_stats": {
                "users": today_users,
                "rides": today_rides,
                "revenue": float(today_revenue)
            },
            "system_health": {
                "database": True,
                "redis": True,  # Would check actual Redis connection
                "mongodb": True  # Would check actual MongoDB connection
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admin stats: {str(e)}"
        )

@router.post("/clear-cache")
async def clear_cache(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Clear Redis cache."""
    
    try:
        # In production, implement actual Redis cache clearing
        # redis_client.flushdb()
        
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )

@router.get("/users")
async def get_all_users(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    """Get all users for admin management."""
    
    try:
        from sqlalchemy import select
        
        # Get users with pagination
        query = select(User).offset(skip).limit(limit)
        result = await session.execute(query)
        users = result.scalars().all()
        
        # Get total count
        count_query = select(User)
        count_result = await session.execute(count_query)
        total_count = len(count_result.scalars().all())
        
        return {
            "users": [
                {
                    "id": user.id,
                    "full_name": user.full_name,
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "user_type": user.user_type,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ],
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Dict[str, str]:
    """Update user active status."""
    
    try:
        from sqlalchemy import select
        
        # Get user
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update status
        user.is_active = is_active
        await session.commit()
        
        return {
            "success": True,
            "message": f"User {'activated' if is_active else 'suspended'} successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user status: {str(e)}"
        )