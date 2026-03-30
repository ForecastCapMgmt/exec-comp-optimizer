import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, date

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
    federal_tax_rate = st.slider("Your Estimated Marginal Federal Tax Rate (%)", 22, 37, 32)

# AMT input - only for ISO
amt_rate = 0
if option_type == "ISO":
    amt_rate = st.slider("Estimated AMT Rate (%)", 0, 28, 26)

# Vesting Date Input
st.subheader("Vesting Information")
next_vesting_date = st.date_input(
    "Next Major Vesting Date",
    value=date(2026, 6, 1),  # Default ~3 months from now (March 2026)
    min_value=date.today(),
    help="When do the next significant number of shares/options vest?"
)

# Concentration Risk Input
st.subheader("Concentration Risk Assessment")
net_worth = st.number_input(
    "Rough estimate of your total investable assets (excluding primary home) ($)",
    min_value=100000,
    value=2000000,
    step=100000,
    format="%d"
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

# ====================== CALCULATIONS ======================
gross_value = price * shares
intrinsic_value = max(0, price - strike) * shares

days_to_vesting = (next_vesting_date - date.today()).days
months_to_vesting = days_to_vesting // 30

if option_type == "RSU":
    tax_due = gross_value * (federal_tax_rate / 100)
    net_value = gross_value - tax_due
    tax_note = f"RSU: Taxed as ordinary income at vesting (${tax_due:,.0f} est. federal tax)"
    base_rec = "RSUs are taxed as ordinary income upon vesting."

elif option_type == "NSO":
    tax_due = intrinsic_value * (federal_tax_rate / 100)
    net_value = intrinsic_value - tax_due + (shares * strike)
    tax_note = f"NSO: Ordinary income tax on spread at exercise (${tax_due:,.0f} est.)"
    base_rec = "NSOs trigger ordinary income tax on the bargain element when exercised."

else:  # ISO
    amt_tax = intrinsic_value * (amt_rate / 100)
    tax_due = amt_tax
    net_value = intrinsic_value - amt_tax + (shares * strike)
    tax_note = f"ISO: No regular income tax at exercise, but AMT on spread ≈ ${amt_tax:,.0f}"
    base_rec = "ISOs offer long-term capital gains potential if held properly (1 year after exercise + 2 years after grant)."

# Timing-based smarter recommendation
if months_to_vesting <= 3:
    timing_advice = f"With vesting coming in the next {months_to_vesting} months, consider building a post-vesting sell plan to manage taxes and concentration."
elif months_to_vesting <= 12:
    timing_advice = f"Vesting is expected in about {months_to_vesting} months. This gives you time to plan a diversification strategy around the vesting event."
else:
    timing_advice = "Vesting is further out. Use this time to model different exercise/sale scenarios and tax implications."

recommendation = f"{base_rec} {timing_advice}"

# Concentration Risk
position_value = gross_value if option_type == "RSU" else (intrinsic_value + shares * strike)
concentration_pct = (position_value / net_worth * 100) if net_worth > 0 else 0

if concentration_pct < 10:
    risk_color = "green"
    risk_text = "Low concentration"
elif concentration_pct < 20:
    risk_color = "orange"
    risk_text = "Moderate concentration"
else:
    risk_color = "red"
    risk_text = "High concentration — consider diversifying"

# ====================== DISPLAY ======================
st.subheader("📊 Your Results")
c1, c2, c3 = st.columns(3)
c1.metric("Current Share Price", f"${price:,.2f}")
c2.metric("Gross Position Value", f"${gross_value:,.0f}")
c3.metric("**Net After-Tax Value**", f"${net_value:,.0f}", delta=f"-{federal_tax_rate}% federal")

st.info(f"**Tax Note**: {tax_note}")
st.info(f"**Recommendation**: {recommendation}")

# Concentration Risk
st.subheader("⚠️ Concentration Risk")
st.markdown(f"**This position represents** <span style='color:{risk_color}; font-weight:bold'>{concentration_pct:.1f}%</span> **of your investable assets**", unsafe_allow_html=True)
st.progress(concentration_pct / 100)
st.markdown(f"**Risk Level**: <span style='color:{risk_color}'>{risk_text}</span>", unsafe_allow_html=True)

if concentration_pct >= 15:
    st.warning("🔴 Many financial planners recommend keeping any single stock under 10–15% of investable assets.")

# Growth Scenario Chart
st.subheader("What if the stock price grows in the next year?")
growth_rates = [0.0, 0.05, 0.10, 0.15, 0.20]
future_net_values = []

for rate in growth_rates:
    future_price = price * (1 + rate)
    if option_type == "RSU":
        future_gross = future_price * shares
        future_net = future_gross * (1 - federal_tax_rate/100)
    else:
        future_intrinsic = max(0, future_price - strike) * shares
        future_net = future_intrinsic * (1 - federal_tax_rate/100) + (shares * strike)
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

st.caption("⚠️ Illustrative only. Not financial, tax, or investment advice. Consult your CPA and financial advisor before making decisions.")
