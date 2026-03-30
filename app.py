import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Exec Comp Optimizer", layout="centered", page_icon="🚀")

st.title("🚀 Exec Comp Optimizer")
st.markdown("### Stock Options & RSU Decision Tool for Executives")

st.info("💡 Enter your details below to see your personalized analysis.")

# Input fields
ticker = st.text_input("Stock Ticker Symbol (e.g. AAPL)", value="AAPL").upper().strip()

col1, col2 = st.columns(2)
with col1:
    shares = st.number_input("Number of Shares / Options", min_value=100, value=5000, step=100)
    option_type = st.selectbox("Type of Compensation", ["RSU", "NSO", "ISO"])

with col2:
    strike = st.number_input("Strike Price per Share ($)", min_value=0.0, value=45.0, step=0.01)
    tax_rate = st.slider("Your Estimated Federal Tax Rate (%)", 22, 37, 32)

# Fetch current stock price
price = None
if ticker:
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        st.success(f"✅ Current price of {ticker}: **${price:,.2f}**")
    except:
        st.warning("Could not fetch price automatically.")
        price = st.number_input("Enter current price manually ($)", value=150.0, step=0.01)

if not price:
    price = 150.0

# Calculations
gross_value = price * shares
intrinsic = max(0, price - strike) * shares

if option_type == "RSU":
    tax_due = gross_value * (tax_rate / 100)
    net_value = gross_value - tax_due
else:  # NSO or ISO (simplified)
    tax_due = intrinsic * (tax_rate / 100)
    net_value = intrinsic - tax_due + (shares * strike)

# Results
st.subheader("📊 Your Results")
c1, c2, c3 = st.columns(3)
c1.metric("Current Price", f"${price:,.2f}")
c2.metric("Gross Value", f"${gross_value:,.0f}")
c3.metric("**Net After-Tax**", f"${net_value:,.0f}", delta=f"-{tax_rate}% tax")

st.caption("⚠️ This is a simplified tool for illustration only. Not financial advice. Consult your advisor.")
