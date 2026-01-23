"""Unit tests for dictionary repository."""
import pytest
from sqlalchemy.orm import Session

from app.dictionary.repository import DictionaryRepository
from app.dictionary.db_models import DictionaryEntry


class TestDictionaryRepository:
    """Test cases for DictionaryRepository."""
    
    def test_find_by_word_exists(self, db_session):
        """Test finding an existing word."""
        # Create a word first
        entry = DictionaryEntry(word="test", definition="A test")
        db_session.add(entry)
        db_session.commit()
        
        repository = DictionaryRepository(db_session)
        result = repository.find_by_word("test")
        
        assert result is not None
        assert result.word == "test"
        assert result.definition == "A test"
    
    def test_find_by_word_case_insensitive(self, db_session):
        """Test case-insensitive word search."""
        entry = DictionaryEntry(word="test", definition="A test")
        db_session.add(entry)
        db_session.commit()
        
        repository = DictionaryRepository(db_session)
        
        # Should find with different cases
        assert repository.find_by_word("TEST") is not None
        assert repository.find_by_word("Test") is not None
        assert repository.find_by_word("test") is not None
    
    def test_find_by_word_not_exists(self, db_session):
        """Test finding a non-existent word."""
        repository = DictionaryRepository(db_session)
        result = repository.find_by_word("nonexistent")
        
        assert result is None
    
    def test_find_by_word_empty_string(self, db_session):
        """Test finding with empty string."""
        repository = DictionaryRepository(db_session)
        result = repository.find_by_word("")
        
        assert result is None
    
    def test_create_word_success(self, db_session):
        """Test successfully creating a word."""
        repository = DictionaryRepository(db_session)
        entry = repository.create("test", "A test definition")
        
        assert entry.word == "test"
        assert entry.definition == "A test definition"
        assert entry.id is not None
    
    def test_create_word_strips_whitespace(self, db_session):
        """Test that word and definition are stripped."""
        repository = DictionaryRepository(db_session)
        entry = repository.create("  test  ", "  A test  ")
        
        assert entry.word == "test"
        assert entry.definition == "A test"
    
    def test_create_word_empty_word_raises_error(self, db_session):
        """Test that empty word raises error."""
        repository = DictionaryRepository(db_session)
        
        with pytest.raises(ValueError, match="Word cannot be empty"):
            repository.create("", "definition")
        
        with pytest.raises(ValueError, match="Word cannot be empty"):
            repository.create("   ", "definition")
    
    def test_create_word_empty_definition_raises_error(self, db_session):
        """Test that empty definition raises error."""
        repository = DictionaryRepository(db_session)
        
        with pytest.raises(ValueError, match="Definition cannot be empty"):
            repository.create("word", "")
        
        with pytest.raises(ValueError, match="Definition cannot be empty"):
            repository.create("word", "   ")
    
    def test_commit(self, db_session):
        """Test commit operation."""
        repository = DictionaryRepository(db_session)
        entry = repository.create("test", "A test")
        
        # Entry should not be committed yet
        db_session.rollback()
        db_session.refresh(entry, attribute_names=[])
        
        # Now commit
        repository.commit()
        
        # Verify it's persisted
        result = repository.find_by_word("test")
        assert result is not None
    
    def test_rollback(self, db_session):
        """Test rollback operation."""
        repository = DictionaryRepository(db_session)
        entry = repository.create("test", "A test")
        repository.rollback()
        
        # Entry should not be persisted
        result = repository.find_by_word("test")
        assert result is None
    
    def test_transaction_context_manager_success(self, db_session):
        """Test transaction context manager on success."""
        repository = DictionaryRepository(db_session)
        
        with repository.transaction():
            repository.create("test", "A test")
        
        # Should be committed
        result = repository.find_by_word("test")
        assert result is not None
    
    def test_transaction_context_manager_rollback(self, db_session):
        """Test transaction context manager on exception."""
        repository = DictionaryRepository(db_session)
        
        with pytest.raises(ValueError):
            with repository.transaction():
                repository.create("test", "A test")
                raise ValueError("Test error")
        
        # Should be rolled back
        result = repository.find_by_word("test")
        assert result is None

