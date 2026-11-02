"""
health.py

System Health Check & Diagnostic Endpoint for SmartRoute AI
Verifies that the FastAPI application is alive, operational, and responsive.
"""

from fastapi import APIRouter, status
from datetime import datetime, timezone
from app.config import settings
from app.database import db_manager

router = APIRouter(prefix="/health", tags=["System Health"])

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="API Health Check",
    description="Returns current operational status, API version, server environment, and database diagnostics."
)
async def check_health():
    """
    Diagnostic endpoint to verify server responsiveness and database connectivity.
    """
    db_status = db_manager.get_status()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "modules": {
            "navigation_engine": "ready",
            "cors_middleware": "active",
            "api_prefix": settings.API_PREFIX
        }
    }
