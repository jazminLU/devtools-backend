from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, List, Optional
import re
import json


class ShoppingTotalRequest(BaseModel):
    costs: Dict[str, float] = Field(
        ...,
        min_length=1,
        description="Dictionary mapping item names to their costs (price per item)",
        examples=[{"apple": 1.50, "banana": 2.00, "orange": 1.75}]
    )
    items: List[str] = Field(
        ...,
        min_items=1,
        description="List of items to calculate total for",
        examples=[["apple", "banana", "apple"]]
    )
    tax: float = Field(
        ...,
        ge=0,
        le=1,
        description="Tax rate as a decimal (e.g., 0.1 for 10%, 0.15 for 15%)",
        examples=[0.1]
    )
    
    @field_validator('costs')
    @classmethod
    def validate_costs(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate that all costs are non-negative."""
        for item, cost in v.items():
            if cost < 0:
                raise ValueError(f"Cost for '{item}' cannot be negative: {cost}")
        return v
    
    @field_validator('items')
    @classmethod
    def validate_items_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure items list is not empty."""
        if not v:
            raise ValueError("At least one item is required")
        # Filter out empty strings
        filtered = [item.strip() for item in v if item and item.strip()]
        if not filtered:
            raise ValueError("Items list cannot contain only empty strings")
        return filtered


class ShoppingTotalSimpleRequest(BaseModel):
    """
    Simple request format that accepts plain text inputs instead of JSON.
    
    User-friendly format that parses plain text into structured data.
    """
    costs_input: str = Field(
        ...,
        description=(
            "Item costs in simple format. Accepts:\n"
            "- JSON: {\"apple\": 1.50, \"banana\": 0.75}\n"
            "- Key:Value pairs (one per line): apple: 1.50\\nbanana: 0.75\n"
            "- Comma separated: apple: 1.50, banana: 0.75"
        ),
        examples=["apple: 1.50\nbanana: 0.75\norange: 2.00"]
    )
    items_input: str = Field(
        ...,
        description=(
            "Items to calculate in simple format. Accepts:\n"
            "- Comma separated: apple, banana, orange\n"
            "- Newline separated: apple\\nbanana\\norange\n"
            "- Space separated: apple banana orange"
        ),
        examples=["apple, banana, orange"]
    )
    tax: float = Field(
        ...,
        ge=0,
        le=1,
        description="Tax rate as a decimal (e.g., 0.1 for 10%, 0.15 for 15%)",
        examples=[0.1]
    )
    
    @model_validator(mode='after')
    def parse_inputs(self) -> 'ShoppingTotalSimpleRequest':
        """Parse simple text inputs into structured format."""
        # Parse costs_input into Dict[str, float]
        costs_dict = self._parse_costs(self.costs_input)
        
        # Parse items_input into List[str]
        items_list = self._parse_items(self.items_input)
        
        # Replace the input strings with parsed structures
        # Store as private attributes that we'll use later
        self._parsed_costs = costs_dict
        self._parsed_items = items_list
        
        return self
    
    @staticmethod
    def _parse_costs(costs_input: str) -> Dict[str, float]:
        """
        Parse costs input string into dictionary.
        
        Supports multiple formats:
        1. JSON: {"apple": 1.50, "banana": 0.75}
        2. Key:Value lines: apple: 1.50\\nbanana: 0.75
        3. Comma separated: apple: 1.50, banana: 0.75
        """
        costs_input = costs_input.strip()
        if not costs_input:
            raise ValueError("Costs input cannot be empty")
        
        costs_dict: Dict[str, float] = {}
        
        # Try to parse as JSON first
        if costs_input.strip().startswith('{'):
            try:
                costs_dict = json.loads(costs_input)
                # Validate all values are numbers
                for key, value in costs_dict.items():
                    if not isinstance(value, (int, float)):
                        raise ValueError(f"Cost for '{key}' must be a number, got: {value}")
                    if value < 0:
                        raise ValueError(f"Cost for '{key}' cannot be negative: {value}")
                    costs_dict[key] = float(value)
                return costs_dict
            except json.JSONDecodeError:
                # Not valid JSON, continue to other formats
                pass
        
        # Try key:value format (lines or comma-separated)
        # Pattern: "item: price" or "item:price"
        lines = re.split(r'[,;\n]', costs_input)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match "item: price" or "item:price" format
            match = re.match(r'^(.+?)[:]\s*(.+)$', line)
            if match:
                item = match.group(1).strip()
                price_str = match.group(2).strip()
                
                if not item:
                    continue
                
                try:
                    price = float(price_str)
                    if price < 0:
                        raise ValueError(f"Cost for '{item}' cannot be negative: {price}")
                    costs_dict[item] = price
                except ValueError as e:
                    if "cannot be negative" in str(e):
                        raise
                    raise ValueError(f"Invalid price format for '{item}': '{price_str}'. Must be a number.")
            else:
                # If no colon found, skip this line (might be part of another format)
                # Could be a simple list, but we need key:value pairs for costs
                continue
        
        if not costs_dict:
            raise ValueError(
                "Could not parse costs input. Use format: 'item: price' (one per line or comma-separated) "
                "or JSON format: {\"item\": price}"
            )
        
        return costs_dict
    
    @staticmethod
    def _parse_items(items_input: str) -> List[str]:
        """
        Parse items input string into list.
        
        Supports multiple formats:
        1. Comma separated: apple, banana, orange
        2. Newline separated: apple\\nbanana\\norange
        3. Space separated: apple banana orange
        """
        items_input = items_input.strip()
        if not items_input:
            raise ValueError("Items input cannot be empty")
        
        items: List[str] = []
        
        # Try comma-separated first
        if ',' in items_input:
            items = [item.strip() for item in items_input.split(',') if item.strip()]
        # Try newline-separated
        elif '\n' in items_input:
            items = [item.strip() for item in items_input.split('\n') if item.strip()]
        # Try space-separated (only if it looks like a list, not a single word)
        elif ' ' in items_input and len(items_input.split()) > 1:
            items = [item.strip() for item in items_input.split() if item.strip()]
        else:
            # Single item
            items = [items_input.strip()] if items_input.strip() else []
        
        # Filter out empty items
        items = [item for item in items if item]
        
        if not items:
            raise ValueError("At least one item is required")
        
        return items
    
    def to_standard_request(self) -> 'ShoppingTotalRequest':
        """Convert simple request to standard request format."""
        return ShoppingTotalRequest(
            costs=self._parsed_costs,
            items=self._parsed_items,
            tax=self.tax
        )


class ShoppingTotalResponse(BaseModel):
    subtotal: float = Field(..., description="Total cost of items before tax (rounded to 2 decimals)")
    tax_amount: float = Field(..., description="Tax amount calculated (rounded to 2 decimals)")
    total: float = Field(..., description="Final total including tax (rounded to 2 decimals)")
    items_found: List[str] = Field(..., description="Items that were found in the costs dictionary")
    items_not_found: List[str] = Field(..., description="Items that were not found in the costs dictionary")
    items_count: int = Field(..., description="Total number of items processed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subtotal": 5.00,
                "tax_amount": 0.50,
                "total": 5.50,
                "items_found": ["apple", "banana", "apple"],
                "items_not_found": [],
                "items_count": 3
            }
        }

