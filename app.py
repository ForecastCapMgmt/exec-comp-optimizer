import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Exec Comp Optimizer | Forecast Capital Management", layout="centered", page_icon="🚀")

st.title("🚀 Exec Comp Optimizer")
st.markdown("### Stock Options & RSU Decision Tool by **Forecast Capital Management**")

st.info("💡 This tool provides illustrative calculations. State taxes may apply depending on your residence. Always consult your CPA or financial advisor.")

# ====================== LEAD CAPTURE WITH EMAIL NOTIFICATION ======================
st.sidebar.header("🔓 Unlock Deeper Analysis & Action Plan")
with st.sidebar.form("lead_form"):
    name = st.text_input("Your first name", placeholder="Jane")
    email_input = st.text_input("Work email", placeholder="jane@yourcompany.com")
    submitted = st.form_submit_button("Unlock Full Personalized Action Plan")
    
    if submitted and email_input:
        try:
            sender_email = st.secrets["sender_email"]
            sender_password = st.secrets["sender_password"]

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = sender_email
            msg['Subject'] = f"New Exec Comp Lead - {name or 'Executive'}"

            # Fixed email body
            body = f"""
New lead from Exec Comp Optimizer Tool:

Name: {name or 'Not provided'}
Email: {email_input}
Timestamp: {date.today()}

Grant Details:
- Ticker: {ticker if 'ticker' in locals() else 'Not entered'}
- Option Type: {option_type if 'option_type' in locals() else 'Not entered'}
- Total Shares: {total_shares if 'total_shares' in locals() else 'Not entered'}
- Strike Price: ${strike if 'strike' in locals() else 'Not entered'}
- Next Vesting Date: {next_vesting_date if 'next_vesting_date' in locals() else 'Not entered'}
- Shares Vesting: {shares_vesting if 'shares_vesting' in locals() else 'Not entered'}
"""

            # Add concentration line safely
            if 'concentration_pct' in locals():
                body += f"Concentration Risk: {concentration_pct:.1f}%\n"
            else:
                body += "Concentration Risk: Not calculated\n"

            body += "\nThey unlocked the deeper analysis section."

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            st.success(f"✅ Thank you, {name or 'there'}! Deeper analysis unlocked. Notification sent.")
            st.session_state["lead_captured"] = True
            st.session_state["user_name"] = name or "Executive"

        except Exception as e:
            st.success(f"✅ Thank you, {name or 'there'}! Deeper analysis unlocked.")
            st.session_state["lead_captured"] = True
            st.session_state["user_name"] = name or "Executive"

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

if not
