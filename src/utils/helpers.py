"""
Helper utilities
"""

import logging
from datetime import datetime
from typing import Any, Dict


def setup_logging(level=logging.INFO):
    """
    Setup logging configuration

    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def format_currency_name(name: str) -> str:
    """
    Format currency name for display

    Args:
        name (str): Raw currency name

    Returns:
        str: Formatted name
    """
    return name.replace('-', ' ').title()


def format_chaos_value(value: float) -> str:
    """
    Format chaos value for display

    Args:
        value (float): Chaos value

    Returns:
        str: Formatted string
    """
    if value >= 1:
        return f"{value:.2f}c"
    else:
        return f"1:{int(1/value)}c" if value > 0 else "N/A"


def format_percentage(value: float, show_sign: bool = True) -> str:
    """
    Format percentage value

    Args:
        value (float): Percentage value
        show_sign (bool): Whether to show + sign for positive values

    Returns:
        str: Formatted percentage
    """
    if show_sign:
        return f"{value:+.2f}%"
    return f"{value:.2f}%"


def format_timestamp(timestamp: str) -> str:
    """
    Format ISO timestamp for display

    Args:
        timestamp (str): ISO format timestamp

    Returns:
        str: Formatted timestamp
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp


def calculate_time_ago(timestamp: str) -> str:
    """
    Calculate human-readable time ago

    Args:
        timestamp (str): ISO format timestamp

    Returns:
        str: Time ago string
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        now = datetime.now()
        diff = now - dt

        seconds = diff.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"
    except:
        return "unknown"


def validate_currency_data(data: Dict) -> bool:
    """
    Validate currency data structure

    Args:
        data (dict): Currency data

    Returns:
        bool: True if valid
    """
    required_fields = ['chaosEquivalent']
    return all(field in data for field in required_fields)


def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """
    Safely divide two numbers

    Args:
        numerator (float): Numerator
        denominator (float): Denominator
        default (float): Default value if division fails

    Returns:
        float: Result or default
    """
    try:
        if denominator != 0:
            return numerator / denominator
    except:
        pass
    return default
