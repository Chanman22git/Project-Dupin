import streamlit as st
from datetime import datetime, timezone
from database.models import UserSessionLinkDB, ConversationDB, DiscoverySessionDB

# Hide sidebar for user-facing page
st.markdown(
    """<style>[data-testid="stSidebar"] {display: none;}</style>""",
    unsafe_allow_html=True,
)

# Get token from query params
token = st.query_params.get("token")

if not token:
    st.error("No session token provided. Please use the link shared by your product manager.")
    st.stop()

# Validate token
link = UserSessionLinkDB.get_by_token(token)

if not link:
    st.error("Invalid session link. Please contact your product manager for a valid link.")
    st.stop()

# Check expiry
if link["status"] == "expired" or (
    link["expires_at"] and datetime.fromisoformat(link["expires_at"]) < datetime.now(timezone.utc)
):
    if link["status"] != "expired":
        UserSessionLinkDB.update_status(link["id"], "expired")
    st.warning("This session link has expired. Please contact your product manager for a new link.")
    st.stop()

# Check if completed
if link["status"] == "completed":
    st.success("This conversation has been completed. Thank you for your participation!")
    st.stop()

# Load session context
session = DiscoverySessionDB.get(link["discovery_session_id"])
if not session:
    st.error("Session configuration not found.")
    st.stop()

st.title("Discovery Conversation")
st.caption(f"Welcome, {link['user_name']}. This conversation will help us understand your experience.")

st.divider()
st.info("The conversational agent will be implemented in Phase 3. For now, this is a placeholder.")
