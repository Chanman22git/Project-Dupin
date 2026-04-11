from __future__ import annotations
import json
import streamlit as st
from database.models import ProductContextDB, DiscoverySessionDB, ContextImprovementDB
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

inject_custom_css()

ctx_id = st.session_state.get("selected_context_id")
if not ctx_id:
    st.warning("No product context selected.")
    if st.button("Go to Home"):
        st.switch_page("pages/1_Home.py")
    st.stop()

ctx = ProductContextDB.get(ctx_id)
if not ctx:
    st.error("Product context not found.")
    st.stop()

# ── Header ──
col_name, col_back = st.columns([4, 1])
with col_name:
    new_name = st.text_input(
        "Context Name", value=ctx["name"], key=f"ctx_name_{ctx_id}", label_visibility="collapsed"
    )
    if new_name != ctx["name"]:
        ProductContextDB.update(ctx_id, name=new_name)
        ctx["name"] = new_name
with col_back:
    if st.button("< All Contexts", use_container_width=True):
        st.switch_page("pages/1_Home.py")

# ── Tabs ──
tab_overview, tab_sessions, tab_improvements = st.tabs(
    ["Overview", "Discovery Sessions", "Context Improvements"]
)

# ═══════════════════════════════════════════════
# Overview Tab
# ═══════════════════════════════════════════════
with tab_overview:
    col_display, col_chat = st.columns([1, 1], gap="large")

    with col_display:
        # Progress ring
        fields = ["description", "documentation", "current_state"]
        filled = sum(1 for f in fields if ctx.get(f))
        pct = int((filled / len(fields)) * 100)

        col_hdr, col_ring = st.columns([3, 1])
        with col_hdr:
            render_section_header("document", "Product Context")
        with col_ring:
            render_progress_ring(pct, "Complete")

        render_info_field("Description", ctx.get("description"), "Chat with the assistant to define this")
        render_info_field("Documentation", ctx.get("documentation"), "Paste docs, APIs, or specs")
        render_info_field("Current State", ctx.get("current_state"), "What does the product do today?")

    with col_chat:
        render_section_header("chat", "Setup Assistant")

        chat_key = f"pm_context_chat_{ctx_id}"
        if chat_key not in st.session_state:
            saved = ctx.get("context_conversation_history", [])
            if isinstance(saved, str):
                saved = json.loads(saved) if saved else []
            st.session_state[chat_key] = saved

        def context_agent_callback(messages):
            raw_response = get_context_agent_response(messages, ctx)
            should_save, clean_response = detect_save(raw_response, SAVE_MARKER)

            if should_save:
                with st.spinner("Saving context..."):
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

        render_chat(
            session_key=chat_key,
            agent_callback=context_agent_callback,
            placeholder="Describe your product, paste docs, or say 'save this'...",
            initial_assistant_message=(
                "Hi! I'm here to help you define your product context. "
                "Tell me about the product you're researching \u2014 what is it, "
                "who uses it, and what does it currently do? You can also paste "
                "any documentation or specs you have."
            ),
        )

# ═══════════════════════════════════════════════
# Discovery Sessions Tab
# ═══════════════════════════════════════════════
with tab_sessions:
    sessions = DiscoverySessionDB.list_by_context(ctx_id)

    col_hdr, col_btn = st.columns([3, 1])
    with col_hdr:
        render_section_header("target", "Discovery Sessions")
    with col_btn:
        if st.button("+ New Session", type="primary", use_container_width=True):
            new_session = DiscoverySessionDB.create(
                product_context_id=ctx_id, name="Untitled Session"
            )
            st.session_state["selected_session_id"] = new_session["id"]
            st.switch_page("pages/3_Discovery_Session.py")

    if not sessions:
        render_empty_state(
            "target",
            "No discovery sessions yet",
            "Create a session to start exploring user journeys and pain points.",
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
                    if st.button("Open", key=f"open_session_{session['id']}", use_container_width=True):
                        st.session_state["selected_session_id"] = session["id"]
                        st.switch_page("pages/3_Discovery_Session.py")

# ═══════════════════════════════════════════════
# Context Improvements Tab
# ═══════════════════════════════════════════════
with tab_improvements:
    render_section_header("lightbulb", "Context Improvements")
    improvements = ContextImprovementDB.list_by_context(ctx_id)

    if not improvements:
        render_empty_state(
            "lightbulb",
            "No improvement suggestions yet",
            "Run discovery sessions and generate insights to get suggestions.",
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
                            ContextImprovementDB.update_status(imp["id"], "accepted")
                            st.rerun()
                        if st.button("Reject", key=f"rej_{imp['id']}"):
                            ContextImprovementDB.update_status(imp["id"], "rejected")
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
