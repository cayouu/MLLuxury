"""
Validation utilities for forecast requests
"""
from typing import List
from datetime import datetime

def validate_product_ids(product_ids: List[str]) -> bool:
    """Valider les IDs de produits"""
    if not product_ids:
        return False
    if len(product_ids) > 100:  # Limite raisonnable
        return False
    return True

def validate_date(date_str: str) -> bool:
    """Valider le format de date"""
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False

def validate_horizon(weeks: int) -> bool:
    """Valider l'horizon de prévision"""
    return 1 <= weeks <= 52  # Entre 1 semaine et 1 an
