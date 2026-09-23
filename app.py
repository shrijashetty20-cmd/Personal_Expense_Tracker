import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime
from database import (
    get_transactions,
    add_transaction,
    delete_transaction,
    get_budget,
    set_budget,
)

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #F7F8FA;
    }

    [data-testid="stSidebar"] {
        background: #111827;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    .main-title {
        font-size: 34px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 4px;
    }

    .sub-title {
        font-size: 15px;
        color: #6B7280;
        margin-bottom: 22px;
    }

    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.05);
        min-height: 125px;
    }

    .metric-label {
        font-size: 14px;
        font-weight: 600;
        color: #6B7280;
        margin-bottom: 10px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #111827;
    }

    .income-value {
        color: #15803D;
    }

    .expense-value {
        color: #DC2626;
    }

    .balance-value {
        color: #2563EB;
    }

    .section-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 9px;
    }

    h1, h2, h3 {
        color: #111827;
    }

    .success-box {
        padding: 12px 16px;
        border-radius: 10px;
        background: #ECFDF5;
        color: #166534;
        border: 1px solid #BBF7D0;
    }

    .danger-box {
        padding: 12px 16px;
        border-radius: 10px;
        background: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def money(value):
    return f"₹{float(value):,.0f}"


def load_transactions():
    rows = get_transactions()
    if not rows:
        return pd.DataFrame(
            columns=["id", "date", "category", "description", "type", "amount"]
        )

    df = pd.DataFrame(rows)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    return df


def totals(df):
    if df.empty:
        return 0.0, 0.0, 0.0

    income = float(df.loc[df["type"] == "income", "amount"].sum())
    expense = float(df.loc[df["type"] == "expense", "amount"].sum())
    balance = income - expense

    return income, expense, balance


def go_to(page):
    st.session_state.page = page
    st.session_state.editing_id = None


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<h2 style='color:white;margin-bottom:2px;'>💰 Expense Tracker</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#CBD5E1;'>Manage your personal finances</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    pages = {
        "Dashboard": "🏠 Dashboard",
        "Transactions": "💳 Transactions",
        "Add Transaction": "➕ Add Transaction",
        "Analytics": "📊 Analytics",
        "Budget": "🎯 Budget",
        "Settings": "⚙️ Settings",
    }

    for key, label in pages.items():
        if st.button(
            label,
            key=f"nav_{key}",
            use_container_width=True,
        ):
            go_to(key)
            st.rerun()

    st.divider()
    st.caption("Personal Expense Tracker")
    st.caption("Python + Streamlit + SQLite")


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------
df = load_transactions()
income, expenses, balance = totals(df)


# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------
if st.session_state.page == "Dashboard":
    st.markdown("<div class='main-title'>Dashboard</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-title'>Overview of your personal finances</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">TOTAL INCOME</div>
                <div class="metric-value income-value">{money(income)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">TOTAL EXPENSES</div>
                <div class="metric-value expense-value">{money(expenses)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">AVAILABLE BALANCE</div>
                <div class="metric-value balance-value">{money(balance)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    left, right = st.columns([1.35, 1])

    with left:
        st.markdown("### Recent Transactions")

        if df.empty:
            st.info("No transactions yet. Click **Add Transaction** to begin.")
        else:
            recent = df.head(8).copy()
            recent["Type"] = recent["type"].str.title()
            recent["Amount"] = recent["amount"].apply(money)

            recent = recent[
                ["date", "category", "description", "Type", "Amount"]
            ]
            recent.columns = [
                "Date",
                "Category",
                "Description",
                "Type",
                "Amount",
            ]

            st.dataframe(
                recent,
                use_container_width=True,
                hide_index=True,
            )

    with right:
        st.markdown("### Quick Actions")

        if st.button("➕ Add New Transaction", use_container_width=True):
            go_to("Add Transaction")
            st.rerun()

        if st.button("✏️ Edit Transactions", use_container_width=True):
            go_to("Transactions")
            st.rerun()

        if st.button("📊 View Analytics", use_container_width=True):
            go_to("Analytics")
            st.rerun()


# ------------------------------------------------------------
# ADD TRANSACTION
# ------------------------------------------------------------
elif st.session_state.page == "Add Transaction":
    st.markdown("<div class='main-title'>Add Transaction</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-title'>Record a new income or expense</div>",
        unsafe_allow_html=True,
    )

    with st.form("add_transaction_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            transaction_type = st.selectbox(
                "Transaction Type",
                ["expense", "income"],
                format_func=lambda x: x.title(),
            )

            categories = (
                ["Food", "Travel", "Shopping", "Education", "Bills", "Entertainment", "Other"]
                if transaction_type == "expense"
                else ["Salary", "Freelance", "Investment", "Other"]
            )

            category = st.selectbox("Category", categories)
            amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                step=100.0,
                format="%.2f",
            )

        with col2:
            transaction_date = st.date_input("Date", value=date.today())
            description = st.text_input(
                "Description",
                placeholder="e.g. Electricity Bill",
            )

        st.write("")
        save = st.form_submit_button(
            "💾 Save Transaction",
            use_container_width=True,
        )

    if save:
        clean_description = description.strip()

        if not clean_description:
            st.error("Please enter a description.")
        elif amount <= 0:
            st.error("Amount must be greater than zero.")
        else:
            add_transaction(
                transaction_date.strftime("%Y-%m-%d"),
                category,
                clean_description,
                transaction_type,
                float(amount),
            )
            st.success("Transaction added successfully!")
            st.session_state.page = "Transactions"
            st.rerun()

    st.write("")
    if st.button("← Back to Dashboard"):
        go_to("Dashboard")
        st.rerun()


# ------------------------------------------------------------
# TRANSACTIONS - VIEW / EDIT / DELETE
# ------------------------------------------------------------
elif st.session_state.page == "Transactions":
    st.markdown("<div class='main-title'>Transactions</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-title'>View, edit and delete your transactions</div>",
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("No transactions found. Add your first transaction.")
    else:
        f1, f2, f3 = st.columns(3)

        with f1:
            search = st.text_input(
                "🔎 Search",
                placeholder="Search description or category...",
            )

        with f2:
            category_options = ["All"] + sorted(df["category"].dropna().unique().tolist())
            category_filter = st.selectbox("Category", category_options)

        with f3:
            type_filter = st.selectbox(
                "Type",
                ["All", "Income", "Expense"],
            )

        filtered = df.copy()

        if search.strip():
            term = search.strip().lower()
            filtered = filtered[
                filtered["description"].str.lower().str.contains(term, na=False)
                | filtered["category"].str.lower().str.contains(term, na=False)
            ]

        if category_filter != "All":
            filtered = filtered[filtered["category"] == category_filter]

        if type_filter != "All":
            filtered = filtered[filtered["type"] == type_filter.lower()]

        st.write("")

        display = filtered.copy()
        display["Type"] = display["type"].str.title()
        display["Amount"] = display["amount"].apply(money)
        display = display[
            ["id", "date", "category", "description", "Type", "Amount"]
        ]
        display.columns = [
            "ID",
            "Date",
            "Category",
            "Description",
            "Type",
            "Amount",
        ]

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
        )

        st.write("")
        st.markdown("### Edit or Delete a Transaction")

        transaction_ids = filtered["id"].tolist()

        if transaction_ids:
            selected_id = st.selectbox(
                "Select Transaction ID",
                transaction_ids,
                key="selected_transaction_id",
            )

            selected = df[df["id"] == selected_id].iloc[0]

            a, b = st.columns(2)

            with a:
                if st.button("✏️ Edit Selected Transaction", use_container_width=True):
                    st.session_state.editing_id = int(selected_id)
                    st.rerun()

            with b:
                if st.button("🗑️ Delete Selected Transaction", use_container_width=True):
                    delete_transaction(int(selected_id))
                    st.success("Transaction deleted successfully!")
                    st.session_state.editing_id = None
                    st.rerun()

            if st.session_state.editing_id == int(selected_id):
                st.write("")
                st.markdown("#### Edit Transaction")

                current_type = str(selected["type"])
                current_categories = (
                    ["Food", "Travel", "Shopping", "Education", "Bills", "Entertainment", "Other"]
                    if current_type == "expense"
                    else ["Salary", "Freelance", "Investment", "Other"]
                )

                with st.form("edit_transaction_form"):
                    e1, e2 = st.columns(2)

                    with e1:
                        edit_type = st.selectbox(
                            "Transaction Type",
                            ["expense", "income"],
                            index=0 if current_type == "expense" else 1,
                            format_func=lambda x: x.title(),
                        )

                        edit_categories = (
                            ["Food", "Travel", "Shopping", "Education", "Bills", "Entertainment", "Other"]
                            if edit_type == "expense"
                            else ["Salary", "Freelance", "Investment", "Other"]
                        )

                        current_category = str(selected["category"])
                        category_index = (
                            edit_categories.index(current_category)
                            if current_category in edit_categories
                            else 0
                        )

                        edit_category = st.selectbox(
                            "Category",
                            edit_categories,
                            index=category_index,
                        )

                        edit_amount = st.number_input(
                            "Amount (₹)",
                            min_value=0.01,
                            value=float(selected["amount"]),
                            step=100.0,
                            format="%.2f",
                        )

                    with e2:
                        try:
                            current_date = datetime.strptime(
                                str(selected["date"]), "%Y-%m-%d"
                            ).date()
                        except ValueError:
                            current_date = date.today()

                        edit_date = st.date_input(
                            "Date",
                            value=current_date,
                        )

                        edit_description = st.text_input(
                            "Description",
                            value=str(selected["description"]),
                        )

                    save_edit = st.form_submit_button(
                        "💾 Save Changes",
                        use_container_width=True,
                    )

                if save_edit:
                    clean_description = edit_description.strip()

                    if not clean_description:
                        st.error("Description cannot be empty.")
                    elif edit_amount <= 0:
                        st.error("Amount must be greater than zero.")
                    else:
                        # SQLite update is done directly here because the existing
                        # database.py has add/delete but no update function.
                        import sqlite3
                        from pathlib import Path

                        database_path = (
                            Path(__file__).resolve().parent / "expense_tracker.db"
                        )

                        connection = sqlite3.connect(database_path)
                        cursor = connection.cursor()

                        cursor.execute(
                            """
                            UPDATE transactions
                            SET date = ?, category = ?, description = ?,
                                type = ?, amount = ?
                            WHERE id = ?
                            """,
                            (
                                edit_date.strftime("%Y-%m-%d"),
                                edit_category,
                                clean_description,
                                edit_type,
                                float(edit_amount),
                                int(selected_id),
                            ),
                        )

                        connection.commit()
                        connection.close()

                        st.session_state.editing_id = None
                        st.success("Transaction updated successfully!")
                        st.rerun()


# ------------------------------------------------------------
# ANALYTICS
# ------------------------------------------------------------
elif st.session_state.page == "Analytics":
    st.markdown("<div class='main-title'>Analytics</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-title'>Understand where your money is going</div>",
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("Add some transactions to see analytics.")
    else:
        expenses_df = df[df["type"] == "expense"].copy()

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Expense by Category")

            if expenses_df.empty:
                st.info("No expense transactions yet.")
            else:
                category_totals = (
                    expenses_df.groupby("category")["amount"]
                    .sum()
                    .sort_values(ascending=False)
                )

                fig, ax = plt.subplots(figsize=(6, 4))
                ax.pie(
                    category_totals.values,
                    labels=category_totals.index,
                    autopct="%1.0f%%",
                    startangle=90,
                )
                ax.set_title("Expense Distribution")
                st.pyplot(fig)
                plt.close(fig)

        with c2:
            st.markdown("### Income vs Expense")

            chart_df = df.copy()
            chart_df["date"] = pd.to_datetime(chart_df["date"], errors="coerce")
            chart_df["Month"] = chart_df["date"].dt.to_period("M").astype(str)

            monthly = (
                chart_df.groupby(["Month", "type"])["amount"]
                .sum()
                .unstack(fill_value=0)
            )

            if "income" not in monthly.columns:
                monthly["income"] = 0
            if "expense" not in monthly.columns:
                monthly["expense"] = 0

            monthly = monthly[["income", "expense"]]

            fig, ax = plt.subplots(figsize=(6, 4))
            monthly.plot(kind="bar", ax=ax)
            ax.set_title("Monthly Income vs Expense")
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount (₹)")
            ax.tick_params(axis="x", rotation=0)
            st.pyplot(fig)
            plt.close(fig)

        st.write("")
        st.markdown("### Spending Summary")

        s1, s2, s3 = st.columns(3)
        s1.metric("Total Income", money(income))
        s2.metric("Total Expenses", money(expenses))
        s3.metric("Available Balance", money(balance))


# ------------------------------------------------------------
# BUDGET
# ------------------------------------------------------------
elif st.session_state.page == "Budget":
    st.markdown("<div class='main-title'>Budget</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-title'>Set and monitor your monthly spending limit</div>",
        unsafe_allow_html=True,
    )

    budget = float(get_budget())
    remaining = budget - expenses

    b1, b2, b3 = st.columns(3)

    with b1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">MONTHLY BUDGET</div>
                <div class="metric-value">{money(budget)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with b2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">TOTAL SPENT</div>
                <div class="metric-value expense-value">{money(expenses)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with b3:
        remaining_class = "balance-value" if remaining >= 0 else "expense-value"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">REMAINING</div>
                <div class="metric-value {remaining_class}">{money(remaining)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    with st.form("budget_form"):
        new_budget = st.number_input(
            "Set Monthly Budget (₹)",
            min_value=1.0,
            value=budget,
            step=1000.0,
            format="%.2f",
        )

        update_budget = st.form_submit_button(
            "💾 Update Budget",
            use_container_width=True,
        )

    if update_budget:
        set_budget(float(new_budget))
        st.success("Budget updated successfully!")
        st.rerun()

    if budget > 0:
        progress = min(max(expenses / budget, 0.0), 1.0)
        st.write("")
        st.markdown("### Budget Progress")
        st.progress(progress)
        st.write(f"{money(expenses)} spent out of {money(budget)}")

    if not df.empty:
        expense_df = df[df["type"] == "expense"]

        if not expense_df.empty:
            st.write("")
            st.markdown("### Category-wise Spending")

            category_spend = (
                expense_df.groupby("category")["amount"]
                .sum()
                .sort_values(ascending=False)
            )

            st.bar_chart(category_spend)


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------
elif st.session_state.page == "Settings":
    st.markdown("<div class='main-title'>Settings</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-title'>Application information and preferences</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-card">
            <h3>Personal Expense Tracker</h3>
            <p style="color:#6B7280;">
                A Python-based personal finance management application.
            </p>
            <p><b>Technology:</b> Python, Streamlit, SQLite, Pandas, Matplotlib</p>
            <p><b>Features:</b> Add, edit, delete, search, analytics and budget tracking</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown("### Data Management")

    export_df = load_transactions()

    if export_df.empty:
        st.info("There are no transactions to export yet.")
    else:
        csv_data = export_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Export Transactions as CSV",
            data=csv_data,
            file_name="expense_tracker_transactions.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.write("")
    st.caption("Your transactions are stored locally in the SQLite database.")


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.divider()
st.caption("Personal Expense Tracker • Built with Python, Streamlit and SQLite")
