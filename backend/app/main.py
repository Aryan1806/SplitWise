"""
Main FastAPI Application
Entry point for the SplitMint backend API.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.config import settings
from app.database import engine, Base
from app.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="SplitMint API",
    description="Backend API for SplitMint - AI-powered expense splitting application",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS Middleware
# Allows frontend to make requests from different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # List of allowed origins
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    
    Returns user-friendly error messages for invalid input.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors.
    
    Logs the error and returns a generic message to the user.
    """
    logger.error(f"Database error: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "A database error occurred. Please try again later."
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other uncaught exceptions.
    
    Prevents exposing internal errors to users.
    """
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later."
        }
    )


# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """
    Run when the application starts.
    
    Creates database tables if they don't exist.
    """
    logger.info("Starting up SplitMint API...")
    
    # Create tables (in production, use Alembic migrations instead)
    if settings.DEBUG:
        logger.info("Debug mode: Creating database tables if they don't exist")
        Base.metadata.create_all(bind=engine)
    
    logger.info("SplitMint API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run when the application shuts down.
    
    Clean up resources.
    """
    logger.info("Shutting down SplitMint API...")


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        200 OK if the service is running
    
    Example Response:
        {
            "status": "healthy",
            "version": "1.0.0",
            "environment": "development"
        }
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.
    
    Returns basic API information.
    """
    return {
        "message": "Welcome to SplitMint API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "health": "/health"
    }


# Include API Router
# All API routes will be prefixed with /api
app.include_router(api_router, prefix="/api")


# Main entry point for running with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,  # Auto-reload on code changes in debug mode
        log_level="info" if settings.DEBUG else "warning"
    )