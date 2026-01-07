"""Word concatenation API routes."""
from fastapi import APIRouter
import logging

from app.words.models import WordConcatRequest, WordConcatResponse
from app.words.service import WordConcatenationService

logger = logging.getLogger(__name__)

router = APIRouter()
concatenation_service = WordConcatenationService()


@router.post("/concat", response_model=WordConcatResponse)
async def concatenate_words(
    request: WordConcatRequest
) -> WordConcatResponse:
    """
    Concatenate the n-th letter of each word, where n is the index of the word.
    
    Args:
        request: Word concatenation request with list of words
        
    Returns:
        Word concatenation response with result
    """
    return concatenation_service.concatenate_words(request)

