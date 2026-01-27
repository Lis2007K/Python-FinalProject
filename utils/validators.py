def validate_username(username: str) -> bool:
    return isinstance(username, str) and 3 <= len(username) <= 20


def validate_password(password: str) -> bool:
    return isinstance(password, str) and len(password) >= 6


def validate_amount(amount: float) -> bool:
    return isinstance(amount, (int, float)) and amount > 0


def validate_transaction_type(ttype: str) -> bool:
    return ttype in ("income", "expense")
