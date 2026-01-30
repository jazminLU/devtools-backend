"""Unit tests for custom exceptions."""
import pytest
from fastapi import status

from app.core.exceptions import (
    DictionaryWordNotFoundError,
    DictionaryWordAlreadyExistsError,
    DatabaseConnectionError,
    ServiceError
)


class TestDictionaryWordNotFoundError:
    """Test cases for DictionaryWordNotFoundError."""
    
    def test_initialization(self):
        """Test exception initialization."""
        word = "test"
        error = DictionaryWordNotFoundError(word)
        
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert word in str(error.detail)
        assert "not found" in str(error.detail).lower()
    
    def test_detail_message(self):
        """Test error detail message."""
        error = DictionaryWordNotFoundError("python")
        
        assert "python" in error.detail
        assert "not found" in error.detail.lower()


class TestDictionaryWordAlreadyExistsError:
    """Test cases for DictionaryWordAlreadyExistsError."""
    
    def test_initialization(self):
        """Test exception initialization."""
        word = "test"
        error = DictionaryWordAlreadyExistsError(word)
        
        assert error.status_code == status.HTTP_409_CONFLICT
        assert word in str(error.detail)
        assert "already exists" in str(error.detail).lower()
    
    def test_detail_message(self):
        """Test error detail message."""
        error = DictionaryWordAlreadyExistsError("python")
        
        assert "python" in error.detail
        assert "already exists" in error.detail.lower()


class TestDatabaseConnectionError:
    """Test cases for DatabaseConnectionError."""
    
    def test_initialization(self):
        """Test exception initialization."""
        error = DatabaseConnectionError("Connection failed")
        
        assert isinstance(error, Exception)
        assert "Connection failed" in str(error)


class TestServiceError:
    """Test cases for ServiceError."""
    
    def test_initialization(self):
        """Test exception initialization."""
        error = ServiceError("Service error occurred")
        
        assert isinstance(error, Exception)
        assert "Service error occurred" in str(error)

