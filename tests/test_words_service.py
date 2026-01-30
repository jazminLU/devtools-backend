"""Unit tests for word concatenation service."""
import pytest
from app.words.service import WordConcatenationService
from app.words.models import WordConcatRequest


class TestWordConcatenationService:
    """Test cases for WordConcatenationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = WordConcatenationService()
    
    def test_is_valid_index_valid(self):
        """Test valid index check."""
        assert self.service._is_valid_index("hello", 0) is True
        assert self.service._is_valid_index("hello", 4) is True
        assert self.service._is_valid_index("test", 3) is True
    
    def test_is_valid_index_invalid(self):
        """Test invalid index check."""
        assert self.service._is_valid_index("hi", 2) is False
        assert self.service._is_valid_index("a", 1) is False
        assert self.service._is_valid_index("", 0) is False
    
    def test_is_valid_index_edge_cases(self):
        """Test edge cases for index validation."""
        assert self.service._is_valid_index("hello", -1) is False
        assert self.service._is_valid_index("hello", 5) is False
        assert self.service._is_valid_index("a", 0) is True
    
    def test_extract_characters_by_index_basic(self):
        """Test basic character extraction."""
        words = ["hello", "world"]
        chars, skipped = self.service._extract_characters_by_index(words)
        
        assert chars == ["h", "o"]
        assert skipped == 0
    
    def test_extract_characters_by_index_multiple(self):
        """Test extraction from multiple words."""
        words = ["hello", "world", "test"]
        chars, skipped = self.service._extract_characters_by_index(words)
        
        assert chars == ["h", "o", "s"]
        assert skipped == 0
    
    def test_extract_characters_by_index_with_short_word(self):
        """Test extraction with word too short."""
        words = ["hi", "world"]
        chars, skipped = self.service._extract_characters_by_index(words)
        
        assert chars == ["h", "o"]
        assert skipped == 0  # "hi" at index 0 is valid, "world" at index 1 is valid
    
    def test_extract_characters_by_index_skips_short(self):
        """Test that short words are skipped."""
        words = ["hello", "hi", "test"]
        chars, skipped = self.service._extract_characters_by_index(words)
        
        # "hello"[0] = 'h', "hi"[1] is invalid (length 2, need index 1), "test"[2] = 's'
        assert chars == ["h", "s"]
        assert skipped == 1
    
    def test_extract_characters_by_index_all_skipped(self):
        """Test when all words are too short."""
        words = ["a", "b"]
        chars, skipped = self.service._extract_characters_by_index(words)
        
        # "a"[0] = 'a', "b"[1] is invalid
        assert chars == ["a"]
        assert skipped == 1
    
    def test_extract_characters_by_index_empty_list(self):
        """Test extraction with empty list."""
        words = []
        chars, skipped = self.service._extract_characters_by_index(words)
        
        assert chars == []
        assert skipped == 0
    
    def test_concatenate_words_basic(self):
        """Test basic word concatenation."""
        request = WordConcatRequest(words=["hello", "world"])
        result = self.service.concatenate_words(request)
        
        assert result.result == "ho"
        assert result.words == ["hello", "world"]
        assert result.characters_extracted == 2
        assert result.characters_skipped == 0
    
    def test_concatenate_words_multiple(self):
        """Test concatenation with multiple words."""
        request = WordConcatRequest(words=["hello", "world", "python"])
        result = self.service.concatenate_words(request)
        
        assert result.result == "hot"
        assert result.characters_extracted == 3
        assert result.characters_skipped == 0
    
    def test_concatenate_words_with_skips(self):
        """Test concatenation with skipped words."""
        request = WordConcatRequest(words=["hello", "hi", "test"])
        result = self.service.concatenate_words(request)
        
        assert result.result == "hs"
        assert result.characters_extracted == 2
        assert result.characters_skipped == 1
    
    def test_concatenate_words_single_word(self):
        """Test concatenation with single word."""
        request = WordConcatRequest(words=["test"])
        result = self.service.concatenate_words(request)
        
        assert result.result == "t"
        assert result.characters_extracted == 1
        assert result.characters_skipped == 0
    
    def test_concatenate_words_empty_result(self):
        """Test concatenation that results in empty string."""
        request = WordConcatRequest(words=["a"])
        result = self.service.concatenate_words(request)
        
        assert result.result == "a"
        assert result.characters_extracted == 1
        assert result.characters_skipped == 0

