# app.py
import streamlit as st
import requests

# Page config
st.set_page_config(page_title="InvoiceBot Launcher")

# Title and description
st.title("🧾 Invoice Processing Bot")
st.write("""
Click the button below to start your unattended Invoice Processing workflow
in UiPath Orchestrator.
""")

# Load configuration from .streamlit/secrets.toml
orchestrator_url = st.secrets["uipath"]["url"]
tenant_name      = st.secrets["uipath"]["tenant"]
folder_id        = st.secrets["uipath"]["folder_id"]
slug             = st.secrets["uipath"]["slug"]
bearer_token     = st.secrets["uipath"]["bearer_token"]

# Construct the full trigger URL
trigger_url = (
    f"{orchestrator_url}"
    f"/{tenant_name}"
    "/orchestrator_/t/"
    f"{folder_id}"
    f"/{slug}"
)

# Prepare headers for the POST request
headers = {
    "Authorization":             f"Bearer {bearer_token}",
    "Content-Type":              "application/json",
    "X-UIPATH-TenantName":       tenant_name,
    "X-UIPATH-OrganizationUnitId": folder_id
}

# Function to execute the trigger
def run_trigger():
    try:
        response = requests.post(trigger_url, json={}, headers=headers, timeout=10)
        response.raise_for_status()
        st.success(f"✅ Started successfully! HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to trigger: {e}")

# Button to fire the trigger
if st.button("Run InvoiceBot"):
    with st.spinner("Triggering bot…"):
        run_trigger()
