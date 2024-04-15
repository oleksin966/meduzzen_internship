from aioredis import Redis
from core.config import settings

REDIS_URL = settings.redis_url

async def get_redis_client() -> Redis:
    redis = Redis.from_url(
        REDIS_URL, max_connections=10, decode_responses=True
    )
    return redis