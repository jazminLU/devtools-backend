"""Additional unit tests for routers."""
import pytest
from fastapi.testclient import TestClient


class TestShoppingRouter:
    """Additional test cases for shopping router."""
    
    def test_calculate_total_simple_format(self, client):
        """Test calculating total with simple text format."""
        response = client.post(
            "/shopping/total",
            json={
                "costs_input": "apple: 1.50, banana: 0.75",
                "items_input": "apple, banana",
                "tax": 0.1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["subtotal"] == 2.25
        assert "items_found" in data
    
    def test_calculate_total_invalid_format(self, client):
        """Test calculating total with invalid format."""
        response = client.post(
            "/shopping/total",
            json={
                "costs": {"apple": 1.50},
                "items": [],
                "tax": 0.1
            }
        )
        
        assert response.status_code == 400
    
    def test_calculate_total_simple_endpoint(self, client):
        """Test the /total-simple endpoint."""
        response = client.post(
            "/shopping/total-simple",
            json={
                "costs_input": "apple: 1.50",
                "items_input": "apple",
                "tax": 0.1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "subtotal" in data
        assert "total" in data
    
    def test_calculate_total_negative_cost(self, client):
        """Test calculating total with negative cost."""
        response = client.post(
            "/shopping/total",
            json={
                "costs": {"apple": -1.50},
                "items": ["apple"],
                "tax": 0.1
            }
        )
        
        assert response.status_code == 400
    
    def test_calculate_total_tax_out_of_range(self, client):
        """Test calculating total with tax out of range."""
        response = client.post(
            "/shopping/total",
            json={
                "costs": {"apple": 1.50},
                "items": ["apple"],
                "tax": 1.5
            }
        )
        
        assert response.status_code == 400


class TestWordsRouter:
    """Additional test cases for words router."""
    
    def test_concatenate_words_empty_list(self, client):
        """Test concatenation with empty list."""
        response = client.post(
            "/word/concat",
            json={"words": []}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_concatenate_words_with_empty_string(self, client):
        """Test concatenation with empty string in list."""
        response = client.post(
            "/word/concat",
            json={"words": ["hello", ""]}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_concatenate_words_complex(self, client):
        """Test concatenation with complex word list."""
        response = client.post(
            "/word/concat",
            json={"words": ["hello", "world", "fastapi", "python"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert data["characters_extracted"] == 4


class TestDictionaryRouter:
    """Additional test cases for dictionary router."""
    
    def test_add_word_empty_word(self, client):
        """Test adding word with empty word."""
        response = client.post(
            "/dictionary/add",
            json={"word": "", "definition": "A definition"}
        )
        
        assert response.status_code == 400
    
    def test_add_word_empty_definition(self, client):
        """Test adding word with empty definition."""
        response = client.post(
            "/dictionary/add",
            json={"word": "test", "definition": ""}
        )
        
        assert response.status_code == 400
    
    def test_get_word_empty(self, client):
        """Test getting word with empty parameter."""
        response = client.get("/dictionary/")
        
        # This might be a routing issue, but should handle gracefully
        assert response.status_code in [404, 422]
    
    def test_add_word_whitespace_only(self, client):
        """Test adding word with only whitespace."""
        response = client.post(
            "/dictionary/add",
            json={"word": "   ", "definition": "A definition"}
        )
        
        assert response.status_code == 400

