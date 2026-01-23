"""Unit tests for application configuration."""
import pytest
import os
from unittest.mock import patch

from app.core.config import Settings


class TestSettings:
    """Test cases for Settings class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        settings = Settings()
        
        assert settings.DB_HOST == "localhost"
        assert settings.DB_PORT == "5432"
        assert settings.DB_NAME == "devtools"
        assert settings.APP_NAME == "DevTools Playground API"
        assert settings.APP_VERSION == "1.0.0"
    
    def test_cors_origins_list_comma_separated(self):
        """Test parsing comma-separated CORS origins."""
        settings = Settings(CORS_ORIGINS="http://localhost:3000,http://localhost:5173")
        
        origins = settings.cors_origins_list
        
        assert len(origins) == 2
        assert "http://localhost:3000" in origins
        assert "http://localhost:5173" in origins
    
    def test_cors_origins_list_json_format(self):
        """Test parsing JSON array format CORS origins."""
        settings = Settings(CORS_ORIGINS='["http://localhost:3000", "http://localhost:5173"]')
        
        origins = settings.cors_origins_list
        
        assert len(origins) == 2
        assert "http://localhost:3000" in origins
        assert "http://localhost:5173" in origins
    
    def test_cors_origins_list_empty(self):
        """Test empty CORS origins."""
        settings = Settings(CORS_ORIGINS="")
        
        origins = settings.cors_origins_list
        
        assert origins == []
    
    def test_cors_origins_list_with_whitespace(self):
        """Test CORS origins with whitespace."""
        settings = Settings(CORS_ORIGINS=" http://localhost:3000 , http://localhost:5173 ")
        
        origins = settings.cors_origins_list
        
        assert len(origins) == 2
        assert "http://localhost:3000" in origins
        assert "http://localhost:5173" in origins
    
    def test_database_url_from_components(self):
        """Test database URL construction from components."""
        settings = Settings(
            DB_USER="testuser",
            DB_PASSWORD="testpass",
            DB_HOST="testhost",
            DB_PORT="5433",
            DB_NAME="testdb"
        )
        
        url = settings.database_url
        
        assert url == "postgresql://testuser:testpass@testhost:5433/testdb"
    
    def test_database_url_from_full_url(self):
        """Test database URL from DATABASE_URL."""
        settings = Settings(DATABASE_URL="postgresql://user:pass@host:5432/db")
        
        url = settings.database_url
        
        assert url == "postgresql://user:pass@host:5432/db"
    
    def test_is_sqlite_true(self):
        """Test SQLite detection."""
        settings = Settings(DATABASE_URL="sqlite:///test.db")
        
        assert settings.is_sqlite is True
    
    def test_is_sqlite_false(self):
        """Test non-SQLite detection."""
        settings = Settings(DATABASE_URL="postgresql://user:pass@host:5432/db")
        
        assert settings.is_sqlite is False
    
    def test_is_sqlite_case_insensitive(self):
        """Test SQLite detection is case-insensitive."""
        settings = Settings(DATABASE_URL="SQLITE:///test.db")
        
        assert settings.is_sqlite is True

