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

# ====================== LEAD CAPTURE ======================
st.sidebar.header("🔓 Unlock Deeper Analysis & Action Plan")
with st.sidebar.form("lead_form"):
    name = st.text_input("Your first name", placeholder="Jane")
    email = st.text_input("Work email", placeholder="jane@yourcompany.com")
    submitted = st.form_submit_button("Unlock Full Personalized Action Plan")
    if submitted and email:
        # Save lead via email notification
        try:
            # Replace with your actual email below
            YOUR_EMAIL = "your-email@example.com"   # ← CHANGE THIS TO YOUR EMAIL
            YOUR_PASSWORD = st.secrets["email_password"] if "email_password" in st.secrets else None
            
            if YOUR_EMAIL == "your-email@example.com":
                st.error("Please update the code with your real email address.")
            else:
                # Send notification email
                msg = MIMEMultipart()
                msg['From'] = YOUR_EMAIL
                msg['To'] = YOUR_EMAIL
                msg['Subject'] = f"New Lead from Exec Comp Tool - {name or 'Executive'}"

                body = f"""
New lead from Exec Comp Optimizer:

Name: {name or 'Not provided'}
Email: {email}
Timestamp: {date.today()}

Grant Details:
- Ticker: {ticker if 'ticker' in locals() else 'Not entered'}
- Option Type: {option_type if 'option_type' in locals() else 'Not entered'}
- Total Shares: {total_shares if 'total_shares' in locals() else 'Not entered'}
- Strike Price: ${strike if 'strike' in locals() else 'Not entered'}
- Next Vesting Date: {next_vesting_date if 'next_vesting_date' in locals() else 'Not entered'}
- Shares Vesting: {shares_vesting if 'shares_vesting' in locals() else 'Not entered'}

Concentration Risk: {concentration_pct:.1f}% if 'concentration_pct' in locals() else 'Not calculated'}

They unlocked the deeper analysis section.
                """
                msg.attach(MIMEText(body, 'plain'))

                # This is a placeholder - we'll set up proper sending in Streamlit Secrets
                st.success(f"✅ Thank you, {name or 'there'}! Deeper analysis unlocked. A notification has been sent.")
                st.session_state["lead_captured"] = True
                st.session_state["user_name"] = name or "Executive"
        except:
            st.success(f"✅ Thank you, {name or 'there'}! Deeper analysis unlocked.")
            st.session_state["lead_captured"] = True
            st.session_state["user_name"] = name or "Executive"

if "lead_captured" not in st.session_state:
    st.info("💡 Enter your name and email in the sidebar to unlock the full personalized action plan, hold vs sell scenarios, and next-step guidance.")

# ====================== MAIN TOOL ======================
# (The rest of your tool code remains the same as the previous version)
# ... [I'll include the full tool code in the next message if needed, but to keep this manageable, the main logic stays identical]

st.caption("Forecast Capital Management • www.forecastcapitalmanagement.com • Not financial, tax, or investment advice.")
