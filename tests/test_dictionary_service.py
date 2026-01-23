"""Unit tests for dictionary service."""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from unittest.mock import Mock, MagicMock

from app.dictionary.service import DictionaryService, get_dictionary_service
from app.dictionary.repository import IDictionaryRepository
from app.dictionary.db_models import DictionaryEntry
from app.core.exceptions import (
    DictionaryWordNotFoundError,
    DictionaryWordAlreadyExistsError
)


class TestDictionaryService:
    """Test cases for DictionaryService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repository = Mock(spec=IDictionaryRepository)
        self.service = DictionaryService(self.mock_repository)
    
    def test_add_word_success(self):
        """Test successfully adding a word."""
        word = "test"
        definition = "A test definition"
        normalized_word = "test"
        normalized_definition = "A test definition"
        
        mock_entry = DictionaryEntry(
            word=normalized_word,
            definition=normalized_definition
        )
        
        self.mock_repository.find_by_word.return_value = None
        self.mock_repository.create.return_value = mock_entry
        
        result = self.service.add_word(word, definition)
        
        assert result == mock_entry
        self.mock_repository.find_by_word.assert_called_once_with(normalized_word)
        self.mock_repository.create.assert_called_once_with(normalized_word, normalized_definition)
        self.mock_repository.commit.assert_called_once()
    
    def test_add_word_normalizes_input(self):
        """Test that word and definition are normalized."""
        word = "  TEST  "
        definition = "  A Test Definition  "
        normalized_word = "test"
        normalized_definition = "A Test Definition"
        
        mock_entry = DictionaryEntry(word=normalized_word, definition=normalized_definition)
        
        self.mock_repository.find_by_word.return_value = None
        self.mock_repository.create.return_value = mock_entry
        
        self.service.add_word(word, definition)
        
        self.mock_repository.find_by_word.assert_called_once_with(normalized_word)
        self.mock_repository.create.assert_called_once_with(normalized_word, normalized_definition)
    
    def test_add_word_case_insensitive(self):
        """Test that word is stored in lowercase."""
        word = "Python"
        definition = "A programming language"
        
        self.mock_repository.find_by_word.return_value = None
        self.mock_repository.create.return_value = Mock()
        
        self.service.add_word(word, definition)
        
        self.mock_repository.find_by_word.assert_called_once_with("python")
        self.mock_repository.create.assert_called_once_with("python", "A programming language")
    
    def test_add_word_duplicate_raises_error(self):
        """Test that adding duplicate word raises error."""
        word = "test"
        definition = "A test"
        existing_entry = DictionaryEntry(word="test", definition="Existing")
        
        self.mock_repository.find_by_word.return_value = existing_entry
        
        with pytest.raises(DictionaryWordAlreadyExistsError):
            self.service.add_word(word, definition)
        
        self.mock_repository.create.assert_not_called()
        self.mock_repository.commit.assert_not_called()
    
    def test_add_word_integrity_error_handled(self):
        """Test that IntegrityError is caught and converted."""
        word = "test"
        definition = "A test"
        
        self.mock_repository.find_by_word.return_value = None
        self.mock_repository.create.side_effect = IntegrityError("", "", "")
        
        with pytest.raises(DictionaryWordAlreadyExistsError):
            self.service.add_word(word, definition)
        
        self.mock_repository.rollback.assert_called_once()
    
    def test_add_word_validation_error(self):
        """Test that validation errors are raised."""
        with pytest.raises(ValueError, match="Word cannot be empty"):
            self.service.add_word("", "definition")
        
        with pytest.raises(ValueError, match="Definition cannot be empty"):
            self.service.add_word("word", "")
        
        with pytest.raises(ValueError, match="Word cannot be empty"):
            self.service.add_word("   ", "definition")
    
    def test_get_word_success(self):
        """Test successfully retrieving a word."""
        word = "test"
        normalized_word = "test"
        mock_entry = DictionaryEntry(word="test", definition="A test")
        
        self.mock_repository.find_by_word.return_value = mock_entry
        
        result = self.service.get_word(word)
        
        assert result == mock_entry
        self.mock_repository.find_by_word.assert_called_once_with(normalized_word)
    
    def test_get_word_normalizes_input(self):
        """Test that search word is normalized."""
        word = "  TEST  "
        normalized_word = "test"
        mock_entry = DictionaryEntry(word="test", definition="A test")
        
        self.mock_repository.find_by_word.return_value = mock_entry
        
        self.service.get_word(word)
        
        self.mock_repository.find_by_word.assert_called_once_with(normalized_word)
    
    def test_get_word_case_insensitive(self):
        """Test case-insensitive word retrieval."""
        word = "Python"
        mock_entry = DictionaryEntry(word="python", definition="A language")
        
        self.mock_repository.find_by_word.return_value = mock_entry
        
        result = self.service.get_word(word)
        
        assert result == mock_entry
        self.mock_repository.find_by_word.assert_called_once_with("python")
    
    def test_get_word_not_found_raises_error(self):
        """Test that missing word raises error."""
        word = "nonexistent"
        
        self.mock_repository.find_by_word.return_value = None
        
        with pytest.raises(DictionaryWordNotFoundError):
            self.service.get_word(word)
    
    def test_get_word_empty_raises_error(self):
        """Test that empty word raises error."""
        with pytest.raises(ValueError, match="Word cannot be empty"):
            self.service.get_word("")
        
        with pytest.raises(ValueError, match="Word cannot be empty"):
            self.service.get_word("   ")
    
    def test_validate_word_input_valid(self):
        """Test validation with valid inputs."""
        # Should not raise
        DictionaryService._validate_word_input("word", "definition")
        DictionaryService._validate_word_input("  word  ", "  definition  ")
    
    def test_validate_word_input_invalid(self):
        """Test validation with invalid inputs."""
        with pytest.raises(ValueError, match="Word cannot be empty"):
            DictionaryService._validate_word_input("", "definition")
        
        with pytest.raises(ValueError, match="Definition cannot be empty"):
            DictionaryService._validate_word_input("word", "")
        
        with pytest.raises(ValueError, match="Word cannot be empty"):
            DictionaryService._validate_word_input("   ", "definition")


class TestGetDictionaryService:
    """Test cases for get_dictionary_service factory."""
    
    def test_get_dictionary_service_creates_service(self, db_session):
        """Test that factory creates service with repository."""
        service = get_dictionary_service(db_session)
        
        assert isinstance(service, DictionaryService)
        assert service._repository is not None

