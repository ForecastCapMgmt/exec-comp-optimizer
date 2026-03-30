import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Exec Comp Optimizer", layout="centered", page_icon="🚀")

st.title("🚀 Exec Comp Optimizer")
st.markdown("### Stock Options & RSU Decision Tool for Executives")

st.info("💡 This tool provides illustrative calculations. State taxes may apply depending on your residence. Always consult your CPA or financial advisor.")

# ====================== INPUTS ======================
st.subheader("Enter your grant details")

col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Stock Ticker Symbol (e.g. AAPL)", value="AAPL").upper().strip()
    shares = st.number_input("Number of Shares / Options", min_value=100, value=5000, step=100)
    option_type = st.selectbox("Type of Compensation", ["RSU", "NSO", "ISO"])

with col2:
    strike = st.number_input("Strike Price per Share ($)", min_value=0.0, value=45.0, step=0.01)
    tax_rate = st.slider("Your Estimated Marginal Federal Tax Rate (%)", 22, 37, 32)

# New: Concentration Risk Input
st.subheader("Concentration Risk Assessment")
net_worth = st.number_input(
    "Rough estimate of your total investable assets (excluding primary home) ($)",
    min_value=100000,
    value=2000000,
    step=100000,
    format="%d",
    help="This helps estimate how concentrated you are in this single stock."
)

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
    recommendation = "RSUs are taxed as ordinary income upon vesting. Consider selling a portion to reduce concentration risk."
else:
    tax_due = intrinsic_value * (tax_rate / 100)
    net_value = intrinsic_value - tax_due + (shares * strike)
    if option_type == "ISO":
        recommendation = "ISOs offer potential long-term capital gains treatment if held properly. AMT may apply in the year of exercise."
    else:
        recommendation = "NSOs trigger ordinary income tax on the spread at exercise. This can provide liquidity but increases your tax bill now."

# Concentration Risk Calculation
position_value = gross_value if option_type == "RSU" else (intrinsic_value + shares * strike)
concentration_pct = (position_value / net_worth * 100) if net_worth > 0 else 0

# Color for risk level
if concentration_pct < 10:
    risk_color = "green"
    risk_text = "Low concentration"
elif concentration_pct < 20:
    risk_color = "orange"
    risk_text = "Moderate concentration"
else:
    risk_color = "red"
    risk_text = "High concentration — consider diversifying"

# ====================== RESULTS ======================
st.subheader("📊 Your Results")
c1, c2, c3 = st.columns(3)
c1.metric("Current Share Price", f"${price:,.2f}")
c2.metric("Gross Position Value", f"${gross_value:,.0f}")
c3.metric("**Net After-Tax Value**", f"${net_value:,.0f}", delta=f"-{tax_rate}% federal")

st.info(f"**Recommendation**: {recommendation}")

# Concentration Risk Display
st.subheader("⚠️ Concentration Risk")
st.markdown(f"**This position represents** <span style='color:{risk_color}; font-weight:bold'>{concentration_pct:.1f}%</span> **of your investable assets**", unsafe_allow_html=True)

st.progress(concentration_pct / 100)

st.markdown(f"**Risk Level**: <span style='color:{risk_color}'>{risk_text}</span>", unsafe_allow_html=True)

if concentration_pct >= 15:
    st.warning("🔴 Many financial planners recommend keeping any single stock position under 10–15% of your total investable assets to manage risk.")

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

st.caption("⚠️ Illustrative only. Not financial, tax, or investment advice. Tax rules are complex. Consult your CPA and financial advisor before making any decisions.")
