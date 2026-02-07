import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import calendar


def initialize_demo_data():
    """Create realistic demo data for the past 6 months"""
    current_date = datetime.now()
    demo_data = {}

    # Generate data for past 6 months
    for i in range(6, 0, -1):
        month = current_date.month - i
        year = current_date.year

        # Handle year rollover
        if month <= 0:
            month += 12
            year -= 1

        month_key = f"{year}-{month:02d}"

        # Simulate realistic spending patterns with slight improvements over time
        base_income = 5000
        base_spending = 3500 - (i * 50)  # Spending improves over time
        variation = np.random.randint(-200, 200)

        total_spending = base_spending + variation

        demo_data[month_key] = {
            'income': base_income,
            'subscriptions': np.random.randint(400, 600),
            'expenses': total_spending - np.random.randint(400, 600),
            'total_spending': total_spending,
            'remaining': base_income - total_spending
        }

    return demo_data


def render():
    st.markdown("# Budget Tracker")
    st.caption("Monitor your monthly income and expenses")
    st.markdown("---")

    # Initialize session state
    if 'subscriptions' not in st.session_state:
        st.session_state.subscriptions = []
    if 'expenses' not in st.session_state:
        st.session_state.expenses = []
    if 'monthly_income' not in st.session_state:
        st.session_state.monthly_income = 5000.0
    if 'budget_limits' not in st.session_state:
        st.session_state.budget_limits = {
            'Food': 500,
            'Entertainment': 200,
            'Transport': 300,
            'Shopping': 250,
            'Bills': 400,
            'Healthcare': 200,
            'Software': 150,
            'Gym': 100,
            'Music': 50,
            'Cloud Storage': 50,
            'Other': 200
        }
    if 'monthly_history' not in st.session_state:
        # Initialize with demo data
        st.session_state.monthly_history = initialize_demo_data()
    if 'current_month_tracked' not in st.session_state:
        st.session_state.current_month_tracked = None

    # Get current month key
    current_month = datetime.now().strftime("%Y-%m")

    # Check if we've moved to a new month
    if st.session_state.current_month_tracked and st.session_state.current_month_tracked != current_month:
        # New month detected! Reset current month data
        st.session_state.subscriptions = []
        st.session_state.expenses = []
        st.info(f"🗓️ New month detected! Starting fresh tracking for {datetime.now().strftime('%B %Y')}")

    st.session_state.current_month_tracked = current_month

    monthly_income = st.session_state.monthly_income

    # Calculate totals for current month
    total_subs = sum(s['Cost'] for s in st.session_state.subscriptions)
    total_expenses = sum(e['Cost'] for e in st.session_state.expenses)
    total_spending = total_subs + total_expenses
    remaining = monthly_income - total_spending

    # Save current month data
    st.session_state.monthly_history[current_month] = {
        'income': monthly_income,
        'subscriptions': total_subs,
        'expenses': total_expenses,
        'total_spending': total_spending,
        'remaining': remaining
    }

    # Calculate spending by category
    category_spending = {}
    for sub in st.session_state.subscriptions:
        cat = sub['Category']
        category_spending[cat] = category_spending.get(cat, 0) + sub['Cost']
    for exp in st.session_state.expenses:
        cat = exp['Category']
        category_spending[cat] = category_spending.get(cat, 0) + exp['Cost']

    # Check for budget limit violations
    alerts = []
    for category, spent in category_spending.items():
        limit = st.session_state.budget_limits.get(category, 0)
        if limit > 0 and spent > limit:
            over_amount = spent - limit
            alerts.append({
                'category': category,
                'spent': spent,
                'limit': limit,
                'over': over_amount
            })

    # Show alerts
    if alerts:
        for alert in alerts:
            st.markdown(f"""
                <div style="
                    background: rgba(255, 68, 68, 0.1);
                    border-left: 4px solid #ff4444;
                    padding: 16px 20px;
                    border-radius: 8px;
                    margin-bottom: 12px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-weight: 600; font-size: 15px; color: #ffffff;">{alert['category']}</span>
                            <span style="color: #999999; margin-left: 12px; font-size: 14px;">
                                ${alert['spent']:.2f} spent · limit ${alert['limit']:.2f}
                            </span>
                        </div>
                        <span style="color: #ff4444; font-weight: 600; font-size: 14px;">
                            +${alert['over']:.2f}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("---")

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

    # Current month visualizations FIRST
    if st.session_state.subscriptions or st.session_state.expenses:
        st.markdown("### This Month")
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

    # Yearly Overview SECOND (below current month)
    if len(st.session_state.monthly_history) > 1:
        st.markdown("### Yearly Overview")

        # Prepare data for charts
        months = sorted(st.session_state.monthly_history.keys())
        monthly_data = []

        for month in months:
            data = st.session_state.monthly_history[month]
            month_name = datetime.strptime(month, "%Y-%m").strftime("%b %Y")
            monthly_data.append({
                'Month': month_name,
                'Income': data['income'],
                'Spending': data['total_spending'],
                'Savings': data['remaining']
            })

        history_df = pd.DataFrame(monthly_data)

        # Calculate trend (are they improving?)
        if len(history_df) >= 2:
            recent_savings = history_df['Savings'].tail(3).mean()
            older_savings = history_df['Savings'].head(3).mean()
            trend_improving = recent_savings > older_savings
            trend_pct = ((recent_savings - older_savings) / abs(older_savings) * 100) if older_savings != 0 else 0

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Monthly Spending Trend")

            fig = go.Figure()

            # Add spending line
            fig.add_trace(go.Scatter(
                x=history_df['Month'],
                y=history_df['Spending'],
                mode='lines+markers',
                name='Spending',
                line=dict(color='#ff4444', width=3),
                marker=dict(size=8)
            ))

            # Add income line
            fig.add_trace(go.Scatter(
                x=history_df['Month'],
                y=history_df['Income'],
                mode='lines+markers',
                name='Income',
                line=dict(color='#00ff00', width=3, dash='dash'),
                marker=dict(size=8)
            ))

            fig.update_layout(
                height=300,
                template='plotly_dark',
                xaxis_title="",
                yaxis_title="Amount ($)",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True, key="trend_chart")

        with col2:
            st.markdown("#### Savings Trend")

            fig = go.Figure()

            # Add savings bars
            colors = ['#00ff00' if s > 0 else '#ff4444' for s in history_df['Savings']]

            fig.add_trace(go.Bar(
                x=history_df['Month'],
                y=history_df['Savings'],
                marker_color=colors,
                name='Savings'
            ))

            # Add trend line
            if len(history_df) >= 2:
                z = np.polyfit(range(len(history_df)), history_df['Savings'], 1)
                p = np.poly1d(z)
                trend_line = p(range(len(history_df)))

                fig.add_trace(go.Scatter(
                    x=history_df['Month'],
                    y=trend_line,
                    mode='lines',
                    name='Trend',
                    line=dict(color='#ffffff', width=2, dash='dash')
                ))

            fig.update_layout(
                height=300,
                template='plotly_dark',
                xaxis_title="",
                yaxis_title="Savings ($)",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True, key="savings_chart")

        # Trend indicator
        if len(history_df) >= 2:
            if trend_improving:
                st.success(
                    f"📈 Your spending habits are improving! Savings up {abs(trend_pct):.1f}% compared to earlier months.")
            else:
                st.warning(
                    f"📉 Your spending has increased. Savings down {abs(trend_pct):.1f}% compared to earlier months.")

        st.markdown("---")

    # Budget Limits Section
    st.markdown("### Budget Limits")
    st.caption("Set spending limits for each category")

    with st.expander("Edit Limits", expanded=False):
        col1, col2, col3 = st.columns(3)

        categories = list(st.session_state.budget_limits.keys())

        for i, category in enumerate(categories):
            with [col1, col2, col3][i % 3]:
                current_limit = st.session_state.budget_limits[category]
                current_spent = category_spending.get(category, 0)

                new_limit = st.number_input(
                    f"{category}",
                    min_value=0.0,
                    value=float(current_limit),
                    step=10.0,
                    key=f"limit_{category}",
                    help=f"Spent: ${current_spent:.2f}"
                )

                if new_limit != current_limit:
                    st.session_state.budget_limits[category] = new_limit

        if st.button("Save Limits", type="primary", key="save_limits"):
            st.success("Saved")
            st.rerun()

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