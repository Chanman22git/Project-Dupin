from __future__ import annotations
import os
import streamlit as st
from database.models import ProductContextDB, DiscoverySessionDB, ConversationDB
from components.styles import inject_custom_css
from components.graphics import (
    render_metric_card,
    render_empty_state,
    icon,
)
from components.guidance import render_page_guide

inject_custom_css()

render_page_guide(
    "Case Board — Your Products Dashboard",
    "Each <strong>Case</strong> represents a product or initiative you're researching. "
    "Open a case to define it, then launch investigations to interview users and gather insights."
)

# ── Hero Banner ──
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #E8E3D8 0%, #F0EDE6 50%, #E8E3D8 100%);
    border-radius: 16px;
    padding: 2.5rem 2.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    border: 1px solid #D0CAC0;
">
    <div style="position: absolute; right: 2rem; top: 50%; transform: translateY(-50%); opacity: 0.06;">
        <svg width="180" height="180" viewBox="0 0 180 180" fill="none">
            <circle cx="90" cy="90" r="80" stroke="#3D3D35" stroke-width="2"/>
            <circle cx="90" cy="90" r="55" stroke="#3D3D35" stroke-width="1.5"/>
            <circle cx="90" cy="90" r="30" stroke="#3D3D35" stroke-width="1"/>
            <line x1="90" y1="10" x2="90" y2="170" stroke="#3D3D35" stroke-width="0.5"/>
            <line x1="10" y1="90" x2="170" y2="90" stroke="#3D3D35" stroke-width="0.5"/>
        </svg>
    </div>
    <div style="position: relative; z-index: 1;">
        <h4 style="margin:0 0 0.5rem 0 !important; font-size:1.1rem !important;">
            "The most important thing is not to stop questioning."
        </h4>
        <p style="color: #8C8878 !important; font-size: 1rem; margin: 0; max-width: 520px; line-height: 1.75;">
            Open a case, launch investigations, conduct interviews.
            Dupin's AI agents uncover what your users really think.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Metrics Row ──
cases = ProductContextDB.list_all()
total_cases = len(cases)

total_investigations = 0
total_interviews = 0
for c in cases:
    inv_count = ProductContextDB.count_sessions(c["id"])
    total_investigations += inv_count
    investigations = DiscoverySessionDB.list_by_context(c["id"])
    for inv in investigations:
        interviews = ConversationDB.list_by_session(inv["id"])
        total_interviews += len(interviews)

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("folder", "Open Cases", total_cases, "#C4823A")
with col2:
    render_metric_card("magnifier", "Investigations", total_investigations, "#E8B87A")
with col3:
    render_metric_card("chat", "Interviews", total_interviews, "#5C7A6E")
with col4:
    render_metric_card("lightbulb", "Clues", 0, "#8C8878")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ── Create New Case ──
col_left, col_right = st.columns([3, 1])
with col_left:
    new_case_name = st.text_input(
        "New case name", placeholder="e.g., Onboarding Redesign, Mobile App v3, Checkout Flow",
        label_visibility="collapsed", key="new_case_name",
    )
with col_right:
    if st.button("+ Open New Case", type="primary", use_container_width=True):
        case_name = new_case_name.strip() if new_case_name else "Untitled Case"
        new_ctx = ProductContextDB.create(name=case_name)
        st.session_state["selected_context_id"] = new_ctx["id"]
        st.switch_page("pages/2_Product_Context.py")

# ── Case Cards ──
if not cases:
    render_empty_state(
        "folder",
        "No cases on the board yet",
        "Open your first case to start investigating your product."
    )
else:
    for c in cases:
        inv_count = ProductContextDB.count_sessions(c["id"])
        summary = c.get("summary", "")
        desc = c.get("description", "")
        docs = c.get("documentation", "")
        state = c.get("current_state", "")
        conv_history = c.get("context_conversation_history", [])

        # Build a clean one-liner from whatever we have
        if not summary and desc:
            summary = desc.split(".")[0].strip()
        if not summary and state:
            summary = state.split(".")[0].strip()

        # Enforce max length — true one-liner
        if summary and len(summary) > 100:
            summary = summary[:97] + "..."

        with st.container(border=True):
            col_main, col_meta, col_action = st.columns([3, 2, 1])
            with col_main:
                st.markdown(f"#### {c['name']}")
                if summary:
                    st.markdown(
                        f'<p style="color:#8C8878; font-size:0.9rem; line-height:1.5;">{summary}</p>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<p style="color:#B8B4A8; font-size:0.9rem; font-style:italic;">Open the case and chat with Dupin to build the brief</p>',
                        unsafe_allow_html=True,
                    )
            with col_meta:
                st.markdown(
                    f"""
                    <div style="display:flex; gap:1.5rem; margin-top:0.5rem;">
                        <div style="text-align:center;">
                            <div style="font-size:1.4rem; font-weight:700; color:#C4823A;">{inv_count}</div>
                            <div style="font-size:0.75rem; color:#B8B4A8; text-transform:uppercase; letter-spacing:0.05em;">Investigations</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:0.8rem; color:#B8B4A8; margin-top:0.5rem;">{icon("clock", 14, "#B8B4A8")} Updated</div>
                            <div style="font-size:0.85rem; color:#8C8878;">{c['updated_at'][:10]}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_action:
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                if st.button("Open Case", key=f"open_{c['id']}", use_container_width=True):
                    st.session_state["selected_context_id"] = c["id"]
                    st.switch_page("pages/2_Product_Context.py")
                if st.button("Close Case", key=f"del_{c['id']}", use_container_width=True):
                    ProductContextDB.delete(c["id"])
                    st.rerun()
