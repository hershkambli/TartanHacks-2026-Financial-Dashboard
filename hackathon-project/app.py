import streamlit as st
import pandas as pd
from styles import load_css
from utils import calculate_portfolio_metrics

# Import tab modules
from tabs import markets, ai_assistant, portfolio, settings, investments

# Page config
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

# Sidebar
with st.sidebar:
    st.markdown("### FinDash")
    st.markdown("---")

    api_key = st.text_input("API Key", type="password", placeholder="sk-ant-...")

    st.markdown("---")
    st.markdown("#### Quick Stats")

    if st.session_state.portfolio:
        portfolio_df = pd.DataFrame(st.session_state.portfolio)
        metrics = calculate_portfolio_metrics(portfolio_df)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Portfolio", f"${metrics['total_value']:,.0f}")
        with col2:
            st.metric("Sharpe", f"{metrics['sharpe_ratio']:.2f}")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Portfolio", "$0")
        with col2:
            st.metric("Sharpe", "N/A")

# Tabs - Add Investments tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Budget", "Investments", "Markets", "AI Assistant", "Settings"])

with tab1:
    portfolio.render()

with tab2:
    investments.render()

with tab3:
    markets.render()

with tab4:
    ai_assistant.render(api_key)

with tab5:
    settings.render()