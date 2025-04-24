import os
import redis


redis_host = os.environ.get("REDIS_HOST", "redis_")
redis_port = os.environ.get("REDIS_PORT", 6370)


redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)