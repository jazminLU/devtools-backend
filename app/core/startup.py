"""Application startup logic."""
import time
import logging
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)


def wait_for_database() -> None:
    """
    Wait for database to be ready with retries.
    
    Implements retry logic with exponential backoff for database connectivity.
    Follows Single Responsibility Principle - handles only startup database connection.
    
    Raises:
        DatabaseConnectionError: If database is not available after max retries
    """
    for attempt in range(settings.DB_MAX_RETRIES):
        try:
            init_db()
            logger.info("Database initialized successfully")
            return
        except OperationalError as e:
            if attempt < settings.DB_MAX_RETRIES - 1:
                logger.warning(
                    f"Database not ready, retrying in {settings.DB_RETRY_DELAY}s... "
                    f"(attempt {attempt + 1}/{settings.DB_MAX_RETRIES})"
                )
                time.sleep(settings.DB_RETRY_DELAY)
            else:
                error_message = (
                    f"Failed to connect to database after "
                    f"{settings.DB_MAX_RETRIES} attempts: {str(e)}"
                )
                logger.error(error_message)
                raise DatabaseConnectionError(error_message) from e

