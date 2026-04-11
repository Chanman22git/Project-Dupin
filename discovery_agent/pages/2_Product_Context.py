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
# Case Brief Tab
# ═══════════════════════════════════════════════
with tab_overview:
    # Check if case brief has any content
    fields = ["description", "documentation", "current_state"]
    filled = sum(1 for f in fields if ctx.get(f))
    has_brief = filled > 0

    # Chat state init (needed regardless of layout)
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
            with st.spinner("Filing case brief..."):
                full_messages = messages + [
                    {"role": "assistant", "content": clean_response}
                ]
                extracted = extract_product_context(full_messages)
                update_kwargs = {}
                for field in ["name", "description", "documentation", "current_state"]:
                    val = extracted.get(field)
                    if val and val != "null":
                        update_kwargs[field] = val
                update_kwargs["context_conversation_history"] = (
                    st.session_state[chat_key]
                    + [{"role": "assistant", "content": clean_response}]
                )
                ProductContextDB.update(ctx_id, **update_kwargs)

        return clean_response

    if not has_brief:
        # ── Chat-only mode: no brief yet ──
        render_tab_guide(
            "Tell Dupin about your product — what it does, who uses it, any docs you have. "
            "When you're ready, say 'save this' and Dupin will file the case brief."
        )
        render_chat(
            session_key=chat_key,
            agent_callback=context_agent_callback,
            placeholder="Describe your product, paste evidence, or say 'save this'...",
            initial_assistant_message=(
                "Welcome, detective. I'm Dupin, your discovery assistant. "
                "Let's build the case brief \u2014 tell me about the product "
                "you're investigating. What is it, who uses it, and what does "
                "it currently do? You can also paste any documentation or specs.\n\n"
                "When you're happy with what we've covered, just say **\"save this\"** "
                "and I'll file the case brief."
            ),
        )
    else:
        # ── Brief exists: show structured view + chat for updates ──
        render_tab_guide("Your case brief is filed. Chat with Dupin to update it, or review the details below.")

        # Brief display
        col_hdr, col_ring = st.columns([3, 1])
        with col_hdr:
            render_section_header("document", "Case Brief")
        with col_ring:
            pct = int((filled / len(fields)) * 100)
            render_progress_ring(pct, "Complete")

        render_info_field("Subject", ctx.get("description"))
        render_info_field("Evidence & Documentation", ctx.get("documentation"))
        render_info_field("Current State of Affairs", ctx.get("current_state"))

        st.divider()

        # Collapsible chat for updates
        with st.expander("Chat with Dupin to update the brief", expanded=False):
            render_chat(
                session_key=chat_key,
                agent_callback=context_agent_callback,
                placeholder="Ask Dupin to update the brief, or say 'save this'...",
                initial_assistant_message=(
                    "The case brief is filed. Need to update anything? "
                    "Tell me what's changed and say **\"save this\"** when ready."
                ),
            )

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
                            lead_text = f"\n\n[From investigation] {imp.get('title', '')}: {imp.get('description', '')}"

                            if stype in ("new_info", "gap"):
                                # Append to description
                                current = ctx.get("description", "") or ""
                                ProductContextDB.update(ctx_id, description=current + lead_text)
                            elif stype == "correction":
                                # Append to current_state as a correction note
                                current = ctx.get("current_state", "") or ""
                                ProductContextDB.update(ctx_id, current_state=current + lead_text)
                            elif stype == "conflicting_assumption":
                                # Append to documentation as a flagged assumption
                                current = ctx.get("documentation", "") or ""
                                ProductContextDB.update(ctx_id, documentation=current + lead_text)

                            ContextImprovementDB.update_status(imp["id"], "accepted")
                            st.rerun()
                        if st.button("Dismiss", key=f"rej_{imp['id']}"):
                            ContextImprovementDB.update_status(imp["id"], "rejected")
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
