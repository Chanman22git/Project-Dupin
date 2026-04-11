from __future__ import annotations
import json
import streamlit as st
from datetime import datetime, timezone
from database.models import (
    UserSessionLinkDB,
    ConversationDB,
    DiscoverySessionDB,
    ProductContextDB,
)
from agents.base import AgentError
from agents.user_agent import (
    get_user_agent_response,
    extract_summary_from_response,
    infer_state_from_messages,
    clean_messages_for_display,
)
from components.chat_ui import render_chat
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

# ── Token Validation ──
token = st.query_params.get("token")

if not token:
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem;">
        <div style="opacity:0.15; margin-bottom:1.5rem;">
            {icon("link", 80, "#C4823A")}
        </div>
        <h2 style="color:#3D3D35;">No Session Link Provided</h2>
        <p style="color:#B8B4A8; max-width:400px; margin:0 auto; line-height:1.6;">
            Please use the link shared by your product manager to access this conversation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

link = UserSessionLinkDB.get_by_token(token)

if not link:
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem;">
        <div style="opacity:0.15; margin-bottom:1.5rem;">
            {icon("warning", 80, "#A64B2A")}
        </div>
        <h2 style="color:#3D3D35;">Invalid Link</h2>
        <p style="color:#B8B4A8; max-width:400px; margin:0 auto; line-height:1.6;">
            This session link is not valid. Please contact your product manager for a new link.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Expiry Check ──
if link["status"] == "expired" or (
    link["expires_at"]
    and datetime.fromisoformat(link["expires_at"]) < datetime.now(timezone.utc)
):
    if link["status"] != "expired":
        UserSessionLinkDB.update_status(link["id"], "expired")
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem;">
        <div style="opacity:0.15; margin-bottom:1.5rem;">
            {icon("clock", 80, "#E8B87A")}
        </div>
        <h2 style="color:#3D3D35;">Link Expired</h2>
        <p style="color:#B8B4A8; max-width:400px; margin:0 auto; line-height:1.6;">
            This session link has expired. Please contact your product manager for a new link.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Completion Check ──
if link["status"] == "completed":
    st.markdown(f"""
    <div style="text-align:center; padding:4rem 2rem;">
        <div style="opacity:0.15; margin-bottom:1.5rem;">
            {icon("check", 80, "#5C7A6E")}
        </div>
        <h2 style="color:#3D3D35;">Conversation Complete</h2>
        <p style="color:#B8B4A8; max-width:400px; margin:0 auto; line-height:1.6;">
            Thank you for your participation! Your feedback has been recorded.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Load Session Context ──
session = DiscoverySessionDB.get(link["discovery_session_id"])
if not session:
    st.error("Session configuration not found.")
    st.stop()

product_ctx = ProductContextDB.get(session["product_context_id"])
product_name = product_ctx.get("name", "our product") if product_ctx else "our product"

# ── Branded Header ──
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #E8E3D8 0%, #F0EDE6 100%);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid #D0CAC0;
">
    <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.5rem;">
        {icon("chat", 28, "#C4823A")}
        <h2 style="margin:0 !important; padding:0 !important; font-size:1.5rem !important;">
            Interview Session
        </h2>
    </div>
    <p style="color:#8C8878; margin:0; font-size:0.95rem; line-height:1.5;">
        Welcome, <strong>{link['user_name']}</strong>. This is a brief, confidential conversation about your
        experience with <strong>{product_name}</strong>. Our AI assistant will ask about your workflows,
        challenges, and expectations. Your feedback directly shapes the product.
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# Conversation Init / Resume
# ═══════════════════════════════════════════════
link_id = link["id"]
state_key = f"user_conversation_state_{link_id}"
conv_id_key = f"user_conversation_id_{link_id}"
chat_key = f"user_chat_messages_{link_id}"
complete_key = f"user_chat_complete_{link_id}"

if conv_id_key not in st.session_state:
    existing_conv = ConversationDB.get_by_link(link_id)

    if existing_conv and existing_conv["status"] == "in_progress":
        # Resume existing conversation
        st.session_state[conv_id_key] = existing_conv["id"]
        saved_messages = existing_conv.get("messages", [])
        if isinstance(saved_messages, str):
            saved_messages = json.loads(saved_messages) if saved_messages else []
        st.session_state[state_key] = infer_state_from_messages(saved_messages)
        st.session_state[chat_key] = clean_messages_for_display(saved_messages)

    elif existing_conv and existing_conv["status"] == "completed":
        st.session_state[complete_key] = True

    else:
        # Create new conversation
        new_conv = ConversationDB.create(link_id, link["discovery_session_id"])
        st.session_state[conv_id_key] = new_conv["id"]
        st.session_state[chat_key] = []
        st.session_state[state_key] = "GREETING"

# ═══════════════════════════════════════════════
# Render Chat or Completion
# ═══════════════════════════════════════════════
if st.session_state.get(complete_key):
    st.markdown(f"""
    <div style="text-align:center; padding:3rem 2rem;">
        <div style="opacity:0.15; margin-bottom:1.5rem;">
            {icon("check", 80, "#5C7A6E")}
        </div>
        <h2 style="color:#3D3D35;">Conversation Complete</h2>
        <p style="color:#B8B4A8; max-width:400px; margin:0 auto; line-height:1.6;">
            Thank you for your participation! Your feedback has been recorded.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Build greeting
    greeting = (
        f"Hi {link['user_name']}! I'm here to learn about your experience with "
        f"{product_name}. This conversation is confidential and will help the team "
        f"improve the product.\n\n"
        f"Let's start \u2014 could you tell me a bit about your role and how you "
        f"interact with {product_name}?"
    )

    # Save greeting to DB on first load
    greeting_saved_key = f"greeting_saved_{link_id}"
    if not st.session_state.get(greeting_saved_key) and conv_id_key in st.session_state:
        # Only save if conversation is new (no messages yet)
        conv = ConversationDB.get(st.session_state[conv_id_key])
        if conv and not conv.get("messages"):
            ConversationDB.add_message(
                st.session_state[conv_id_key],
                "assistant",
                f"{greeting}\n[STATE:GREETING]",
            )
        st.session_state[greeting_saved_key] = True

    # Agent callback
    def user_agent_callback(messages):
        conv_id = st.session_state[conv_id_key]
        current_state = st.session_state.get(state_key, "GREETING")

        # Persist the user's message to DB
        user_msg = messages[-1]
        ConversationDB.add_message(conv_id, "user", user_msg["content"])

        # Get agent response
        try:
            clean_response, new_state, is_complete = get_user_agent_response(
                messages=messages,
                product_context=product_ctx or {},
                session=session,
                link=link,
                conversation_state=current_state,
            )
        except (AgentError, Exception) as e:
            return "I'm having a brief connection issue. Could you try sending that again?"

        # Persist assistant response WITH state marker to DB for state recovery
        db_content = f"{clean_response}\n[STATE:{new_state}]"
        if is_complete:
            db_content = f"{clean_response}\n[CONVERSATION_COMPLETE]\n[STATE:{new_state}]"
        ConversationDB.add_message(conv_id, "assistant", db_content)

        # Update state
        st.session_state[state_key] = new_state

        # Handle completion
        if is_complete:
            summary = extract_summary_from_response(clean_response)
            ConversationDB.complete(conv_id, user_summary=summary)
            UserSessionLinkDB.update_status(link_id, "completed")
            st.session_state[complete_key] = True

        return clean_response

    render_chat(
        session_key=chat_key,
        agent_callback=user_agent_callback,
        placeholder="Type your response...",
        initial_assistant_message=greeting,
        enable_file_upload=False,
    )
