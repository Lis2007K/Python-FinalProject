"""
Streamlit frontend (main entry).
Provides basic register/login, add transactions, view list + simple charts.
"""

import streamlit as st
from datetime import date
import matplotlib.pyplot as plt

from config import settings
from database.db import init_db, create_user, verify_user, add_transaction, get_transactions_by_user, get_balance, get_monthly_summary
from database.models import Transaction

# Initialize DB
init_db()

st.set_page_config(page_title="Personal Finance Tracker", layout="centered")

# ---- Helpers ----
def hash_msg(msg: str) -> str:
    # not used for passwords here (handled in db), but kept for demonstration
    import hashlib
    return hashlib.sha256(msg.encode()).hexdigest()


def ensure_session():
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None

ensure_session()

# Predefined categories (you can expand)
CATEGORIES = ["Food", "Rent", "Transport", "Utilities", "Salary", "Entertainment", "Other"]

# ---- Sidebar: Auth ----
st.sidebar.title("Account")
auth_mode = st.sidebar.radio("Choose", ["Login", "Register", "Logout"] if st.session_state["user_id"] else ["Login", "Register"])

if auth_mode == "Register":
    st.sidebar.subheader("Create account")
    new_username = st.sidebar.text_input("Username", key="reg_user")
    new_password = st.sidebar.text_input("Password", type="password", key="reg_pw")
    if st.sidebar.button("Register"):
        if not new_username or not new_password:
            st.sidebar.error("Provide username and password")
        else:
            ok, msg = create_user(new_username.strip(), new_password)
            if ok:
                st.sidebar.success("User created. Please login.")
            else:
                st.sidebar.error(msg)

elif auth_mode == "Login":
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username", key="login_user")
    password = st.sidebar.text_input("Password", type="password", key="login_pw")
    if st.sidebar.button("Login"):
        ok, user = verify_user(username.strip(), password)
        if ok and user:
            st.session_state["user_id"] = user.id
            st.session_state["username"] = user.username
            st.sidebar.success(f"Logged in as {user.username}")
        else:
            st.sidebar.error("Invalid credentials")

elif auth_mode == "Logout":
    if st.sidebar.button("Logout"):
        st.session_state["user_id"] = None
        st.session_state["username"] = None
        st.sidebar.success("Logged out")

# ---- Main UI ----
st.title("Personal Finance Tracker")

if not st.session_state["user_id"]:
    st.info("Please register or login from the left sidebar to begin.")
    st.write("Why this project is useful: track your expenses, see monthly overviews, and learn core Python concepts.")
    st.write("After login you can add transactions and view summaries and charts.")
    st.stop()

user_id = st.session_state["user_id"]
st.write(f"Hello, **{st.session_state['username']}** — Balance: **{settings.DEFAULT_CURRENCY} {get_balance(user_id):.2f}**")

# Add Transaction
st.header("Add Transaction")
with st.form("tx_form"):
    tx_date = st.date_input("Date", value=date.today())
    ttype = st.selectbox("Type", ["expense", "income"])
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    category = st.selectbox("Category", CATEGORIES)
    description = st.text_input("Description (optional)")
    submitted = st.form_submit_button("Save")
    if submitted:
        if amount <= 0:
            st.error("Amount must be positive")
        else:
            ok, msg = add_transaction(
                user_id=user_id,
                date_iso=tx_date.isoformat(),
                amount=float(amount),
                category=category,
                ttype=ttype,
                description=description or None
            )
            if ok:
                st.success("Transaction saved")
            else:
                st.error(msg)

# Recent Transactions
st.header("Recent Transactions")
transactions = get_transactions_by_user(user_id, limit=100)
if transactions:
    # simple table-like display
    for t in transactions[:50]:
        sign = "+" if t.ttype == "income" else "-"
        st.write(f"{t.date} — {t.category} — {sign}{abs(t.amount):.2f} {settings.DEFAULT_CURRENCY} — {t.description or ''}")
else:
    st.write("No transactions yet. Add one above.")

# Monthly Summary & Charts
st.header("Monthly Summary")
summary = get_monthly_summary(user_id)
if summary:
    months = [s["month"] for s in summary]
    incomes = [s["income"] for s in summary]
    expenses = [s["expense"] for s in summary]

    fig, ax = plt.subplots()
    ax.plot(months, incomes, marker='o', label="Income")
    ax.plot(months, expenses, marker='o', label="Expense")
    ax.set_title("Monthly Income vs Expense")
    ax.set_xlabel("Month")
    ax.set_ylabel(settings.DEFAULT_CURRENCY)
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Pie chart of last month's categories (simple)
    import collections
    last_month = summary[-1]["month"]
    # gather transactions for last_month
    cat_sums = collections.Counter()
    for t in transactions:
        if t.date.startswith(last_month):
            if t.ttype == "expense":
                cat_sums[t.category] += t.amount
    if cat_sums:
        fig2, ax2 = plt.subplots()
        labels = list(cat_sums.keys())
        sizes = list(cat_sums.values())
        ax2.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax2.set_title(f"Expenses by category ({last_month})")
        st.pyplot(fig2)
    else:
        st.info(f"No expenses recorded in {last_month} to show category breakdown.")
else:
    st.info("No monthly data yet. Add transactions to generate a summary.")
