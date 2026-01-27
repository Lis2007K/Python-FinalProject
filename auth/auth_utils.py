from utils.validators import validate_username, validate_password


def validate_username_password(username: str, password: str):
    if not validate_username(username):
        return False, "Username must be 3–20 characters long"

    if not validate_password(password):
        return False, "Password must be at least 6 characters"

    return True, "Validation successful"
