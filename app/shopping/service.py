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
    Handles monetary calculations with proper rounding (2 decimal places).
    Follows Single Responsibility Principle.
    """
    
    DECIMAL_PLACES = 2
    ROUNDING_PRECISION = Decimal('0.01')
    
    @classmethod
    def _round_to_decimal_places(cls, value: float) -> float:
        """
        Round a float to 2 decimal places using standard rounding (half up).
        
        Used for all monetary values to ensure proper currency formatting.
        
        Args:
            value: The value to round
            
        Returns:
            Rounded value to 2 decimal places
            
        Example:
            >>> _round_to_decimal_places(10.555)
            10.56
            >>> _round_to_decimal_places(10.554)
            10.55
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
        Calculate subtotal and categorize items by availability.
        
        Processes each item in the list and looks up its cost in the costs dictionary.
        Items not found are logged and returned separately.
        
        Args:
            items: List of items to calculate (may contain duplicates)
            costs: Dictionary mapping item names to their unit costs
            
        Returns:
            Tuple containing:
            - subtotal: Sum of costs for all found items
            - items_found: List of items that were successfully priced
            - items_not_found: List of items that were not in the costs dictionary
        """
        subtotal = 0.0
        items_found: List[str] = []
        items_not_found: List[str] = []
        
        for item in items:
            item_stripped = item.strip() if item else ""
            if not item_stripped:
                continue  # Skip empty items (should be validated upstream)
                
            item_cost = costs.get(item_stripped)
            if item_cost is not None:
                subtotal += item_cost
                items_found.append(item_stripped)
            else:
                items_not_found.append(item_stripped)
                logger.warning(
                    f"Item '{item_stripped}' not found in costs dictionary. "
                    f"Available items: {list(costs.keys())[:5]}..."
                )
        
        return subtotal, items_found, items_not_found
    
    def _calculate_tax_and_total(
        self,
        subtotal: float,
        tax_rate: float
    ) -> Tuple[float, float]:
        """
        Calculate tax amount and final total.
        
        Tax is calculated as: tax_amount = subtotal * tax_rate
        Total is calculated as: total = subtotal + tax_amount
        
        Args:
            subtotal: Subtotal before tax (must be >= 0)
            tax_rate: Tax rate as decimal (e.g., 0.1 for 10%, 0.15 for 15%)
                     Must be between 0 and 1 (inclusive)
            
        Returns:
            Tuple of (tax_amount, total) where both are positive floats
            
        Example:
            >>> _calculate_tax_and_total(100.0, 0.1)
            (10.0, 110.0)
        """
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        return tax_amount, total
    
    def calculate_total(self, request: ShoppingTotalRequest) -> ShoppingTotalResponse:
        """
        Calculate total cost of purchased items plus tax.
        
        Processes a shopping cart with items and their costs, applies tax,
        and returns a detailed breakdown of the calculation.
        
        **Calculation Process:**
        1. Calculate subtotal by summing costs of all found items
        2. Calculate tax amount: subtotal × tax_rate
        3. Calculate total: subtotal + tax_amount
        4. Round all monetary values to 2 decimal places
        
        Items not found in the costs dictionary are listed separately
        and do not contribute to the total.
        
        Args:
            request: Shopping calculation request containing:
                    - costs: Dictionary of item prices
                    - items: List of items to purchase
                    - tax: Tax rate as decimal (0.0 to 1.0)
            
        Returns:
            Shopping total response with:
            - subtotal: Cost before tax (rounded)
            - tax_amount: Tax amount (rounded)
            - total: Final total including tax (rounded)
            - items_found: Items successfully priced
            - items_not_found: Items without prices
            - items_count: Total number of items processed
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
        
        # Round all monetary values to 2 decimal places
        subtotal_rounded = self._round_to_decimal_places(subtotal)
        tax_amount_rounded = self._round_to_decimal_places(tax_amount)
        total_rounded = self._round_to_decimal_places(total)
        
        items_count = len(items_found) + len(items_not_found)
        
        logger.info(
            f"Calculated shopping total: ${total_rounded:.2f} "
            f"(subtotal: ${subtotal_rounded:.2f}, tax: ${tax_amount_rounded:.2f}) "
            f"for {len(items_found)} items found, {len(items_not_found)} items not found"
        )
        
        return ShoppingTotalResponse(
            subtotal=subtotal_rounded,
            tax_amount=tax_amount_rounded,
            total=total_rounded,
            items_found=items_found,
            items_not_found=items_not_found,
            items_count=items_count
        )

