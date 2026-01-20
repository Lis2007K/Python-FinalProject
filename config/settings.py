
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "finance.db")
DEFAULT_CURRENCY = "USD"

# Simple salt for password hashing (ok for school project).
# For production, use a secure per-user salt and a proper password hashing library.
SECRET_SALT = "replace_with_some_random_string_for_school_project"
