"""
Enhanced chart helpers with professional visualizations.
Each function returns a matplotlib.figure.Figure that Streamlit can display with st.pyplot().
"""

from typing import List, Dict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from database.models import Transaction
import collections


def plot_monthly_summary(summary: List[Dict]) -> "plt.Figure":
    """
    Line chart showing income and expense trends over time.
    summary: list of dicts with keys 'month', 'income', 'expense'
    returns matplotlib Figure
    """
    if not summary:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No monthly data available", ha="center", va="center", fontsize=12)
        ax.set_title("Monthly Trend", fontsize=14, fontweight="bold")
        return fig

    months = [s["month"] for s in summary]
    incomes = [float(s["income"]) for s in summary]
    expenses = [float(s["expense"]) for s in summary]
    net = [inc - exp for inc, exp in zip(incomes, expenses)]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    x = range(len(months))
    
    # Plot lines with markers
    ax.plot(x, incomes, marker="o", linewidth=3, markersize=9, 
            label="Income", color="#27ae60", markerfacecolor="#2ecc71", markeredgewidth=2)
    ax.plot(x, expenses, marker="s", linewidth=3, markersize=9, 
            label="Expense", color="#c0392b", markerfacecolor="#e74c3c", markeredgewidth=2)
    ax.plot(x, net, marker="D", linewidth=2.5, markersize=8, linestyle="--",
            label="Net (Income - Expense)", color="#3498db", markerfacecolor="#5dade2", markeredgewidth=2)
    
    # Add value labels
    for i, (income, expense, n) in enumerate(zip(incomes, expenses, net)):
        ax.text(i, income + 50, f'${income:,.0f}', ha='center', va='bottom', fontsize=8, color="#27ae60", fontweight="bold")
        ax.text(i, expense - 100, f'${expense:,.0f}', ha='center', va='top', fontsize=8, color="#c0392b", fontweight="bold")
    
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("Month", fontsize=12, fontweight="bold")
    ax.set_ylabel("Amount ($)", fontsize=12, fontweight="bold")
    ax.set_title("Monthly Income, Expense & Net Trend", fontsize=14, fontweight="bold", pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.legend(fontsize=11, loc="upper left")
    ax.grid(True, alpha=0.3, linestyle="--")
    
    plt.tight_layout()
    return fig


def pie_expense_by_category(transactions: List[Transaction], month_iso: str = None) -> "plt.Figure":
    """
    Enhanced horizontal bar chart for expenses by category with better styling.
    transactions: list of Transaction dataclasses
    month_iso: optional YYYY-MM string to filter by month
    Returns a chart figure of expenses per category.
    """
    cat_sums = collections.Counter()
    for t in transactions:
        if t.ttype != "expense":
            continue
        if month_iso and not t.date.startswith(month_iso):
            continue
        cat_sums[t.category] += t.amount

    fig, ax = plt.subplots(figsize=(10, 6))
    
    if cat_sums:
        # Sort by amount (descending)
        sorted_cats = sorted(cat_sums.items(), key=lambda x: x[1], reverse=True)
        categories = [item[0] for item in sorted_cats]
        amounts = [item[1] for item in sorted_cats]
        
        # Create horizontal bar chart with gradient colors
        colors = plt.cm.Spectral(range(len(categories)))
        bars = ax.barh(categories, amounts, color=colors, edgecolor="black", linewidth=1.2)
        
        # Add value labels on bars
        for i, (bar, amount) in enumerate(zip(bars, amounts)):
            ax.text(amount, i, f" ${amount:.2f}", va="center", fontsize=9, fontweight="bold")
        
        ax.set_xlabel("Amount ($)", fontsize=11, fontweight="bold")
        ax.set_title(f"Expenses by Category{(' - ' + month_iso) if month_iso else ''}", 
                     fontsize=14, fontweight="bold", pad=20)
        ax.grid(True, axis="x", alpha=0.3, linestyle="--")
    else:
        ax.text(0.5, 0.5, "No expense data", ha="center", va="center", fontsize=12)
        ax.set_title("Expenses by Category", fontsize=14, fontweight="bold")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    
    plt.tight_layout()
    return fig


def plot_income_vs_expense_bars(summary: List[Dict]) -> "plt.Figure":
    """
    Side-by-side bar chart comparing income and expenses by month.
    """
    if not summary:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=12)
        return fig

    months = [s["month"] for s in summary]
    incomes = [s["income"] for s in summary]
    expenses = [s["expense"] for s in summary]

    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(months))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], incomes, width, label="Income", color="#2ecc71", edgecolor="black", linewidth=1)
    bars2 = ax.bar([i + width/2 for i in x], expenses, width, label="Expense", color="#e74c3c", edgecolor="black", linewidth=1)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:.0f}', ha='center', va='bottom', fontsize=8)
    
    ax.set_xlabel("Month", fontsize=11, fontweight="bold")
    ax.set_ylabel("Amount ($)", fontsize=11, fontweight="bold")
    ax.set_title("Income vs Expense Comparison", fontsize=14, fontweight="bold", pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.legend(fontsize=10)
    ax.grid(True, axis="y", alpha=0.3, linestyle="--")
    
    plt.tight_layout()
    return fig


def plot_category_income_expense(transactions: List[Transaction]) -> "plt.Figure":
    """
    Donut chart showing distribution across all transaction categories (both income and expense).
    """
    cat_sums = collections.Counter()
    for t in transactions:
        cat_sums[t.category] += t.amount

    fig, ax = plt.subplots(figsize=(8, 8))
    
    if cat_sums:
        labels = list(cat_sums.keys())
        sizes = list(cat_sums.values())
        
        # Create donut chart
        colors = plt.cm.Set3(range(len(labels)))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct="%1.1f%%",
                                           colors=colors, startangle=90,
                                           wedgeprops=dict(edgecolor="white", linewidth=2))
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(9)
        
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight("bold")
        
        # Draw circle in center for donut effect
        centre_circle = plt.Circle((0, 0), 0.70, fc="white", edgecolor="black", linewidth=2)
        ax.add_artist(centre_circle)
        
        ax.set_title("Transaction Distribution by Category", fontsize=14, fontweight="bold", pad=20)
    else:
        ax.text(0.5, 0.5, "No transaction data", ha="center", va="center", fontsize=12)
        ax.set_title("Transaction Distribution by Category", fontsize=14, fontweight="bold")
    
    plt.tight_layout()
    return fig


