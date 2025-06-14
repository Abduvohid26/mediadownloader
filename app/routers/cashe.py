import os
import redis


redis_host = os.environ.get("REDIS_HOST", "redis")
redis_port = os.environ.get("REDIS_PORT", 6379)


redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)



import secrets


async def generate_unique_id():
    return secrets.token_urlsafe(16)


