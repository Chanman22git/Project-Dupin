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
from agents.base import AgentError
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
from components.guidance import render_page_guide, render_tab_guide

inject_custom_css()

session_id = st.session_state.get("selected_session_id")
if not session_id:
    st.warning("No investigation selected.")
    if st.button("Go to Case Board"):
        st.switch_page("pages/1_Home.py")
    st.stop()

session = DiscoverySessionDB.get(session_id)
if not session:
    st.error("Investigation not found.")
    st.stop()

product_ctx = ProductContextDB.get(session["product_context_id"])

# ── Header ──
col_name, col_back = st.columns([4, 1])
with col_name:
    new_name = st.text_input(
        "Investigation Name", value=session["name"], key=f"session_name_{session_id}",
        label_visibility="collapsed",
    )
    if new_name != session["name"]:
        DiscoverySessionDB.update(session_id, name=new_name)
        session["name"] = new_name
with col_back:
    if st.button("< Back to Case", use_container_width=True):
        st.session_state["selected_context_id"] = session["product_context_id"]
        st.switch_page("pages/2_Product_Context.py")

render_page_guide(
    "Investigation — Focused Research Session",
    "An <strong>Investigation</strong> is a scoped research effort within a case. "
    "Define what you want to learn, configure how Dupin interviews users, "
    "issue <strong>Summons</strong> (shareable links) to invite participants, and review transcripts."
)

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
    render_metric_card("link", "Summons Sent", len(links), "#C4823A")
with mc2:
    render_metric_card("users", "Awaiting", active_links, "#5C7A6E")
with mc3:
    render_metric_card("chat", "Interviews", len(conversations), "#E8B87A")
with mc4:
    render_metric_card("check", "Concluded", completed_convs, "#8C8878")

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# ── Tabs ──
tab_config, tab_links, tab_interviews, tab_clues = st.tabs(
    ["Investigation Plan", "Interview Summons", "Interview Transcripts", "Clues"]
)

