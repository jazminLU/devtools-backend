"""Repository pattern for dictionary data access."""
from abc import ABC, abstractmethod
from typing import Optional
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dictionary.db_models import DictionaryEntry


class IDictionaryRepository(ABC):
    """Interface for dictionary repository operations."""
    
    @abstractmethod
    def find_by_word(self, word: str) -> Optional[DictionaryEntry]:
        """
        Find a dictionary entry by word (case-insensitive).
        
        Args:
            word: The word to search for
            
        Returns:
            DictionaryEntry if found, None otherwise
        """
        pass
    
    @abstractmethod
    def create(self, word: str, definition: str) -> DictionaryEntry:
        """
        Create a new dictionary entry.
        
        Args:
            word: The word to add
            definition: The definition of the word
            
        Returns:
            The created DictionaryEntry
        """
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback current transaction."""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Commit current transaction."""
        pass


class DictionaryRepository(IDictionaryRepository):
    """
    Concrete implementation of dictionary repository.
    
    Handles all database operations for dictionary entries.
    """
    
    def __init__(self, db: Session) -> None:
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self._db = db
    
    def find_by_word(self, word: str) -> Optional[DictionaryEntry]:
        """
        Find a dictionary entry by word (case-insensitive).
        
        Args:
            word: The word to search for
            
        Returns:
            DictionaryEntry if found, None otherwise
        """
        if not word or not word.strip():
            return None
            
        word_lower = word.lower().strip()
        return self._db.query(DictionaryEntry).filter(
            func.lower(DictionaryEntry.word) == word_lower
        ).first()
    
    def create(self, word: str, definition: str) -> DictionaryEntry:
        """
        Create a new dictionary entry.
        
        Args:
            word: The word to add
            definition: The definition of the word
            
        Returns:
            The created DictionaryEntry
            
        Raises:
            ValueError: If word or definition is empty
        """
        if not word or not word.strip():
            raise ValueError("Word cannot be empty")
        if not definition or not definition.strip():
            raise ValueError("Definition cannot be empty")
        
        entry = DictionaryEntry(
            word=word.strip(),
            definition=definition.strip()
        )
        self._db.add(entry)
        self._db.flush()  # Flush to get ID without committing
        self._db.refresh(entry)
        return entry
    
    def commit(self) -> None:
        """Commit current transaction."""
        self._db.commit()
    
    def rollback(self) -> None:
        """Rollback current transaction."""
        self._db.rollback()
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Usage:
            with repository.transaction():
                repository.create(...)
        """
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

