import pytest


def test_add_word(client):
    """Test adding a word to the dictionary"""
    response = client.post(
        "/dictionary/add",
        json={"word": "test", "definition": "A test definition"}
    )
    assert response.status_code == 201
    assert response.json()["word"] == "test"


def test_add_duplicate_word(client):
    """Test that adding a duplicate word returns 409"""
    # Add word first time
    response = client.post(
        "/dictionary/add",
        json={"word": "duplicate", "definition": "First definition"}
    )
    assert response.status_code == 201
    
    # Try to add same word again
    response = client.post(
        "/dictionary/add",
        json={"word": "duplicate", "definition": "Second definition"}
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_get_word(client):
    """Test retrieving a word from the dictionary"""
    # First add a word
    client.post(
        "/dictionary/add",
        json={"word": "example", "definition": "An example definition"}
    )
    
    # Then retrieve it
    response = client.get("/dictionary/example")
    assert response.status_code == 200
    assert response.json()["word"] == "example"
    assert response.json()["definition"] == "An example definition"


def test_get_word_not_found(client):
    """Test retrieving a word that doesn't exist"""
    response = client.get("/dictionary/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_word_case_insensitive(client):
    """Test that dictionary is case insensitive"""
    client.post(
        "/dictionary/add",
        json={"word": "Test", "definition": "A test"}
    )
    
    # Should find it with different case
    response = client.get("/dictionary/test")
    assert response.status_code == 200
    assert response.json()["definition"] == "A test"
    
    # Should also find it with uppercase
    response = client.get("/dictionary/TEST")
    assert response.status_code == 200
    assert response.json()["definition"] == "A test"

