import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


def render():
    st.markdown("# Budget Tracker")
    st.caption("Monitor your monthly income and expenses")
    st.markdown("---")

    # Initialize session state - NO plaid_holdings here
    if 'subscriptions' not in st.session_state:
        st.session_state.subscriptions = []
    if 'expenses' not in st.session_state:
        st.session_state.expenses = []
    if 'monthly_income' not in st.session_state:
        st.session_state.monthly_income = 5000.0

    monthly_income = st.session_state.monthly_income

    # Calculate totals
    total_subs = sum(s['Cost'] for s in st.session_state.subscriptions)
    total_expenses = sum(e['Cost'] for e in st.session_state.expenses)
    total_spending = total_subs + total_expenses
    remaining = monthly_income - total_spending

    # Budget Summary
    st.markdown("### Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Income", f"${monthly_income:,.2f}")
    with col2:
        st.metric("Recurring", f"${total_subs:,.2f}")
    with col3:
        st.metric("One-time", f"${total_expenses:,.2f}")
    with col4:
        delta_color = "normal" if remaining >= 0 else "inverse"
        st.metric("Balance", f"${remaining:,.2f}",
                  delta=f"{(remaining / monthly_income * 100):.1f}%" if monthly_income > 0 else "0%",
                  delta_color=delta_color)

    st.markdown("")

    # Visualizations
    if st.session_state.subscriptions or st.session_state.expenses:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Spending by Category")

            all_items = []
            for sub in st.session_state.subscriptions:
                all_items.append({'Category': sub['Category'], 'Amount': sub['Cost']})
            for exp in st.session_state.expenses:
                all_items.append({'Category': exp['Category'], 'Amount': exp['Cost']})

            if all_items:
                spending_df = pd.DataFrame(all_items)
                category_totals = spending_df.groupby('Category')['Amount'].sum().reset_index()
                fig = px.pie(category_totals, values='Amount', names='Category', hole=0.4)
                fig.update_layout(height=300, showlegend=True, template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True, key="budget_pie_chart")

        with col2:
            st.markdown("#### Spending Breakdown")

            all_items = []
            for sub in st.session_state.subscriptions:
                all_items.append({'Category': sub['Category'], 'Amount': sub['Cost']})
            for exp in st.session_state.expenses:
                all_items.append({'Category': exp['Category'], 'Amount': exp['Cost']})

            if all_items:
                spending_df = pd.DataFrame(all_items)
                category_totals = spending_df.groupby('Category')['Amount'].sum().reset_index()
                category_totals = category_totals.sort_values('Amount', ascending=False)

                fig = px.bar(
                    category_totals,
                    x='Category',
                    y='Amount',
                    color='Amount',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(
                    height=300,
                    showlegend=False,
                    template='plotly_dark',
                    xaxis_title="",
                    yaxis_title="Amount ($)"
                )
                st.plotly_chart(fig, use_container_width=True, key="budget_bar_chart")

    st.markdown("---")

    # Monthly Income
    st.markdown("### Income")
    new_income = st.number_input("Monthly income", min_value=0.0, value=monthly_income, step=100.0,
                                 key="budget_income_input")
    if new_income != monthly_income:
        st.session_state.monthly_income = new_income
        st.rerun()

    st.markdown("---")

    # Two columns
    col1, col2 = st.columns(2)

    # Subscriptions
    with col1:
        st.markdown("### Recurring Payments")
        st.caption("Monthly subscriptions and regular bills")

        with st.expander("Add new", expanded=False):
            sub_name = st.text_input("Description", placeholder="Netflix, Spotify, etc.", key="budget_sub_name")
            sub_cost = st.number_input("Amount", min_value=0.0, step=0.01, key="budget_sub_cost")
            sub_category = st.selectbox("Category",
                                        ["Entertainment", "Software", "Gym", "Music", "Cloud Storage", "Other"],
                                        key="budget_sub_category")

            if st.button("Add", type="primary", key="budget_add_sub"):
                if sub_name and sub_cost > 0:
                    st.session_state.subscriptions.append({
                        'Name': sub_name,
                        'Cost': sub_cost,
                        'Category': sub_category,
                        'Date Added': datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success(f"Added {sub_name}")
                    st.rerun()

        if st.session_state.subscriptions:
            subs_df = pd.DataFrame(st.session_state.subscriptions)
            total_subs_display = subs_df['Cost'].sum()
            st.metric("Total", f"${total_subs_display:,.2f}")
            st.markdown("")
            st.dataframe(subs_df[['Name', 'Cost', 'Category']], use_container_width=True, hide_index=True)

            if len(st.session_state.subscriptions) > 0:
                st.markdown("")
                sub_to_delete = st.selectbox(
                    "Remove:",
                    options=range(len(st.session_state.subscriptions)),
                    format_func=lambda x: st.session_state.subscriptions[x]['Name'],
                    key="budget_sub_delete_select"
                )
                if st.button("Delete", key="budget_delete_sub"):
                    deleted = st.session_state.subscriptions.pop(sub_to_delete)
                    st.success(f"Removed {deleted['Name']}")
                    st.rerun()
        else:
            st.info("No recurring payments tracked yet")

    # Expenses
    with col2:
        st.markdown("### Other Expenses")
        st.caption("One-time purchases and variable costs")

        with st.expander("Add new", expanded=False):
            exp_name = st.text_input("Description", placeholder="Groceries, gas, etc.", key="budget_exp_name")
            exp_cost = st.number_input("Amount", min_value=0.0, step=0.01, key="budget_exp_cost")
            exp_category = st.selectbox("Category",
                                        ["Food", "Transport", "Shopping", "Bills", "Healthcare", "Other"],
                                        key="budget_exp_category")

            if st.button("Add", type="primary", key="budget_add_exp"):
                if exp_name and exp_cost > 0:
                    st.session_state.expenses.append({
                        'Name': exp_name,
                        'Cost': exp_cost,
                        'Category': exp_category,
                        'Date': datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success(f"Added {exp_name}")
                    st.rerun()

        if st.session_state.expenses:
            exp_df = pd.DataFrame(st.session_state.expenses)
            total_expenses_display = exp_df['Cost'].sum()
            st.metric("Total", f"${total_expenses_display:,.2f}")
            st.markdown("")
            st.dataframe(exp_df[['Name', 'Cost', 'Category']], use_container_width=True, hide_index=True)

            if len(st.session_state.expenses) > 0:
                st.markdown("")
                exp_to_delete = st.selectbox(
                    "Remove:",
                    options=range(len(st.session_state.expenses)),
                    format_func=lambda x: st.session_state.expenses[x]['Name'],
                    key="budget_exp_delete_select"
                )
                if st.button("Delete", key="budget_delete_exp"):
                    deleted = st.session_state.expenses.pop(exp_to_delete)
                    st.success(f"Removed {deleted['Name']}")
                    st.rerun()
        else:
            st.info("No expenses tracked yet")

    # Clear all button
    st.markdown("")
    if st.session_state.subscriptions or st.session_state.expenses:
        if st.button("Clear All Data", key="budget_clear_all"):
            st.session_state.subscriptions = []
            st.session_state.expenses = []
            st.rerun()