# ═══════════════════════════════════════════════
# Investigation Plan Tab
# ═══════════════════════════════════════════════
with tab_config:
    render_tab_guide("Set the objective, scope, and target personas. Configure how Dupin conducts interviews — depth, focus, and boundaries.")
    render_section_header("target", "Investigation Details")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        render_info_field("Objective", session.get("objective"))
        render_info_field("Scope", session.get("scope"))
    with col_d2:
        personas = session.get("target_personas", [])
        if personas:
            st.markdown(
                '<div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.06em; '
                'color:#B8B4A8; margin-bottom:0.5rem;">Persons of Interest</div>',
                unsafe_allow_html=True,
            )
            for p in personas:
                if isinstance(p, dict):
                    render_persona_card(p.get("name", "Unknown"), p.get("description", ""))
                else:
                    render_persona_card(str(p))
        else:
            render_info_field("Persons of Interest", "")

    st.divider()

    col_controls, col_chat = st.columns([1, 1], gap="large")

    behavior = session.get("agent_behavior", {})
    if isinstance(behavior, str):
        behavior = json.loads(behavior)

    with col_controls:
        render_section_header("settings", "Interrogation Style")

        research_depth = st.select_slider(
            "Interrogation Depth",
            options=["listener", "balanced", "deep_researcher"],
            value=behavior.get("research_depth", "balanced"),
            key=f"rd_{session_id}",
            help="How deeply Dupin probes during interviews",
        )

        clarification_mode = st.radio(
            "Contradiction Handling",
            options=["realtime", "balanced", "flagged"],
            index=["realtime", "balanced", "flagged"].index(
                behavior.get("clarification_mode", "balanced")
            ),
            key=f"cm_{session_id}",
            horizontal=True,
            help="How Dupin handles contradictions across interviews",
        )

        max_q_val = behavior.get("max_questions") or 0
        max_questions = st.number_input(
            "Max Questions (0 = no limit)",
            min_value=0, max_value=50, value=max_q_val,
            key=f"mq_{session_id}",
        )

        focus_areas_str = st.text_input(
            "Lines of Inquiry (comma-separated)",
            value=", ".join(behavior.get("focus_areas", [])),
            key=f"fa_{session_id}",
        )

        avoid_areas_str = st.text_input(
            "Off-Limits Topics (comma-separated)",
            value=", ".join(behavior.get("avoid_areas", [])),
            key=f"aa_{session_id}",
        )

        if st.button("Save Settings", type="primary", key=f"save_beh_{session_id}",
                      use_container_width=True):
            new_behavior = {
                "research_depth": research_depth,
                "clarification_mode": clarification_mode,
                "max_questions": max_questions if max_questions > 0 else None,
                "focus_areas": [a.strip() for a in focus_areas_str.split(",") if a.strip()],
                "avoid_areas": [a.strip() for a in avoid_areas_str.split(",") if a.strip()],
            }
            DiscoverySessionDB.update(session_id, agent_behavior=new_behavior)
            st.success("Investigation settings saved.")
            st.rerun()

    with col_chat:
        render_section_header("chat", "Dupin Assistant")

        chat_key = f"pm_session_chat_{session_id}"
        if chat_key not in st.session_state:
            saved = session.get("context_conversation_history", [])
            if isinstance(saved, str):
                saved = json.loads(saved) if saved else []
            st.session_state[chat_key] = saved

        def session_agent_callback(messages):
            try:
                raw = get_session_agent_response(messages, session, product_ctx or {})
            except (AgentError, Exception) as e:
                return f"I'm having a brief connection issue. Please try again. ({type(e).__name__})"
            should_save, clean = detect_save(raw, SESSION_SAVE_MARKER)

            if should_save:
                with st.spinner("Filing investigation plan..."):
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
            placeholder="Define objectives, persons of interest, or say 'save this'...",
            initial_assistant_message=(
                "Let's plan this investigation. What are we trying to uncover? "
                "Who are the persons of interest we should interview? "
                "What specific areas should Dupin focus on?"
            ),
        )

    # Section C: Status Management
    st.divider()
    render_section_header("layers", "Investigation Status")

    col_s1, col_s2, col_s3, _ = st.columns([1, 1, 1, 3])
    current_status = session.get("status", "draft")
    with col_s1:
        if current_status == "draft":
            if st.button("Begin Investigation", type="primary", use_container_width=True):
                if not session.get("objective"):
                    st.error("Set an objective before beginning.")
                else:
                    DiscoverySessionDB.update(session_id, status="active")
                    st.rerun()
    with col_s2:
        if current_status == "active":
            if st.button("Close Investigation", use_container_width=True):
                DiscoverySessionDB.update(session_id, status="completed")
                st.rerun()
    with col_s3:
        if current_status != "draft":
            if st.button("Reopen", use_container_width=True):
                DiscoverySessionDB.update(session_id, status="draft")
                st.rerun()

