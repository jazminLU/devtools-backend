"""Business logic layer for dictionary operations."""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    DictionaryWordNotFoundError,
    DictionaryWordAlreadyExistsError
)
from app.dictionary.repository import IDictionaryRepository, DictionaryRepository
from app.dictionary.db_models import DictionaryEntry

logger = logging.getLogger(__name__)


class DictionaryService:
    """
    Service for dictionary business logic.
    
    Implements business rules and orchestrates repository operations.
    Follows Single Responsibility Principle - handles business logic only.
    """
    
    def __init__(self, repository: IDictionaryRepository) -> None:
        """
        Initialize service with repository dependency.
        
        Args:
            repository: Dictionary repository implementation
        """
        self._repository = repository
    
    def add_word(self, word: str, definition: str) -> DictionaryEntry:
        """
        Add a word with its definition to the dictionary.
        
        Validates input, checks for duplicates (case-insensitive), and creates
        a new dictionary entry. Normalizes word to lowercase for storage.
        
        Args:
            word: The word to add (will be normalized to lowercase)
            definition: The definition of the word
            
        Returns:
            The created dictionary entry
            
        Raises:
            DictionaryWordAlreadyExistsError: If word already exists (case-insensitive)
            ValueError: If word or definition is invalid
        """
        # Validate and normalize inputs
        self._validate_word_input(word, definition)
        normalized_word = word.strip().lower()
        normalized_definition = definition.strip()
        
        # Check if word already exists (case-insensitive)
        existing = self._repository.find_by_word(normalized_word)
        if existing:
            logger.warning(
                f"Attempted to add duplicate word: '{word}' "
                f"(normalized: '{normalized_word}')"
            )
            raise DictionaryWordAlreadyExistsError(normalized_word)
        
        # Create entry with transaction handling
        try:
            entry = self._repository.create(normalized_word, normalized_definition)
            self._repository.commit()
            logger.info(
                f"Successfully added word: '{normalized_word}' "
                f"with definition: '{normalized_definition[:50]}...'"
            )
            return entry
        except IntegrityError as e:
            self._repository.rollback()
            logger.error(
                f"Database integrity error adding word: '{normalized_word}' - {str(e)}"
            )
            raise DictionaryWordAlreadyExistsError(normalized_word)
        except ValueError as e:
            self._repository.rollback()
            logger.error(f"Validation error adding word: '{word}' - {str(e)}")
            raise
    
    def get_word(self, word: str) -> DictionaryEntry:
        """
        Retrieve a dictionary entry by word (case-insensitive search).
        
        Normalizes the input word to lowercase for lookup. Returns the
        dictionary entry if found, otherwise raises an exception.
        
        Args:
            word: The word to retrieve (will be normalized to lowercase)
            
        Returns:
            The dictionary entry with word and definition
            
        Raises:
            DictionaryWordNotFoundError: If word not found (after normalization)
            ValueError: If word is invalid or empty
        """
        if not word or not word.strip():
            raise ValueError("Word cannot be empty or only whitespace")
        
        normalized_word = word.strip().lower()
        entry = self._repository.find_by_word(normalized_word)
        
        if not entry:
            logger.warning(
                f"Word not found: '{word}' (searched as: '{normalized_word}')"
            )
            raise DictionaryWordNotFoundError(normalized_word)
        
        logger.info(f"Retrieved definition for word: '{normalized_word}'")
        return entry
    
    @staticmethod
    def _validate_word_input(word: str, definition: str) -> None:
        """
        Validate word and definition inputs.
        
        Args:
            word: The word to validate
            definition: The definition to validate
            
        Raises:
            ValueError: If validation fails
        """
        if not word or not word.strip():
            raise ValueError("Word cannot be empty")
        if not definition or not definition.strip():
            raise ValueError("Definition cannot be empty")


def get_dictionary_service(db: Session) -> DictionaryService:
    """
    Factory function to create dictionary service with repository.
    
    Implements Dependency Injection pattern.
    
    Args:
        db: Database session
        
    Returns:
        Configured DictionaryService instance
    """
    repository = DictionaryRepository(db)
    return DictionaryService(repository)

