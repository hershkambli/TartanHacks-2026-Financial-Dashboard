import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np


def calculate_diversification_score(holdings_df):
    """Calculate how diversified the portfolio is (0-100)"""
    if holdings_df.empty:
        return 0

    total_value = holdings_df['value'].sum()
    holdings_df['weight'] = holdings_df['value'] / total_value
    herfindahl = (holdings_df['weight'] ** 2).sum()

    num_holdings = len(holdings_df)
    min_herfindahl = 1 / num_holdings

    if herfindahl <= min_herfindahl:
        return 100

    diversification_score = max(0, 100 * (1 - (herfindahl - min_herfindahl) / (1 - min_herfindahl)))

    return round(diversification_score, 1)


def generate_random_portfolio():
    """Generate a random portfolio worth over 200k with more stocks"""
    holdings = []

    # More stocks (tech heavy)
    stocks = [
        {'name': 'Apple Inc.', 'ticker': 'AAPL', 'price': 182.52, 'sector': 'Technology'},
        {'name': 'Microsoft Corp.', 'ticker': 'MSFT', 'price': 378.91, 'sector': 'Technology'},
        {'name': 'Amazon.com Inc.', 'ticker': 'AMZN', 'price': 178.25, 'sector': 'Retail'},
        {'name': 'NVIDIA Corp.', 'ticker': 'NVDA', 'price': 495.22, 'sector': 'Technology'},
        {'name': 'Tesla Inc.', 'ticker': 'TSLA', 'price': 248.50, 'sector': 'Automotive'},
        {'name': 'Google', 'ticker': 'GOOGL', 'price': 142.35, 'sector': 'Technology'},
        {'name': 'Meta', 'ticker': 'META', 'price': 465.80, 'sector': 'Technology'},
        {'name': 'Netflix', 'ticker': 'NFLX', 'price': 625.40, 'sector': 'Media'},
        {'name': 'Adobe', 'ticker': 'ADBE', 'price': 548.20, 'sector': 'Technology'},
        {'name': 'Salesforce', 'ticker': 'CRM', 'price': 285.60, 'sector': 'Technology'},
        {'name': 'Johnson & Johnson', 'ticker': 'JNJ', 'price': 152.80, 'sector': 'Healthcare'},
        {'name': 'Procter & Gamble', 'ticker': 'PG', 'price': 165.30, 'sector': 'Consumer Goods'},
        {'name': 'Walmart', 'ticker': 'WMT', 'price': 178.90, 'sector': 'Retail'},
        {'name': 'Visa', 'ticker': 'V', 'price': 285.40, 'sector': 'Financials'},
        {'name': 'JPMorgan Chase', 'ticker': 'JPM', 'price': 198.75, 'sector': 'Financials'},
    ]

    # Bonds (less allocation)
    bonds = [
        {'name': 'iShares Core US Aggregate Bond ETF', 'ticker': 'AGG', 'price': 98.75, 'sector': 'Bonds'},
        {'name': 'Vanguard Total Bond Market ETF', 'ticker': 'BND', 'price': 72.30, 'sector': 'Bonds'},
    ]

    # REITs
    reits = [
        {'name': 'Vanguard Real Estate ETF', 'ticker': 'VNQ', 'price': 85.40, 'sector': 'Real Estate'},
        {'name': 'Digital Realty Trust', 'ticker': 'DLR', 'price': 142.60, 'sector': 'Real Estate'},
    ]

    # Commodities
    commodities = [
        {'name': 'SPDR Gold Shares', 'ticker': 'GLD', 'price': 188.90, 'sector': 'Commodities'},
        {'name': 'Invesco DB Commodity Index', 'ticker': 'DBC', 'price': 22.15, 'sector': 'Commodities'},
    ]

    # Crypto
    crypto = [
        {'name': 'Grayscale Bitcoin Trust', 'ticker': 'GBTC', 'price': 58.30, 'sector': 'Crypto'},
    ]

    # International
    international = [
        {'name': 'Vanguard FTSE Developed Markets ETF', 'ticker': 'VEA', 'price': 48.25, 'sector': 'International'},
    ]

    # Target: 250k-600k portfolio, heavily weighted toward stocks
    target_value = np.random.uniform(250000, 600000)

    # Allocate 70-80% to stocks
    stock_value = target_value * np.random.uniform(0.70, 0.80)
    other_value = target_value - stock_value

    # Distribute stock value
    for asset in stocks:
        allocation_pct = np.random.uniform(0.03, 0.12)
        value = stock_value * allocation_pct
        quantity = int(value / asset['price'])
        actual_value = quantity * asset['price']

        if quantity > 0:
            holdings.append({
                'name': asset['name'],
                'ticker': asset['ticker'],
                'quantity': quantity,
                'institution_price': asset['price'],
                'value': actual_value,
                'sector': asset['sector']
            })

    # Distribute other assets
    other_assets = bonds + reits + commodities + crypto + international
    for asset in other_assets:
        allocation_pct = np.random.uniform(0.01, 0.05)
        value = other_value * allocation_pct
        quantity = int(value / asset['price'])
        actual_value = quantity * asset['price']

        if quantity > 0:
            holdings.append({
                'name': asset['name'],
                'ticker': asset['ticker'],
                'quantity': quantity,
                'institution_price': asset['price'],
                'value': actual_value,
                'sector': asset['sector']
            })

    return holdings


