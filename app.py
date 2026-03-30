import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="Exec Comp Optimizer", layout="centered", page_icon="🚀")

st.title("🚀 Exec Comp Optimizer")
st.markdown("### Stock Options & RSU Decision Tool for Executives")

st.info("💡 This tool provides illustrative calculations. State taxes may apply depending on your residence. Always consult your CPA or financial advisor.")

# ====================== LEAD CAPTURE (Marketing Funnel) ======================
st.sidebar.header("👋 Get Your Free Personalized PDF Report")
with st.sidebar.form("lead_form"):
    name = st.text_input("Your first name", placeholder="Jane")
    email = st.text_input("Work email", placeholder="jane@yourcompany.com")
    submitted = st.form_submit_button("Unlock Full Report + PDF")
    if submitted and email:
        st.session_state["lead_captured"] = True
        st.session_state["user_name"] = name or "Executive"
        st.session_state["user_email"] = email
        st.success(f"Thanks, {name or 'there'}! PDF unlocked.")

if "lead_captured" not in st.session_state:
    st.info("💡 Complete the form in the sidebar to unlock your personalized PDF report (includes vesting tax estimate, risk summary, and next-step guidance).")

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

# Calculations
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
    timing_advice = f"With {shares_vesting:,} shares vesting in the next {months_to_vesting} months, plan for the immediate tax impact and consider a post-vesting diversification strategy."
elif months_to_vesting <= 12:
    timing_advice = f"{shares_vesting:,} shares vesting in about {months_to_vesting} months gives you time to prepare a tax-efficient sell plan."
else:
    timing_advice = "Vesting is further out — good opportunity to model multiple scenarios in advance."

recommendation = f"{base_rec} {timing_advice}"

# Concentration
position_value = gross_value if option_type == "RSU" else (intrinsic_value + total_shares * strike)
concentration_pct = (position_value / net_worth * 100) if net_worth > 0 else 0
if concentration_pct < 10:
    risk_color = "green"; risk_text = "Low concentration"
elif concentration_pct < 20:
    risk_color = "orange"; risk_text = "Moderate concentration"
else:
    risk_color = "red"; risk_text = "High concentration — consider diversifying"

vesting_concentration = (vesting_gross / net_worth * 100) if net_worth > 0 else 0

# ====================== RESULTS ======================
st.subheader("📊 Your Results")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Price", f"${price:,.2f}")
c2.metric("Total Gross Value", f"${gross_value:,.0f}")
c3.metric("**Net After-Tax**", f"${net_value:,.0f}")
c4.metric("Est. Tax on Next Vesting", f"${vesting_tax:,.0f}")

st.info(f"**Tax Note**: {tax_note}")
st.info(f"**Recommendation**: {recommendation}")

st.subheader("⚠️ Concentration Risk")
st.markdown(f"**Full Position**: <span style='color:{risk_color}; font-weight:bold'>{concentration_pct:.1f}%</span> of your investable assets", unsafe_allow_html=True)
st.progress(concentration_pct / 100)
if vesting_concentration > 5:
    st.warning(f"⚠️ Next vesting could add ~{vesting_concentration:.1f}% concentration impact.")
st.markdown(f"**Risk Level**: <span style='color:{risk_color}'>{risk_text}</span>", unsafe_allow_html=True)

# Growth Chart
st.subheader("What if the stock price grows in the next year?")
growth_rates = [0.0, 0.05, 0.10, 0.15, 0.20]
future_net_values = []
for rate in growth_rates:
    fp = price * (1 + rate)
    if option_type == "RSU":
        future_net_values.append(fp * total_shares * (1 - federal_tax_rate/100))
    else:
        fi = max(0, fp - strike) * total_shares
        future_net_values.append(fi * (1 - federal_tax_rate/100) + total_shares * strike)

fig = go.Figure()
fig.add_trace(go.Bar(x=[f"{int(r*100)}%" for r in growth_rates], y=future_net_values, marker_color="#00cc96"))
fig.update_layout(title="Projected Net After-Tax Value in 1 Year", xaxis_title="Annual Growth Rate", yaxis_title="Net Value ($)", template="plotly_white", height=400)
st.plotly_chart(fig, use_container_width=True)

# ====================== PDF DOWNLOAD (only after email) ======================
if "lead_captured" in st.session_state:
    if st.button("📄 Download My Professional PDF Report"):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 18)
        p.drawString(50, 750, f"Exec Comp Optimizer Report — {date.today().strftime('%B %d, %Y')}")
        p.setFont("Helvetica", 12)
        y = 700
        p.drawString(50, y, f"Executive: {st.session_state['user_name']}")
        p.drawString(50, y-20, f"Company Ticker: {ticker}")
        p.drawString(50, y-40, f"Type: {option_type} • Total Shares: {total_shares:,}")
        p.drawString(50, y-60, f"Current Price: ${price:,.2f} → Gross Value: ${gross_value:,.0f}")
        p.drawString(50, y-80, f"Net After-Tax Value: ${net_value:,.0f}")
        p.drawString(50, y-100, f"Est. Tax on Next Vesting ({shares_vesting:,} shares): ${vesting_tax:,.0f}")
        p.drawString(50, y-120, f"Concentration Risk: {concentration_pct:.1f}% ({risk_text})")
        p.drawString(50, y-160, "Recommendation:")
        p.drawString(70, y-180, recommendation[:200] + "..." if len(recommendation) > 200 else recommendation)
        p.drawString(50, y-220, "Next Steps:")
        p.drawString(70, y-240, "• Consider a post-vesting sell-to-cover or diversification plan")
        p.drawString(70, y-260, "• Review with your CPA for AMT / long-term capital gains strategy")
        p.drawString(50, y-300, "Ready to optimize your executive compensation plan?")
        p.drawString(70, y-320, "Book a 30-minute strategy call with Forecast Capital Management")
        p.drawString(70, y-340, "→ https://calendly.com/forecastcap (or reply to this report)")
        p.save()
        buffer.seek(0)
        st.download_button(
            label="⬇️ Download PDF Now",
            data=buffer,
            file_name=f"Exec_Comp_Report_{ticker}.pdf",
            mime="application/pdf"
        )

st.caption("⚠️ Illustrative only. Not financial, tax, or investment advice.")
