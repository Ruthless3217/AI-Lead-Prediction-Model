import hashlib
import json
from .redis_client import get_redis

class ChatCache:
    TTL = 3600 * 24 # 24 Hours cache
    
    @staticmethod
    def _generate_key(message, context):
        """Generate a deterministic key for the prompt"""
        # We only cache based on message + context content
        # Sort context if it's a dict, or just stringify
        content = f"{str(message)}|{str(context)}"
        return f"chat_cache:{hashlib.md5(content.encode()).hexdigest()}"

    @staticmethod
    def get_cached_response(message, context):
        r = get_redis()
        if not r: return None
        
        try:
            key = ChatCache._generate_key(message, context)
            val = r.get(key)
            if val:
                print("⚡ Cache Hit for chat query")
                return val
        except Exception as e:
            print(f"Cache Read Error: {e}")
            return None
            
    @staticmethod
    def cache_response(message, context, response):
        r = get_redis()
        if not r: return
        
        try:
            key = ChatCache._generate_key(message, context)
            r.setex(key, ChatCache.TTL, response)
        except Exception as e:
            print(f"Cache Write Error: {e}")
