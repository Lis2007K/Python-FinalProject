import streamlit as st

from auth import register_user, login_user, current_user_safe
from finance import (
    get_categories,
    add_transaction_validated,
    get_transactions_filtered,
    export_transactions_csv,
    get_monthly_summary
)
from visualization.charts import (
    plot_monthly_summary,
    pie_expense_by_category
)


st.set_page_config(page_title="Personal Finance Tracker", layout="wide")

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
    fig_summary = plot_monthly_summary(summary)
    st.pyplot(fig_summary)
    fig_pie = pie_expense_by_category(transactions)
    st.pyplot(fig_pie)
