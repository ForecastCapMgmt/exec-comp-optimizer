import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(
    page_title="Exec Comp Optimizer | Forecast Capital Management",
    layout="centered",
    page_icon="🚀"
)

# ====================== DESIGN SYSTEM: NQDC-MATCHED AESTHETIC ======================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@300;400;500&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet">

<style>
:root {
  --navy:        #0c1824;
  --navy-mid:    #142035;
  --navy-light:  #1b2d47;
  --navy-border: #243858;
  --gold:        #c9a84c;
  --gold-light:  #e4c97a;
  --gold-dim:    rgba(201,168,76,0.15);
  --cream:       #f2ede6;
  --cream-dim:   #7a8fa8;
  --green:       #4caf7d;
  --red:         #e05c5c;
  --yellow:      #f0b429;
  --font-display: 'Playfair Display', Georgia, serif;
  --font-mono:   'IBM Plex Mono', 'Courier New', monospace;
  --font-sans:   'DM Sans', system-ui, sans-serif;
}

/* ── Global background & text ── */
.stApp, .stApp > header, .main, .block-container {
  background-color: var(--navy) !important;
  color: var(--cream) !important;
  font-family: var(--font-sans) !important;
}
.block-container { padding-top: 0 !important; max-width: 800px; }

/* ── Site header bar ── */
.site-header {
  border-bottom: 1px solid var(--navy-border);
  padding: 1.25rem 0 1.25rem 0;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo-name {
  font-family: var(--font-display);
  font-size: 1.05rem;
  color: var(--gold);
  letter-spacing: 0.02em;
  line-height: 1.2;
}
.logo-sub {
  font-family: var(--font-sans);
  font-size: 0.68rem;
  font-weight: 300;
  color: var(--cream-dim);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.header-pill {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--cream-dim);
  border: 1px solid var(--navy-border);
  padding: 0.3rem 0.7rem;
  border-radius: 2px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* ── Hero section ── */
.hero { padding: 2.5rem 0 2rem; border-bottom: 1px solid var(--navy-border); margin-bottom: 2rem; }
.eyebrow {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--gold);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  margin-bottom: 0.8rem;
}
.hero h1 {
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3.5vw, 2.75rem);
  font-weight: 600;
  line-height: 1.2;
  margin-bottom: 0.75rem;
  color: var(--cream);
}
.hero h1 em { color: var(--gold); font-style: italic; }
.hero p { font-size: 0.9rem; color: var(--cream-dim); max-width: 580px; }

/* ── Section labels ── */
.section-label {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  color: var(--gold);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--navy-border);
}

/* ── Streamlit headings override ── */
h1, h2, h3 {
  font-family: var(--font-display) !important;
  color: var(--cream) !important;
}
h2, h3 { color: var(--cream) !important; font-size: 1.15rem !important; font-weight: 600 !important; }

/* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox select {
  background-color: var(--navy-mid) !important;
  border: 1px solid var(--navy-border) !important;
  border-radius: 3px !important;
  color: var(--cream) !important;
  font-family: var(--font-sans) !important;
  font-size: 0.875rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 2px var(--gold-dim) !important;
}
.stTextInput label, .stNumberInput label, .stDateInput label,
.stSelectbox label, .stSlider label {
  font-family: var(--font-mono) !important;
  font-size: 0.65rem !important;
  color: var(--cream-dim) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
  background-color: var(--navy-mid) !important;
  border: 1px solid var(--navy-border) !important;
  color: var(--cream) !important;
  border-radius: 3px !important;
}

/* ── Slider ── */
.stSlider > div > div > div > div { background-color: var(--gold) !important; }
.stSlider > div > div > div { background-color: var(--navy-border) !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
  background-color: var(--navy-mid) !important;
  border: 1px solid var(--navy-border) !important;
  border-radius: 4px !important;
  padding: 1rem !important;
}
[data-testid="metric-container"] label {
  font-family: var(--font-mono) !important;
  font-size: 0.6rem !important;
  color: var(--cream-dim) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: var(--font-display) !important;
  font-size: 1.6rem !important;
  color: var(--gold) !important;
  font-weight: 600 !important;
}

