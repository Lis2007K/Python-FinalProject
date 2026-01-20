

import re
from typing import Tuple


def validate_username_password(username: str, password: str) -> Tuple[bool, str]:

    if not username or not password:
        return False, 

    username = username.strip()
    if len(username) < 3 or len(username) > 30:
        return False, 

    if not re.match(r"^[A-Za-z0-9_.-]+$", username):
        return False, 
    # Password rules (basic)
    if len(password) < 6:
        return False, 

    # Encourage a digit and a letter (not required, just a soft check)
    if not (re.search(r"[0-9]", password) and re.search(r"[A-Za-z]", password)):
        return False, 

    return True, 
