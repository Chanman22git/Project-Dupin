from __future__ import annotations
import streamlit as st
from datetime import datetime, timezone
from database.models import UserSessionLinkDB, ConversationDB, DiscoverySessionDB, ProductContextDB
from components.styles import inject_custom_css
from components.graphics import icon

inject_custom_css()

# Hide sidebar for user-facing page
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
    .stApp > header { display: none; }
</style>
""", unsafe_allow_html=True)

# Get token from query params
token = st.query_params.get("token")

if not token:
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem;">
        <div style="opacity:0.15; margin-bottom:1.5rem;">
            {icon("link", 80, "#8B7355")}
        </div>
        <h2 style="color:#3D3529;">No Session Link Provided</h2>
        <p style="color:#A89F91; max-width:400px; margin:0 auto; line-height:1.6;">
            Please use the link shared by your product manager to access this conversation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Validate token
link = UserSessionLinkDB.get_by_token(token)

if not link:
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem;">
        <div style="opacity:0.15; margin-bottom:1.5rem;">
            {icon("warning", 80, "#C27C6E")}
        </div>
        <h2 style="color:#3D3529;">Invalid Link</h2>
        <p style="color:#A89F91; max-width:400px; margin:0 auto; line-height:1.6;">
            This session link is not valid. Please contact your product manager for a new link.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Check expiry
if link["status"] == "expired" or (
    link["expires_at"]
    and datetime.fromisoformat(link["expires_at"]) < datetime.now(timezone.utc)
):
    if link["status"] != "expired":
        UserSessionLinkDB.update_status(link["id"], "expired")
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem;">
        <div style="opacity:0.15; margin-bottom:1.5rem;">
            {icon("clock", 80, "#D4A056")}
        </div>
        <h2 style="color:#3D3529;">Link Expired</h2>
        <p style="color:#A89F91; max-width:400px; margin:0 auto; line-height:1.6;">
            This session link has expired. Please contact your product manager for a new link.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Check if completed
if link["status"] == "completed":
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem;">
        <div style="opacity:0.15; margin-bottom:1.5rem;">
            {icon("check", 80, "#7A9E7E")}
        </div>
        <h2 style="color:#3D3529;">Conversation Complete</h2>
        <p style="color:#A89F91; max-width:400px; margin:0 auto; line-height:1.6;">
            Thank you for your participation! Your feedback has been recorded.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Load session context
session = DiscoverySessionDB.get(link["discovery_session_id"])
if not session:
    st.error("Session configuration not found.")
    st.stop()

product_ctx = ProductContextDB.get(session["product_context_id"])
product_name = product_ctx.get("name", "our product") if product_ctx else "our product"

# ── Branded Header ──
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #F2EDE8 0%, #FAFAF8 100%);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid #E8E0D8;
">
    <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.5rem;">
        {icon("chat", 28, "#8B7355")}
        <h2 style="margin:0 !important; padding:0 !important; font-size:1.5rem !important;">
            Discovery Conversation
        </h2>
    </div>
    <p style="color:#6B6156; margin:0; font-size:0.95rem; line-height:1.5;">
        Welcome, <strong>{link['user_name']}</strong>. We'd love to learn about your experience
        with {product_name}. This conversation is confidential and will help us improve the product.
    </p>
</div>
""", unsafe_allow_html=True)

st.info("The conversational agent will be implemented in Phase 3. For now, this is a placeholder.")