def plot_cumulative_balance(transactions: List[Transaction]) -> "plt.Figure":
    """
    Line chart showing cumulative balance over time.
    """
    if not transactions:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=12)
        return fig

    # Sort transactions by date
    sorted_txs = sorted(transactions, key=lambda t: t.date)
    
    dates = []
    balances = []
    cumulative = 0
    
    for t in sorted_txs:
        dates.append(t.date)
        if t.ttype == "income":
            cumulative += t.amount
        else:
            cumulative -= t.amount
        balances.append(cumulative)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Color the line based on positive/negative balance
    colors = ["#2ecc71" if b >= 0 else "#e74c3c" for b in balances]
    
    ax.plot(dates, balances, marker="o", linewidth=2.5, markersize=6, color="#3498db")
    ax.fill_between(range(len(dates)), balances, alpha=0.2, color="#3498db")
    ax.axhline(y=0, color="black", linestyle="--", linewidth=1, alpha=0.5)
    
    ax.set_xlabel("Date", fontsize=11, fontweight="bold")
    ax.set_ylabel("Cumulative Balance ($)", fontsize=11, fontweight="bold")
    ax.set_title("Cumulative Balance Over Time", fontsize=14, fontweight="bold", pad=20)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_xticklabels(dates[::max(1, len(dates)//6)], rotation=45, ha="right")
    
    plt.tight_layout()
    return fig
