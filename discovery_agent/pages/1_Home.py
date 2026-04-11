from __future__ import annotations
import os
import streamlit as st
from database.models import ProductContextDB, DiscoverySessionDB, ConversationDB
from components.styles import inject_custom_css
from components.graphics import (
    render_hero_banner,
    render_metric_card,
    render_empty_state,
    render_status_pill,
    icon,
)

inject_custom_css()

# ── Hero Banner with Logo ──
_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo_path = os.path.join(_APP_DIR, "assets", "logo.png")

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
        <p style="color: #8C8878 !important; font-size: 1.05rem; margin: 0; max-width: 500px; line-height: 1.75;">
            AI-powered user research platform. Deploy conversational agents to interview users,
            uncover journeys, and synthesize insights across conversations.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Metrics Row ──
contexts = ProductContextDB.list_all()
total_contexts = len(contexts)

# Count all sessions and conversations across contexts
total_sessions = 0
total_conversations = 0
for ctx in contexts:
    session_count = ProductContextDB.count_sessions(ctx["id"])
    total_sessions += session_count
    sessions = DiscoverySessionDB.list_by_context(ctx["id"])
    for s in sessions:
        convs = ConversationDB.list_by_session(s["id"])
        total_conversations += len(convs)

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("folder", "Product Contexts", total_contexts, "#C4823A")
with col2:
    render_metric_card("target", "Discovery Sessions", total_sessions, "#E8B87A")
with col3:
    render_metric_card("chat", "Conversations", total_conversations, "#7A9E7E")
with col4:
    render_metric_card("lightbulb", "Insights", 0, "#D4A056")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ── Create Button ──
col_left, col_right = st.columns([3, 1])
with col_right:
    if st.button("+ New Product Context", type="primary", use_container_width=True):
        new_ctx = ProductContextDB.create(name="Untitled Product Context")
        st.session_state["selected_context_id"] = new_ctx["id"]
        st.switch_page("pages/2_Product_Context.py")

# ── Context Cards ──
if not contexts:
    render_empty_state(
        "folder",
        "No product contexts yet",
        "Create your first product context to start conducting user research."
    )
else:
    for ctx in contexts:
        session_count = ProductContextDB.count_sessions(ctx["id"])
        desc = ctx.get("description", "")

        with st.container(border=True):
            col_main, col_meta, col_action = st.columns([3, 2, 1])
            with col_main:
                st.markdown(f"#### {ctx['name']}")
                if desc:
                    truncated = desc[:180] + ("..." if len(desc) > 180 else "")
                    st.markdown(
                        f'<p style="color:#8C8878; font-size:0.9rem; line-height:1.5;">{truncated}</p>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<p style="color:#B8B4A8; font-size:0.9rem; font-style:italic;">No description yet</p>',
                        unsafe_allow_html=True,
                    )
            with col_meta:
                st.markdown(
                    f"""
                    <div style="display:flex; gap:1.5rem; margin-top:0.5rem;">
                        <div style="text-align:center;">
                            <div style="font-size:1.4rem; font-weight:700; color:#C4823A;">{session_count}</div>
                            <div style="font-size:0.75rem; color:#B8B4A8; text-transform:uppercase; letter-spacing:0.05em;">Sessions</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:0.8rem; color:#B8B4A8; margin-top:0.5rem;">{icon("clock", 14, "#B8B4A8")} Updated</div>
                            <div style="font-size:0.85rem; color:#8C8878;">{ctx['updated_at'][:10]}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_action:
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                if st.button("Open", key=f"open_{ctx['id']}", use_container_width=True):
                    st.session_state["selected_context_id"] = ctx["id"]
                    st.switch_page("pages/2_Product_Context.py")
                if st.button("Delete", key=f"del_{ctx['id']}", use_container_width=True):
                    ProductContextDB.delete(ctx["id"])
                    st.rerun()
