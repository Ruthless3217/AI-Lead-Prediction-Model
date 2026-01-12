import sys
import os

# Add the parent directory to sys.path to allow imports from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.main import app
    print("Successfully imported backend.main.app")
except Exception as e:
    print(f"Failed to import backend.main.app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
