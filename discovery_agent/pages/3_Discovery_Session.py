from __future__ import annotations
import json
import streamlit as st
from datetime import datetime, timedelta, timezone
from database.models import (
    DiscoverySessionDB,
    ProductContextDB,
    UserSessionLinkDB,
    ConversationDB,
)
from agents.pm_agent import (
    get_session_agent_response,
    detect_save,
    extract_session_config,
    SESSION_SAVE_MARKER,
)
from components.chat_ui import render_chat
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

product_ctx = ProductContextDB.get(session["product_context_id"])

# --- Editable name ---
new_name = st.text_input("Session Name", value=session["name"], key=f"session_name_{session_id}")
if new_name != session["name"]:
    DiscoverySessionDB.update(session_id, name=new_name)
    session["name"] = new_name

# Back link
if st.button("< Back to Product Context", type="secondary"):
    st.session_state["selected_context_id"] = session["product_context_id"]
    st.switch_page("pages/2_Product_Context.py")

# --- Tabs ---
tab_config, tab_links, tab_conversations, tab_insights = st.tabs(
    ["Configuration", "User Links", "Conversations", "Insights"]
)

# ═══════════════════════════════════════════════
# Configuration Tab
# ═══════════════════════════════════════════════
with tab_config:
    # Section A: Session details
    st.subheader("Session Details")
    col_detail1, col_detail2 = st.columns(2)
    with col_detail1:
        st.write(f"**Objective:** {session.get('objective') or '_Not set_'}")
        st.write(f"**Scope:** {session.get('scope') or '_Not set_'}")
    with col_detail2:
        status_badge = {"draft": "Draft", "active": "Active", "completed": "Completed"}
        st.write(f"**Status:** {status_badge.get(session['status'], session['status'])}")
        personas = session.get("target_personas", [])
        if personas:
            if isinstance(personas[0], dict):
                persona_names = ", ".join(p.get("name", str(p)) for p in personas)
            else:
                persona_names = ", ".join(str(p) for p in personas)
            st.write(f"**Personas:** {persona_names}")
        else:
            st.write("**Personas:** _Not set_")

    st.divider()

    # Section B: Behavior controls + Chat
    col_controls, col_chat = st.columns([1, 1])

    behavior = session.get("agent_behavior", {})
    if isinstance(behavior, str):
        behavior = json.loads(behavior)

    with col_controls:
        st.subheader("Agent Behavior")

        research_depth = st.select_slider(
            "Research Depth",
            options=["listener", "balanced", "deep_researcher"],
            value=behavior.get("research_depth", "balanced"),
            key=f"rd_{session_id}",
        )

        clarification_mode = st.radio(
            "Clarification Mode",
            options=["realtime", "balanced", "flagged"],
            index=["realtime", "balanced", "flagged"].index(
                behavior.get("clarification_mode", "balanced")
            ),
            key=f"cm_{session_id}",
            horizontal=True,
        )

        max_q_val = behavior.get("max_questions") or 0
        max_questions = st.number_input(
            "Max Questions (0 = no limit)",
            min_value=0,
            max_value=50,
            value=max_q_val,
            key=f"mq_{session_id}",
        )

        focus_areas_str = st.text_input(
            "Focus Areas (comma-separated)",
            value=", ".join(behavior.get("focus_areas", [])),
            key=f"fa_{session_id}",
        )

        avoid_areas_str = st.text_input(
            "Avoid Areas (comma-separated)",
            value=", ".join(behavior.get("avoid_areas", [])),
            key=f"aa_{session_id}",
        )

        if st.button("Save Behavior Settings", type="primary", key=f"save_behavior_{session_id}"):
            new_behavior = {
                "research_depth": research_depth,
                "clarification_mode": clarification_mode,
                "max_questions": max_questions if max_questions > 0 else None,
                "focus_areas": [a.strip() for a in focus_areas_str.split(",") if a.strip()],
                "avoid_areas": [a.strip() for a in avoid_areas_str.split(",") if a.strip()],
            }
            DiscoverySessionDB.update(session_id, agent_behavior=new_behavior)
            st.success("Behavior settings saved.")
            st.rerun()

    with col_chat:
        st.subheader("Setup Assistant")

        chat_key = f"pm_session_chat_{session_id}"
        if chat_key not in st.session_state:
            saved = session.get("context_conversation_history", [])
            if isinstance(saved, str):
                saved = json.loads(saved) if saved else []
            st.session_state[chat_key] = saved

        def session_agent_callback(messages):
            raw = get_session_agent_response(messages, session, product_ctx or {})
            should_save, clean = detect_save(raw, SESSION_SAVE_MARKER)

            if should_save:
                with st.spinner("Saving session config..."):
                    full_messages = messages + [
                        {"role": "assistant", "content": clean}
                    ]
                    extracted = extract_session_config(full_messages)

                    update_kwargs = {}
                    for field in ["objective", "scope", "name"]:
                        val = extracted.get(field)
                        if val and val != "null":
                            update_kwargs[field] = val

                    personas_val = extracted.get("target_personas")
                    if personas_val:
                        update_kwargs["target_personas"] = personas_val

                    behavior_val = extracted.get("agent_behavior")
                    if behavior_val and isinstance(behavior_val, dict):
                        merged = {**behavior}
                        for k, v in behavior_val.items():
                            if v is not None:
                                merged[k] = v
                        update_kwargs["agent_behavior"] = merged

                    update_kwargs["context_conversation_history"] = (
                        st.session_state[chat_key]
                        + [{"role": "assistant", "content": clean}]
                    )
                    DiscoverySessionDB.update(session_id, **update_kwargs)

            return clean

        render_chat(
            session_key=chat_key,
            agent_callback=session_agent_callback,
            placeholder="Define objectives, personas, scope, or say 'save this'...",
            initial_assistant_message=(
                "Hi! Let's configure this discovery session. "
                "What do you want to learn? Who should we interview? "
                "What specific features or scenarios should we focus on?"
            ),
        )

    # Section C: Status Management
    st.divider()
    st.subheader("Session Status")
    current_status = session.get("status", "draft")

    col_s1, col_s2, col_s3, _ = st.columns([1, 1, 1, 3])
    with col_s1:
        if current_status == "draft":
            if st.button("Activate Session", type="primary"):
                if not session.get("objective"):
                    st.error("Set an objective before activating (use the chat or save session config).")
                else:
                    DiscoverySessionDB.update(session_id, status="active")
                    st.rerun()
    with col_s2:
        if current_status == "active":
            if st.button("Complete Session"):
                DiscoverySessionDB.update(session_id, status="completed")
                st.rerun()
    with col_s3:
        if current_status != "draft":
            if st.button("Reset to Draft"):
                DiscoverySessionDB.update(session_id, status="draft")
                st.rerun()

