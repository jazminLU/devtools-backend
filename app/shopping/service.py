"""Business logic for shopping calculator."""
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple

from app.shopping.models import ShoppingTotalRequest, ShoppingTotalResponse

logger = logging.getLogger(__name__)


class ShoppingCalculatorService:
    """
    Service for shopping cost calculations.
    
    Implements business logic for calculating shopping totals with tax.
    Follows Single Responsibility Principle.
    """
    
    DECIMAL_PLACES = 2
    ROUNDING_PRECISION = Decimal('0.01')
    
    @classmethod
    def _round_to_decimal_places(cls, value: float) -> float:
        """
        Round a float to specified decimal places using banker's rounding.
        
        Args:
            value: The value to round
            
        Returns:
            Rounded value to 2 decimal places
        """
        decimal_value = Decimal(str(value))
        rounded = decimal_value.quantize(
            cls.ROUNDING_PRECISION,
            rounding=ROUND_HALF_UP
        )
        return float(rounded)
    
    def _calculate_subtotal(
        self,
        items: List[str],
        costs: dict[str, float]
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculate subtotal and categorize items.
        
        Args:
            items: List of items to calculate
            costs: Dictionary mapping items to their costs
            
        Returns:
            Tuple of (subtotal, items_found, items_not_found)
        """
        subtotal = 0.0
        items_found: List[str] = []
        items_not_found: List[str] = []
        
        for item in items:
            item_cost = costs.get(item)
            if item_cost is not None:
                subtotal += item_cost
                items_found.append(item)
            else:
                items_not_found.append(item)
                logger.warning(f"Item not found in costs dictionary: {item}")
        
        return subtotal, items_found, items_not_found
    
    def _calculate_tax_and_total(
        self,
        subtotal: float,
        tax_rate: float
    ) -> Tuple[float, float]:
        """
        Calculate tax amount and total.
        
        Args:
            subtotal: Subtotal before tax
            tax_rate: Tax rate as decimal (e.g., 0.1 for 10%)
            
        Returns:
            Tuple of (tax_amount, total)
        """
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        return tax_amount, total
    
    def calculate_total(self, request: ShoppingTotalRequest) -> ShoppingTotalResponse:
        """
        Calculate total cost of purchased items plus tax.
        
        Args:
            request: Shopping calculation request
            
        Returns:
            Shopping total response with breakdown
        """
        # Calculate subtotal and categorize items
        subtotal, items_found, items_not_found = self._calculate_subtotal(
            request.items,
            request.costs
        )
        
        # Calculate tax and total
        tax_amount, total = self._calculate_tax_and_total(
            subtotal,
            request.tax
        )
        
        # Round all monetary values
        subtotal_rounded = self._round_to_decimal_places(subtotal)
        tax_amount_rounded = self._round_to_decimal_places(tax_amount)
        total_rounded = self._round_to_decimal_places(total)
        
        logger.info(
            f"Calculated total: {total_rounded} for "
            f"{len(items_found)} items (subtotal: {subtotal_rounded}, "
            f"tax: {tax_amount_rounded})"
        )
        
        return ShoppingTotalResponse(
            subtotal=subtotal_rounded,
            tax_amount=tax_amount_rounded,
            total=total_rounded,
            items_found=items_found,
            items_not_found=items_not_found
        )

