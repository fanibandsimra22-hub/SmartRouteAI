"""
run_backend.py

Single-command development launcher for SmartRoute AI FastAPI Backend.
Executes Uvicorn with hot-reloading enabled.
"""

import uvicorn
import os
import sys

# Ensure backend directory is in Python module search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("-" * 65)
    print("  Starting SmartRoute AI FastAPI Backend Server")
    print("  URL: http://127.0.0.1:8000")
    print("  API Docs (Swagger UI): http://127.0.0.1:8000/docs")
    print("  Health Check: http://127.0.0.1:8000/api/health")
    print("-" * 65)
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
