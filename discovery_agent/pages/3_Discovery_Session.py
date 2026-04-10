import streamlit as st
from datetime import datetime, timedelta, timezone
from database.models import DiscoverySessionDB, UserSessionLinkDB, ConversationDB
from config import BASE_URL, DEFAULT_LINK_EXPIRY_HOURS

session_id = st.session_state.get("selected_session_id")
if not session_id:
    st.warning("No discovery session selected.")
    if st.button("Go to Home"):
        st.switch_page("pages/1_Home.py")
    st.stop()

session = DiscoverySessionDB.get(session_id)
if not session:
    st.error("Discovery session not found.")
    st.stop()

st.title(session["name"])

# --- Tabs ---
tab_config, tab_links, tab_conversations, tab_insights = st.tabs(
    ["Configuration", "User Links", "Conversations", "Insights"]
)

with tab_config:
    st.subheader("Session Details")
    st.write(f"**Objective:** {session.get('objective') or '_Not set_'}")
    st.write(f"**Scope:** {session.get('scope') or '_Not set_'}")
    st.write(f"**Status:** {session.get('status', 'draft')}")

    st.subheader("Agent Behavior")
    behavior = session.get("agent_behavior", {})
    if isinstance(behavior, str):
        import json
        behavior = json.loads(behavior)

    st.write(f"- Research Depth: **{behavior.get('research_depth', 'balanced')}**")
    st.write(f"- Clarification Mode: **{behavior.get('clarification_mode', 'balanced')}**")
    st.write(f"- Max Questions: **{behavior.get('max_questions') or 'No limit'}**")
    st.write(f"- Focus Areas: {', '.join(behavior.get('focus_areas', [])) or '_None_'}")
    st.write(f"- Avoid Areas: {', '.join(behavior.get('avoid_areas', [])) or '_None_'}")

    st.divider()
    st.caption("Conversational session setup and behavior configuration UI will be implemented in Phase 2.")

with tab_links:
    st.subheader("Generate User Links")

    # Expire old links first
    UserSessionLinkDB.expire_old_links()

    with st.form("generate_link"):
        user_name = st.text_input("User Name")
        user_role = st.text_input("User Role")
        user_department = st.text_input("Department (optional)")
        expiry_hours = st.number_input("Link Expiry (hours)", min_value=1, max_value=720,
                                       value=DEFAULT_LINK_EXPIRY_HOURS)
        submitted = st.form_submit_button("Generate Link", type="primary")

        if submitted and user_name:
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=expiry_hours)).isoformat()
            link = UserSessionLinkDB.create(
                discovery_session_id=session_id,
                user_name=user_name,
                user_role=user_role,
                user_department=user_department,
                expires_at=expires_at,
            )
            st.success(f"Link generated for {user_name}")
            st.code(f"{BASE_URL}?page=chat&token={link['token']}")
            st.rerun()

    st.divider()
    st.subheader("Existing Links")
    links = UserSessionLinkDB.list_by_session(session_id)
    if not links:
        st.info("No links generated yet.")
    else:
        for link in links:
            status_icon = {"active": "🟢", "expired": "🔴", "completed": "✅"}.get(link["status"], "⚪")
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{status_icon} **{link['user_name']}** ({link['user_role']})")
                    st.caption(f"Status: {link['status']} | Expires: {link['expires_at'][:16]}")
                with col2:
                    url = f"{BASE_URL}?page=chat&token={link['token']}"
                    st.code(url, language=None)

with tab_conversations:
    st.subheader("Conversations")
    conversations = ConversationDB.list_by_session(session_id)
    if not conversations:
        st.info("No conversations yet. Share user links to start collecting insights.")
    else:
        for conv in conversations:
            messages = conv.get("messages", [])
            with st.expander(
                f"Conversation ({conv['status']}) - {len(messages)} messages - {conv['started_at'][:16]}"
            ):
                for msg in messages:
                    role_label = "Agent" if msg["role"] == "assistant" else "User"
                    st.markdown(f"**{role_label}:** {msg['content']}")
                if conv.get("user_summary"):
                    st.divider()
                    st.markdown(f"**Summary:** {conv['user_summary']}")

with tab_insights:
    st.subheader("Insights")
    st.caption("Insight generation will be implemented in Phase 4.")
    st.info("Complete some user conversations first, then generate insights.")
