import streamlit as st
import pandas as pd
import plotly.express as px
from utils import calculate_portfolio_metrics


def render():
    st.markdown("# Portfolio Management")
    st.caption("Track and analyze your investment portfolio")
    st.markdown("---")

    st.markdown("#### Add to Portfolio")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        new_ticker = st.text_input("Ticker", placeholder="e.g., AAPL", label_visibility="collapsed",
                                   key="portfolio_ticker")
    with col2:
        shares = st.number_input("Shares", min_value=0.0, step=0.1, label_visibility="collapsed",
                                 key="portfolio_shares")
    with col3:
        price = st.number_input("Price", min_value=0.0, step=0.01, label_visibility="collapsed", key="portfolio_price")
    with col4:
        if st.button("Add", type="primary", use_container_width=True):
            if new_ticker and shares > 0 and price > 0:
                st.session_state.portfolio.append({
                    'Ticker': new_ticker.upper(),
                    'Shares': shares,
                    'Price': price,
                    'Value': shares * price
                })
                st.success(f"✅ Added {shares} shares of {new_ticker.upper()}")
                st.rerun()

    st.markdown("")

    if st.session_state.portfolio:
        portfolio_df = pd.DataFrame(st.session_state.portfolio)
        metrics = calculate_portfolio_metrics(portfolio_df)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Value", f"${metrics['total_value']:,.2f}")
        with col2:
            st.metric("Avg Return", f"{metrics['avg_return'] * 100:.2f}%")
        with col3:
            st.metric("Volatility", f"{metrics['volatility'] * 100:.2f}%")
        with col4:
            st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")

        st.markdown("")
        st.dataframe(portfolio_df[['Ticker', 'Shares', 'Price', 'Value']], use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Asset Allocation")
            fig = px.pie(portfolio_df, values='Value', names='Ticker', hole=0.4)
            fig.update_layout(height=300, template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Expected Returns")
            fig = px.bar(portfolio_df, x='Ticker', y='Returns', color='Returns')
            fig.update_layout(height=300, template='plotly_dark', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        if st.button("🗑️ Clear Portfolio"):
            st.session_state.portfolio = []
            st.rerun()
    else:
        st.info("📝 Add stocks to your portfolio to see analysis")