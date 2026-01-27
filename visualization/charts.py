"""
Reusable chart helpers based on matplotlib.
Each function returns a matplotlib.figure.Figure that Streamlit can display with st.pyplot().
"""

from typing import List, Dict
import matplotlib.pyplot as plt
from database.models import Transaction


def plot_monthly_summary(summary: List[Dict]) -> "plt.Figure":
    """
    summary: list of dicts with keys 'month', 'income', 'expense'
    returns matplotlib Figure
    """
    months = [s["month"] for s in summary]
    incomes = [s["income"] for s in summary]
    expenses = [s["expense"] for s in summary]

    fig, ax = plt.subplots()
    ax.plot(months, incomes, marker="o", label="Income")
    ax.plot(months, expenses, marker="o", label="Expense")
    ax.set_title("Monthly Income vs Expense")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def pie_expense_by_category(transactions: List[Transaction], month_iso: str = None) -> "plt.Figure":
    """
    transactions: list of Transaction dataclasses
    month_iso: optional YYYY-MM string to filter by month
    Returns a pie chart figure of expenses per category.
    """
    import collections
    cat_sums = collections.Counter()
    for t in transactions:
        if t.ttype != "expense":
            continue
        if month_iso and not t.date.startswith(month_iso):
            continue
        cat_sums[t.category] += t.amount

    fig, ax = plt.subplots()
    if cat_sums:
        labels = list(cat_sums.keys())
        sizes = list(cat_sums.values())
        ax.pie(sizes, labels=labels, autopct="%1.1f%%")
        ax.set_title(f"Expenses by category{(' (' + month_iso + ')') if month_iso else ''}")
    else:
        ax.text(0.5, 0.5, "No expense data", ha="center", va="center")
        ax.set_title("Expenses by category")
    plt.tight_layout()
    return fig
