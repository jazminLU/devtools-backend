"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Create engine with connection pooling
connect_args = {}
if settings.is_sqlite:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,    # Recycle connections after 5 minutes
    echo=False,          # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI routes.
    
    Provides a database session and ensures it's properly closed.
    Implements dependency injection pattern.
    
    Yields:
        Database session
        
    Example:
        @router.get("/items")
        async def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This should be called on application startup.
    Imports all models to ensure they're registered with Base.
    """
    # Import all models to ensure they're registered with Base
    from app.dictionary.db_models import DictionaryEntry  # noqa
    
    Base.metadata.create_all(bind=engine)

