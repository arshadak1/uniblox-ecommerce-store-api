"""
Main FastAPI application module.
Sets up the application with all routers, middleware, and configuration.
"""
import logging
from fastapi import FastAPI

from app.config import settings
from app.routers import cart

# logging config
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# all routers
app.include_router(cart.router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": f"{settings.API_PREFIX}/admin/health"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Simple health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
