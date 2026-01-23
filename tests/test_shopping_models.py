"""Unit tests for shopping models."""
import pytest
from pydantic import ValidationError

from app.shopping.models import (
    ShoppingTotalRequest,
    ShoppingTotalSimpleRequest,
    ShoppingTotalResponse
)


class TestShoppingTotalRequest:
    """Test cases for ShoppingTotalRequest model."""
    
    def test_valid_request(self):
        """Test valid request creation."""
        request = ShoppingTotalRequest(
            costs={"apple": 1.50, "banana": 0.75},
            items=["apple", "banana"],
            tax=0.1
        )
        
        assert request.costs == {"apple": 1.50, "banana": 0.75}
        assert request.items == ["apple", "banana"]
        assert request.tax == 0.1
    
    def test_validate_costs_non_negative(self):
        """Test that costs must be non-negative."""
        with pytest.raises(ValidationError) as exc_info:
            ShoppingTotalRequest(
                costs={"apple": -1.50},
                items=["apple"],
                tax=0.1
            )
        
        assert "cannot be negative" in str(exc_info.value)
    
    def test_validate_costs_zero_allowed(self):
        """Test that zero cost is allowed."""
        request = ShoppingTotalRequest(
            costs={"free": 0.0},
            items=["free"],
            tax=0.1
        )
        
        assert request.costs["free"] == 0.0
    
    def test_validate_items_not_empty(self):
        """Test that items list cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            ShoppingTotalRequest(
                costs={"apple": 1.50},
                items=[],
                tax=0.1
            )
        
        assert "At least one item is required" in str(exc_info.value)
    
    def test_validate_items_filters_empty_strings(self):
        """Test that empty strings in items are filtered."""
        with pytest.raises(ValidationError) as exc_info:
            ShoppingTotalRequest(
                costs={"apple": 1.50},
                items=["   ", ""],
                tax=0.1
            )
        
        assert "cannot contain only empty strings" in str(exc_info.value)
    
    def test_validate_items_strips_whitespace(self):
        """Test that items are stripped of whitespace."""
        request = ShoppingTotalRequest(
            costs={"apple": 1.50},
            items=["  apple  ", "  banana  "],
            tax=0.1
        )
        
        assert request.items == ["apple", "banana"]
    
    def test_validate_tax_range(self):
        """Test that tax must be between 0 and 1."""
        # Valid tax values
        request1 = ShoppingTotalRequest(
            costs={"apple": 1.50},
            items=["apple"],
            tax=0.0
        )
        assert request1.tax == 0.0
        
        request2 = ShoppingTotalRequest(
            costs={"apple": 1.50},
            items=["apple"],
            tax=1.0
        )
        assert request2.tax == 1.0
        
        # Invalid tax values
        with pytest.raises(ValidationError):
            ShoppingTotalRequest(
                costs={"apple": 1.50},
                items=["apple"],
                tax=-0.1
            )
        
        with pytest.raises(ValidationError):
            ShoppingTotalRequest(
                costs={"apple": 1.50},
                items=["apple"],
                tax=1.1
            )


class TestShoppingTotalSimpleRequest:
    """Test cases for ShoppingTotalSimpleRequest model."""
    
    def test_parse_costs_json_format(self):
        """Test parsing costs from JSON format."""
        request = ShoppingTotalSimpleRequest(
            costs_input='{"apple": 1.50, "banana": 0.75}',
            items_input="apple, banana",
            tax=0.1
        )
        
        assert request._parsed_costs == {"apple": 1.50, "banana": 0.75}
    
    def test_parse_costs_key_value_lines(self):
        """Test parsing costs from key:value lines."""
        request = ShoppingTotalSimpleRequest(
            costs_input="apple: 1.50\nbanana: 0.75",
            items_input="apple, banana",
            tax=0.1
        )
        
        assert request._parsed_costs == {"apple": 1.50, "banana": 0.75}
    
    def test_parse_costs_comma_separated(self):
        """Test parsing costs from comma-separated format."""
        request = ShoppingTotalSimpleRequest(
            costs_input="apple: 1.50, banana: 0.75",
            items_input="apple, banana",
            tax=0.1
        )
        
        assert request._parsed_costs == {"apple": 1.50, "banana": 0.75}
    
    def test_parse_costs_invalid_raises_error(self):
        """Test that invalid costs format raises error."""
        with pytest.raises(ValidationError):
            ShoppingTotalSimpleRequest(
                costs_input="invalid format",
                items_input="apple",
                tax=0.1
            )
    
    def test_parse_costs_negative_raises_error(self):
        """Test that negative costs raise error."""
        with pytest.raises(ValidationError):
            ShoppingTotalSimpleRequest(
                costs_input="apple: -1.50",
                items_input="apple",
                tax=0.1
            )
    
    def test_parse_items_comma_separated(self):
        """Test parsing items from comma-separated format."""
        request = ShoppingTotalSimpleRequest(
            costs_input="apple: 1.50",
            items_input="apple, banana, orange",
            tax=0.1
        )
        
        assert request._parsed_items == ["apple", "banana", "orange"]
    
    def test_parse_items_newline_separated(self):
        """Test parsing items from newline-separated format."""
        request = ShoppingTotalSimpleRequest(
            costs_input="apple: 1.50",
            items_input="apple\nbanana\norange",
            tax=0.1
        )
        
        assert request._parsed_items == ["apple", "banana", "orange"]
    
    def test_parse_items_space_separated(self):
        """Test parsing items from space-separated format."""
        request = ShoppingTotalSimpleRequest(
            costs_input="apple: 1.50",
            items_input="apple banana orange",
            tax=0.1
        )
        
        assert request._parsed_items == ["apple", "banana", "orange"]
    
    def test_parse_items_empty_raises_error(self):
        """Test that empty items input raises error."""
        with pytest.raises(ValidationError):
            ShoppingTotalSimpleRequest(
                costs_input="apple: 1.50",
                items_input="",
                tax=0.1
            )
    
    def test_to_standard_request(self):
        """Test conversion to standard request."""
        simple_request = ShoppingTotalSimpleRequest(
            costs_input="apple: 1.50, banana: 0.75",
            items_input="apple, banana",
            tax=0.1
        )
        
        standard_request = simple_request.to_standard_request()
        
        assert isinstance(standard_request, ShoppingTotalRequest)
        assert standard_request.costs == {"apple": 1.50, "banana": 0.75}
        assert standard_request.items == ["apple", "banana"]
        assert standard_request.tax == 0.1


class TestShoppingTotalResponse:
    """Test cases for ShoppingTotalResponse model."""
    
    def test_valid_response(self):
        """Test valid response creation."""
        response = ShoppingTotalResponse(
            subtotal=5.00,
            tax_amount=0.50,
            total=5.50,
            items_found=["apple", "banana"],
            items_not_found=[],
            items_count=2
        )
        
        assert response.subtotal == 5.00
        assert response.tax_amount == 0.50
        assert response.total == 5.50
        assert response.items_found == ["apple", "banana"]
        assert response.items_not_found == []
        assert response.items_count == 2

