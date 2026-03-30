import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Exec Comp Optimizer", layout="centered", page_icon="🚀")

st.title("🚀 Exec Comp Optimizer")
st.markdown("### Stock Options & RSU Decision Tool for Executives")

st.info("💡 This tool provides illustrative calculations. State taxes may apply depending on your residence. Always consult your CPA or financial advisor.")

# Input section
st.subheader("Enter your grant details")

col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Stock Ticker Symbol (e.g. AAPL)", value="AAPL").upper().strip()
    shares = st.number_input("Number of Shares / Options", min_value=100, value=5000, step=100)
    option_type = st.selectbox("Type of Compensation", ["RSU", "NSO", "ISO"])

with col2:
    strike = st.number_input("Strike Price per Share ($)", min_value=0.0, value=45.0, step=0.01)
    tax_rate = st.slider("Your Estimated Marginal Federal Tax Rate (%)", 22, 37, 32)

# Fetch current price
price = None
if ticker:
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        st.success(f"✅ Current market price for {ticker}: **${price:,.2f}**")
    except:
        st.warning("Could not fetch live price. Please enter manually.")
        price = st.number_input("Manual current fair market value ($)", value=150.0, step=0.01)

if not price:
    price = 150.0

# Calculations
gross_value = price * shares
intrinsic_value = max(0, price - strike) * shares

if option_type == "RSU":
    tax_due = gross_value * (tax_rate / 100)
    net_value = gross_value - tax_due
    recommendation = "RSUs are taxed as ordinary income upon vesting. Many executives sell a portion immediately to diversify and manage concentration risk."
else:
    tax_due = intrinsic_value * (tax_rate / 100)
    net_value = intrinsic_value - tax_due + (shares * strike)
    if option_type == "ISO":
        recommendation = "ISOs have special tax rules. Consider holding for long-term capital gains treatment (1 year after exercise + 2 years after grant). AMT may apply in the year of exercise."
    else:
        recommendation = "NSOs are taxed as ordinary income on the spread at exercise. Exercising and selling can provide immediate liquidity but triggers tax now."

# Display results
st.subheader("📊 Your Results")
c1, c2, c3 = st.columns(3)
c1.metric("Current Share Price", f"${price:,.2f}")
c2.metric("Gross Value", f"${gross_value:,.0f}")
c3.metric("**Net After-Tax Value**", f"${net_value:,.0f}", delta=f"-{tax_rate}% federal tax")

st.info(f"**Recommendation**: {recommendation}")

# Growth Scenario Chart
st.subheader("What if the stock price grows in the next year?")
growth_rates = [0.0, 0.05, 0.10, 0.15, 0.20]
future_net_values = []

for rate in growth_rates:
    future_price = price * (1 + rate)
    if option_type == "RSU":
        future_gross = future_price * shares
        future_net = future_gross * (1 - tax_rate/100)
    else:
        future_intrinsic = max(0, future_price - strike) * shares
        future_net = future_intrinsic * (1 - tax_rate/100) + (shares * strike)
    future_net_values.append(future_net)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=[f"{int(rate*100)}%" for rate in growth_rates],
    y=future_net_values,
    marker_color="#00cc96"
))
fig.update_layout(
    title="Projected Net After-Tax Value in 1 Year",
    xaxis_title="Expected Annual Stock Growth Rate",
    yaxis_title="Net After-Tax Value ($)",
    template="plotly_white",
    height=400
)
st.plotly_chart(fig, use_container_width=True)

st.caption("⚠️ Illustrative only. Not financial, tax, or investment advice. Tax rules are complex and can change. Consult your professional advisors before making decisions.")
