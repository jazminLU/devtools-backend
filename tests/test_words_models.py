"""Unit tests for words models."""
import pytest
from pydantic import ValidationError

from app.words.models import WordConcatRequest, WordConcatResponse


class TestWordConcatRequest:
    """Test cases for WordConcatRequest model."""
    
    def test_valid_request(self):
        """Test valid request creation."""
        request = WordConcatRequest(words=["hello", "world"])
        
        assert request.words == ["hello", "world"]
    
    def test_validate_words_not_empty_list(self):
        """Test that words list cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            WordConcatRequest(words=[])
        
        assert "At least one word is required" in str(exc_info.value)
    
    def test_validate_words_not_empty_strings(self):
        """Test that words cannot be empty strings."""
        with pytest.raises(ValidationError) as exc_info:
            WordConcatRequest(words=["hello", ""])
        
        assert "cannot be empty" in str(exc_info.value)
    
    def test_validate_words_strips_whitespace(self):
        """Test that words are stripped of whitespace."""
        request = WordConcatRequest(words=["  hello  ", "  world  "])
        
        assert request.words == ["hello", "world"]
    
    def test_validate_words_single_word(self):
        """Test that single word is valid."""
        request = WordConcatRequest(words=["test"])
        
        assert request.words == ["test"]


class TestWordConcatResponse:
    """Test cases for WordConcatResponse model."""
    
    def test_valid_response(self):
        """Test valid response creation."""
        response = WordConcatResponse(
            result="hw",
            words=["hello", "world"],
            characters_extracted=2,
            characters_skipped=0
        )
        
        assert response.result == "hw"
        assert response.words == ["hello", "world"]
        assert response.characters_extracted == 2
        assert response.characters_skipped == 0
    
    def test_response_with_skipped(self):
        """Test response with skipped characters."""
        response = WordConcatResponse(
            result="h",
            words=["hello", "hi"],
            characters_extracted=1,
            characters_skipped=1
        )
        
        assert response.result == "h"
        assert response.characters_skipped == 1

