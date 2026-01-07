"""SQLAlchemy models for dictionary module."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class DictionaryEntry(Base):
    """
    SQLAlchemy model for dictionary entries.
    
    Represents a word and its definition in the dictionary.
    """
    
    __tablename__ = "dictionary_entries"
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key identifier"
    )
    word = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        doc="The word (case-sensitive storage, case-insensitive lookup)"
    )
    definition = Column(
        String,
        nullable=False,
        doc="The definition of the word"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the entry was created"
    )
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<DictionaryEntry(id={self.id}, word='{self.word}')>"

