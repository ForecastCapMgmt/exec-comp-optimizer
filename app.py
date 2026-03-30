import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Exec Comp Optimizer | Forecast Capital Management", layout="centered", page_icon="🚀")

# Display Logo at the top
st.image("https://i.imgur.com/PLACEHOLDER.png", width=180)  # ← Replace this URL with your actual logo link later

st.title("🚀 Exec Comp Optimizer")
st.markdown("### Stock Options & RSU Decision Tool by **Forecast Capital Management**")

st.info("💡 This tool provides illustrative calculations. State taxes may apply depending on your residence. Always consult your CPA or financial advisor.")

# ====================== LEAD CAPTURE ======================
st.sidebar.header("🔓 Unlock Deeper Analysis & Action Plan")
with st.sidebar.form("lead_form"):
    name = st.text_input("Your first name", placeholder="Jane")
    email = st.text_input("Work email", placeholder="jane@yourcompany.com")
    submitted = st.form_submit_button("Unlock Full Personalized Action Plan")
    if submitted and email:
        st.session_state["lead_captured"] = True
        st.session_state["user_name"] = name or "Executive"
        st.session_state["user_email"] = email
        st.success(f"Thanks, {name or 'there'}! Deeper analysis unlocked.")

if "lead_captured" not in st.session_state:
    st.info("💡 Enter your name and email in the sidebar to unlock the full personalized action plan, hold vs sell scenarios, and next-step guidance.")

# ====================== MAIN TOOL ======================
st.subheader("Enter your grant details")

col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Stock Ticker Symbol (e.g. AAPL)", value="AAPL").upper().strip()
    total_shares = st.number_input("Total Shares / Options in Grant", min_value=100, value=5000, step=100)
    option_type = st.selectbox("Type of Compensation", ["RSU", "NSO", "ISO"])

with col2:
    strike = st.number_input("Strike Price per Share ($)", min_value=0.0, value=45.0, step=0.01)
    federal_tax_rate = st.slider("Your Estimated Marginal Federal Tax Rate (%)", 22, 37, 32)

amt_rate = 0
if option_type == "ISO":
    amt_rate = st.slider("Estimated AMT Rate (%)", 0, 28, 26)

# Vesting Details
st.subheader("Vesting Information")
col_v1, col_v2 = st.columns(2)
with col_v1:
    next_vesting_date = st.date_input(
        "Next Major Vesting Date",
        value=date(2026, 6, 1),
        min_value=date.today()
    )
with col_v2:
    shares_vesting = st.number_input(
        "Number of Shares Vesting on That Date",
        min_value=0,
        value=1250,
        step=100
    )

# Concentration Risk
st.subheader("Concentration Risk Assessment")
net_worth = st.number_input(
    "Rough estimate of your total investable assets (excluding primary home) ($)",
    min_value=100000,
    value=2000000,
    step=100000,
    format="%d"
)

# Fetch price
price = None
if ticker:
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        st.success(f"✅ Current {ticker} price: **${price:,.2f}**")
    except:
        price = st.number_input("Manual current fair market value ($)", value=150.0, step=0.01)

if not price:
    price = 150.0

# Calculations (same as before)
gross_value = price * total_shares
intrinsic_value = max(0, price - strike) * total_shares
vesting_gross = price * shares_vesting
vesting_intrinsic = max(0, price - strike) * shares_vesting

if option_type == "RSU":
    vesting_tax = vesting_gross * (federal_tax_rate / 100)
    net_value = gross_value * (1 - federal_tax_rate/100)
    tax_note = f"RSU: Est. tax on next vesting ≈ ${vesting_tax:,.0f}"
    base_rec = "RSUs are taxed as ordinary income upon vesting."
else:
    vesting_tax = vesting_intrinsic * (federal_tax_rate / 100) if option_type == "NSO" else vesting_intrinsic * (amt_rate / 100)
    net_value = (intrinsic_value * (1 - federal_tax_rate/100)) + (total_shares * strike) if option_type != "ISO" else (vesting_intrinsic - vesting_tax) + (total_shares * strike)
    tax_note = f"ISO: Est. AMT on next vesting spread ≈ ${vesting_tax:,.0f}" if option_type == "ISO" else f"NSO: Est. tax on next vesting spread ≈ ${vesting_tax:,.0f}"
    base_rec = "ISOs offer long-term capital gains potential if held properly." if option_type == "ISO" else "NSOs trigger ordinary income tax on the bargain element when exercised."

