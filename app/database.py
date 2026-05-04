"""
Database connection management.
Uses PostgreSQL when available, falls back to SQLite for local development.
Redis and MongoDB are optional — the app degrades gracefully without them.
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

# ── SQLAlchemy Base ──────────────────────────────────────────────────────────
Base = declarative_base()


# ── Database Engine: PostgreSQL → SQLite fallback ───────────────────────────
def _create_engine():
    """Try PostgreSQL first; fall back to SQLite if unavailable."""
    # 1. Try PostgreSQL
    try:
        pg_engine = create_engine(
            settings.postgres_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={"connect_timeout": 3},
        )
        # Quick connectivity test
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Connected to PostgreSQL at %s:%s/%s",
                    settings.postgres_host, settings.postgres_port, settings.postgres_db)
        return pg_engine, "postgresql"
    except Exception as pg_err:
        logger.warning("⚠️  PostgreSQL unavailable (%s). Falling back to SQLite.", pg_err)

    # 2. Fall back to SQLite
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rideconnect_local.db")
    sqlite_url = f"sqlite:///{db_path}"
    sqlite_engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
    )
    logger.info("✅ Using SQLite database at %s", db_path)
    return sqlite_engine, "sqlite"


engine, _db_backend = _create_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """Create all tables (used on startup)."""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables ensured (backend: %s)", _db_backend)


# ── Redis: optional ──────────────────────────────────────────────────────────
class _FakeRedis:
    """In-memory Redis stub used when the real Redis is unavailable."""
    def __init__(self):
        self._store: dict = {}
        self._expiry: dict = {}
        logger.warning("⚠️  Redis unavailable. Using in-memory stub (sessions won't persist across restarts).")

    def hset(self, name, mapping=None, **kwargs):
        if mapping:
            self._store.setdefault(name, {}).update(mapping)

    def hget(self, name, key):
        return self._store.get(name, {}).get(key)

    def hgetall(self, name):
        return self._store.get(name, {})

    def expire(self, name, seconds):
        self._expiry[name] = seconds

    def delete(self, *names):
        for n in names:
            self._store.pop(n, None)

    def exists(self, *names):
        return sum(1 for n in names if n in self._store)

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        if nx and name in self._store:
            return None
        self._store[name] = value
        return True

    def get(self, name):
        return self._store.get(name)

    def setex(self, name, time, value):
        self._store[name] = value

    def incr(self, name):
        val = int(self._store.get(name, 0)) + 1
        self._store[name] = str(val)
        return val

    def lpush(self, name, *values):
        lst = self._store.setdefault(name, [])
        for v in reversed(values):
            lst.insert(0, v)

    def lrange(self, name, start, end):
        lst = self._store.get(name, [])
        return lst[start: None if end == -1 else end + 1]

    def ping(self):
        return True

    def close(self):
        pass


def _create_redis():
    try:
        import redis as redis_lib
        client = redis_lib.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password if settings.redis_password else None,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        client.ping()
        logger.info("✅ Connected to Redis at %s:%s", settings.redis_host, settings.redis_port)
        return client
    except Exception as e:
        return _FakeRedis()


redis_client = _create_redis()


def get_redis():
    """Dependency for getting the Redis client."""
    return redis_client


# ── MongoDB: optional ────────────────────────────────────────────────────────
class _FakeMongoDB:
    """Minimal MongoDB stub when the real MongoDB is unavailable."""
    def __init__(self):
        self._collections: dict = {}
        logger.warning("⚠️  MongoDB unavailable. Location data will not be persisted.")

    def __getitem__(self, name):
        return self._collections.setdefault(name, _FakeCollection(name))

    def __getattr__(self, name):
        return self._collections.setdefault(name, _FakeCollection(name))


class _FakeCollection:
    def __init__(self, name):
        self._name = name
        self._docs: list = []

    async def insert_one(self, doc):
        self._docs.append(doc)
        class _R:
            inserted_id = "fake_id"
        return _R()

    async def find_one(self, query=None):
        return None

    def find(self, query=None):
        return _FakeCursor([])

    async def update_one(self, *a, **kw):
        pass

    async def delete_one(self, *a, **kw):
        pass


class _FakeCursor:
    def __init__(self, docs):
        self._docs = docs

    def sort(self, *a, **kw):
        return self

    def limit(self, n):
        return self

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration


def _create_mongodb():
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=1000,
            connectTimeoutMS=1000,
            socketTimeoutMS=1000,
        )
        db = client[settings.mongodb_db]
        logger.info("✅ MongoDB client created for %s", settings.mongodb_db)
        return db
    except Exception as e:
        logger.warning("⚠️  MongoDB unavailable (%s). Using in-memory stub.", e)
        return _FakeMongoDB()


mongodb = _create_mongodb()


def get_mongodb():
    """Dependency for getting the MongoDB database."""
    return mongodb
