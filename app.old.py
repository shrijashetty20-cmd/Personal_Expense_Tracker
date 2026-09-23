import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

from database import (
    add_transaction,
    delete_transaction,
    get_budget,
    get_transactions,
    set_budget,
)

# -----------------------------
# PAGE SETUP
# -----------------------------

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# -----------------------------
# CUSTOM STYLE
# -----------------------------

st.markdown("""
<style>

.stApp {
    background-color: #f7f8fa;
}

.main-title {
    font-size: 32px;
    font-weight: 700;
    color: #111827;
}

.subtitle {
    color: #6b7280;
    font-size: 15px;
    margin-bottom: 25px;
}

div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #e5e7eb;
    padding: 20px;
    border-radius: 14px;
}

.section-title {
    font-size: 22px;
    font-weight: 650;
    margin-top: 20px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# CONSTANTS
# -----------------------------

EXPENSE_CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Education",
    "Bills",
    "Entertainment",
    "Other"
]

INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Investment",
    "Other"
]


# -----------------------------
# FUNCTIONS
# -----------------------------

def format_inr(amount):
    return f"₹{float(amount):,.2f}"


def get_data():
    return get_transactions()


# -----------------------------
# SIDEBAR
# -----------------------------

if "show_add_transaction" not in st.session_state:
    st.session_state.show_add_transaction = False

with st.sidebar:

    st.markdown("## 💰 Expense Tracker")
    st.caption("Personal Expense Management")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Transactions",
            "Analytics",
            "Budget",
            "Settings"
        ]
    )

    st.divider()

    st.markdown("### Quick Actions")

if st.button(
    "➕ Add Transaction",
    width="stretch"
):
    st.session_state.show_add_transaction = True

# -----------------------------
# ADD TRANSACTION
# -----------------------------

if st.session_state.show_add_transaction:

    st.subheader("Add Transaction")

    with st.form("transaction_form"):

        col1, col2 = st.columns(2)

        with col1:

            transaction_type = st.selectbox(
                "Type",
                ["expense", "income"]
            )
     
        if transaction_type == "expense":
            categories = EXPENSE_CATEGORIES
        else:
             categories = INCOME_CATEGORIES

        category = st.selectbox(
            "Category",
             options=categories,
             key=f"category_{transaction_type}"
)

        amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                value=100.0,
                step=50.0
            )

        with col2:

            transaction_date = st.date_input(
                "Date",
                value=date.today()
            )

            description = st.text_input(
                "Description"
            )

        submitted = st.form_submit_button(
            "Save Transaction"
        )

        if submitted:

            if description.strip() == "":
                st.error("Please enter a description.")

            else:

                add_transaction(
                    transaction_date.strftime("%Y-%m-%d"),
                    category,
                    description.strip(),
                    transaction_type,
                    float(amount)
                )

                st.success(
                    "Transaction added successfully!"
                )

                st.session_state.show_add_transaction = False

                st.rerun()

    if st.button("Cancel"):
        st.session_state.show_add_transaction = False
        st.rerun()

# -----------------------------
# LOAD DATA
# -----------------------------

transactions = get_data()

income = sum(
    float(t["amount"])
    for t in transactions
    if t["type"] == "income"
)

expenses = sum(
    float(t["amount"])
    for t in transactions
    if t["type"] == "expense"
)

balance = income - expenses

budget = get_budget()

remaining = budget - expenses


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.markdown(
        '<div class="main-title">Personal Expense Tracker</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Track your income, expenses and budget in one place.'
        '</div>',
        unsafe_allow_html=True
    )

    # KPI CARDS

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Balance",
        format_inr(balance)
    )

    col2.metric(
        "Total Income",
        format_inr(income)
    )

    col3.metric(
        "Total Expenses",
        format_inr(expenses)
    )

    st.markdown(
        '<div class="section-title">Recent Transactions</div>',
        unsafe_allow_html=True
    )

    if transactions:

        df = pd.DataFrame(transactions)

        df = df[
            [
                "date",
                "category",
                "description",
                "type",
                "amount"
            ]
        ]

        df.columns = [
            "Date",
            "Category",
            "Description",
            "Type",
            "Amount"
        ]

        df["Type"] = df["Type"].str.title()

        df["Amount"] = df["Amount"].apply(format_inr)

        st.dataframe(
            df.head(8),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No transactions have been added yet."
        )


# =========================================================
# TRANSACTIONS
# =========================================================

elif page == "Transactions":

    st.markdown(
        '<div class="main-title">Transactions</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'View and manage all your transactions.'
        '</div>',
        unsafe_allow_html=True
    )

    if transactions:

        df = pd.DataFrame(transactions)

        # FILTERS

        col1, col2, col3 = st.columns(3)

        with col1:

            search = st.text_input(
                "Search",
                placeholder="Search description..."
            )

        with col2:

            categories = [
                "All"
            ] + sorted(
                df["category"].unique().tolist()
            )

            selected_category = st.selectbox(
                "Category",
                categories
            )

        with col3:

            selected_type = st.selectbox(
                "Type",
                [
                    "All",
                    "Income",
                    "Expense"
                ]
            )

        filtered = df.copy()

        # SEARCH

        if search:

            filtered = filtered[
                filtered["description"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        # CATEGORY FILTER

        if selected_category != "All":

            filtered = filtered[
                filtered["category"]
                == selected_category
            ]

        # TYPE FILTER

        if selected_type != "All":

            filtered = filtered[
                filtered["type"]
                == selected_type.lower()
            ]

        display_df = filtered[
            [
                "date",
                "category",
                "description",
                "type",
                "amount"
            ]
        ].copy()

        display_df.columns = [
            "Date",
            "Category",
            "Description",
            "Type",
            "Amount"
        ]

        display_df["Type"] = display_df["Type"].str.title()

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # DELETE

        st.markdown("### Delete Transaction")

        transaction_options = {}

        for t in transactions:

            label = (
                f'#{t["id"]} | '
                f'{t["date"]} | '
                f'{t["description"]} | '
                f'{format_inr(t["amount"])}'
            )

            transaction_options[label] = t["id"]

        selected_transaction = st.selectbox(
            "Select transaction",
            list(transaction_options.keys())
        )

        if st.button("🗑️ Delete Transaction"):

            transaction_id = transaction_options[
                selected_transaction
            ]

            delete_transaction(transaction_id)

            st.success(
                "Transaction deleted successfully."
            )

            st.rerun()

    else:

        st.info("No transactions found.")


# =========================================================
# ANALYTICS
# =========================================================

elif page == "Analytics":

    st.markdown(
        '<div class="main-title">Analytics</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Understand your spending patterns.'
        '</div>',
        unsafe_allow_html=True
    )

    if transactions:

        df = pd.DataFrame(transactions)

        expenses_df = df[
            df["type"] == "expense"
        ]

        col1, col2 = st.columns(2)

        # EXPENSE BREAKDOWN

        with col1:

            st.subheader(
                "Expense Breakdown"
            )

            if not expenses_df.empty:

                category_totals = (
                    expenses_df
                    .groupby("category")["amount"]
                    .sum()
                )

                fig, ax = plt.subplots()

                ax.pie(
                    category_totals.values,
                    labels=category_totals.index,
                    autopct="%1.0f%%",
                    startangle=90
                )

                ax.set_title(
                    "Expenses by Category"
                )

                st.pyplot(fig)

                plt.close(fig)

            else:

                st.info(
                    "No expense data available."
                )

        # INCOME VS EXPENSE

        with col2:

            st.subheader(
                "Income vs Expense"
            )

            df["month"] = pd.to_datetime(
                df["date"]
            ).dt.strftime("%b %Y")

            monthly = (
                df.groupby(
                    ["month", "type"]
                )["amount"]
                .sum()
                .unstack(fill_value=0)
            )

            fig, ax = plt.subplots()

            monthly.plot(
                kind="bar",
                ax=ax
            )

            ax.set_ylabel(
                "Amount (₹)"
            )

            ax.set_xlabel(
                "Month"
            )

            ax.set_title(
                "Monthly Income vs Expense"
            )

            plt.xticks(
                rotation=45
            )

            plt.tight_layout()

            st.pyplot(fig)

            plt.close(fig)

    else:

        st.info(
            "Add transactions to view analytics."
        )


# =========================================================
# BUDGET
# =========================================================

elif page == "Budget":

    st.markdown(
        '<div class="main-title">Budget</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Manage your monthly spending limit.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Monthly Budget",
        format_inr(budget)
    )

    col2.metric(
        "Spent",
        format_inr(expenses)
    )

    col3.metric(
        "Remaining",
        format_inr(remaining)
    )

    st.markdown("### Update Budget")

    with st.form("budget_form"):

        new_budget = st.number_input(
            "Monthly Budget (₹)",
            min_value=0.01,
            value=float(budget),
            step=500.0
        )

        save_budget = st.form_submit_button(
            "Save Budget"
        )

        if save_budget:

            set_budget(
                float(new_budget)
            )

            st.success(
                "Budget updated successfully!"
            )

            st.rerun()

    st.markdown(
        "### Category-wise Spending"
    )

    if transactions:

        expense_df = pd.DataFrame(
            [
                t
                for t in transactions
                if t["type"] == "expense"
            ]
        )

        if not expense_df.empty:

            category_spending = (
                expense_df
                .groupby("category")["amount"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            st.bar_chart(
                category_spending
            )

        else:

            st.info(
                "No expenses recorded."
            )

    else:

        st.info(
            "No transactions recorded."
        )


# =========================================================
# SETTINGS
# =========================================================

elif page == "Settings":

    st.markdown(
        '<div class="main-title">Settings</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Manage your profile.'
        '</div>',
        unsafe_allow_html=True
    )

    name = st.text_input(
        "Name",
        value="User"
    )

    email = st.text_input(
        "Email"
    )

    if st.button(
        "Save Profile"
    ):

        st.success(
            "Profile updated successfully!"
        )

    st.markdown("### About")

    st.info(
        "Personal Expense Tracker is a Python-based "
        "application for managing income, expenses, "
        "budgets and financial analytics."
    )