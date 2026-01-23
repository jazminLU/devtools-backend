"""Unit tests for shopping calculator service."""
import pytest
from app.shopping.service import ShoppingCalculatorService
from app.shopping.models import ShoppingTotalRequest


class TestShoppingCalculatorService:
    """Test cases for ShoppingCalculatorService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = ShoppingCalculatorService()
    
    def test_round_to_decimal_places_standard(self):
        """Test rounding to 2 decimal places."""
        assert self.service._round_to_decimal_places(10.555) == 10.56
        assert self.service._round_to_decimal_places(10.554) == 10.55
        assert self.service._round_to_decimal_places(10.5) == 10.5
        assert self.service._round_to_decimal_places(10.0) == 10.0
    
    def test_round_to_decimal_places_edge_cases(self):
        """Test rounding edge cases."""
        assert self.service._round_to_decimal_places(0.0) == 0.0
        assert self.service._round_to_decimal_places(0.001) == 0.0
        assert self.service._round_to_decimal_places(0.005) == 0.01
        assert self.service._round_to_decimal_places(999.999) == 1000.0
    
    def test_calculate_subtotal_basic(self):
        """Test basic subtotal calculation."""
        costs = {"apple": 1.50, "banana": 0.75}
        items = ["apple", "banana"]
        subtotal, found, not_found = self.service._calculate_subtotal(items, costs)
        
        assert subtotal == 2.25
        assert found == ["apple", "banana"]
        assert not_found == []
    
    def test_calculate_subtotal_with_duplicates(self):
        """Test subtotal with duplicate items."""
        costs = {"apple": 1.50, "banana": 0.75}
        items = ["apple", "banana", "apple"]
        subtotal, found, not_found = self.service._calculate_subtotal(items, costs)
        
        assert subtotal == 3.0
        assert found == ["apple", "banana", "apple"]
        assert not_found == []
    
    def test_calculate_subtotal_with_missing_items(self):
        """Test subtotal with items not in costs."""
        costs = {"apple": 1.50, "banana": 0.75}
        items = ["apple", "nonexistent", "banana"]
        subtotal, found, not_found = self.service._calculate_subtotal(items, costs)
        
        assert subtotal == 2.25
        assert found == ["apple", "banana"]
        assert not_found == ["nonexistent"]
    
    def test_calculate_subtotal_empty_items(self):
        """Test subtotal with empty items list."""
        costs = {"apple": 1.50}
        items = []
        subtotal, found, not_found = self.service._calculate_subtotal(items, costs)
        
        assert subtotal == 0.0
        assert found == []
        assert not_found == []
    
    def test_calculate_subtotal_with_whitespace(self):
        """Test subtotal with items containing whitespace."""
        costs = {"apple": 1.50, "banana": 0.75}
        items = [" apple ", "banana"]
        subtotal, found, not_found = self.service._calculate_subtotal(items, costs)
        
        assert subtotal == 2.25
        assert found == ["apple", "banana"]
        assert not_found == []
    
    def test_calculate_subtotal_skips_empty_strings(self):
        """Test that empty strings are skipped."""
        costs = {"apple": 1.50}
        items = ["apple", "", "  "]
        subtotal, found, not_found = self.service._calculate_subtotal(items, costs)
        
        assert subtotal == 1.50
        assert found == ["apple"]
        assert not_found == []
    
    def test_calculate_tax_and_total_basic(self):
        """Test basic tax and total calculation."""
        tax_amount, total = self.service._calculate_tax_and_total(100.0, 0.1)
        
        assert tax_amount == 10.0
        assert total == 110.0
    
    def test_calculate_tax_and_total_zero_tax(self):
        """Test tax calculation with zero tax."""
        tax_amount, total = self.service._calculate_tax_and_total(100.0, 0.0)
        
        assert tax_amount == 0.0
        assert total == 100.0
    
    def test_calculate_tax_and_total_max_tax(self):
        """Test tax calculation with maximum tax (100%)."""
        tax_amount, total = self.service._calculate_tax_and_total(100.0, 1.0)
        
        assert tax_amount == 100.0
        assert total == 200.0
    
    def test_calculate_tax_and_total_zero_subtotal(self):
        """Test tax calculation with zero subtotal."""
        tax_amount, total = self.service._calculate_tax_and_total(0.0, 0.1)
        
        assert tax_amount == 0.0
        assert total == 0.0
    
    def test_calculate_total_complete(self):
        """Test complete calculation flow."""
        request = ShoppingTotalRequest(
            costs={"apple": 1.50, "banana": 0.75},
            items=["apple", "banana"],
            tax=0.1
        )
        result = self.service.calculate_total(request)
        
        assert result.subtotal == 2.25
        assert result.tax_amount == 0.23
        assert result.total == 2.48
        assert result.items_found == ["apple", "banana"]
        assert result.items_not_found == []
        assert result.items_count == 2
    
    def test_calculate_total_with_rounding(self):
        """Test calculation with rounding precision."""
        request = ShoppingTotalRequest(
            costs={"item": 10.555},
            items=["item"],
            tax=0.1
        )
        result = self.service.calculate_total(request)
        
        assert result.subtotal == 10.56
        assert result.tax_amount == 1.06
        assert result.total == 11.62
    
    def test_calculate_total_with_missing_items(self):
        """Test calculation with some missing items."""
        request = ShoppingTotalRequest(
            costs={"apple": 1.50},
            items=["apple", "missing1", "missing2"],
            tax=0.1
        )
        result = self.service.calculate_total(request)
        
        assert result.subtotal == 1.50
        assert result.tax_amount == 0.15
        assert result.total == 1.65
        assert result.items_found == ["apple"]
        assert result.items_not_found == ["missing1", "missing2"]
        assert result.items_count == 3

