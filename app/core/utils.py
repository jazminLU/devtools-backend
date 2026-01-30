"""Utility functions for common operations."""
from typing import Optional


def normalize_string(value: str, to_lower: bool = False) -> str:
    """
    Normalize a string by stripping whitespace and optionally converting to lowercase.
    
    Args:
        value: The string to normalize
        to_lower: If True, convert to lowercase after stripping
        
    Returns:
        Normalized string
        
    Raises:
        ValueError: If the normalized string is empty
    """
    if not value:
        raise ValueError("String cannot be empty")
    
    normalized = value.strip()
    
    if not normalized:
        raise ValueError("String cannot be only whitespace")
    
    if to_lower:
        normalized = normalized.lower()
    
    return normalized


def is_empty_or_whitespace(value: Optional[str]) -> bool:
    """
    Check if a string is empty or contains only whitespace.
    
    Args:
        value: The string to check
        
    Returns:
        True if empty or only whitespace, False otherwise
    """
    if not value:
        return True
    return not value.strip()


def validate_not_empty(value: str, field_name: str = "Field") -> str:
    """
    Validate that a string is not empty or only whitespace.
    
    Args:
        value: The string to validate
        field_name: Name of the field for error message
        
    Returns:
        Stripped string
        
    Raises:
        ValueError: If the string is empty or only whitespace
    """
    if is_empty_or_whitespace(value):
        raise ValueError(f"{field_name} cannot be empty or only whitespace")
    
    return value.strip()