# ═══════════════════════════════════════════════
# User Links Tab
# ═══════════════════════════════════════════════
with tab_links:
    st.subheader("Generate User Links")

    UserSessionLinkDB.expire_old_links()

    if session.get("status") != "active":
        st.warning("Activate the session before generating user links.")
    else:
        with st.form("generate_link"):
            user_name = st.text_input("User Name")
            user_role = st.text_input("User Role")
            user_department = st.text_input("Department (optional)")
            expiry_hours = st.number_input(
                "Link Expiry (hours)", min_value=1, max_value=720,
                value=DEFAULT_LINK_EXPIRY_HOURS,
            )
            submitted = st.form_submit_button("Generate Link", type="primary")

            if submitted and user_name:
                expires_at = (
                    datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
                ).isoformat()
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
            status_icon = {"active": "🟢", "expired": "🔴", "completed": "✅"}.get(
                link["status"], "⚪"
            )
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{status_icon} **{link['user_name']}** ({link['user_role']})")
                    st.caption(f"Status: {link['status']} | Expires: {link['expires_at'][:16]}")
                with col2:
                    url = f"{BASE_URL}?page=chat&token={link['token']}"
                    st.code(url, language=None)

# ═══════════════════════════════════════════════
# Conversations Tab
# ═══════════════════════════════════════════════
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

# ═══════════════════════════════════════════════
# Insights Tab
# ═══════════════════════════════════════════════
with tab_insights:
    st.subheader("Insights")
    st.caption("Insight generation will be implemented in Phase 4.")
    st.info("Complete some user conversations first, then generate insights.")
