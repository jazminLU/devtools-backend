import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_concatenate_words():
    """Test word concatenation"""
    response = client.post(
        "/word/concat",
        json={"words": ["hello", "world"]}
    )
    assert response.status_code == 200
    data = response.json()
    # h (index 0 of "hello") + w (index 1 of "world")
    assert data["result"] == "hw"
    assert data["words"] == ["hello", "world"]


def test_concatenate_multiple_words():
    """Test concatenating multiple words"""
    response = client.post(
        "/word/concat",
        json={"words": ["cat", "dog", "bird"]}
    )
    assert response.status_code == 200
    data = response.json()
    # c (index 0) + o (index 1) + i (index 2)
    assert data["result"] == "coi"


def test_concatenate_short_word():
    """Test concatenation when word is shorter than its index"""
    response = client.post(
        "/word/concat",
        json={"words": ["hi", "world"]}
    )
    assert response.status_code == 200
    data = response.json()
    # h (index 0 of "hi") + w (index 1 of "world")
    assert data["result"] == "hw"


def test_concatenate_single_word():
    """Test concatenating a single word"""
    response = client.post(
        "/word/concat",
        json={"words": ["test"]}
    )
    assert response.status_code == 200
    data = response.json()
    # t (index 0 of "test")
    assert data["result"] == "t"

