import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd


def render():
    st.markdown("# Stock Analysis")
    st.caption("Investor trend, performance, and fundamentals overview")
    st.markdown("---")

    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ticker = st.text_input("Stock Ticker", "AAPL", label_visibility="collapsed",
                               placeholder="Enter ticker (e.g., AAPL)", key="markets_ticker")
    with col2:
        view_mode = st.selectbox("View", ["Day", "Week", "Month"], label_visibility="collapsed", key="markets_view")
    with col3:
        analyze_btn = st.button("Analyze", type="primary", use_container_width=True, key="markets_analyze")

    # Clean ticker
    ticker = ticker.strip().upper() if ticker else ""

    if not analyze_btn and not ticker:
        st.info("Enter a stock ticker and click Analyze to view data")
        return

    if not ticker:
        st.error("Please enter a valid ticker symbol")
        return

    try:
        # Load Stock Data
        with st.spinner(f"Loading data for {ticker}..."):
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")

            if hist.empty:
                st.error(f"No historical data found for ticker '{ticker}'. Please check the symbol and try again.")
                return

            # Fetch stock info
            try:
                info = stock.info
                company_name = info.get('longName', ticker)
            except:
                info = {}
                company_name = ticker

        # Display Company Name and Ticker
        st.markdown(f"## {company_name}")
        st.caption(f"Ticker: {ticker}")
        st.markdown("---")

        # Resample based on view mode
        if view_mode == "Week":
            hist = hist.resample("W").agg({
                "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
            })
        elif view_mode == "Month":
            hist = hist.resample("ME").agg({
                "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
            })
        hist.dropna(inplace=True)

        # Key Metrics
        start_price = hist["Close"].iloc[0]
        current_price = hist["Close"].iloc[-1]
        pct_change = (current_price / start_price - 1) * 100

        st.markdown("### Key Metrics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", f"${current_price:.2f}", f"{pct_change:+.2f}%")
        c2.metric("High", f"${hist['High'].max():.2f}")
        c3.metric("Low", f"${hist['Low'].min():.2f}")
        c4.metric("Avg Volume", f"{hist['Volume'].mean() / 1e6:.1f}M")

        st.markdown("")

        # Trend Summary
        st.markdown("### Trend Overview")
        if pct_change > 10:
            trend_text = f"Strong positive trend with {pct_change:.1f}% increase over the period"
        elif pct_change > 0:
            trend_text = f"Moderate upward movement with {pct_change:.1f}% gain"
        elif pct_change < -10:
            trend_text = f"Significant decline of {pct_change:.1f}% over the period"
        else:
            trend_text = f"Relatively flat performance with {pct_change:.1f}% change"

        st.write(trend_text)

        st.markdown("---")

        # Trend Chart
        st.markdown("### Price Trend")
        hist["MA20"] = hist["Close"].rolling(20).mean()
        hist["MA50"] = hist["Close"].rolling(50).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close", line=dict(color='#3b82f6', width=2)))
        fig.add_trace(
            go.Scatter(x=hist.index, y=hist["MA20"], name="MA20", line=dict(color='#10b981', width=1.5, dash='dash')))
        fig.add_trace(
            go.Scatter(x=hist.index, y=hist["MA50"], name="MA50", line=dict(color='#f59e0b', width=1.5, dash='dot')))
        fig.update_layout(height=450, template="plotly_dark", xaxis_title="", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True, key="markets_trend_chart")

        st.markdown("---")

        # Performance Comparison
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Relative Performance vs S&P 500")
            spy = yf.Ticker("SPY").history(period="6mo")["Close"]
            if view_mode == "Week":
                spy = spy.resample("W").last()
            elif view_mode == "Month":
                spy = spy.resample("ME").last()

            aligned = pd.concat([hist["Close"], spy], axis=1).dropna()
            aligned.columns = [ticker, "SPY"]
            aligned = aligned / aligned.iloc[0]

            rel_fig = px.line(aligned, labels={'value': 'Normalized Price', 'variable': 'Asset'})
            rel_fig.update_layout(height=350, template="plotly_dark", xaxis_title="",
                                  yaxis_title="Relative Performance")
            st.plotly_chart(rel_fig, use_container_width=True, key="markets_relative_chart")

        with col2:
            st.markdown("### Drawdown From Peak")
            drawdown = (hist["Close"] / hist["Close"].cummax() - 1) * 100

            dd_fig = go.Figure()
            dd_fig.add_trace(go.Scatter(
                x=drawdown.index,
                y=drawdown,
                fill='tozeroy',
                line=dict(color='#ff4444', width=2),
                name='Drawdown'
            ))
            dd_fig.update_layout(height=350, template="plotly_dark", xaxis_title="", yaxis_title="Drawdown (%)")
            st.plotly_chart(dd_fig, use_container_width=True, key="markets_drawdown_chart")

        st.markdown("---")

        # Volume
        st.markdown("### Trading Volume")
        vol_fig = px.bar(hist, x=hist.index, y="Volume")
        vol_fig.update_layout(height=250, template="plotly_dark", xaxis_title="", yaxis_title="Volume",
                              showlegend=False)
        st.plotly_chart(vol_fig, use_container_width=True, key="markets_volume_chart")

        st.markdown("---")

        # Investment Scenario
        st.markdown("### Investment Scenario")
        col1, col2, col3 = st.columns(3)

        with col1:
            invest = st.number_input("Initial Investment", min_value=100, value=1000, step=100,
                                     key="markets_investment")

        with col2:
            shares = invest / start_price
            st.metric("Shares Purchased", f"{shares:.2f}")

        with col3:
            value_now = shares * current_price
            profit = value_now - invest
            st.metric("Value Today", f"${value_now:,.2f}", delta=f"${profit:+,.2f}")

        st.markdown("---")

        # Fundamentals
        st.markdown("### Company Fundamentals")
        f1, f2 = st.columns(2)

        with f1:
            st.write(f"**Company:** {info.get('longName', 'N/A')}")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")

        with f2:
            mc = info.get("marketCap")
            st.write(f"**Market Cap:** ${mc / 1e9:.2f}B" if mc else "**Market Cap:** N/A")
            pe = info.get('trailingPE')
            st.write(f"**P/E Ratio:** {pe:.2f}" if pe else "**P/E Ratio:** N/A")
            div_yield = info.get('dividendYield')
            st.write(f"**Dividend Yield:** {div_yield * 100:.2f}%" if div_yield else "**Dividend Yield:** N/A")

        st.markdown("---")

        # Download Data
        csv_data = hist.to_csv().encode()
        st.download_button(
            "Download Historical Data (CSV)",
            csv_data,
            f"{ticker}_data.csv",
            "text/csv",
            key="markets_download"
        )

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        st.info("Please verify the ticker symbol is correct and try again.")

