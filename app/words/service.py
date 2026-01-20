"""Business logic for word concatenation."""
import logging
from typing import List, Tuple

from app.words.models import WordConcatRequest, WordConcatResponse

logger = logging.getLogger(__name__)


class WordConcatenationService:
    """
    Service for word concatenation operations.
    
    Implements business logic for concatenating specific characters from words.
    Extracts the character at position 'n' from each word at index 'n' in the list.
    Follows Single Responsibility Principle.
    """
    
    def _extract_characters_by_index(
        self, 
        words: List[str]
    ) -> Tuple[List[str], int]:
        """
        Extract characters from words based on their index position.
        
        Args:
            words: List of words to process
            
        Returns:
            Tuple of (extracted_characters, skipped_count)
        """
        result_chars: List[str] = []
        skipped_count = 0
        
        for index, word in enumerate(words):
            if self._is_valid_index(word, index):
                result_chars.append(word[index])
            else:
                skipped_count += 1
                logger.warning(
                    f"Word '{word}' at position {index} is too short "
                    f"(length: {len(word)}, required: {index + 1}). Skipping."
                )
        
        return result_chars, skipped_count
    
    @staticmethod
    def _is_valid_index(word: str, index: int) -> bool:
        """
        Check if index is valid for word extraction.
        
        The word must have at least (index + 1) characters to extract
        the character at the specified index position.
        
        Args:
            word: The word to check
            index: The index position (0-based)
            
        Returns:
            True if index is valid, False otherwise
        """
        return 0 <= index < len(word)
    
    def concatenate_words(self, request: WordConcatRequest) -> WordConcatResponse:
        """
        Concatenate the n-th letter of each word, where n is the index.
        
        For example: ["hello", "world", "test"] -> "hos"
        - 'h' from word at index 0 ("hello" at position 0)
        - 'o' from word at index 1 ("world" at position 1)  
        - 's' from word at index 2 ("test" at position 2)
        
        Words that are too short are skipped with a warning.
        
        Args:
            request: Word concatenation request
            
        Returns:
            Word concatenation response with result and statistics
        """
        extracted_chars, skipped_count = self._extract_characters_by_index(request.words)
        result = "".join(extracted_chars)
        extracted_count = len(extracted_chars)
        
        logger.info(
            f"Concatenated {extracted_count} characters from "
            f"{len(request.words)} words. Result: '{result}'. "
            f"Skipped {skipped_count} characters."
        )
        
        return WordConcatResponse(
            result=result,
            words=request.words,
            characters_extracted=extracted_count,
            characters_skipped=skipped_count
        )

