import redis
import os
import time

class RedisClient:
    _instance = None
    _attempted = False
    
    @classmethod
    def get_instance(cls):
        # If we already have a connection, return it
        if cls._instance:
            return cls._instance
            
        # If we failed before, don't retry incessantly
        if cls._attempted:
            return None

        # First attempt
        cls._attempted = True
        
        # Use docker service name 'redis' by default
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        try:
            # Short timeout to fail fast
            client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=1)
            # Test connection
            client.ping()
            print(f"✅ Connected to Redis at {redis_url}")
            cls._instance = client
        except Exception as e:
            # Determine if we should log explicitly
            # Simple "host not found" is expected in local dev without docker
            msg = str(e)
            if "not known" in msg or "Connection refused" in msg:
                 print(f"ℹ️ Redis not available ({msg}). Caching disabled.")
            else:
                 print(f"⚠️ Redis connection error: {e}")
            cls._instance = None
            
        return cls._instance

# Functional helper
def get_redis():
    return RedisClient.get_instance()
