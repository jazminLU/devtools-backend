"""Unit tests for startup logic."""
import pytest
import time
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError

from app.core.startup import wait_for_database
from app.core.exceptions import DatabaseConnectionError


class TestWaitForDatabase:
    """Test cases for wait_for_database function."""
    
    @patch('app.core.startup.init_db')
    def test_wait_for_database_success_first_attempt(self, mock_init_db):
        """Test successful database connection on first attempt."""
        mock_init_db.return_value = None
        
        # Should not raise
        wait_for_database()
        
        mock_init_db.assert_called_once()
    
    @patch('app.core.startup.time.sleep')
    @patch('app.core.startup.init_db')
    def test_wait_for_database_retries_on_failure(self, mock_init_db, mock_sleep):
        """Test retry logic on database connection failure."""
        # Fail first two attempts, succeed on third
        mock_init_db.side_effect = [
            OperationalError("", "", ""),
            OperationalError("", "", ""),
            None
        ]
        
        wait_for_database()
        
        assert mock_init_db.call_count == 3
        assert mock_sleep.call_count == 2
    
    @patch('app.core.startup.settings')
    @patch('app.core.startup.time.sleep')
    @patch('app.core.startup.init_db')
    def test_wait_for_database_max_retries(self, mock_init_db, mock_sleep, mock_settings):
        """Test that max retries are respected."""
        mock_settings.DB_MAX_RETRIES = 3
        mock_settings.DB_RETRY_DELAY = 0.1
        mock_init_db.side_effect = OperationalError("", "", "")
        
        with pytest.raises(DatabaseConnectionError):
            wait_for_database()
        
        assert mock_init_db.call_count == 3
        assert mock_sleep.call_count == 2  # Sleeps between attempts, not after last

