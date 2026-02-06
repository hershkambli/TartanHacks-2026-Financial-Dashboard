import streamlit as st


def render():
    st.markdown("# Settings & Preferences")
    st.caption("Customize your dashboard experience")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Display Options")
        theme = st.selectbox("Color Theme", ["Dark", "Light", "Auto"])
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY"])

    with col2:
        st.markdown("#### Risk Preferences")
        risk_tolerance = st.slider("Risk Tolerance", 1, 10, 5, help="1 = Conservative, 10 = Aggressive")
        time_horizon = st.selectbox("Investment Horizon",
                                    ["Short (< 2 years)", "Medium (2-5 years)", "Long (5+ years)"])

    st.markdown("")
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")