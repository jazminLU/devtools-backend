"""Word concatenation API routes."""
from fastapi import APIRouter, HTTPException, status
import logging

from app.words.models import WordConcatRequest, WordConcatResponse
from app.words.service import WordConcatenationService

logger = logging.getLogger(__name__)

router = APIRouter()
concatenation_service = WordConcatenationService()


@router.post(
    "/concat",
    response_model=WordConcatResponse,
    status_code=status.HTTP_200_OK,
    summary="Concatenate characters from words",
    description="""
    Concatenate characters from a list of words by extracting the character 
    at position 'n' from each word at index 'n' in the list.
    
    **Example:**
    - Input: `["hello", "world", "test"]`
    - Process:
      - Word 0 ("hello"): extract character at position 0 → 'h'
      - Word 1 ("world"): extract character at position 1 → 'o'
      - Word 2 ("test"): extract character at position 2 → 's'
    - Output: `"hos"`
    
    **Note:** Words that are too short (length < position + 1) are skipped.
    """
)
async def concatenate_words(
    request: WordConcatRequest
) -> WordConcatResponse:
    """
    Concatenate the n-th letter of each word, where n is the index of the word.
    
    **What it does:**
    - Takes a list of words
    - Extracts the character at position 'n' from the word at index 'n'
    - Concatenates all extracted characters into a result string
    - Returns the result along with statistics about extracted/skipped characters
    
    **Example:**
    ```
    Request: {"words": ["hello", "world", "python"]}
    Response: {
        "result": "hot",
        "words": ["hello", "world", "python"],
        "characters_extracted": 3,
        "characters_skipped": 0
    }
    ```
    Explanation:
    - "hello"[0] = 'h'
    - "world"[1] = 'o'
    - "python"[2] = 't'
    
    Args:
        request: Word concatenation request with list of words
        
    Returns:
        Word concatenation response with:
        - result: The concatenated string
        - words: Original words processed
        - characters_extracted: Number of characters successfully extracted
        - characters_skipped: Number of words skipped due to insufficient length
        
    Raises:
        HTTPException: If validation fails (empty words, invalid format)
    """
    try:
        result = concatenation_service.concatenate_words(request)
        
        # Provide warning if some characters were skipped
        if result.characters_skipped > 0:
            logger.warning(
                f"Some characters were skipped: {result.characters_skipped} out of "
                f"{len(request.words)} words were too short"
            )
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )

