"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.startup import wait_for_database
from app.dictionary.router import router as dictionary_router
from app.shopping.router import router as shopping_router
from app.words.router import router as words_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application on startup."""
    wait_for_database()
    logger.info("Application startup complete")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    dictionary_router,
    prefix="/dictionary",
    tags=["Dictionary"]
)
app.include_router(
    shopping_router,
    prefix="/shopping",
    tags=["Shopping"]
)
app.include_router(
    words_router,
    prefix="/word",
    tags=["Words"]
)


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}

