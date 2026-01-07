"""Dictionary API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.exceptions import (
    DictionaryWordNotFoundError,
    DictionaryWordAlreadyExistsError
)
from app.dictionary.schemas import WordAddRequest, WordDefinitionResponse
from app.dictionary.service import get_dictionary_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_word(
    request: WordAddRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    Add a word with its definition to the dictionary.
    
    Args:
        request: Word add request containing word and definition
        db: Database session
        
    Returns:
        Success message with the added word
        
    Raises:
        HTTPException: If word already exists or validation fails
    """
    try:
        service = get_dictionary_service(db)
        service.add_word(request.word, request.definition)
        
        logger.info(f"Successfully added word: {request.word}")
        return {
            "message": f"Word '{request.word}' added successfully",
            "word": request.word
        }
    except DictionaryWordAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.detail)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{word}", response_model=WordDefinitionResponse)
async def get_word(
    word: str,
    db: Session = Depends(get_db)
) -> WordDefinitionResponse:
    """
    Retrieve the definition of a word.
    
    Args:
        word: The word to retrieve
        db: Database session
        
    Returns:
        Word definition response with word and definition
        
    Raises:
        HTTPException: If word not found or validation fails
    """
    try:
        service = get_dictionary_service(db)
        entry = service.get_word(word)
        
        return WordDefinitionResponse(
            word=entry.word,
            definition=entry.definition
        )
    except DictionaryWordNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e.detail)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

