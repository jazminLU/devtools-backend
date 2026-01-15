"""Business logic for word concatenation."""
import logging
from typing import List

from app.words.models import WordConcatRequest, WordConcatResponse

logger = logging.getLogger(__name__)


class WordConcatenationService:
    """
    Service for word concatenation operations.
    
    Implements business logic for concatenating specific characters from words.
    Follows Single Responsibility Principle.
    """
    
    def _extract_characters_by_index(self, words: List[str]) -> List[str]:
        """
        Extract characters from words based on their index position.
        
        Args:
            words: List of words to process
            
        Returns:
            List of extracted characters
        """
        result_chars: List[str] = []
        
        for index, word in enumerate(words):
            if self._is_valid_index(word, index):
                result_chars.append(word[index])
            else:
                logger.warning(
                    f"Word '{word}' at index {index} is too short (length: {len(word)}), skipping"
                )
        
        return result_chars
    
    @staticmethod
    def _is_valid_index(word: str, index: int) -> bool:
        """
        Check if index is valid for word extraction.
        
        Args:
            word: The word to check
            index: The index position
            
        Returns:
            True if index is valid, False otherwise
        """
        return 0 <= index < len(word)
    
    def concatenate_words(self, request: WordConcatRequest) -> WordConcatResponse:
        """
        Concatenate the n-th letter of each word, where n is the index.
        
        For example: ["hello", "world"] -> "hw" 
        (h from index 0, w from index 1)
        
        Args:
            request: Word concatenation request
            
        Returns:
            Word concatenation response with result
        """
        extracted_chars = self._extract_characters_by_index(request.words)
        result = "".join(extracted_chars)
        
        logger.info(
            f"Concatenated {len(extracted_chars)} characters from "
            f"{len(request.words)} words. Result: '{result}'"
        )
        
        return WordConcatResponse(
            result=result,
            words=request.words
        )

