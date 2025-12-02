"""
Main FastAPI application module.
Sets up the application with all routers, middleware, and configuration.
"""
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from starlette.responses import FileResponse

from app.config import settings
from app.routers import cart, checkout, admin, products

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
    docs_url="/docs"
)

# Static Files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Static files mounted from: {static_dir}")


# all routers
app.include_router(cart.router, prefix=settings.API_PREFIX)
app.include_router(checkout.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)
app.include_router(products.router, prefix=settings.API_PREFIX)


@app.get("/api", tags=["Root"])
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


@app.get("/", include_in_schema=False)
async def index():
    """
    Serve the frontend HTML file.
    """
    static_file = os.path.join(static_dir, "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    else:
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": f"{settings.API_V1_PREFIX}/admin/health",
            "note": "Frontend not found. Place index.html in the 'static' folder."
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
