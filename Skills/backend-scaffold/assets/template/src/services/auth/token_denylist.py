"""
Token denylist — Redis-based JWT revocation. `jti` keys auto-expire with the token.
"""
import uuid
from datetime import datetime, timezone

import redis.asyncio as redis

from configs.settings import settings


class TokenDenylistService:
    PREFIX = "token:denied:"

    def __init__(self, redis_client: redis.Redis | None = None):
        self._redis = redis_client
        self._redis_url = settings.REDIS_URL

    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = await redis.from_url(
                self._redis_url, encoding="utf-8", decode_responses=True,
            )
        return self._redis

    async def add_to_denylist(self, jti: str, expires_at: datetime | None = None,
                              ttl_seconds: int | None = None) -> None:
        r = await self._get_redis()
        if ttl_seconds is not None:
            ttl = ttl_seconds
        elif expires_at is not None:
            ttl = max(int((expires_at - datetime.now(timezone.utc)).total_seconds()), 1)
        else:
            ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        await r.setex(f"{self.PREFIX}{jti}", ttl, "1")

    async def is_denied(self, jti: str) -> bool:
        r = await self._get_redis()
        return (await r.exists(f"{self.PREFIX}{jti}")) > 0

    async def deny_all_for_user(self, user_id: uuid.UUID, ttl_seconds: int | None = None) -> None:
        r = await self._get_redis()
        ttl = ttl_seconds or (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        await r.setex(f"{self.PREFIX}user:{user_id}", ttl, "1")

    async def un_deny_all_for_user(self, user_id: uuid.UUID) -> None:
        r = await self._get_redis()
        await r.delete(f"{self.PREFIX}user:{user_id}")

    async def is_user_denied(self, user_id: uuid.UUID) -> bool:
        r = await self._get_redis()
        return (await r.exists(f"{self.PREFIX}user:{user_id}")) > 0


# Global singleton
token_denylist = TokenDenylistService()
