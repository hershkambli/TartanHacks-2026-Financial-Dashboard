import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import calendar


def initialize_demo_data():
    """Create realistic demo data for the past 6 months with varying income"""
    current_date = datetime.now()
    demo_data = {}

    for i in range(6, 0, -1):
        month = current_date.month - i
        year = current_date.year

        if month <= 0:
            month += 12
            year -= 1

        month_key = f"{year}-{month:02d}"

        base_income = 5000
        income_variation = np.random.randint(-500, 1000)
        monthly_income = base_income + income_variation

        base_spending = 3500 - (i * 50)
        variation = np.random.randint(-200, 200)
        total_spending = base_spending + variation

        demo_data[month_key] = {
            'income': monthly_income,
            'subscriptions': np.random.randint(400, 600),
            'expenses': total_spending - np.random.randint(400, 600),
            'rent': 1200,
            'total_spending': total_spending,
            'remaining': monthly_income - total_spending
        }

    return demo_data


def generate_demo_transactions():
    """Generate realistic demo bank transactions"""
    transactions = []
    categories_map = {
        'Food': ['Whole Foods', 'Chipotle', 'Starbucks', 'Subway', 'Pizza Hut'],
        'Transport': ['Uber', 'Lyft', 'Shell Gas', 'Parking Meter'],
        'Shopping': ['Amazon', 'Target', 'Walmart', 'Best Buy'],
        'Entertainment': ['Netflix', 'Spotify', 'AMC Theaters', 'Steam'],
        'Bills': ['Electric Bill', 'Internet Bill', 'Water Bill'],
        'Healthcare': ['CVS Pharmacy', 'Doctor Visit'],
        'Other': ['Misc Purchase', 'Cash Withdrawal', 'ATM Fee']
    }

    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")

        for _ in range(np.random.randint(0, 3)):
            category = np.random.choice(list(categories_map.keys()))
            merchant = np.random.choice(categories_map[category])
            amount = round(np.random.uniform(5, 80), 2)

            transactions.append({
                'date': date,
                'merchant': merchant,
                'amount': amount,
                'category': category
            })

    return transactions


