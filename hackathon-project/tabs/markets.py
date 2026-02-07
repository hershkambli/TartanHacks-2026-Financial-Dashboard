import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd


def render():
    st.markdown("# Stock Analysis")
    st.caption("Investor trend, performance, risk, and scorecard view")
    st.markdown("---")

    # ---------- Controls ----------
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

    with c1:
        ticker = st.text_input(
            "Ticker",
            "AAPL",
            label_visibility="collapsed",
            placeholder="Enter ticker"
        )

    with c2:
        view_mode = st.selectbox(
            "View",
            ["Day", "Week", "Month"],
            label_visibility="collapsed"
        )

    with c3:
        show_relative = st.toggle("vs Market", value=True)

    with c4:
        analyze_btn = st.button("Analyze", type="primary", use_container_width=True)

    if not analyze_btn:
        return

    try:
        # ---------- Load ----------
        with st.spinner("Loading data..."):
            stock = yf.Ticker(ticker.upper())
            hist = stock.history(period="6mo")
            info = stock.info

        if hist.empty:
            st.error("❌ No data found.")
            return

        # ---------- Resample ----------
        if view_mode == "Week":
            hist = hist.resample("W").agg({
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum"
            })
        elif view_mode == "Month":
            hist = hist.resample("M").agg({
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum"
            })

        hist.dropna(inplace=True)

        # ---------- Metrics ----------
        start_price = hist["Close"].iloc[0]
        current_price = hist["Close"].iloc[-1]
        pct_change = (current_price / start_price - 1) * 100

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Price", f"${current_price:.2f}", f"{pct_change:+.2f}%")
        m2.metric("Period High", f"${hist['High'].max():.2f}")
        m3.metric("Period Low", f"${hist['Low'].min():.2f}")
        m4.metric("Avg Volume", f"{hist['Volume'].mean()/1e6:.1f}M")

        # ---------- Moving Averages ----------
        hist["MA20"] = hist["Close"].rolling(20).mean()
        hist["MA50"] = hist["Close"].rolling(50).mean()

        # ---------- Trend Label ----------
        if hist["MA20"].iloc[-1] > hist["MA50"].iloc[-1]:
            trend = "Uptrend"
        elif hist["MA20"].iloc[-1] < hist["MA50"].iloc[-1]:
            trend = "Downtrend"
        else:
            trend = "Sideways"

        st.info(f"Trend Signal: **{trend}**")

        # ---------- Investor Scorecard ----------
        score = 0
        reasons = []

        # Trend factor
        if hist["MA20"].iloc[-1] > hist["MA50"].iloc[-1]:
            score += 2
            reasons.append("Positive MA trend")

        # Return factor
        if pct_change > 15:
            score += 2
            reasons.append("Strong 6M return")
        elif pct_change > 5:
            score += 1

        # Drawdown factor
        running_max = hist["Close"].cummax()
        drawdown = hist["Close"] / running_max - 1
        max_dd = drawdown.min()

        if max_dd > -0.15:
            score += 2
            reasons.append("Low drawdown risk")
        elif max_dd > -0.30:
            score += 1

        # Valuation factor
        pe = info.get("forwardPE")
        pb = info.get("priceToBook")

        if pe and pe < 25:
            score += 2
            reasons.append("Reasonable PE")

        if pb and pb < 5:
            score += 1

        # Dividend factor
        if info.get("dividendYield"):
            score += 1
            reasons.append("Pays dividend")

        # Cap score
        score = min(score, 10)

        if score >= 8:
            label = "Strong"
        elif score >= 5:
            label = "Moderate"
        else:
            label = "Weak"

        st.markdown("### 📊 Investor Scorecard")
        s1, s2 = st.columns([1, 3])
        s1.metric("Score", f"{score}/10")
        s2.write(f"**Rating:** {label}")
        st.caption(", ".join(reasons))

        # ---------- Trend Chart ----------
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Price"))
        fig.add_trace(go.Scatter(x=hist.index, y=hist["MA20"], name="MA20"))
        fig.add_trace(go.Scatter(x=hist.index, y=hist["MA50"], name="MA50"))

        fig.update_layout(
            title=f"{ticker.upper()} Trend — 6 Months ({view_mode})",
            height=450,
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

        # ---------- Relative vs Market ----------
        if show_relative:
            spy = yf.Ticker("SPY").history(period="6mo")["Close"]
            if view_mode == "Week":
                spy = spy.resample("W").last()
            elif view_mode == "Month":
                spy = spy.resample("M").last()

            aligned = pd.concat([hist["Close"], spy], axis=1).dropna()
            aligned.columns = ["Stock", "SPY"]
            aligned = aligned / aligned.iloc[0]

            rel_fig = px.line(aligned, title="Relative Performance vs S&P 500")
            rel_fig.update_layout(height=350, template="plotly_dark")
            st.plotly_chart(rel_fig, use_container_width=True)

        # ---------- Drawdown Chart ----------
        dd_fig = px.area(drawdown, title="Drawdown From Peak")
        dd_fig.update_layout(height=250, template="plotly_dark")
        st.plotly_chart(dd_fig, use_container_width=True)

        # ---------- Volume ----------
        vol_fig = px.bar(hist, x=hist.index, y="Volume", title="Volume")
        vol_fig.update_layout(height=250, template="plotly_dark")
        st.plotly_chart(vol_fig, use_container_width=True)

        # ---------- Investment Scenario ----------
        st.markdown("### Investment Scenario")
        invest = st.number_input("Initial Investment ($)", 1000)
        shares = invest / start_price
        value_now = shares * current_price
        st.metric("Value Today", f"${value_now:,.2f}", f"{value_now - invest:+.2f}")

        # ---------- Download ----------
        st.download_button(
            "Download CSV",
            hist.to_csv().encode(),
            f"{ticker}_data.csv",
            "text/csv"
        )

        # ---------- Fundamentals ----------
        with st.expander("📋 Company Fundamentals"):
            c1, c2 = st.columns(2)

            with c1:
                st.write(f"**Company:** {info.get('longName', 'N/A')}")
                st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                st.write(f"**Industry:** {info.get('industry', 'N/A')}")

            with c2:
                mc = info.get("marketCap")
                st.write(f"**Market Cap:** ${mc/1e9:.2f}B" if mc else "N/A")
                st.write(f"**Forward PE:** {info.get('forwardPE', 'N/A')}")
                st.write(f"**Price/Book:** {info.get('priceToBook', 'N/A')}")
                st.write(f"**Dividend Yield:** {info.get('dividendYield', 'N/A')}")

    except Exception as e:
        st.error(f"❌ Error: {e}")

