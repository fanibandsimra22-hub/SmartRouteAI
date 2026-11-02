"""
main.py

SmartRoute AI – Core FastAPI Application Entry Point
Initializes FastAPI, configures CORS, registers API routers, and defines lifespan handlers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from app.config import settings
from app.database import db_manager
from app.routes.health import router as health_router
from app.routes.locations import router as locations_router
from app.routes.routing import router as routing_router
from app.routes.routes_history import router as routes_history_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("smartroute.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for application startup and shutdown."""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Debug: {settings.DEBUG}")
    logger.info(f"Permitted CORS Origins: {settings.CORS_ORIGINS}")
    logger.info(f"Swagger Documentation: http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}/docs")
    logger.info("=" * 60)
    
    # Initialize Database Connection
    db_manager.connect()

    yield

    # Teardown
    db_manager.close()
    logger.info(f"Shutting down {settings.PROJECT_NAME} gracefully...")

# Initialize FastAPI instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "SmartRoute AI – AI-Powered Real-World City Navigation System REST API.\n\n"
        "Provides road network graph calculations (A*, Dijkstra), traffic penalty integration, "
        "geocoding, and user navigation history management."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS) for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler for unhandled errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred in the SmartRoute AI backend engine.",
            "path": request.url.path
        }
    )

# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API Root Information",
    description="Returns welcome information, API documentation links, and active version."
)
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "health_check": f"{settings.API_PREFIX}/health"
    }

# Register API Routers under settings.API_PREFIX (/api)
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(locations_router, prefix=settings.API_PREFIX)
app.include_router(routing_router, prefix=settings.API_PREFIX)
app.include_router(routes_history_router, prefix=settings.API_PREFIX)
