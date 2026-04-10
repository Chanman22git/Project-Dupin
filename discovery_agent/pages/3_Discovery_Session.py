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
from components.styles import inject_custom_css
from components.graphics import (
    render_section_header,
    render_info_field,
    render_status_flow,
    render_metric_card,
    render_persona_card,
    render_empty_state,
    render_status_pill,
    icon,
)
from config import BASE_URL, DEFAULT_LINK_EXPIRY_HOURS

inject_custom_css()

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

# ── Header ──
col_name, col_back = st.columns([4, 1])
with col_name:
    new_name = st.text_input(
        "Session Name", value=session["name"], key=f"session_name_{session_id}",
        label_visibility="collapsed",
    )
    if new_name != session["name"]:
        DiscoverySessionDB.update(session_id, name=new_name)
        session["name"] = new_name
with col_back:
    if st.button("< Back to Context", use_container_width=True):
        st.session_state["selected_context_id"] = session["product_context_id"]
        st.switch_page("pages/2_Product_Context.py")

# ── Status Flow ──
render_status_flow(session.get("status", "draft"))

# ── Metrics Row ──
UserSessionLinkDB.expire_old_links()
links = UserSessionLinkDB.list_by_session(session_id)
conversations = ConversationDB.list_by_session(session_id)
active_links = sum(1 for l in links if l["status"] == "active")
completed_convs = sum(1 for c in conversations if c["status"] == "completed")

mc1, mc2, mc3, mc4 = st.columns(4)
with mc1:
    render_metric_card("link", "Total Links", len(links), "#8B7355")
with mc2:
    render_metric_card("users", "Active Links", active_links, "#7A9E7E")
with mc3:
    render_metric_card("chat", "Conversations", len(conversations), "#C4956A")
with mc4:
    render_metric_card("check", "Completed", completed_convs, "#6B8EAE")

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# ── Tabs ──
tab_config, tab_links, tab_conversations, tab_insights = st.tabs(
    ["Configuration", "User Links", "Conversations", "Insights"]
)

