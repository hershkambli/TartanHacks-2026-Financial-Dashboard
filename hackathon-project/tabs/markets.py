import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf


def render():
    st.markdown("# Stock Analysis")
    st.caption("Real-time market data and technical analysis")
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ticker = st.text_input("Stock Ticker", "AAPL", label_visibility="collapsed",
                               placeholder="Enter ticker (e.g., AAPL)", key="ticker_input")
    with col2:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "5y"], label_visibility="collapsed")
    with col3:
        analyze_btn = st.button("Analyze", type="primary", use_container_width=True)

    if analyze_btn:
        try:
            with st.spinner(f"Loading {ticker.upper()} data..."):
                stock = yf.Ticker(ticker.upper())
                hist = stock.history(period=period)
                info = stock.info

                if hist.empty:
                    st.error("❌ Could not fetch data. Please check the ticker symbol.")
                else:
                    st.success(f"✅ Data loaded for {ticker.upper()}")

                    current_price = hist['Close'].iloc[-1]
                    price_change = hist['Close'].iloc[-1] - hist['Close'].iloc[0]
                    price_change_pct = (price_change / hist['Close'].iloc[0]) * 100

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Current Price", f"${current_price:.2f}", f"{price_change_pct:+.2f}%")
                    col2.metric("Volume", f"{hist['Volume'].iloc[-1] / 1e6:.1f}M")
                    col3.metric("High", f"${hist['High'].max():.2f}")
                    col4.metric("Low", f"${hist['Low'].min():.2f}")

                    fig = go.Figure(data=[go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close']
                    )])

                    fig.update_layout(
                        title=f'{ticker.upper()} Stock Price',
                        yaxis_title='Price ($)',
                        height=400,
                        template='plotly_dark'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    fig2 = px.bar(hist, x=hist.index, y='Volume', title='Trading Volume')
                    fig2.update_layout(height=250, template='plotly_dark')
                    st.plotly_chart(fig2, use_container_width=True)

                    with st.expander("📋 Company Information"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Company:** {info.get('longName', 'N/A')}")
                            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                            st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                        with col2:
                            st.write(f"**Market Cap:** ${info.get('marketCap', 0) / 1e9:.2f}B")
                            st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
                            st.write(f"**52W High:** ${info.get('fiftyTwoWeekHigh', 'N/A')}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")