# ═══════════════════════════════════════════════
# Interview Summons Tab
# ═══════════════════════════════════════════════
with tab_links:
    render_tab_guide("Generate unique, expiring links for each user you want to interview. Share the link — they'll chat with Dupin directly.")
    render_section_header("link", "Interview Summons")

    if session.get("status") != "active":
        st.warning("Begin the investigation before sending interview summons.")
    else:
        with st.form("generate_link"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                user_name = st.text_input("Witness Name")
                user_role = st.text_input("Role / Title")
            with col_f2:
                user_department = st.text_input("Department (optional)")
                expiry_hours = st.number_input(
                    "Link Expiry (hours)", min_value=1, max_value=720,
                    value=DEFAULT_LINK_EXPIRY_HOURS,
                )
            submitted = st.form_submit_button("Send Summons", type="primary",
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
                st.success(f"Summons issued for {user_name}")
                st.code(f"{BASE_URL}?page=chat&token={link['token']}")
                st.rerun()

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    if not links:
        render_empty_state("link", "No summons issued yet",
                           "Issue summons above to invite witnesses for interviews.")
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
                            <span style="color:#B8B4A8; font-size:0.8rem; margin-left:0.75rem;">
                                {icon("clock", 12, "#B8B4A8")} Expires: {link['expires_at'][:16]}
                            </span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with col3:
                    url = f"{BASE_URL}?page=chat&token={link['token']}"
                    st.code(url, language=None)

# ═══════════════════════════════════════════════
# Interview Transcripts Tab
# ═══════════════════════════════════════════════
with tab_interviews:
    render_tab_guide("Full transcripts of each user interview. Click to expand and review what Dupin uncovered.")
    render_section_header("chat", "Interview Transcripts")

    if not conversations:
        render_empty_state("chat", "No interviews conducted yet",
                           "Issue summons and wait for witnesses to respond.")
    else:
        for conv in conversations:
            messages = conv.get("messages", [])
            msg_count = len(messages)

            with st.expander(
                f"{conv['started_at'][:16]}  |  {msg_count} exchanges  |  {conv['status']}"
            ):
                for msg in messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                if conv.get("user_summary"):
                    st.divider()
                    render_section_header("document", "Deposition Summary")
                    st.markdown(conv["user_summary"])

# ═══════════════════════════════════════════════
# Clues Tab
# ═══════════════════════════════════════════════
with tab_clues:
    render_tab_guide("Synthesized insights extracted from interviews — pain points, user journeys, expectations, and contradictions.")

    # Load existing analysis data
    from database.models import InsightDB, DiscrepancyDB, UserJourneyDB, ExpectationDB
    from agents.analysis_agent import analyze_session
    from components.insight_cards import (
        render_analysis_summary,
        render_insight_card,
        render_discrepancy_card,
        render_journey_card,
        render_expectation_card,
    )

    existing_insights = InsightDB.list_by_session(session_id)
    existing_discrepancies = DiscrepancyDB.list_by_session(session_id)
    existing_journeys = UserJourneyDB.list_by_session(session_id)
    existing_expectations = ExpectationDB.list_by_session(session_id)

    completed_count = sum(1 for c in conversations if c.get("status") == "completed")
    has_results = existing_insights or existing_discrepancies or existing_journeys or existing_expectations

    # Analyze button
    col_hdr, col_btn = st.columns([3, 1])
    with col_hdr:
        render_section_header("lightbulb", "Clues & Evidence")
    with col_btn:
        if completed_count > 0:
            if st.button("Analyze Interviews", type="primary", use_container_width=True,
                         key="analyze_btn"):
                with st.status("Dupin is analyzing the transcripts...", expanded=True) as status:
                    st.write("Reading interview transcripts...")
                    st.write(f"Analyzing {completed_count} completed interview(s)...")
                    counts = analyze_session(session_id)
                    if "error" in counts:
                        st.error(counts["error"])
                    else:
                        st.write("Extracting clues and evidence...")
                        status.update(label="Analysis complete!", state="complete")
                        st.rerun()

    if not has_results and completed_count == 0:
        render_empty_state(
            "lightbulb",
            "No interviews to analyze yet",
            "Complete some interviews first, then click 'Analyze Interviews'.",
        )
    elif not has_results and completed_count > 0:
        render_empty_state(
            "magnifier",
            f"{completed_count} interview(s) ready for analysis",
            "Click 'Analyze Interviews' above to let Dupin extract the clues.",
        )
    else:
        # Show summary
        render_analysis_summary({
            "insights": len(existing_insights),
            "discrepancies": len(existing_discrepancies),
            "journeys": len(existing_journeys),
            "expectations": len(existing_expectations),
        })

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # Sub-tabs for different types
        clue_tabs = st.tabs(["Pain Points & Insights", "Journeys", "Expectations", "Contradictions"])

        with clue_tabs[0]:
            if existing_insights:
                for ins in existing_insights:
                    render_insight_card(ins)
            else:
                render_empty_state("lightbulb", "No insights extracted yet")

        with clue_tabs[1]:
            if existing_journeys:
                for j in existing_journeys:
                    render_journey_card(j)
            else:
                render_empty_state("target", "No journeys mapped yet")

        with clue_tabs[2]:
            if existing_expectations:
                for exp in existing_expectations:
                    render_expectation_card(exp)
            else:
                render_empty_state("users", "No expectations captured yet")

        with clue_tabs[3]:
            if existing_discrepancies:
                for d in existing_discrepancies:
                    render_discrepancy_card(d)
            else:
                render_empty_state("warning", "No contradictions found")
