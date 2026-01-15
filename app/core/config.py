"""Application configuration module using Pydantic Settings."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic Settings for validation and type safety.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database settings
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: str = Field(default="5432", description="Database port")
    DB_NAME: str = Field(default="devtools", description="Database name")
    DB_USER: str = Field(default="devtools", description="Database user")
    DB_PASSWORD: str = Field(default="devtools", description="Database password")
    DATABASE_URL: str | None = Field(default=None, description="Full database URL (optional)")
    
    # Application settings
    APP_NAME: str = Field(default="DevTools Playground API", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    APP_DESCRIPTION: str = Field(
        default="A collection of developer utilities",
        description="Application description"
    )
    
    # CORS settings
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Allowed CORS origins (comma-separated)"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        if not self.CORS_ORIGINS:
            return []
        # Support JSON array format or comma-separated values
        if self.CORS_ORIGINS.strip().startswith('['):
            import json
            return json.loads(self.CORS_ORIGINS)
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]
    
    # Database connection retry settings
    DB_MAX_RETRIES: int = Field(default=30, ge=1, description="Max database connection retries")
    DB_RETRY_DELAY: int = Field(default=2, ge=1, description="Delay between retries in seconds")
    
    @property
    def database_url(self) -> str:
        """
        Construct database URL from components or use provided URL.
        
        Returns:
            Complete database connection URL
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    @property
    def is_sqlite(self) -> bool:
        """
        Check if using SQLite database.
        
        Returns:
            True if database URL contains 'sqlite', False otherwise
        """
        return "sqlite" in self.database_url.lower()


# Global settings instance
settings = Settings()

