"""Shopping calculator API routes."""
from fastapi import APIRouter
import logging

from app.shopping.models import ShoppingTotalRequest, ShoppingTotalResponse
from app.shopping.service import ShoppingCalculatorService

logger = logging.getLogger(__name__)

router = APIRouter()
calculator_service = ShoppingCalculatorService()


@router.post("/total", response_model=ShoppingTotalResponse)
async def calculate_total(
    request: ShoppingTotalRequest
) -> ShoppingTotalResponse:
    """
    Calculate total cost of purchased items plus tax.
    
    Args:
        request: Shopping calculation request with costs, items, and tax rate
        
    Returns:
        Shopping total response with breakdown
    """
    return calculator_service.calculate_total(request)