# ═══════════════════════════════════════════════
# Configuration Tab
# ═══════════════════════════════════════════════
with tab_config:
    # Section A: Session details
    render_section_header("target", "Session Details")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        render_info_field("Objective", session.get("objective"))
        render_info_field("Scope", session.get("scope"))
    with col_d2:
        personas = session.get("target_personas", [])
        if personas:
            st.markdown(
                '<div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.06em; '
                'color:#A89F91; margin-bottom:0.5rem;">Target Personas</div>',
                unsafe_allow_html=True,
            )
            for p in personas:
                if isinstance(p, dict):
                    render_persona_card(p.get("name", "Unknown"), p.get("description", ""))
                else:
                    render_persona_card(str(p))
        else:
            render_info_field("Target Personas", "")

    st.divider()

    # Section B: Behavior controls + Chat
    col_controls, col_chat = st.columns([1, 1], gap="large")

    behavior = session.get("agent_behavior", {})
    if isinstance(behavior, str):
        behavior = json.loads(behavior)

    with col_controls:
        render_section_header("settings", "Agent Behavior")

        research_depth = st.select_slider(
            "Research Depth",
            options=["listener", "balanced", "deep_researcher"],
            value=behavior.get("research_depth", "balanced"),
            key=f"rd_{session_id}",
            help="How deeply the agent probes during conversations",
        )

        clarification_mode = st.radio(
            "Clarification Mode",
            options=["realtime", "balanced", "flagged"],
            index=["realtime", "balanced", "flagged"].index(
                behavior.get("clarification_mode", "balanced")
            ),
            key=f"cm_{session_id}",
            horizontal=True,
            help="How the agent handles contradictions with prior insights",
        )

        max_q_val = behavior.get("max_questions") or 0
        max_questions = st.number_input(
            "Max Questions (0 = no limit)",
            min_value=0, max_value=50, value=max_q_val,
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

        if st.button("Save Behavior Settings", type="primary", key=f"save_beh_{session_id}",
                      use_container_width=True):
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
        render_section_header("chat", "Setup Assistant")

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
                    full_messages = messages + [{"role": "assistant", "content": clean}]
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
    render_section_header("layers", "Session Status")

    col_s1, col_s2, col_s3, _ = st.columns([1, 1, 1, 3])
    current_status = session.get("status", "draft")
    with col_s1:
        if current_status == "draft":
            if st.button("Activate Session", type="primary", use_container_width=True):
                if not session.get("objective"):
                    st.error("Set an objective before activating.")
                else:
                    DiscoverySessionDB.update(session_id, status="active")
                    st.rerun()
    with col_s2:
        if current_status == "active":
            if st.button("Complete Session", use_container_width=True):
                DiscoverySessionDB.update(session_id, status="completed")
                st.rerun()
    with col_s3:
        if current_status != "draft":
            if st.button("Reset to Draft", use_container_width=True):
                DiscoverySessionDB.update(session_id, status="draft")
                st.rerun()

# ═══════════════════════════════════════════════
# User Links Tab
# ═══════════════════════════════════════════════
with tab_links:
    render_section_header("link", "User Interview Links")

    if session.get("status") != "active":
        st.warning("Activate the session before generating user links.")
    else:
        with st.form("generate_link"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                user_name = st.text_input("User Name")
                user_role = st.text_input("User Role")
            with col_f2:
                user_department = st.text_input("Department (optional)")
                expiry_hours = st.number_input(
                    "Link Expiry (hours)", min_value=1, max_value=720,
                    value=DEFAULT_LINK_EXPIRY_HOURS,
                )
            submitted = st.form_submit_button("Generate Link", type="primary",
                                               use_container_width=True)
            if submitted and user_name:
                expires_at = (
                    datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
                ).isoformat()
                link = UserSessionLinkDB.create(
                    discovery_session_id=session_id,
                    user_name=user_name, user_role=user_role,
                    user_department=user_department, expires_at=expires_at,
                )
                st.success(f"Link generated for {user_name}")
                st.code(f"{BASE_URL}?page=chat&token={link['token']}")
                st.rerun()

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    if not links:
        render_empty_state("link", "No links generated yet",
                           "Generate links above to invite users for interviews.")
    else:
        for link in links:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    render_persona_card(
                        link["user_name"],
                        link.get("user_role", ""),
                        link.get("user_department", ""),
                    )
                with col2:
                    st.markdown(
                        f"""<div style="margin-top:0.5rem;">
                            {render_status_pill(link['status'])}
                            <span style="color:#A89F91; font-size:0.8rem; margin-left:0.75rem;">
                                {icon("clock", 12, "#A89F91")} Expires: {link['expires_at'][:16]}
                            </span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with col3:
                    url = f"{BASE_URL}?page=chat&token={link['token']}"
                    st.code(url, language=None)

# ═══════════════════════════════════════════════
# Conversations Tab
# ═══════════════════════════════════════════════
with tab_conversations:
    render_section_header("chat", "Conversations")

    if not conversations:
        render_empty_state("chat", "No conversations yet",
                           "Share user links to start collecting insights.")
    else:
        for conv in conversations:
            messages = conv.get("messages", [])
            msg_count = len(messages)
            status_html = render_status_pill(conv["status"])

            with st.expander(
                f"{conv['started_at'][:16]}  |  {msg_count} messages  |  {conv['status']}"
            ):
                for msg in messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                if conv.get("user_summary"):
                    st.divider()
                    render_section_header("document", "Summary")
                    st.markdown(conv["user_summary"])

# ═══════════════════════════════════════════════
# Insights Tab
# ═══════════════════════════════════════════════
with tab_insights:
    render_section_header("lightbulb", "Insights")
    render_empty_state(
        "lightbulb",
        "Insights will appear here after analysis",
        "Complete user conversations, then generate insights (Phase 4).",
    )
