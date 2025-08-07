# app.py
import streamlit as st
import requests
import time

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Invoice Bot Launcher",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---- CUSTOM CSS ----
st.markdown(
    """
    <style>
    .header {
        font-size: 36px;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .description {
        font-size: 18px;
        margin-bottom: 1.5rem;
        color: #555;
    }
    .trigger-btn {
        background-color: #4a90e2;
        color: white !important;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- SECRETS & CONFIG ----
AUTH_URL      = "https://account.uipath.com/oauth/token"
CLIENT_ID     = st.secrets["uipath"]["client_id"]
CLIENT_SECRET = st.secrets["uipath"]["client_secret"]
ORCH_URL      = st.secrets["uipath"]["url"]
TENANT        = st.secrets["uipath"]["tenant"]
FOLDER_ID     = st.secrets["uipath"]["folder_id"]
SLUG          = st.secrets["uipath"]["slug"]

# Build trigger URL
TRIGGER_URL = f"{ORCH_URL}/{TENANT}/orchestrator_/t/{FOLDER_ID}/{SLUG}"

@st.experimental_singleton
def get_token_info():
    resp = requests.post(
        AUTH_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "OR.Jobs.ReadWrite"
        }
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "access_token": data["access_token"],
        "expires_at": time.time() + data["expires_in"] - 30
    }

# ---- AUTH UTILITY ----

def fetch_token():
    token_info = get_token_info()
    if time.time() >= token_info["expires_at"]:
        get_token_info.clear()
        token_info = get_token_info()
    return token_info["access_token"]

# ---- LAYOUT ----
st.markdown('<div class="header">Invoice Processing Bot Launcher</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Click the button below to trigger UiPath Invoice Processing workflow.</div>', unsafe_allow_html=True)

# Add image or logo if desired
# st.image("logo.png", width=120)

# Center the button using columns
a, b, c = st.columns([1, 2, 1])
with b:
    if st.button("Run InvoiceBot", key="trigger", help="Start your unattended automation", css_class="trigger-btn"):
        with st.spinner("Authenticating & triggering…"):
            try:
                token = fetch_token()
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "X-UIPATH-TenantName": TENANT,
                    "X-UIPATH-OrganizationUnitId": FOLDER_ID
                }
                response = requests.post(TRIGGER_URL, json={}, headers=headers, timeout=10)
                response.raise_for_status()
                st.success(f"Bot started! (HTTP {response.status_code})")
            except Exception as ex:
                st.error(f"Error: {ex}")
