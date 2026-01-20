from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    created_at: str

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return User(id=row[0], username=row[1], password_hash=row[2], created_at=row[3])


@dataclass
class Transaction:
    id: int
    user_id: int
    date: str    # ISO date string YYYY-MM-DD
    amount: float
    category: str
    ttype: str   # 'income' or 'expense'
    description: Optional[str]

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return Transaction(
            id=row[0],
            user_id=row[1],
            date=row[2],
            amount=float(row[3]),
            category=row[4],
            ttype=row[5],
            description=row[6]
        )
