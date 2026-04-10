from __future__ import annotations
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

# ── Hero Banner ──
render_hero_banner(
    "Discovery Agent",
    "AI-powered user research platform. Deploy conversational agents to interview users, "
    "uncover journeys, and synthesize insights across conversations."
)

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
    render_metric_card("folder", "Product Contexts", total_contexts, "#8B7355")
with col2:
    render_metric_card("target", "Discovery Sessions", total_sessions, "#C4956A")
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
                        f'<p style="color:#6B6156; font-size:0.9rem; line-height:1.5;">{truncated}</p>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<p style="color:#A89F91; font-size:0.9rem; font-style:italic;">No description yet</p>',
                        unsafe_allow_html=True,
                    )
            with col_meta:
                st.markdown(
                    f"""
                    <div style="display:flex; gap:1.5rem; margin-top:0.5rem;">
                        <div style="text-align:center;">
                            <div style="font-size:1.4rem; font-weight:700; color:#8B7355;">{session_count}</div>
                            <div style="font-size:0.75rem; color:#A89F91; text-transform:uppercase; letter-spacing:0.05em;">Sessions</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:0.8rem; color:#A89F91; margin-top:0.5rem;">{icon("clock", 14, "#A89F91")} Updated</div>
                            <div style="font-size:0.85rem; color:#6B6156;">{ctx['updated_at'][:10]}</div>
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
