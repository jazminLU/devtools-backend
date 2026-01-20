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

# Create FastAPI application with enhanced OpenAPI/Swagger configuration
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    A collection of developer utilities
    
    ## Interactive Documentation
    
    This API includes interactive documentation (Swagger UI) that allows you to:
    - Test all endpoints directly from the browser
    - View request and response examples
    - Validate your data before sending
    - No need to start the frontend for testing
    
    ## Available Endpoints
    
    ### Dictionary
    - POST /dictionary/add - Add word to dictionary
    - GET /dictionary/{{word}} - Search word definition
    
    ### Shopping Calculator
    - POST /shopping/total - Calculate shopping total with tax
      - Accepts JSON or simple text format (auto-detects)
    
    ### Word Concatenation
    - POST /word/concat - Concatenate characters from words
    
    ## Documentation Access
    
    - Swagger UI (Interactive): http://localhost:8000/docs
    - ReDoc (Alternative): http://localhost:8000/redoc
    - OpenAPI JSON: http://localhost:8000/openapi.json
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "DevTools Playground",
        "email": "support@devtools.local"
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {
            "name": "Dictionary",
            "description": "Operaciones para gestionar un diccionario de palabras y definiciones. Requiere base de datos PostgreSQL.",
        },
        {
            "name": "Shopping",
            "description": "Calculadora de compras que calcula totales con impuestos. Acepta formato JSON o texto simple.",
        },
        {
            "name": "Words",
            "description": "Herramienta para concatenar caracteres específicos de palabras según su posición.",
        },
    ],
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


@app.get(
    "/",
    tags=["Info"],
    summary="API Information",
    description="Root endpoint with API information and links to documentation"
)
async def root() -> dict:
    """
    Root endpoint with API information.
    
    Returns basic information about the API and links to interactive documentation.
    """
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "dictionary": "/dictionary",
            "shopping": "/shopping",
            "words": "/word",
            "health": "/health"
        }
    }


@app.get(
    "/health",
    tags=["Info"],
    summary="Health Check",
    description="Health check endpoint to verify the API is running"
)
async def health() -> dict:
    """
    Health check endpoint.
    
    Use this endpoint to verify that the API is running and responding.
    Returns a simple status message.
    """
    return {"status": "healthy"}

