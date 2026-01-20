"""Shopping calculator API routes."""
from fastapi import APIRouter, HTTPException, status, Body
from typing import Dict, Any
import logging

from app.shopping.models import (
    ShoppingTotalRequest,
    ShoppingTotalSimpleRequest,
    ShoppingTotalResponse
)
from app.shopping.service import ShoppingCalculatorService

logger = logging.getLogger(__name__)

router = APIRouter()
calculator_service = ShoppingCalculatorService()


def _detect_and_parse_request(data: Dict[str, Any]) -> ShoppingTotalRequest:
    """
    Detect request format and parse into standard request.
    
    Detects between:
    - Standard format: {"costs": {...}, "items": [...], "tax": ...}
    - Simple format: {"costs_input": "...", "items_input": "...", "tax": ...}
    """
    # Check if it's simple format (has costs_input or items_input)
    if "costs_input" in data or "items_input" in data:
        # Simple format
        try:
            simple_request = ShoppingTotalSimpleRequest(**data)
            return simple_request.to_standard_request()
        except Exception as e:
            raise ValueError(f"Invalid simple format: {str(e)}")
    else:
        # Standard format (original JSON)
        try:
            return ShoppingTotalRequest(**data)
        except Exception as e:
            raise ValueError(f"Invalid standard format: {str(e)}")


@router.post(
    "/total",
    response_model=ShoppingTotalResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate shopping cart total with tax",
    description="""
    Calculate the total cost of items in a shopping cart, including tax.
    
    **Accepts two formats automatically - detects format automatically!**
    
    **Format 1: JSON (original format)**
    ```json
    {
        "costs": {"apple": 1.50, "banana": 2.00, "orange": 1.75},
        "items": ["apple", "banana", "apple"],
        "tax": 0.1
    }
    ```
    
    **Format 2: Simple text (user-friendly - no JSON required!)**
    ```json
    {
        "costs_input": "apple: 1.50\\nbanana: 0.75\\norange: 2.00",
        "items_input": "apple, banana, apple",
        "tax": 0.1
    }
    ```
    
    The endpoint automatically detects which format you're using based on the keys in the request!
    
    **Result:**
    - Subtotal: $5.00 (1.50 + 2.00 + 1.50)
    - Tax (10%): $0.50
    - Total: $5.50
    """
)
async def calculate_total(
    data: Dict[str, Any] = Body(...)
) -> ShoppingTotalResponse:
    """
    Calculate total cost of purchased items plus tax.
    
    Automatically accepts both JSON format and simple text format.
    Detects the format based on the request structure (checks for 'costs_input' or 'items_input' keys).
    
    **Supported Formats:**
    
    **Format 1: Standard JSON (original - backward compatible)**
    ```json
    {
        "costs": {"apple": 1.50, "banana": 2.00},
        "items": ["apple", "banana"],
        "tax": 0.1
    }
    ```
    
    **Format 2: Simple Text (new - user-friendly, no JSON required)**
    ```json
    {
        "costs_input": "apple: 1.50\\nbanana: 0.75",
        "items_input": "apple, banana",
        "tax": 0.1
    }
    ```
    
    **Calculation:**
    1. Subtotal = sum of costs for all found items
    2. Tax Amount = subtotal × tax_rate
    3. Total = subtotal + tax_amount
    
    All monetary values are rounded to 2 decimal places.
    
    Args:
        data: Request body in either JSON or simple text format (detected automatically)
        
    Returns:
        Shopping total response with detailed breakdown
        
    Raises:
        HTTPException 400: If parsing or validation fails
    """
    try:
        # Detect format and parse into standard request
        standard_request = _detect_and_parse_request(data)
        
        # Calculate using the standard request
        result = calculator_service.calculate_total(standard_request)
        
        # Warn user if some items were not found
        if result.items_not_found:
            logger.warning(
                f"Some items were not found in costs dictionary: {result.items_not_found}"
            )
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation failed",
                "message": str(e),
                "hint": "Ensure costs are non-negative, tax is between 0 and 1, and items list is not empty."
            }
        )


@router.post(
    "/total-simple",
    response_model=ShoppingTotalResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate shopping cart total (simple input format)",
    description="""
    Calculate the total cost of items in a shopping cart using simple text inputs.
    
    **User-friendly format - no JSON required!**
    
    **Costs Input Formats:**
    - One per line: `apple: 1.50\nbanana: 0.75\norange: 2.00`
    - Comma separated: `apple: 1.50, banana: 0.75, orange: 2.00`
    - JSON (also supported): `{"apple": 1.50, "banana": 0.75}`
    
    **Items Input Formats:**
    - Comma separated: `apple, banana, orange`
    - Newline separated: `apple\nbanana\norange`
    - Space separated: `apple banana orange`
    
    **Example Request:**
    ```json
    {
        "costs_input": "apple: 1.50\\nbanana: 0.75\\norange: 2.00",
        "items_input": "apple, banana, apple",
        "tax": 0.1
    }
    ```
    """
)
async def calculate_total_simple(
    request: ShoppingTotalSimpleRequest
) -> ShoppingTotalResponse:
    """
    Calculate total cost using simple text inputs (no JSON required).
    
    This endpoint accepts plain text formats that are easier to use than JSON.
    The backend automatically parses the text into structured data.
    
    **Costs Input:**
    - Format: `item: price` (one per line or comma-separated)
    - Example: `apple: 1.50\nbanana: 0.75` or `apple: 1.50, banana: 0.75`
    
    **Items Input:**
    - Format: Comma, newline, or space separated
    - Example: `apple, banana, orange` or `apple\nbanana\norange`
    
    Args:
        request: Simple request with text inputs that will be parsed automatically
        
    Returns:
        Shopping total response with detailed breakdown
        
    Raises:
        HTTPException 400: If parsing fails or validation errors occur
    """
    try:
        # Convert simple request to standard request format
        standard_request = request.to_standard_request()
        
        # Use the same service logic
        result = calculator_service.calculate_total(standard_request)
        
        # Warn user if some items were not found
        if result.items_not_found:
            logger.warning(
                f"Some items were not found in costs dictionary: {result.items_not_found}"
            )
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Parsing or validation failed",
                "message": str(e),
                "hint": (
                    "For costs, use format: 'item: price' (one per line or comma-separated). "
                    "For items, use comma, newline, or space separated values."
                )
            }
        )

