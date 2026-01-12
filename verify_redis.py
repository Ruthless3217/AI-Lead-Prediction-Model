import redis
import sys

try:
    print("Attempting to connect to Redis at localhost:6379...")
    r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
    r.ping()
    print("✅ Connection Successful! Redis is UP and RUNNING.")
    r.set('test_key', 'Hello Redis')
    print(f"Test Key Value: {r.get('test_key').decode('utf-8')}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    sys.exit(1)
