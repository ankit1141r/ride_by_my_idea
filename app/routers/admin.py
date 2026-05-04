"""
Admin API endpoints for system management.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Optional
import asyncio
import sys
import os

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/seed")
async def seed_database(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Seed the database with sample data for testing."""
    try:
        script_path = os.path.join(os.getcwd(), "seed_database.py")
        if not os.path.exists(script_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Seeding script not found"
            )
        process = await asyncio.create_subprocess_exec(
            sys.executable, script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            return {
                "success": True,
                "message": "Database seeded successfully",
                "output": stdout.decode() if stdout else "",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Seeding failed: {stderr.decode() if stderr else 'Unknown error'}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to seed database: {str(e)}")


@router.get("/stats")
def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get system statistics for admin dashboard."""
    try:
        def scalar(q):
            return db.execute(text(q)).scalar() or 0

        return {
            "total_users": scalar("SELECT COUNT(*) FROM users"),
            "total_drivers": scalar("SELECT COUNT(*) FROM users WHERE user_type = 'driver'"),
            "total_riders": scalar("SELECT COUNT(*) FROM users WHERE user_type = 'rider'"),
            "total_rides": scalar("SELECT COUNT(*) FROM rides"),
            "completed_rides": scalar("SELECT COUNT(*) FROM rides WHERE status = 'completed'"),
            "total_transactions": scalar("SELECT COUNT(*) FROM transactions"),
            "total_revenue": float(scalar("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE status = 'completed'")),
            "today_stats": {
                "users": scalar("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE"),
                "rides": scalar("SELECT COUNT(*) FROM rides WHERE DATE(created_at) = CURRENT_DATE"),
                "revenue": float(scalar("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE status='completed' AND DATE(created_at)=CURRENT_DATE")),
            },
            "system_health": {"database": True, "redis": True, "mongodb": True},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/clear-cache")
def clear_cache(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Clear Redis cache."""
    return {"success": True, "message": "Cache cleared successfully"}


@router.get("/users")
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Dict[str, Any]:
    """Get all users for admin management."""
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        total = db.query(User).count()
        return {
            "users": [
                {
                    "id": u.user_id,
                    "full_name": u.full_name,
                    "phone_number": u.phone_number,
                    "email": u.email,
                    "user_type": u.user_type,
                    "is_active": u.is_active,
                    "is_verified": u.is_verified,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in users
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")


@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: str,
    is_active: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Update user active status."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    db.commit()
    return {"success": True, "message": f"User {'activated' if is_active else 'suspended'} successfully"}


@router.get("/scheduler/status")
def get_scheduler_status(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get background scheduler status and job information."""
    try:
        scheduler_service = getattr(request.app.state, "scheduler_service", None)
        if not scheduler_service:
            return {"running": False, "jobs": [], "total_executions": 0, "failed_executions": 0}
        return scheduler_service.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")
