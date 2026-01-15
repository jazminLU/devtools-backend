"""Custom exception classes for the application."""
from fastapi import HTTPException, status


class DictionaryWordNotFoundError(HTTPException):
    """
    Raised when a word is not found in the dictionary.
    
    Attributes:
        status_code: HTTP 404 Not Found
        detail: Error message with the word that was not found
    """
    
    def __init__(self, word: str) -> None:
        """
        Initialize the exception.
        
        Args:
            word: The word that was not found
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Word '{word}' not found in dictionary"
        )


class DictionaryWordAlreadyExistsError(HTTPException):
    """
    Raised when attempting to add a word that already exists.
    
    Attributes:
        status_code: HTTP 409 Conflict
        detail: Error message with the word that already exists
    """
    
    def __init__(self, word: str) -> None:
        """
        Initialize the exception.
        
        Args:
            word: The word that already exists
        """
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Word '{word}' already exists in dictionary"
        )


class DatabaseConnectionError(Exception):
    """
    Raised when database connection fails.
    
    Used for database connectivity issues during startup or operations.
    """
    pass


class ServiceError(Exception):
    """
    Base exception for service layer errors.
    
    Can be extended for specific service-related errors.
    """
    pass