def generate_insights(subscriptions, expenses, category_spending, budget_limits, alerts):
    """Generate personalized spending insights"""
    insights = []

    merchant_spending = {}
    for sub in subscriptions:
        merchant_spending[sub['Name']] = merchant_spending.get(sub['Name'], 0) + sub['Cost']
    for exp in expenses:
        name = exp['Name'].split(' (')[0]
        merchant_spending[name] = merchant_spending.get(name, 0) + exp['Cost']

    if merchant_spending:
        top_merchants = sorted(merchant_spending.items(), key=lambda x: x[1], reverse=True)[:3]
        insights.append({
            'title': 'Top Spending',
            'details': [f"{merchant}: ${amount:.2f}" for merchant, amount in top_merchants],
            'type': 'info'
        })

    for alert in alerts:
        category = alert['category']
        over = alert['over']

        category_merchants = {}
        for sub in subscriptions:
            if sub['Category'] == category:
                category_merchants[sub['Name']] = category_merchants.get(sub['Name'], 0) + sub['Cost']
        for exp in expenses:
            if exp['Category'] == category:
                name = exp['Name'].split(' (')[0]
                category_merchants[name] = category_merchants.get(name, 0) + exp['Cost']

        if category_merchants:
            top_culprit = max(category_merchants.items(), key=lambda x: x[1])
            insights.append({
                'title': f'{category} Over Budget',
                'details': [
                    f"${over:.2f} over limit",
                    f"Biggest contributor: {top_culprit[0]} (${top_culprit[1]:.2f})",
                    f"Recommendation: Reduce {top_culprit[0]} spending by ${over:.2f}"
                ],
                'type': 'warning'
            })

    if subscriptions:
        total_subs = sum(s['Cost'] for s in subscriptions)
        insights.append({
            'title': 'Subscription Analysis',
            'details': [
                f"{len(subscriptions)} active subscriptions",
                f"${total_subs:.2f}/month total",
                f"${total_subs * 12:.2f}/year if kept"
            ],
            'type': 'info'
        })

    for category, amount in category_spending.items():
        limit = budget_limits.get(category, 0)
        if limit > 0:
            usage_pct = (amount / limit) * 100
            if 80 <= usage_pct < 100:
                insights.append({
                    'title': f'{category} Alert',
                    'details': [
                        f"${amount:.2f} spent (${limit:.2f} limit)",
                        f"{usage_pct:.0f}% of budget used",
                        "Consider slowing spending in this category"
                    ],
                    'type': 'info'
                })

    return insights


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
        st.session_state.monthly_income = 0.0
    if 'monthly_rent' not in st.session_state:
        st.session_state.monthly_rent = 0.0
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
        st.session_state.monthly_history = {}
    if 'current_month_tracked' not in st.session_state:
        st.session_state.current_month_tracked = None
    if 'bank_connected' not in st.session_state:
        st.session_state.bank_connected = False
    if 'bank_transactions' not in st.session_state:
        st.session_state.bank_transactions = []
    if 'show_insights' not in st.session_state:
        st.session_state.show_insights = False
    if 'demo_loaded' not in st.session_state:
        st.session_state.demo_loaded = False

    # Get current month key
    current_month = datetime.now().strftime("%Y-%m")
    current_year = datetime.now().year

    if st.session_state.current_month_tracked and st.session_state.current_month_tracked != current_month:
        st.session_state.subscriptions = []
        st.session_state.expenses = []
        st.session_state.bank_connected = False
        st.session_state.bank_transactions = []
        st.info(f"New month detected! Starting fresh tracking for {datetime.now().strftime('%B %Y')}")

    st.session_state.current_month_tracked = current_month

    # Calculate yearly gross income
    yearly_income = 0
    months_in_year = 0

    for month_key, data in st.session_state.monthly_history.items():
        year = int(month_key.split('-')[0])
        if year == current_year:
            yearly_income += data['income']
            months_in_year += 1

    # Calculate improvement
    months_list = sorted(st.session_state.monthly_history.keys())
    show_improvement = False
    if len(months_list) >= 2:
        first_month_data = st.session_state.monthly_history[months_list[0]]
        first_month_savings_rate = (first_month_data['remaining'] / first_month_data['income'] * 100) if \
        first_month_data['income'] > 0 else 0

        recent_months = months_list[-2:]
        recent_savings_rates = []
        for month in recent_months:
            data = st.session_state.monthly_history[month]
            rate = (data['remaining'] / data['income'] * 100) if data['income'] > 0 else 0
            recent_savings_rates.append(rate)
        recent_avg_rate = np.mean(recent_savings_rates)

        improvement = recent_avg_rate - first_month_savings_rate
        is_improving = improvement > 0
        show_improvement = True

    # Yearly Income Display
    if yearly_income > 0:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.metric(f"{current_year} Gross Income (YTD)", f"${yearly_income:,.2f}",
                      delta=f"{months_in_year} months tracked")

        with col2:
            if show_improvement:
                if is_improving:
                    st.metric("Savings Rate", f"+{improvement:.1f}%", delta="Since joining", delta_color="normal")
                else:
                    st.metric("Savings Rate", f"{improvement:.1f}%", delta="Since joining", delta_color="inverse")

        st.markdown("---")

    # Bank Connection Options - TWO OPTIONS: Plaid OR Capital One
    if not st.session_state.bank_connected:
        st.markdown("### Connect Bank Account")

        # Create tabs for different connection methods
        conn_tab1, conn_tab2 = st.tabs(["Plaid", "Capital One"])

        # PLAID TAB
        with conn_tab1:
            st.write("Connect via Plaid to access 12,000+ financial institutions")

            col1, col2 = st.columns(2)
            with col1:
                plaid_client_id = st.text_input("Plaid Client ID", type="password", key="budget_plaid_client")
            with col2:
                plaid_secret = st.text_input("Plaid Secret", type="password", key="budget_plaid_secret")

            st.info("**Demo:** Click 'Connect' to load Plaid sample data")

            if st.button("Connect via Plaid", type="primary", key="connect_plaid_btn"):
                if not st.session_state.demo_loaded:
                    st.session_state.monthly_history = initialize_demo_data()
                    st.session_state.demo_loaded = True

                st.session_state.bank_transactions = generate_demo_transactions()
                st.session_state.bank_connected = True

                for transaction in st.session_state.bank_transactions:
                    recurring_keywords = ['netflix', 'spotify', 'gym', 'internet', 'electric']
                    is_recurring = any(keyword in transaction['merchant'].lower() for keyword in recurring_keywords)

                    if is_recurring and not any(
                            s['Name'] == transaction['merchant'] for s in st.session_state.subscriptions):
                        st.session_state.subscriptions.append({
                            'Name': transaction['merchant'],
                            'Cost': transaction['amount'],
                            'Category': transaction['category'],
                            'Date Added': transaction['date']
                        })
                    else:
                        if not any(e['Name'] == f"{transaction['merchant']} ({transaction['date']})" for e in
                                   st.session_state.expenses):
                            st.session_state.expenses.append({
                                'Name': f"{transaction['merchant']} ({transaction['date']})",
                                'Cost': transaction['amount'],
                                'Category': transaction['category'],
                                'Date': transaction['date']
                            })

                if st.session_state.monthly_income == 0:
                    st.session_state.monthly_income = 5000.0
                if st.session_state.monthly_rent == 0:
                    st.session_state.monthly_rent = 1200.0

                st.success(f"✅ Connected via Plaid! Imported {len(st.session_state.bank_transactions)} transactions")
                st.rerun()

        # CAPITAL ONE TAB
        with conn_tab2:
            st.write("Connect directly to Capital One accounts")

            col1, col2 = st.columns(2)
            with col1:
                c1_api_key = st.text_input("Capital One API Key", type="password", key="c1_api_key")
            with col2:
                c1_customer_id = st.text_input("Customer ID (optional)", key="c1_customer_id",
                                               placeholder="Leave blank for demo")

            st.info("**Demo:** Click 'Connect' to load Capital One sample data")

            if st.button("Connect via Capital One", type="primary", key="connect_c1_btn"):
                if c1_api_key:
                    # Try to connect to real API
                    try:
                        from services.capital_one_service import CapitalOneService

                        c1_service = CapitalOneService(c1_api_key)

                        if c1_customer_id:
                            transactions = c1_service.get_customer_accounts_and_transactions(c1_customer_id)
                        else:
                            # Get all accounts
                            accounts = c1_service.get_accounts()
                            if accounts and len(accounts) > 0:
                                account_id = accounts[0].get('_id')
                                transactions = c1_service.get_transactions(account_id)
                            else:
                                transactions = []

                        if transactions:
                            st.session_state.bank_transactions = transactions
                            st.session_state.bank_connected = True
                            st.success(f"✅ Connected to Capital One! Imported {len(transactions)} transactions")
                        else:
                            st.warning("No transactions found. Loading demo data instead...")
                            # Fall back to demo
                            st.session_state.bank_transactions = generate_demo_transactions()
                            st.session_state.bank_connected = True

                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}. Loading demo data...")
                        st.session_state.bank_transactions = generate_demo_transactions()
                        st.session_state.bank_connected = True
                else:
                    # No API key - use demo
                    st.session_state.bank_transactions = generate_demo_transactions()
                    st.session_state.bank_connected = True
                    st.success("✅ Demo mode: Loaded sample Capital One data")

                # Load demo history
                if not st.session_state.demo_loaded:
                    st.session_state.monthly_history = initialize_demo_data()
                    st.session_state.demo_loaded = True

                # Categorize transactions
                for transaction in st.session_state.bank_transactions:
                    recurring_keywords = ['netflix', 'spotify', 'gym', 'internet', 'electric']
                    is_recurring = any(keyword in transaction['merchant'].lower() for keyword in recurring_keywords)

                    if is_recurring and not any(
                            s['Name'] == transaction['merchant'] for s in st.session_state.subscriptions):
                        st.session_state.subscriptions.append({
                            'Name': transaction['merchant'],
                            'Cost': transaction['amount'],
                            'Category': transaction['category'],
                            'Date Added': transaction['date']
                        })
                    else:
                        if not any(e['Name'] == f"{transaction['merchant']} ({transaction['date']})" for e in
                                   st.session_state.expenses):
                            st.session_state.expenses.append({
                                'Name': f"{transaction['merchant']} ({transaction['date']})",
                                'Cost': transaction['amount'],
                                'Category': transaction['category'],
                                'Date': transaction['date']
                            })

                if st.session_state.monthly_income == 0:
                    st.session_state.monthly_income = 5000.0
                if st.session_state.monthly_rent == 0:
                    st.session_state.monthly_rent = 1200.0

                st.rerun()

        st.markdown("---")

    monthly_income = st.session_state.monthly_income
    monthly_rent = st.session_state.monthly_rent

    # Calculate totals
    total_subs = sum(s['Cost'] for s in st.session_state.subscriptions)
    total_expenses = sum(e['Cost'] for e in st.session_state.expenses)
    total_spending = total_subs + total_expenses + monthly_rent
    remaining = monthly_income - total_spending

    # Save current month data
    if monthly_income > 0:
        st.session_state.monthly_history[current_month] = {
            'income': monthly_income,
            'subscriptions': total_subs,
            'expenses': total_expenses,
            'rent': monthly_rent,
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

    # Check for budget violations
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

    # Show alerts with insights button
    if alerts:
        col1, col2 = st.columns([5, 1])

        with col1:
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

        with col2:
            if st.button("View Insights", key="show_insights_btn"):
                st.session_state.show_insights = not st.session_state.show_insights
                st.rerun()

        if st.session_state.show_insights:
            insights = generate_insights(
                st.session_state.subscriptions,
                st.session_state.expenses,
                category_spending,
                st.session_state.budget_limits,
                alerts
            )

            st.markdown("### Personalized Insights")

            for insight in insights:
                if insight['type'] == 'warning':
                    with st.expander(f"{insight['title']}", expanded=True):
                        for detail in insight['details']:
                            st.write(f"• {detail}")
                else:
                    with st.expander(f"{insight['title']}", expanded=False):
                        for detail in insight['details']:
                            st.write(f"• {detail}")

        st.markdown("---")

    # Budget Summary
    st.markdown("### Summary")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Income", f"${monthly_income:,.2f}")
    with col2:
        st.metric("Rent", f"${monthly_rent:,.2f}")
    with col3:
        st.metric("Recurring", f"${total_subs:,.2f}")
    with col4:
        st.metric("One-time", f"${total_expenses:,.2f}")
    with col5:
        delta_color = "normal" if remaining >= 0 else "inverse"
        st.metric("Balance", f"${remaining:,.2f}",
                  delta=f"{(remaining / monthly_income * 100):.1f}%" if monthly_income > 0 else "0%",
                  delta_color=delta_color)

    st.markdown("")

    # Current month visualizations
    if st.session_state.subscriptions or st.session_state.expenses:
        st.markdown("### This Month")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Spending by Category")

            all_items = []
            if monthly_rent > 0:
                all_items.append({'Category': 'Rent/Mortgage', 'Amount': monthly_rent})
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
            if monthly_rent > 0:
                all_items.append({'Category': 'Rent/Mortgage', 'Amount': monthly_rent})
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

    # Yearly Overview
    if len(st.session_state.monthly_history) > 1:
        st.markdown("### Yearly Overview")

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

        if len(history_df) >= 2:
            recent_savings = history_df['Savings'].tail(3).mean()
            older_savings = history_df['Savings'].head(3).mean()
            trend_improving = recent_savings > older_savings
            trend_pct = ((recent_savings - older_savings) / abs(older_savings) * 100) if older_savings != 0 else 0

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Monthly Income & Spending")

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=history_df['Month'],
                y=history_df['Spending'],
                mode='lines+markers',
                name='Spending',
                line=dict(color='#ff4444', width=3),
                marker=dict(size=8)
            ))

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

            colors = ['#00ff00' if s > 0 else '#ff4444' for s in history_df['Savings']]

            fig.add_trace(go.Bar(
                x=history_df['Month'],
                y=history_df['Savings'],
                marker_color=colors,
                name='Savings'
            ))

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

        if len(history_df) >= 2:
            if trend_improving:
                st.success(
                    f"Your monthly spending trend is improving. Average savings up {abs(trend_pct):.1f}% in recent months.")
            else:
                st.warning(
                    f"Your monthly spending has increased. Average savings down {abs(trend_pct):.1f}% in recent months.")

        st.markdown("---")

    # Budget Limits
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

    # Income and Rent
    st.markdown("### Income & Housing")
    col1, col2 = st.columns(2)

    with col1:
        new_income = st.number_input("Monthly income (can vary)", min_value=0.0, value=monthly_income, step=100.0,
                                     key="budget_income_input")
        if new_income != monthly_income:
            st.session_state.monthly_income = new_income
            st.rerun()

    with col2:
        new_rent = st.number_input("Monthly rent/mortgage", min_value=0.0, value=monthly_rent, step=50.0,
                                   key="budget_rent_input")
        if new_rent != monthly_rent:
            st.session_state.monthly_rent = new_rent
            st.rerun()

    st.markdown("---")

    # Manual Entry
    st.markdown("### Manual Entry")
    st.caption("Add expenses manually if not using bank connection")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Recurring Payments")

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

    with col2:
        st.markdown("#### Other Expenses")

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

    st.markdown("")
    if st.session_state.subscriptions or st.session_state.expenses:
        if st.button("Clear All Data", key="budget_clear_all"):
            st.session_state.subscriptions = []
            st.session_state.expenses = []
            st.rerun()

    # Bank connection at BOTTOM
    if st.session_state.bank_connected:
        st.markdown("---")
        st.markdown("### Bank Connection")

        st.success("✅ Bank account connected")

        with st.expander("View Recent Transactions", expanded=False):
            if st.session_state.bank_transactions:
                trans_df = pd.DataFrame(st.session_state.bank_transactions)
                trans_df = trans_df.sort_values('date', ascending=False).head(20)
                st.dataframe(
                    trans_df[['date', 'merchant', 'amount', 'category']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'date': 'Date',
                        'merchant': 'Merchant',
                        'amount': st.column_config.NumberColumn('Amount', format="$%.2f"),
                        'category': 'Category'
                    }
                )

        if st.button("Disconnect Bank", key="disconnect_bank_btn"):
            st.session_state.bank_connected = False
            st.session_state.bank_transactions = []
            st.session_state.demo_loaded = False
            st.session_state.monthly_history = {}
            st.rerun()