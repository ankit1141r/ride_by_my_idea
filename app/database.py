"""
Database connection management for PostgreSQL, Redis, and MongoDB.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# PostgreSQL Setup
engine = create_engine(
    settings.postgres_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting PostgreSQL database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis Setup
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password if settings.redis_password else None,
    decode_responses=True
)


def get_redis():
    """Dependency for getting Redis client."""
    return redis_client


# MongoDB Setup
mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
mongodb = mongodb_client[settings.mongodb_db]


def get_mongodb():
    """Dependency for getting MongoDB database."""
    return mongodb