def render():
    st.markdown("# Investment Portfolio")
    st.caption("Track your investments and analyze portfolio performance")
    st.markdown("---")

    # Initialize session state
    if 'plaid_holdings' not in st.session_state:
        st.session_state.plaid_holdings = []
    if 'retirement_age' not in st.session_state:
        st.session_state.retirement_age = 65
    if 'retirement_goal' not in st.session_state:
        st.session_state.retirement_goal = 1000000
    if 'current_age' not in st.session_state:
        st.session_state.current_age = 30
    if 'net_worth' not in st.session_state:
        st.session_state.net_worth = 450000
    if 'stock_allocation' not in st.session_state:
        st.session_state.stock_allocation = 70
    if 'bond_allocation' not in st.session_state:
        st.session_state.bond_allocation = 30
    if 'risk_tolerance_pct' not in st.session_state:
        st.session_state.risk_tolerance_pct = 15

    # If connected, show portfolio first
    if st.session_state.plaid_holdings:
        holdings_df = pd.DataFrame(st.session_state.plaid_holdings)
        total_portfolio_value = holdings_df['value'].sum()

        # Calculate metrics
        diversification_score = calculate_diversification_score(holdings_df)

        # Simulate performance
        portfolio_return_ytd = np.random.uniform(5, 15)
        portfolio_volatility = np.random.uniform(10, 25)

        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Portfolio Value", f"${total_portfolio_value:,.2f}", delta=f"+{portfolio_return_ytd:.1f}% YTD")
        with col2:
            st.metric("Diversification Score", f"{diversification_score}/100",
                      delta="Good" if diversification_score >= 70 else "Improve")
        with col3:
            st.metric("Holdings", len(holdings_df))
        with col4:
            st.metric("Volatility", f"{portfolio_volatility:.1f}%")

        st.markdown("")

        # Portfolio Allocation & Diversification
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Asset Class Breakdown")

            # Categorize by sector
            sector_totals = holdings_df.groupby('sector')['value'].sum().reset_index()
            sector_totals = sector_totals.sort_values('value', ascending=False)

            fig = px.pie(sector_totals, values='value', names='sector', hole=0.4)
            fig.update_layout(height=300, showlegend=True, template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True, key="inv_sector_pie")

        with col2:
            st.markdown("#### Sector Diversification")

            sector_totals['percentage'] = (sector_totals['value'] / total_portfolio_value * 100).round(1)

            fig = px.bar(sector_totals, x='sector', y='percentage',
                         color='percentage', color_continuous_scale='Blues')
            fig.update_layout(
                height=300,
                showlegend=False,
                template='plotly_dark',
                xaxis_title="",
                yaxis_title="Portfolio %"
            )
            st.plotly_chart(fig, use_container_width=True, key="inv_sector_bar")

        st.markdown("---")

        # Portfolio Performance Trend
        st.markdown("### Performance")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Portfolio Growth (6 Months)")

            months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb']
            base_value = total_portfolio_value * 0.85
            values = []
            current_val = base_value

            for i in range(6):
                growth = np.random.uniform(0.02, 0.08)
                current_val *= (1 + growth)
                values.append(current_val)

            performance_df = pd.DataFrame({
                'Month': months,
                'Value': values
            })

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=performance_df['Month'],
                y=performance_df['Value'],
                mode='lines+markers',
                fill='tozeroy',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=8)
            ))

            fig.update_layout(
                height=300,
                template='plotly_dark',
                xaxis_title="",
                yaxis_title="Portfolio Value ($)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, key="inv_performance_chart")

        with col2:
            st.markdown("#### Top Holdings Performance")

            holdings_perf = holdings_df.copy()
            holdings_perf['return'] = np.random.uniform(-5, 20, len(holdings_perf))
            holdings_perf = holdings_perf.sort_values('return', ascending=False).head(10)

            fig = px.bar(holdings_perf, x='ticker', y='return',
                         color='return',
                         color_continuous_scale=['#ff4444', '#ffaa00', '#00ff00'])
            fig.update_layout(
                height=300,
                showlegend=False,
                template='plotly_dark',
                xaxis_title="",
                yaxis_title="Return (%)"
            )
            st.plotly_chart(fig, use_container_width=True, key="inv_stock_perf_bar")

        st.markdown("---")

        # ML Recommendations Section (BELOW GRAPHS)
        st.markdown("### AI-Powered Recommendations")
        st.caption("Based on your financial profile and goals")

        # Get user financial data from Budget tab
        monthly_income = st.session_state.get('monthly_income', 0)
        monthly_expenses = sum(s['Cost'] for s in st.session_state.get('subscriptions', [])) + \
                           sum(e['Cost'] for e in st.session_state.get('expenses', [])) + \
                           st.session_state.get('monthly_rent', 0)

        annual_income = monthly_income * 12
        annual_expenses = monthly_expenses * 12

        col1, col2, col3 = st.columns(3)

        with col1:
            current_age = st.number_input("Current Age", min_value=18, max_value=100,
                                          value=st.session_state.current_age, key="inv_current_age")

        with col2:
            retirement_age = st.number_input("Target Retirement Age", min_value=current_age, max_value=100,
                                             value=st.session_state.retirement_age, key="inv_retirement_age")

        with col3:
            # Dropdown for risk tolerance
            risk_options = {
                "Very Conservative (5% max loss)": 5,
                "Conservative (10% max loss)": 10,
                "Moderate (15% max loss)": 15,
                "Moderate-Aggressive (20% max loss)": 20,
                "Aggressive (25% max loss)": 25,
                "Very Aggressive (30%+ max loss)": 30
            }

            current_selection = "Moderate (15% max loss)"
            for label, value in risk_options.items():
                if value == st.session_state.risk_tolerance_pct:
                    current_selection = label
                    break

            risk_selection = st.selectbox(
                "Risk Tolerance",
                options=list(risk_options.keys()),
                index=list(risk_options.keys()).index(current_selection),
                key="inv_risk_dropdown"
            )

            risk_tolerance_pct = risk_options[risk_selection]

        st.markdown("")

        col1, col2 = st.columns(2)

        with col1:
            retirement_goal = st.number_input("Retirement Savings Goal", min_value=0, step=10000,
                                              value=st.session_state.retirement_goal, key="inv_retirement_goal")

        with col2:
            net_worth = st.number_input("Total Net Worth", min_value=0.0, step=1000.0,
                                        value=float(st.session_state.net_worth), key="inv_net_worth")

        # Update session state
        if current_age != st.session_state.current_age:
            st.session_state.current_age = current_age
        if retirement_age != st.session_state.retirement_age:
            st.session_state.retirement_age = retirement_age
        if retirement_goal != st.session_state.retirement_goal:
            st.session_state.retirement_goal = retirement_goal
        if net_worth != st.session_state.net_worth:
            st.session_state.net_worth = net_worth
        if risk_tolerance_pct != st.session_state.risk_tolerance_pct:
            st.session_state.risk_tolerance_pct = risk_tolerance_pct

        st.markdown("")

        # Get ML Recommendations Button
        if st.button("Get ML Recommendations", type="primary", key="get_ml_recs"):
            try:
                from models.portfolio_recommender import PortfolioRecommender

                # Map percentage to 1-10 scale for model
                risk_tolerance_scale = int((risk_tolerance_pct / 30) * 10)
                risk_tolerance_scale = max(1, min(10, risk_tolerance_scale))

                # Prepare user profile
                years_to_retirement = retirement_age - current_age
                monthly_savings = (annual_income - annual_expenses) / 12 if annual_income > 0 else 0
                savings_rate = (annual_income - annual_expenses) / annual_income if annual_income > 0 else 0

                user_profile = {
                    'age': current_age,
                    'years_to_retirement': years_to_retirement,
                    'risk_tolerance': risk_tolerance_scale,
                    'income': annual_income if annual_income > 0 else 60000,
                    'expenses': annual_expenses if annual_expenses > 0 else 40000,
                    'net_worth': net_worth,
                    'portfolio_value': total_portfolio_value,
                    'monthly_savings': monthly_savings if monthly_savings > 0 else 1000,
                    'savings_rate': savings_rate if savings_rate > 0 else 0.3
                }

                # Get recommendations
                recommender = PortfolioRecommender()
                recommendations = recommender.get_recommendations(user_profile)

                # Display recommendations
                st.markdown("---")
                st.markdown("### Your Personalized Portfolio Plan")

                # Risk Profile
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Risk Profile", recommendations['risk_category'])
                with col2:
                    st.metric("Recommended Allocation",
                              f"{recommendations['stock_allocation']:.1f}% Stocks / {recommendations['bond_allocation']:.1f}% Bonds")

                st.markdown("")

                # Stock Recommendations
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Recommended Stocks")

                    stocks_df = pd.DataFrame(recommendations['recommended_stocks'])
                    st.dataframe(
                        stocks_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'ticker': 'Ticker',
                            'name': 'Company',
                            'weight': st.column_config.NumberColumn('Weight %', format="%d%%")
                        }
                    )

                    # Pie chart
                    fig = px.pie(stocks_df, values='weight', names='ticker', hole=0.4)
                    fig.update_layout(height=250, showlegend=True, template='plotly_dark')
                    st.plotly_chart(fig, use_container_width=True, key="ml_stocks_pie")

                with col2:
                    st.markdown("#### Recommended Bonds")

                    bonds_df = pd.DataFrame(recommendations['recommended_bonds'])
                    st.dataframe(
                        bonds_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'type': 'Bond Type',
                            'ticker': 'Ticker',
                            'weight': st.column_config.NumberColumn('Weight %', format="%d%%")
                        }
                    )

                    # Allocation visualization
                    allocation_df = pd.DataFrame({
                        'Asset': ['Stocks', 'Bonds'],
                        'Percentage': [recommendations['stock_allocation'], recommendations['bond_allocation']]
                    })
                    fig = px.pie(allocation_df, values='Percentage', names='Asset', hole=0.4,
                                 color='Asset', color_discrete_map={'Stocks': '#3b82f6', 'Bonds': '#10b981'})
                    fig.update_layout(height=250, showlegend=True, template='plotly_dark')
                    st.plotly_chart(fig, use_container_width=True, key="ml_allocation_pie")

                # Action Items
                st.markdown("#### Recommended Actions")

                current_stock_pct = (st.session_state.stock_allocation)
                target_stock_pct = recommendations['stock_allocation']

                diff = target_stock_pct - current_stock_pct

                if abs(diff) < 5:
                    st.success("Your current allocation is optimal. No changes needed.")
                elif diff > 0:
                    st.info(f"Consider increasing stock allocation by {abs(diff):.1f}% (reduce bonds)")
                else:
                    st.info(f"Consider increasing bond allocation by {abs(diff):.1f}% (reduce stocks)")

                # Specific recommendations
                st.markdown("**Next Steps:**")
                for stock in recommendations['recommended_stocks'][:3]:
                    allocation_amount = (total_portfolio_value * recommendations['stock_allocation'] / 100) * (
                                stock['weight'] / 100)
                    st.write(f"• Allocate ${allocation_amount:,.2f} to {stock['name']} ({stock['ticker']})")

            except Exception as e:
                st.error(f"Error loading ML model: {str(e)}")
                st.info("Make sure you've trained the model by running: python models/train_model.py")

        st.markdown("---")

        # Holdings Details Table
        st.markdown("#### Holdings Details")

        display_df = holdings_df.copy()
        display_df['percentage'] = (display_df['value'] / total_portfolio_value * 100).round(1)

        st.dataframe(
            display_df[['name', 'ticker', 'quantity', 'institution_price', 'value', 'percentage']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'name': 'Asset',
                'ticker': 'Ticker',
                'quantity': 'Shares',
                'institution_price': st.column_config.NumberColumn('Price', format="$%.2f"),
                'value': st.column_config.NumberColumn('Value', format="$%.2f"),
                'percentage': st.column_config.NumberColumn('Portfolio %', format="%.1f%%")
            }
        )

        st.markdown("---")

        # Financial Goals
        st.markdown("### Financial Goals")

        years_to_retirement = retirement_age - current_age
        goal_progress = (total_portfolio_value / retirement_goal * 100) if retirement_goal > 0 else 0

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Current Savings", f"${total_portfolio_value:,.0f}")

        with col2:
            st.metric("Retirement Goal", f"${retirement_goal:,.0f}")

        with col3:
            st.metric("Progress", f"{goal_progress:.1f}%", delta="On Track" if goal_progress >= 50 else "Behind")

        st.markdown("")

        # Progress bar
        st.progress(min(goal_progress / 100, 1.0))

        st.markdown("")

        # Calculate needed monthly savings
        if years_to_retirement > 0 and retirement_goal > total_portfolio_value:
            remaining_needed = retirement_goal - total_portfolio_value
            months_remaining = years_to_retirement * 12
            monthly_needed = remaining_needed / months_remaining

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Years to Retirement", years_to_retirement)
            with col2:
                st.metric("Monthly Savings Needed", f"${monthly_needed:,.2f}")
        elif goal_progress >= 100:
            st.success("You've reached your retirement savings goal!")

        st.markdown("---")

        # Connection management
        st.markdown("### Manage Connection")
        if st.button("Disconnect Brokerage", key="inv_disconnect_btn"):
            st.session_state.plaid_holdings = []
            st.rerun()

    else:
        # Show connection section
        st.markdown("### Connect Your Brokerage")

        with st.expander("Link Investment Account via Plaid", expanded=True):
            st.write("Connect your brokerage account to automatically import your portfolio.")

            st.info("**For Demo:** Click 'Connect' to load sample portfolio")

            if st.button("Connect Brokerage", type="primary", key="inv_connect_btn"):
                # Generate random portfolio over 200k
                st.session_state.plaid_holdings = generate_random_portfolio()
                st.success("Demo portfolio loaded!")
                st.rerun()

        st.markdown("---")
        st.info(
            "Connect your brokerage account to see portfolio analysis, performance tracking, and ML-powered recommendations.")