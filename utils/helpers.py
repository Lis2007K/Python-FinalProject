from datetime import datetime
from dateutil.parser import parse


def parse_date(date_str: str) -> str:
    """
    Parses any valid date string and returns ISO format (YYYY-MM-DD)
    """
    return parse(date_str).date().isoformat()


def format_currency(amount: float, currency: str) -> str:
    return f"{currency} {amount:.2f}"


def safe_str(value) -> str:
    return "" if value is None else str(value)
