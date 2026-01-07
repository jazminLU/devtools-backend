"""
Legacy CRUD functions - deprecated in favor of service layer.
Kept for backward compatibility during migration.
"""
from sqlalchemy.orm import Session
from app.dictionary.service import get_dictionary_service
from app.dictionary.db_models import DictionaryEntry


def get_word_by_word(db: Session, word: str) -> DictionaryEntry | None:
    """Retrieve a dictionary entry by word (case-insensitive) - DEPRECATED."""
    service = get_dictionary_service(db)
    try:
        return service.get_word(word)
    except Exception:
        return None


def create_word(db: Session, word: str, definition: str) -> DictionaryEntry:
    """Create a new dictionary entry - DEPRECATED."""
    service = get_dictionary_service(db)
    return service.add_word(word, definition)

