"""
Application lifespan: database, Redis, and the APScheduler background scheduler.
"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
import redis.asyncio as aioredis
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from configs.settings import settings
from configs.database import init_db, close_db
from configs.rate_limiting import limiter

logger = logging.getLogger(__name__)

# Global Redis client (imported as `from configs import redis_client`)
redis_client: aioredis.Redis | None = None

# Background job scheduler
scheduler = AsyncIOScheduler()


async def init_redis() -> aioredis.Redis:
    """Initialize the global Redis connection."""
    global redis_client
    redis_client = await aioredis.from_url(
        settings.REDIS_URL,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        encoding="utf-8",
        decode_responses=True,
    )
    logger.info("Redis connection established")
    return redis_client


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


def _register_scheduled_jobs() -> None:
    """Register periodic background jobs here (APScheduler).

    Example:
        from src.services.example.example_scheduler import ExampleScheduler
        scheduler.add_job(
            ExampleScheduler.run, trigger="interval", minutes=15,
            id="example_job", replace_existing=True,
        )
    """
    # No jobs by default.
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Optional Sentry init (only when DSN is set)
    if settings.SENTRY_DSN:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=0.1,
            environment="development" if settings.DEBUG else "production",
        )
        logger.info("Sentry initialized")

    await init_db()
    logger.info("Database connection established")

    await init_redis()

    app.state.limiter = limiter

    _register_scheduled_jobs()
    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))

    yield

    logger.info("Shutting down...")
    scheduler.shutdown(wait=False)
    await close_redis()
    await close_db()
    logger.info("Database connection closed")
