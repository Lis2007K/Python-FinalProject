import streamlit as st
from datetime import datetime, timedelta

from auth import register_user, login_user, current_user_safe
from finance import (
    get_categories,
    add_transaction_validated,
    get_transactions_filtered,
    export_transactions_csv,
    get_monthly_summary,
    calculate_balance
)
from visualization.charts import (
    plot_monthly_summary,
    pie_expense_by_category,
    plot_income_vs_expense_bars,
    plot_category_income_expense,
    plot_cumulative_balance
)


st.set_page_config(page_title="Personal Finance Tracker", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; }
    .stat-value { font-size: 28px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Personal Finance Tracker")


if "user" not in st.session_state:
    st.session_state.user = None


if st.session_state.user is None:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            success, user = login_user(username, password)
            if success and user:
                st.session_state.user = current_user_safe(user)
                st.success(f"Logged in as {user.username}")
                st.rerun()
            else:
                st.error("Login failed. Check credentials.")

    with tab2:
        st.subheader("Register")
        new_username = st.text_input("New username")
        new_password = st.text_input("New password", type="password")

        if st.button("Register"):
            success, message = register_user(new_username, new_password)
            if success:
                st.success(message)
            else:
                st.error(message)

    st.stop()


st.sidebar.success(f"Logged in as {st.session_state.user['username']}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()


# ========== DASHBOARD SECTION ==========
st.header("📈 Dashboard")

transactions = get_transactions_filtered(st.session_state.user["id"]) if st.session_state.user else []
balance = calculate_balance(st.session_state.user["id"]) if st.session_state.user else 0

# Calculate metrics
total_income = sum(t.amount for t in transactions if t.ttype == "income")
total_expense = sum(t.amount for t in transactions if t.ttype == "expense")
net_balance = total_income - total_expense

# Display metrics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💵 Total Income", f"${total_income:,.2f}", delta=None)

with col2:
    st.metric("💸 Total Expenses", f"${total_expense:,.2f}", delta=None)

with col3:
    st.metric("📊 Net Balance", f"${net_balance:,.2f}", 
              delta=f"{'Positive' if net_balance >= 0 else 'Negative'}")

with col4:
    st.metric("📌 Current Balance", f"${balance:,.2f}", delta=None)


st.header("➕ Add Transaction")

with st.form("transaction_form"):
    amount = st.number_input("Amount", min_value=0.01, step=0.01)
    ttype = st.selectbox("Type", ["income", "expense"])
    category = st.selectbox("Category", get_categories(ttype))
    date = st.date_input("Date")
    description = st.text_input("Description")

    submitted = st.form_submit_button("Add")

    if submitted:
        success, message = add_transaction_validated(
            user_id=st.session_state.user["id"],
            date_iso=str(date),
            amount=amount,
            category=category,
            ttype=ttype,
            description=description
        )

        if success:
            st.success(message)
        else:
            st.error(message)


st.header("📄 Transactions")

transactions = get_transactions_filtered(st.session_state.user["id"]) if st.session_state.user else []

if transactions:
    st.dataframe([
        {
            "Date": t.date,
            "Type": t.ttype,
            "Category": t.category,
            "Amount": t.amount,
            "Description": t.description
        }
        for t in transactions
    ])

    if st.button("Export to CSV"):
        ok, path_or_err = export_transactions_csv(st.session_state.user["id"], txs=transactions)
        if ok:
            st.success(f"Exported to {path_or_err}")
        else:
            st.error(path_or_err)
else:
    st.info("No transactions yet")


st.header("📊 Analytics")

if transactions:
    summary = get_monthly_summary(st.session_state.user["id"])
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Trend",
        "📊 Comparison",
        "🍰 Distribution",
        "💰 Categories",
        "📉 Cumulative"
    ])
    
    with tab1:
        st.subheader("Monthly Trend Analysis")
        fig_summary = plot_monthly_summary(summary)
        st.pyplot(fig_summary)
    
    with tab2:
        st.subheader("Income vs Expense Comparison")
        fig_bars = plot_income_vs_expense_bars(summary)
        st.pyplot(fig_bars)
    
    with tab3:
        st.subheader("Expense Distribution by Category")
        fig_pie = pie_expense_by_category(transactions)
        st.pyplot(fig_pie)
    
    with tab4:
        st.subheader("All Transactions Distribution")
        fig_donut = plot_category_income_expense(transactions)
        st.pyplot(fig_donut)
    
    with tab5:
        st.subheader("Cumulative Balance Progression")
        fig_cumulative = plot_cumulative_balance(transactions)
        st.pyplot(fig_cumulative)
else:
    st.info("📊 Add transactions to see analytics")