# Timing
days_to_vesting = (next_vesting_date - date.today()).days
months_to_vesting = max(0, days_to_vesting // 30)
if months_to_vesting <= 3:
    timing_advice = f"With {shares_vesting:,} shares vesting in the next {months_to_vesting} months, plan for the immediate tax impact."
elif months_to_vesting <= 12:
    timing_advice = f"{shares_vesting:,} shares vesting in about {months_to_vesting} months gives you planning time."
else:
    timing_advice = "Vesting is further out — good opportunity to model scenarios."

recommendation = f"{base_rec} {timing_advice}"

# Concentration
position_value = gross_value if option_type == "RSU" else (intrinsic_value + total_shares * strike)
concentration_pct = (position_value / net_worth * 100) if net_worth > 0 else 0

if concentration_pct < 10:
    risk_color = "green"; risk_text = "Low"
elif concentration_pct < 20:
    risk_color = "orange"; risk_text = "Moderate"
else:
    risk_color = "red"; risk_text = "High — consider diversifying"

vesting_concentration = (vesting_gross / net_worth * 100) if net_worth > 0 else 0

# ====================== RESULTS ======================
st.subheader("📊 Your Results")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Price", f"${price:,.2f}")
c2.metric("Total Gross Value", f"${gross_value:,.0f}")
c3.metric("**Net After-Tax Value**", f"${net_value:,.0f}")
c4.metric("Est. Tax on Next Vesting", f"${vesting_tax:,.0f}")

st.info(f"**Tax Note**: {tax_note}")
st.info(f"**Recommendation**: {recommendation}")

st.subheader("⚠️ Concentration Risk")
st.markdown(f"**Full Position**: <span style='color:{risk_color}; font-weight:bold'>{concentration_pct:.1f}%</span> of investable assets", unsafe_allow_html=True)
st.progress(concentration_pct / 100)
if vesting_concentration > 5:
    st.warning(f"⚠️ Next vesting could add ~{vesting_concentration:.1f}% concentration.")

st.markdown(f"**Risk Level**: <span style='color:{risk_color}'>{risk_text}</span>", unsafe_allow_html=True)

# Growth Chart
st.subheader("What if the stock price grows in the next year?")
growth_rates = [0.0, 0.05, 0.10, 0.15, 0.20]
future_net = []
for rate in growth_rates:
    fp = price * (1 + rate)
    if option_type == "RSU":
        future_net.append(fp * total_shares * (1 - federal_tax_rate/100))
    else:
        fi = max(0, fp - strike) * total_shares
        future_net.append(fi * (1 - federal_tax_rate/100) + total_shares * strike)

fig = go.Figure()
fig.add_trace(go.Bar(x=[f"{int(r*100)}%" for r in growth_rates], y=future_net, marker_color="#00cc96"))
fig.update_layout(title="Projected Net After-Tax Value in 1 Year", xaxis_title="Annual Growth Rate", yaxis_title="Net Value ($)", template="plotly_white", height=400)
st.plotly_chart(fig, use_container_width=True)

# ====================== DEEPER ANALYSIS (Unlocked) ======================
if "lead_captured" in st.session_state:
    st.subheader("🔓 Deeper Personalized Analysis")
    st.write(f"**Hi {st.session_state['user_name']},** here’s more detailed guidance based on your situation:")

    # Hold vs Sell Scenario
    st.write("**Hold vs Sell Post-Vesting Scenario**")
    sell_after_tax = vesting_gross * (1 - federal_tax_rate/100) if option_type == "RSU" else (vesting_intrinsic * (1 - federal_tax_rate/100))
    hold_value = vesting_gross if option_type == "RSU" else vesting_intrinsic + shares_vesting * strike

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Sell Immediately After Vesting (est. after tax)", f"${sell_after_tax:,.0f}")
    with col_b:
        st.metric("Hold the Vested Shares", f"${hold_value:,.0f}")

    # Post-vesting concentration
    post_vesting_conc = ((position_value + vesting_gross) / net_worth * 100) if net_worth > 0 else 0
    st.metric("Projected Post-Vesting Concentration", f"{post_vesting_conc:.1f}%")

    # Actionable Next Steps
    st.write("**Recommended Next Steps**")
    steps = [
        "Review these numbers with your CPA before the vesting date",
        "Consider a sell-to-cover strategy to pay taxes without selling all shares",
        "Evaluate diversification options if concentration exceeds 15%",
        "Model different scenarios if you have multiple grants or complex tax situations"
    ]
    for step in steps:
        st.write(f"• {step}")

    # Book a Call Button
    st.markdown("---")
    st.markdown("### Ready to create your personalized executive compensation strategy?")
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        st.link_button("📅 Book a Strategy Call", "https://www.forecastcapitalmanagement.com/contact", use_container_width=True)
    with col_btn2:
        st.link_button("🌐 Visit Our Website", "https://www.forecastcapitalmanagement.com", use_container_width=True)

    st.success("✅ Your deeper analysis is unlocked. Feel free to screenshot or save this page.")

else:
    st.info("🔓 Unlock the deeper analysis section (Hold vs Sell scenarios, post-vesting projections, and actionable steps) by entering your details in the sidebar.")

st.caption("Forecast Capital Management • www.forecastcapitalmanagement.com • Not financial, tax, or investment advice.")