/* ── Info / warning / success boxes ── */
.stAlert {
  background-color: var(--navy-mid) !important;
  border: 1px solid var(--navy-border) !important;
  border-radius: 3px !important;
  color: var(--cream) !important;
  font-family: var(--font-sans) !important;
  font-size: 0.85rem !important;
}
.stAlert [data-testid="stMarkdownContainer"] p { color: var(--cream) !important; }

/* ── Success box override ── */
div[data-baseweb="notification"] {
  background-color: rgba(76,175,125,0.12) !important;
  border: 1px solid var(--green) !important;
  border-radius: 3px !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div { background-color: var(--gold) !important; }
.stProgress > div > div > div { background-color: var(--navy-border) !important; border-radius: 2px !important; }

/* ── Buttons ── */
.stButton > button, .stLinkButton > a {
  background-color: transparent !important;
  border: 1px solid var(--gold) !important;
  color: var(--gold) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.7rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
  border-radius: 2px !important;
  padding: 0.5rem 1.25rem !important;
  transition: background 0.2s, color 0.2s !important;
}
.stButton > button:hover, .stLinkButton > a:hover {
  background-color: var(--gold) !important;
  color: var(--navy) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background-color: var(--navy-mid) !important;
  border-right: 1px solid var(--navy-border) !important;
}
section[data-testid="stSidebar"] * { color: var(--cream) !important; }
section[data-testid="stSidebar"] label {
  font-family: var(--font-mono) !important;
  font-size: 0.65rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
  color: var(--cream-dim) !important;
}
section[data-testid="stSidebar"] input {
  background-color: var(--navy-light) !important;
  border: 1px solid var(--navy-border) !important;
  color: var(--cream) !important;
  border-radius: 3px !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
  font-family: var(--font-display) !important;
  color: var(--gold) !important;
}

/* ── Caption / footer ── */
.stCaption, footer { color: var(--cream-dim) !important; font-size: 0.75rem !important; }

/* ── Divider ── */
hr { border-color: var(--navy-border) !important; }

/* ── Hide default Streamlit branding ── */
#MainMenu, footer[data-testid="stFooter"], header[data-testid="stHeader"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ====================== HEADER ======================
st.markdown("""
<div class="site-header">
  <div>
    <div class="logo-name">Forecast Capital Management</div>
    <div class="logo-sub">Executive Financial Planning</div>
  </div>
  <div class="header-pill">Exec Comp Optimizer</div>
</div>
""", unsafe_allow_html=True)

# ====================== HERO ======================
st.markdown("""
<div class="hero">
  <div class="eyebrow">Compensation Planning &middot; Equity</div>
  <h1>You know what your equity is worth.<br><em>Do you know what you'll actually keep?</em></h1>
  <p>Model your RSUs or stock options in 60 seconds — net after-tax value, concentration risk,
  and the real cost of your next vesting event.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:var(--navy-mid);border:1px solid var(--navy-border);border-radius:3px;
  padding:0.85rem 1rem;margin-bottom:0.75rem;font-size:0.82rem;color:var(--cream-dim);">
  <span style="color:var(--gold);font-family:var(--font-mono);font-size:0.65rem;
  text-transform:uppercase;letter-spacing:0.1em;">Note</span><br>
  Illustrative calculations only. State taxes may apply. Always consult your CPA or financial advisor.
</div>
""", unsafe_allow_html=True)

# ====================== LEAD CAPTURE ======================
st.sidebar.markdown("""
<div style="font-family:var(--font-display);font-size:1.1rem;color:var(--gold);
margin-bottom:0.5rem;">Unlock Deeper Analysis</div>
<div style="font-size:0.8rem;color:var(--cream-dim);margin-bottom:1rem;">
Enter your details to unlock the full personalized action plan, hold vs sell scenarios,
and next-step guidance.</div>
""", unsafe_allow_html=True)

with st.sidebar.form("lead_form"):
    name = st.text_input("Your first name", placeholder="Jane")
    email_input = st.text_input("Work email", placeholder="jane@yourcompany.com")
    submitted = st.form_submit_button("Unlock Full Action Plan")

    if submitted and email_input:
        try:
            sender_email = st.secrets["sender_email"]
            sender_password = st.secrets["sender_password"]
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = sender_email
            msg['Subject'] = f"New Exec Comp Lead - {name or 'Executive'}"
            body = f"""
New lead from Exec Comp Optimizer Tool:
Name: {name or 'Not provided'}
Email: {email_input}
Timestamp: {date.today()}
"""
            msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
        except Exception:
            pass
        st.success(f"✅ Thank you, {name or 'there'}! Deeper analysis unlocked.")
        st.session_state["lead_captured"] = True
        st.session_state["user_name"] = name or "Executive"

if "lead_captured" not in st.session_state:
    st.markdown("""
    <div style="background:var(--gold-dim);border:1px solid rgba(201,168,76,0.3);border-radius:3px;
      padding:0.85rem 1rem;margin-bottom:1.5rem;font-size:0.82rem;color:var(--cream-dim);">
      <span style="color:var(--gold);font-family:var(--font-mono);font-size:0.65rem;
      text-transform:uppercase;letter-spacing:0.1em;">Unlock</span><br>
      Enter your name and email in the sidebar to unlock the full personalized action plan,
      hold vs sell scenarios, and next-step guidance.
    </div>
    """, unsafe_allow_html=True)

# ====================== GRANT DETAILS ======================
st.markdown('<div class="section-label">Grant Details</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Stock Ticker Symbol (e.g. AAPL)", value="AAPL").upper().strip()
    total_shares = st.number_input("Total Shares / Options in Grant", min_value=100, value=5000, step=100)
    option_type = st.selectbox("Type of Compensation", ["RSU", "NSO", "ISO"])
with col2:
    strike = st.number_input("Strike Price per Share ($)", min_value=0.0, value=45.0, step=0.01)
    federal_tax_rate = st.slider("Estimated Marginal Federal Tax Rate (%)", 22, 37, 32)

amt_rate = 0
if option_type == "ISO":
    amt_rate = st.slider("Estimated AMT Rate (%)", 0, 28, 26)

st.markdown('<div class="section-label" style="margin-top:1.5rem;">Vesting Information</div>', unsafe_allow_html=True)
col_v1, col_v2 = st.columns(2)
with col_v1:
    next_vesting_date = st.date_input("Next Major Vesting Date", value=date(2026, 6, 1), min_value=date.today())
with col_v2:
    shares_vesting = st.number_input("Number of Shares Vesting on That Date", min_value=0, value=1250, step=100)

st.markdown('<div class="section-label" style="margin-top:1.5rem;">Concentration Risk Assessment</div>', unsafe_allow_html=True)
net_worth = st.number_input(
    "Rough estimate of your total investable assets (excluding primary home) ($)",
    min_value=100000, value=2000000, step=100000, format="%d"
)

# ====================== LIVE PRICE ======================
price = None
if ticker:
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        st.markdown(f"""
        <div style="background:rgba(76,175,125,0.1);border:1px solid rgba(76,175,125,0.35);
          border-radius:3px;padding:0.7rem 1rem;margin:0.75rem 0;
          font-family:var(--font-mono);font-size:0.78rem;color:#4caf7d;">
          ✓ &nbsp; Current {ticker} price: ${price:,.2f}
        </div>
        """, unsafe_allow_html=True)
    except:
        price = st.number_input("Manual current fair market value ($)", value=150.0, step=0.01)

if not price:
    price = 150.0

# ====================== CALCULATIONS ======================
gross_value = price * total_shares
intrinsic_value = max(0, price - strike) * total_shares
vesting_gross = price * shares_vesting
vesting_intrinsic = max(0, price - strike) * shares_vesting

if option_type == "RSU":
    vesting_tax = vesting_gross * (federal_tax_rate / 100)
    net_value = gross_value * (1 - federal_tax_rate / 100)
    tax_note = f"RSU: Est. tax on next vesting ≈ ${vesting_tax:,.0f}"
    base_rec = "RSUs are taxed as ordinary income upon vesting."
else:
    vesting_tax = vesting_intrinsic * (federal_tax_rate / 100) if option_type == "NSO" else vesting_intrinsic * (amt_rate / 100)
    net_value = (intrinsic_value * (1 - federal_tax_rate / 100)) + (total_shares * strike) if option_type != "ISO" else (vesting_intrinsic - vesting_tax) + (total_shares * strike)
    tax_note = f"ISO: Est. AMT on next vesting spread ≈ ${vesting_tax:,.0f}" if option_type == "ISO" else f"NSO: Est. tax on next vesting spread ≈ ${vesting_tax:,.0f}"
    base_rec = "ISOs offer long-term capital gains potential if held properly." if option_type == "ISO" else "NSOs trigger ordinary income tax on the bargain element when exercised."

days_to_vesting = (next_vesting_date - date.today()).days
months_to_vesting = max(0, days_to_vesting // 30)
if months_to_vesting <= 3:
    timing_advice = f"With {shares_vesting:,} shares vesting in the next {months_to_vesting} months, plan for the immediate tax impact."
elif months_to_vesting <= 12:
    timing_advice = f"{shares_vesting:,} shares vesting in about {months_to_vesting} months gives you planning time."
else:
    timing_advice = "Vesting is further out — good opportunity to model scenarios."

recommendation = f"{base_rec} {timing_advice}"

position_value = gross_value if option_type == "RSU" else (intrinsic_value + total_shares * strike)
concentration_pct = (position_value / net_worth * 100) if net_worth > 0 else 0
vesting_concentration = (vesting_gross / net_worth * 100) if net_worth > 0 else 0

if concentration_pct < 10:
    risk_color = "#4caf7d"
    risk_text = "Low"
elif concentration_pct < 20:
    risk_color = "#f0b429"
    risk_text = "Moderate"
else:
    risk_color = "#e05c5c"
    risk_text = "High — consider diversifying"

# ====================== RESULTS ======================
st.markdown('<div class="section-label" style="margin-top:2rem;">Your Results</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Price", f"${price:,.2f}")
c2.metric("Total Gross Value", f"${gross_value:,.0f}")
c3.metric("Net After-Tax Value", f"${net_value:,.0f}")
c4.metric("Est. Tax on Next Vesting", f"${vesting_tax:,.0f}")

st.markdown(f"""
<div style="background:var(--navy-mid);border:1px solid var(--navy-border);border-radius:3px;
  padding:0.85rem 1rem;margin:0.75rem 0;font-size:0.83rem;">
  <span style="font-family:var(--font-mono);font-size:0.6rem;color:var(--gold);
  text-transform:uppercase;letter-spacing:0.1em;">Tax Note</span><br>
  <span style="color:var(--cream-dim);">{tax_note}</span>
</div>
<div style="background:var(--navy-mid);border:1px solid var(--navy-border);border-radius:3px;
  padding:0.85rem 1rem;margin:0.75rem 0;font-size:0.83rem;">
  <span style="font-family:var(--font-mono);font-size:0.6rem;color:var(--gold);
  text-transform:uppercase;letter-spacing:0.1em;">Recommendation</span><br>
  <span style="color:var(--cream-dim);">{recommendation}</span>
</div>
""", unsafe_allow_html=True)

# Concentration
st.markdown('<div class="section-label" style="margin-top:1.5rem;">Concentration Risk</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="margin-bottom:0.5rem;font-size:0.88rem;">
  Full Position: <span style="color:{risk_color};font-family:var(--font-mono);
  font-weight:500;">{concentration_pct:.1f}%</span>
  <span style="color:var(--cream-dim);"> of investable assets</span>
</div>
""", unsafe_allow_html=True)
st.progress(min(concentration_pct / 100, 1.0))

if vesting_concentration > 5:
    st.markdown(f"""
    <div style="background:rgba(240,180,41,0.1);border:1px solid rgba(240,180,41,0.3);
      border-radius:3px;padding:0.7rem 1rem;margin:0.5rem 0;
      font-family:var(--font-mono);font-size:0.75rem;color:var(--yellow);">
      ⚠ &nbsp; Next vesting could add ~{vesting_concentration:.1f}% concentration.
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div style="font-size:0.85rem;margin-top:0.5rem;">
  Risk Level: <span style="color:{risk_color};font-family:var(--font-mono);">{risk_text}</span>
</div>
""", unsafe_allow_html=True)

# ====================== GROWTH CHART ======================
st.markdown('<div class="section-label" style="margin-top:2rem;">What if the stock price grows in the next year?</div>', unsafe_allow_html=True)

growth_rates = [0.0, 0.05, 0.10, 0.15, 0.20]
future_net = []
for rate in growth_rates:
    fp = price * (1 + rate)
    if option_type == "RSU":
        future_net.append(fp * total_shares * (1 - federal_tax_rate / 100))
    else:
        fi = max(0, fp - strike) * total_shares
        future_net.append(fi * (1 - federal_tax_rate / 100) + total_shares * strike)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=[f"{int(r * 100)}%" for r in growth_rates],
    y=future_net,
    marker_color="#c9a84c",
    marker_line_color="#e4c97a",
    marker_line_width=1,
))
fig.update_layout(
    xaxis_title="Annual Growth Rate",
    yaxis_title="Net After-Tax Value ($)",
    paper_bgcolor="#0c1824",
    plot_bgcolor="#142035",
    font=dict(family="DM Sans, sans-serif", color="#f2ede6", size=12),
    xaxis=dict(gridcolor="#243858", tickfont=dict(color="#7a8fa8")),
    yaxis=dict(gridcolor="#243858", tickfont=dict(color="#7a8fa8")),
    height=380,
    margin=dict(l=20, r=20, t=20, b=40),
)
st.plotly_chart(fig, use_container_width=True)

# ====================== DEEPER ANALYSIS ======================
if "lead_captured" in st.session_state:
    st.markdown('<div class="section-label" style="margin-top:2rem;">Deeper Personalized Analysis</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p style="font-size:0.88rem;color:var(--cream-dim);margin-bottom:1rem;">
    Hi <strong style="color:var(--cream);">{st.session_state['user_name']}</strong>,
    here's more detailed guidance based on your situation:
    </p>
    """, unsafe_allow_html=True)

    sell_after_tax = vesting_gross * (1 - federal_tax_rate / 100) if option_type == "RSU" else (vesting_intrinsic * (1 - federal_tax_rate / 100))
    hold_value = vesting_gross if option_type == "RSU" else vesting_intrinsic + shares_vesting * strike

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Sell Immediately After Vesting (est. after tax)", f"${sell_after_tax:,.0f}")
    with col_b:
        st.metric("Hold the Vested Shares", f"${hold_value:,.0f}")

    post_vesting_conc = ((position_value + vesting_gross) / net_worth * 100) if net_worth > 0 else 0
    st.metric("Projected Post-Vesting Concentration", f"{post_vesting_conc:.1f}%")

    st.markdown("""
    <div style="margin-top:1.25rem;margin-bottom:0.75rem;font-family:var(--font-mono);
      font-size:0.65rem;color:var(--gold);text-transform:uppercase;letter-spacing:0.1em;">
      Recommended Next Steps
    </div>
    """, unsafe_allow_html=True)

    steps = [
        "Review these numbers with your CPA before the vesting date",
        "Consider a sell-to-cover strategy to pay taxes without selling all shares",
        "Evaluate diversification options if concentration exceeds 15%",
        "Model different scenarios if you have multiple grants",
    ]
    for step in steps:
        st.markdown(f"""
        <div style="padding:0.6rem 0;border-bottom:1px solid var(--navy-border);
          font-size:0.85rem;color:var(--cream-dim);">
          <span style="color:var(--gold);margin-right:0.5rem;">→</span>{step}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.link_button("Book a Strategy Call", "https://www.forecastcapitalmanagement.com/contact", use_container_width=True)
    with col_btn2:
        st.link_button("Visit Our Website", "https://www.forecastcapitalmanagement.com", use_container_width=True)

else:
    st.markdown("""
    <div style="background:var(--gold-dim);border:1px solid rgba(201,168,76,0.3);border-radius:3px;
      padding:0.85rem 1rem;margin-top:1.5rem;font-size:0.82rem;color:var(--cream-dim);">
      <span style="color:var(--gold);font-family:var(--font-mono);font-size:0.65rem;
      text-transform:uppercase;letter-spacing:0.1em;">Unlock</span><br>
      Enter your details in the sidebar to unlock the deeper analysis section.
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--navy-border);
  font-family:var(--font-mono);font-size:0.62rem;color:var(--cream-dim);
  text-transform:uppercase;letter-spacing:0.08em;">
  Forecast Capital Management &nbsp;·&nbsp; forecastcapitalmanagement.com
  &nbsp;·&nbsp; Not financial, tax, or investment advice.
</div>
""", unsafe_allow_html=True)
