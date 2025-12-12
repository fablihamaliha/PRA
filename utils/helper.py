from datetime import datetime
from typing import Any, Dict, List
import json


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    if dt is None:
        return None
    return dt.isoformat()


def parse_json_field(value: Any) -> List:
    """Parse JSON field from database"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return []


def normalize_ingredient_name(ingredient: str) -> str:
    """Normalize ingredient name for comparison"""
    if not ingredient:
        return ""
    return ingredient.lower().strip().replace('-', ' ').replace('_', ' ')


def calculate_price_score(price: float, budget_min: float, budget_max: float) -> float:
    """Calculate price score (0-1) based on budget range"""
    if budget_min is None or budget_max is None:
        return 0.5

    budget_mid = (budget_min + budget_max) / 2
    budget_range = budget_max - budget_min

    if budget_range == 0:
        return 1.0 if price == budget_mid else 0.0

    # Score is highest at midpoint, decreases toward edges
    distance_from_mid = abs(price - budget_mid)
    score = 1.0 - (distance_from_mid / (budget_range / 2))

    return max(0.0, min(1.0, score))


def deduplicate_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate products based on name and brand"""
    seen = set()
    unique_products = []

    for product in products:
        key = f"{product['brand']}:{product['name']}".lower()
        if key not in seen:
            seen.add(key)
            unique_products.append(product)

    return unique_products


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

