"""
FastAPI server exposing CRUD endpoints for transactions.
Run separately from Streamlit UI on port 8000.

Usage:
  uvicorn api_server:app --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.api_simulation import (
    api_register,
    api_login,
    api_get_transactions,
    api_post_transaction,
    api_update_transaction,
    api_delete_transaction,
    api_get_monthly_summary,
    api_get_categories,
    api_get_balance,
    api_export_csv
)
from database.db import init_db


app = FastAPI(title="Personal Finance Tracker API")


# @app.on_event("startup")
# def startup_event():
#     init_db()


# ============ Request/Response Models ============


# ============ Request/Response Models ============

class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TransactionRequest(BaseModel):
    date_iso: str
    amount: float
    category: str
    ttype: str  # "income" or "expense"
    description: Optional[str] = None


class TransactionUpdateRequest(BaseModel):
    date_iso: str
    amount: float
    category: str
    ttype: str
    description: Optional[str] = None


class CategoriesRequest(BaseModel):
    ttype: str


# ============ Auth Endpoints ============

@app.post("/auth/register")
def register(req: RegisterRequest):
    """Register a new user"""
    result = api_register(req.username, req.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/auth/login")
def login(req: LoginRequest):
    """Login and get user info"""
    result = api_login(req.username, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result


# ============ Transaction CRUD Endpoints ============

@app.get("/transactions")
def get_transactions(user_id: int):
    """Get all transactions for a user"""
    result = api_get_transactions(user_id)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result


@app.post("/transactions")
def create_transaction(user_id: int, req: TransactionRequest):
    """Create a new transaction (CREATE)"""
    result = api_post_transaction(
        user_id=user_id,
        date_iso=req.date_iso,
        amount=req.amount,
        category=req.category,
        ttype=req.ttype,
        description=req.description
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.put("/transactions/{tx_id}")
def update_transaction(user_id: int, tx_id: int, req: TransactionUpdateRequest):
    """Update an existing transaction (UPDATE)"""
    result = api_update_transaction(
        user_id=user_id,
        tx_id=tx_id,
        date_iso=req.date_iso,
        amount=req.amount,
        category=req.category,
        ttype=req.ttype,
        description=req.description
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.delete("/transactions/{tx_id}")
def delete_transaction(user_id: int, tx_id: int):
    """Delete a transaction (DELETE)"""
    result = api_delete_transaction(user_id=user_id, tx_id=tx_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ============ Summary Endpoints ============

@app.get("/monthly-summary")
def get_monthly_summary(user_id: int):
    """Get monthly income/expense summary"""
    result = api_get_monthly_summary(user_id)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result


@app.get("/categories")
def get_categories_endpoint(ttype: str):
    """Get categories for transaction type"""
    result = api_get_categories(ttype)
    return result


@app.get("/balance")
def get_balance(user_id: int):
    """Get current balance"""
    result = api_get_balance(user_id)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result


@app.get("/export-csv")
def export_csv(user_id: int):
    """Export transactions to CSV"""
    result = api_export_csv(user_id)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result


# ============ Root ============

@app.get("/")
def root():
    """API health check"""
    return {"message": "Personal Finance Tracker API is running", "version": "1.0"}
