# app.py
import streamlit as st
import requests

st.set_page_config(page_title="InvoiceBot Launcher")

st.title("🧾 Invoice Processing Bot")

st.write(
    """
    Click the button below to start your unattended Invoice Processing workflow
    in UiPath Orchestrator.
    """
)

# 1) CONFIG: pull these values from .streamlit/secrets.toml
orchestrator_url = st.secrets["uipath"]["url"]
tenant_name      = st.secrets["uipath"]["tenant"]
folder_id        = st.secrets["uipath"]["folder_id"]
slug             = st.secrets["uipath"]["slug"]
bearer_token     = st.secrets["uipath"]["bearer_token"]

trigger_url = f"{orchestrator_url}/{tenant_name}/orchestrator_/t/{folder_id}/{slug}"

headers = {
    "Authorization":           f"Bearer {bearer_token}",
    "Content-Type":            "application/json",
    "X-UIPATH-TenantName":     tenant_name,
    "X-UIPATH-OrganizationUnitId": folder_id
}

if st.button("▶️ Run InvoiceBot"):
    with st.spinner("Triggering bot…"):
        try:
            resp = requests.post(trigger_url, json={}, headers=headers, timeout=10)
            resp.raise_for_status()
            st.success(f"Started successfully! HTTP {resp.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to trigger: {e}")

