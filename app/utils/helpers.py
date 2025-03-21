"""
Helper functions and utilities
"""
import logging
from typing import Dict, Any
import json
from app.models.schemas import DecimalEncoder

logger = logging.getLogger(__name__)

def format_response(data: Dict[str, Any]) -> str:
    """Format response dictionary as pretty JSON string"""
    try:
        return json.dumps(data, indent=2, cls=DecimalEncoder)
    except Exception as e:
        logger.error(f"Error formatting response: {e}")
        return str(data)


def format_address(address: str) -> str:
    """Format Ethereum address for display (0x123...abc)"""
    if not address or len(address) < 10:
        return address
    return f"{address[:6]}...{address[-4:]}"