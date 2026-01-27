"""
Category management (predefined categories + optional simple persistence for custom categories).
Custom categories are stored in data/categories.json
"""

import json
import os
from typing import List
from config import settings

DEFAULT_CATEGORIES = ["Food", "Rent", "Transport", "Utilities", "Salary", "Entertainment", "Other"]
_CATEGORIES_FILE = os.path.join(settings.DATA_DIR, "categories.json")


def _ensure_file():
    if not os.path.exists(settings.DATA_DIR):
        os.makedirs(settings.DATA_DIR, exist_ok=True)
    if not os.path.exists(_CATEGORIES_FILE):
        with open(_CATEGORIES_FILE, "w", encoding="utf-8") as f:
            json.dump({"custom": []}, f)


def get_categories(transaction_type: str):
    if transaction_type == "income":
        return [
            "Salary",
            "Freelance",
            "Gift",
            "Investment"
        ]

    return [
        "Food",
        "Transport",
        "Rent",
        "Entertainment",
        "Utilities",
        "Other"
    ]



def add_custom_category(name: str) -> bool:
    """
    Add a custom category to persistence. Returns True on success.
    """
    if not name or not name.strip():
        return False
    name = name.strip()
    _ensure_file()
    try:
        with open(_CATEGORIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        custom = data.get("custom", [])
        if name in custom:
            return True
        custom.append(name)
        data["custom"] = custom
        with open(_CATEGORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def reset_custom_categories() -> None:
    """
    Reset custom categories to empty.
    """
    _ensure_file()
    with open(_CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump({"custom": []}, f)
