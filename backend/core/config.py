import os
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024 # 50MB


# Limits
MAX_ROWS = 20000   # cap for very large CSVs to prevent OOM

# Caching
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

