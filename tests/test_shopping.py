import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_calculate_total():
    """Test calculating shopping total"""
    response = client.post(
        "/shopping/total",
        json={
            "costs": {"apple": 1.50, "banana": 0.75, "orange": 2.00},
            "items": ["apple", "banana"],
            "tax": 0.1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == 2.25
    assert data["tax_amount"] == 0.23
    assert data["total"] == 2.48
    assert "apple" in data["items_found"]
    assert "banana" in data["items_found"]


def test_calculate_total_with_missing_items():
    """Test calculating total with items not in costs dictionary"""
    response = client.post(
        "/shopping/total",
        json={
            "costs": {"apple": 1.50, "banana": 0.75},
            "items": ["apple", "nonexistent", "banana"],
            "tax": 0.1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == 2.25
    assert "nonexistent" in data["items_not_found"]
    assert len(data["items_found"]) == 2


def test_calculate_total_zero_tax():
    """Test calculating total with zero tax"""
    response = client.post(
        "/shopping/total",
        json={
            "costs": {"item": 10.00},
            "items": ["item"],
            "tax": 0.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == 10.00
    assert data["tax_amount"] == 0.00
    assert data["total"] == 10.00

