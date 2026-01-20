"""Dictionary API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.exceptions import (
    DictionaryWordNotFoundError,
    DictionaryWordAlreadyExistsError
)
from app.dictionary.schemas import (
    WordAddRequest,
    WordAddResponse,
    WordDefinitionResponse
)
from app.dictionary.service import get_dictionary_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
    response_model=WordAddResponse,
    summary="Add a word to the dictionary",
    description="""
    Add a new word with its definition to the dictionary.
    
    **Features:**
    - Case-insensitive word storage (words are stored in lowercase)
    - Automatic whitespace trimming
    - Duplicate detection (prevents adding the same word twice)
    - Input validation (word and definition cannot be empty)
    
    **Example:**
    ```json
    {
        "word": "Python",
        "definition": "A high-level programming language known for simplicity"
    }
    ```
    
    The word will be stored as "python" (lowercase) regardless of input case.
    """
)
async def add_word(
    request: WordAddRequest,
    db: Session = Depends(get_db)
) -> WordAddResponse:
    """
    Add a word with its definition to the dictionary.
    
    The word is normalized to lowercase for storage. If the word already exists
    (case-insensitive), a 409 Conflict error is returned.
    
    Args:
        request: Word add request containing word and definition
        db: Database session
        
    Returns:
        Success response with message, word, and definition
        
    Raises:
        HTTPException 409: If word already exists (case-insensitive)
        HTTPException 400: If validation fails (empty word/definition, invalid format)
    """
    try:
        service = get_dictionary_service(db)
        entry = service.add_word(request.word, request.definition)
        
        logger.info(f"Successfully added word via API: {request.word}")
        return WordAddResponse(
            message=f"Word '{entry.word}' added successfully",
            word=entry.word,
            definition=entry.definition
        )
    except DictionaryWordAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Word already exists",
                "message": str(e.detail),
                "word": request.word.lower().strip(),
                "hint": "Words are stored case-insensitively. Use GET endpoint to retrieve existing word."
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation failed",
                "message": str(e),
                "hint": "Ensure word and definition are not empty and meet length requirements."
            }
        )


@router.get(
    "/{word}",
    response_model=WordDefinitionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get word definition",
    description="""
    Retrieve the definition of a word from the dictionary.
    
    **Features:**
    - Case-insensitive search (searches are normalized to lowercase)
    - Returns the stored word and its definition
    
    **Example:**
    ```
    GET /dictionary/Python
    GET /dictionary/python
    GET /dictionary/PYTHON
    ```
    All return the same result as words are stored in lowercase.
    """
)
async def get_word(
    word: str,
    db: Session = Depends(get_db)
) -> WordDefinitionResponse:
    """
    Retrieve the definition of a word from the dictionary.
    
    The search is case-insensitive - "Python", "python", and "PYTHON"
    will all find the same word (stored as "python").
    
    Args:
        word: The word to retrieve (case-insensitive)
        db: Database session
        
    Returns:
        Word definition response with word and definition
        
    Raises:
        HTTPException 404: If word not found in dictionary
        HTTPException 400: If word is invalid or empty
    """
    try:
        service = get_dictionary_service(db)
        entry = service.get_word(word)
        
        return WordDefinitionResponse(
            word=entry.word,
            definition=entry.definition
        )
    except DictionaryWordNotFoundError as e:
        normalized_word = word.strip().lower()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Word not found",
                "message": str(e.detail),
                "word": normalized_word,
                "hint": "The word may not exist in the dictionary. Use POST /add to add new words."
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation failed",
                "message": str(e),
                "hint": "Ensure the word parameter is not empty."
            }
        )

