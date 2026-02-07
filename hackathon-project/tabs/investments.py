import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


def render():
    st.markdown("# Investment Portfolio")
    st.caption("Connect your brokerage and track your investments")
    st.markdown("---")

    # Initialize session state
    if 'plaid_holdings' not in st.session_state:
        st.session_state.plaid_holdings = []

    # If connected, show portfolio first
    if st.session_state.plaid_holdings:
        st.markdown("### Your Investment Portfolio")

        holdings_df = pd.DataFrame(st.session_state.plaid_holdings)
        total_portfolio_value = holdings_df['value'].sum()

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Portfolio Value", f"${total_portfolio_value:,.2f}")
        with col2:
            st.metric("Number of Holdings", len(holdings_df))
        with col3:
            avg_position = total_portfolio_value / len(holdings_df)
            st.metric("Average Position", f"${avg_position:,.2f}")

        st.markdown("")

        # Visualizations
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Portfolio Allocation")
            fig = px.pie(holdings_df, values='value', names='ticker', hole=0.4)
            fig.update_layout(height=300, showlegend=True, template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True, key="inv_pie_chart")

        with col2:
            st.markdown("#### Holdings by Value")
            fig = px.bar(holdings_df, x='ticker', y='value', color='value', color_continuous_scale='Blues')
            fig.update_layout(
                height=300,
                showlegend=False,
                template='plotly_dark',
                xaxis_title="",
                yaxis_title="Value ($)"
            )
            st.plotly_chart(fig, use_container_width=True, key="inv_bar_chart")

        st.markdown("---")

        # Holdings table
        st.markdown("#### Holdings Details")
        st.dataframe(
            holdings_df[['name', 'ticker', 'quantity', 'institution_price', 'value']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'name': 'Company',
                'ticker': 'Ticker',
                'quantity': 'Shares',
                'institution_price': st.column_config.NumberColumn('Price', format="$%.2f"),
                'value': st.column_config.NumberColumn('Value', format="$%.2f")
            }
        )

        st.markdown("---")

        # Connection section at bottom when connected
        st.markdown("### Manage Connection")
        if st.button("Disconnect Brokerage", key="inv_disconnect_btn"):
            st.session_state.plaid_holdings = []
            st.rerun()

    else:
        # Show connection section first when not connected
        st.markdown("### Connect Your Brokerage")

        with st.expander("Link Investment Account via Plaid", expanded=True):
            st.write("Connect your brokerage account to automatically import your portfolio.")

            col1, col2 = st.columns(2)
            with col1:
                plaid_client_id = st.text_input("Plaid Client ID", type="password", key="inv_plaid_client")
            with col2:
                plaid_secret = st.text_input("Plaid Secret", type="password", key="inv_plaid_secret")

            st.info("**For Demo:** Click 'Connect Brokerage' to load sample portfolio data")

            if st.button("Connect Brokerage", type="primary", key="inv_connect_btn"):
                # Simulated holdings for demo
                st.session_state.plaid_holdings = [
                    {'name': 'Apple Inc.', 'ticker': 'AAPL', 'quantity': 10, 'institution_price': 182.52,
                     'value': 1825.20},
                    {'name': 'Tesla Inc.', 'ticker': 'TSLA', 'quantity': 5, 'institution_price': 248.50,
                     'value': 1242.50},
                    {'name': 'Microsoft Corp.', 'ticker': 'MSFT', 'quantity': 8, 'institution_price': 378.91,
                     'value': 3031.28},
                    {'name': 'NVIDIA Corp.', 'ticker': 'NVDA', 'quantity': 3, 'institution_price': 495.22,
                     'value': 1485.66},
                ]
                st.success("Demo portfolio loaded!")
                st.rerun()

        st.markdown("---")
        st.info(
            "Connect your brokerage account to see your investment portfolio, allocation charts, and holdings details.")