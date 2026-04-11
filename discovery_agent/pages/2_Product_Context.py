from __future__ import annotations
import json
import streamlit as st
from database.models import ProductContextDB, DiscoverySessionDB, ContextImprovementDB
from agents.base import AgentError
from agents.pm_agent import (
    get_context_agent_response,
    detect_save,
    extract_product_context,
    SAVE_MARKER,
)
from components.chat_ui import render_chat
from components.styles import inject_custom_css
from components.graphics import (
    render_section_header,
    render_info_field,
    render_progress_ring,
    render_status_pill,
    render_empty_state,
    icon,
)
from components.guidance import render_page_guide, render_tab_guide

inject_custom_css()

ctx_id = st.session_state.get("selected_context_id")
if not ctx_id:
    st.warning("No case selected.")
    if st.button("Go to Case Board"):
        st.switch_page("pages/1_Home.py")
    st.stop()

ctx = ProductContextDB.get(ctx_id)
if not ctx:
    st.error("Case not found.")
    st.stop()

# ── Header ──
col_name, col_back = st.columns([4, 1])
with col_name:
    new_name = st.text_input(
        "Case Name", value=ctx["name"], key=f"ctx_name_{ctx_id}", label_visibility="collapsed"
    )
    if new_name != ctx["name"]:
        ProductContextDB.update(ctx_id, name=new_name)
        ctx["name"] = new_name
with col_back:
    if st.button("< Case Board", use_container_width=True):
        st.switch_page("pages/1_Home.py")

render_page_guide(
    "Case File — Product Definition",
    "A <strong>Case</strong> is your product or initiative. Build the case brief by chatting with Dupin, "
    "then launch <strong>Investigations</strong> (focused research sessions) to interview users."
)

# ── Tabs ──
tab_overview, tab_investigations, tab_leads = st.tabs(
    ["Case Brief", "Investigations", "New Leads"]
)

# ═══════════════════════════════════════════════
# Case Brief Tab — Always Split: Evidence Board + Dupin Chat
# ═══════════════════════════════════════════════
with tab_overview:
    render_tab_guide(
        "The left panel shows everything Dupin knows about this case. "
        "Chat on the right to add details, ask questions, or update the brief. Changes are tracked."
    )

    # Chat state init
    chat_key = f"pm_context_chat_{ctx_id}"
    if chat_key not in st.session_state:
        saved = ctx.get("context_conversation_history", [])
        if isinstance(saved, str):
            saved = json.loads(saved) if saved else []
        st.session_state[chat_key] = saved

    def context_agent_callback(messages):
        try:
            raw_response = get_context_agent_response(messages, ctx)
        except (AgentError, Exception) as e:
            return f"I'm having a brief connection issue. Please try again. ({type(e).__name__})"
        should_save, clean_response = detect_save(raw_response, SAVE_MARKER)

        if should_save:
            # Extract and save, with history tracking
            full_messages = messages + [
                {"role": "assistant", "content": clean_response}
            ]
            extracted = extract_product_context(full_messages)
            update_kwargs = {}
            changes = []
            for field in ["name", "description", "documentation", "current_state"]:
                val = extracted.get(field)
                if val and val != "null":
                    old_val = ctx.get(field, "")
                    if val != old_val:
                        update_kwargs[field] = val
                        field_label = {"description": "Subject", "documentation": "Evidence & Documentation",
                                       "current_state": "Current State", "name": "Case Name"}.get(field, field)
                        if old_val:
                            changes.append(f"Updated {field_label}")
                        else:
                            changes.append(f"Added {field_label}")
            update_kwargs["context_conversation_history"] = (
                st.session_state[chat_key]
                + [{"role": "assistant", "content": clean_response}]
            )
            if update_kwargs:
                ProductContextDB.update(ctx_id, **update_kwargs)
            # Log history for each change
            for change in changes:
                ProductContextDB.add_history_entry(ctx_id, change, clean_response[:150], "Dupin Assistant")

        return clean_response

    col_evidence, col_chat = st.columns([1, 1], gap="large")

    # ── Left: Evidence Board (What We Know) ──
    with col_evidence:
        render_section_header("document", "What We Know")

        fields = ["description", "documentation", "current_state"]
        filled = sum(1 for f in fields if ctx.get(f))
        has_content = filled > 0

        if has_content:
            if ctx.get("description"):
                render_info_field("Subject", ctx["description"])
            if ctx.get("documentation"):
                render_info_field("Evidence & Documentation", ctx["documentation"])
            if ctx.get("current_state"):
                render_info_field("Current State of Affairs", ctx["current_state"])

            # Show case history
            history = ctx.get("case_history", [])
            if history:
                with st.expander(f"Case History ({len(history)} entries)", expanded=False):
                    for entry in reversed(history):
                        ts = entry.get("timestamp", "")[:16]
                        source = entry.get("source", "PM")
                        action = entry.get("action", "")
                        details = entry.get("details", "")
                        source_color = "#C4823A" if "Dupin" in source else "#5C7A6E" if "Investigation" in source else "#8C8878"
                        st.markdown(
                            f'<div style="border-left:3px solid {source_color};padding:0.4rem 0.75rem;'
                            f'margin-bottom:0.5rem;border-radius:0 4px 4px 0;">'
                            f'<div style="font-size:0.7rem;color:#B8B4A8;">{ts} · {source}</div>'
                            f'<div style="font-size:0.85rem;color:#3D3D35;font-weight:500;">{action}</div>'
                            f'<div style="font-size:0.8rem;color:#8C8878;margin-top:0.15rem;">{details[:120]}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
        else:
            render_empty_state(
                "document",
                "Nothing here yet",
                "Chat with Dupin on the right to start building the case brief. "
                "Information will appear here as you share it."
            )

    # ── Right: Dupin Chat ──
    with col_chat:
        render_section_header("chat", "Dupin Assistant")

        greeting = (
            "Welcome, detective. I'm Dupin, your discovery assistant.\n\n"
            if not has_content else
            "The case brief is taking shape. What else should I know? "
            "You can also ask me **why** something is in the brief \u2014 "
            "I remember how things evolved.\n\n"
        )
        if not has_content:
            greeting += (
                "Let's build the case brief. I'll ask you some questions and "
                "organize everything as we go. To start \u2014 **what product or "
                "initiative are you investigating?**"
            )

        render_chat(
            session_key=chat_key,
            agent_callback=context_agent_callback,
            placeholder="Tell Dupin about your product, or ask about past decisions...",
            initial_assistant_message=greeting,
        )

    st.divider()

# ═══════════════════════════════════════════════
# Investigations Tab
# ═══════════════════════════════════════════════
with tab_investigations:
    render_tab_guide("Each investigation is a focused research session — e.g., exploring onboarding, a specific feature, or a persona's workflow.")
    sessions = DiscoverySessionDB.list_by_context(ctx_id)

    col_hdr, col_btn = st.columns([3, 1])
    with col_hdr:
        render_section_header("magnifier", "Investigations")
    with col_btn:
        if st.button("+ New Investigation", type="primary", use_container_width=True):
            new_session = DiscoverySessionDB.create(
                product_context_id=ctx_id, name="Untitled Investigation"
            )
            st.session_state["selected_session_id"] = new_session["id"]
            st.switch_page("pages/3_Discovery_Session.py")

    if not sessions:
        render_empty_state(
            "magnifier",
            "No investigations opened yet",
            "Start an investigation to uncover user journeys and pain points.",
        )
    else:
        for session in sessions:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"#### {session['name']}")
                    if session.get("objective"):
                        st.markdown(
                            f'<p style="color:#8C8878; font-size:0.9rem;">{session["objective"][:150]}</p>',
                            unsafe_allow_html=True,
                        )
                with col2:
                    st.markdown(
                        f"<div style='margin-top:0.75rem;'>{render_status_pill(session['status'])}</div>",
                        unsafe_allow_html=True,
                    )
                with col3:
                    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
                    if st.button("Investigate", key=f"open_session_{session['id']}", use_container_width=True):
                        st.session_state["selected_session_id"] = session["id"]
                        st.switch_page("pages/3_Discovery_Session.py")

