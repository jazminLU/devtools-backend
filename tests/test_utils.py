"""Unit tests for utility functions."""
import pytest

from app.core.utils import (
    normalize_string,
    is_empty_or_whitespace,
    validate_not_empty
)


class TestNormalizeString:
    """Test cases for normalize_string function."""
    
    def test_normalize_string_basic(self):
        """Test basic string normalization."""
        result = normalize_string("  test  ")
        assert result == "test"
    
    def test_normalize_string_to_lower(self):
        """Test normalization with lowercase conversion."""
        result = normalize_string("  TEST  ", to_lower=True)
        assert result == "test"
    
    def test_normalize_string_no_lower(self):
        """Test normalization without lowercase conversion."""
        result = normalize_string("  TEST  ", to_lower=False)
        assert result == "TEST"
    
    def test_normalize_string_empty_raises_error(self):
        """Test that empty string raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            normalize_string("")
    
    def test_normalize_string_whitespace_only_raises_error(self):
        """Test that whitespace-only string raises error."""
        with pytest.raises(ValueError, match="cannot be only whitespace"):
            normalize_string("   ")
    
    def test_normalize_string_none_raises_error(self):
        """Test that None raises error."""
        with pytest.raises(ValueError):
            normalize_string(None)


class TestIsEmptyOrWhitespace:
    """Test cases for is_empty_or_whitespace function."""
    
    def test_is_empty_or_whitespace_empty_string(self):
        """Test with empty string."""
        assert is_empty_or_whitespace("") is True
    
    def test_is_empty_or_whitespace_whitespace_only(self):
        """Test with whitespace-only string."""
        assert is_empty_or_whitespace("   ") is True
        assert is_empty_or_whitespace("\t\n") is True
    
    def test_is_empty_or_whitespace_none(self):
        """Test with None."""
        assert is_empty_or_whitespace(None) is True
    
    def test_is_empty_or_whitespace_valid_string(self):
        """Test with valid string."""
        assert is_empty_or_whitespace("test") is False
        assert is_empty_or_whitespace("  test  ") is False


class TestValidateNotEmpty:
    """Test cases for validate_not_empty function."""
    
    def test_validate_not_empty_valid(self):
        """Test validation with valid string."""
        result = validate_not_empty("test")
        assert result == "test"
    
    def test_validate_not_empty_strips_whitespace(self):
        """Test that whitespace is stripped."""
        result = validate_not_empty("  test  ")
        assert result == "test"
    
    def test_validate_not_empty_custom_field_name(self):
        """Test with custom field name."""
        with pytest.raises(ValueError, match="CustomField cannot be empty"):
            validate_not_empty("", "CustomField")
    
    def test_validate_not_empty_default_field_name(self):
        """Test with default field name."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            validate_not_empty("")
    
    def test_validate_not_empty_whitespace_only(self):
        """Test that whitespace-only string raises error."""
        with pytest.raises(ValueError):
            validate_not_empty("   ")

