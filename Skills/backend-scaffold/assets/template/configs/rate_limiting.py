"""
Rate limiting via SlowAPI (Redis-backed). Decorate sensitive endpoints with the
RateLimitConfig constants; the decorated handler MUST accept `request: Request`.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from configs.settings import settings


def get_rate_limit_key(request) -> str:
    """Rate-limit by client IP (extend to user id via request.state.user_id)."""
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    enabled=settings.RATE_LIMIT_ENABLED,
    storage_uri=settings.REDIS_URL,
)


class RateLimitConfig:
    """Named rate limits — use these instead of raw strings."""
    LOGIN = "10/minute"
    REGISTER = "5/minute"
    OTP_VERIFICATION = "5/minute"
    REFRESH_TOKEN = "30/minute"
    FORGOT_PASSWORD = "5/minute"
    LIST_RESOURCES = "100/minute"
    CREATE_RESOURCE = "30/minute"
    UPDATE_RESOURCE = "60/minute"
    DELETE_RESOURCE = "30/minute"