# ═══════════════════════════════════════════════
# New Leads Tab (Context Improvements)
# ═══════════════════════════════════════════════
with tab_leads:
    render_tab_guide("Leads are suggestions to update your case brief based on what Dupin uncovered during interviews.")
    render_section_header("lightbulb", "New Leads")
    improvements = ContextImprovementDB.list_by_context(ctx_id)

    if not improvements:
        render_empty_state(
            "lightbulb",
            "No new leads yet",
            "Conduct investigations and interviews to uncover leads.",
        )
    else:
        for imp in improvements:
            stype = imp.get("suggestion_type", "gap")
            st.markdown(
                f'<div class="improvement-card {stype}">',
                unsafe_allow_html=True,
            )
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{imp['title']}**")
                    st.markdown(
                        f'<span class="status-pill {stype}">{stype.replace("_", " ").title()}</span>',
                        unsafe_allow_html=True,
                    )
                    st.write(imp.get("description", ""))
                with col2:
                    if imp["status"] == "pending":
                        if st.button("Accept", key=f"acc_{imp['id']}"):
                            # Apply the lead to the case brief
                            stype = imp.get("suggestion_type", "new_info")
                            imp_title = imp.get("title", "")
                            imp_desc = imp.get("description", "")
                            lead_text = f"\n\n[From investigation] {imp_title}: {imp_desc}"

                            field_updated = ""
                            if stype in ("new_info", "gap"):
                                current = ctx.get("description", "") or ""
                                ProductContextDB.update(ctx_id, description=current + lead_text)
                                field_updated = "Subject"
                            elif stype == "correction":
                                current = ctx.get("current_state", "") or ""
                                ProductContextDB.update(ctx_id, current_state=current + lead_text)
                                field_updated = "Current State"
                            elif stype == "conflicting_assumption":
                                current = ctx.get("documentation", "") or ""
                                ProductContextDB.update(ctx_id, documentation=current + lead_text)
                                field_updated = "Evidence & Documentation"

                            # Log to case history
                            ProductContextDB.add_history_entry(
                                ctx_id,
                                f"Accepted lead: {imp_title}",
                                f"Added to {field_updated}. {imp_desc[:100]}",
                                source=f"Investigation Finding ({stype})",
                            )

                            ContextImprovementDB.update_status(imp["id"], "accepted")
                            st.rerun()
                        if st.button("Dismiss", key=f"rej_{imp['id']}"):
                            ContextImprovementDB.update_status(imp["id"], "rejected")
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
