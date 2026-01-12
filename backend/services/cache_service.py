import hashlib
import json
import os
from typing import Dict, Any, Optional
from backend.core.config import REDIS_URL

# Try importing redis, but don't crash if missing (though it should be installed)
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis library not installed. Falling back to in-memory cache.")

def compute_file_hash(file_path: str, chunk_size: int = 4096) -> str:
    """
    Computes the SHA-256 fingerprint of a file's content.
    Determinisitcally identifies the file regardless of filename.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error computing hash: {e}")
        return "unknown_hash"

class CacheService:
    """
    Hybrid Cache Service:
    1. Attempts to use Redis for production-grade caching.
    2. Falls back to in-memory dictionary if Redis is unavailable.
    """
    def __init__(self, redis_url: str = REDIS_URL):
        self.redis_client = None
        self.memory_cache = {}
        
        if REDIS_AVAILABLE:
            try:
                # Initialize Redis client
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Quick ping to verify connection
                self.redis_client.ping()
                print(f"✅ Connected to Redis at {redis_url}")
            except Exception as e:
                print(f"⚠️ Redis connection failed ({e}). using in-memory fallback.")
                self.redis_client = None
        
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache (Redis or Memory)"""
        try:
            if self.redis_client:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
                return None
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            print(f"Cache GET error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (default 1 hour)"""
        try:
            json_val = json.dumps(value)
            
            if self.redis_client:
                self.redis_client.setex(key, ttl, json_val)
            else:
                self.memory_cache[key] = value
                # Note: Memory cache doesn't implement TTL clean-up in this simple version
        except Exception as e:
            print(f"Cache SET error: {e}")

# Global Instance
cache_service = CacheService()
