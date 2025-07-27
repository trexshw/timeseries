"""Main FastAPI application entry point."""

from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.stock_routes import router as stock_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(stock_router)

    return app


# Create the application instance
app = create_app()


@app.get("/", response_model=dict)
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Stock Trading Data Management System API",
        "version": settings.api_version,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", response_model=dict)
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.api_version,
        "environment": settings.environment
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
