from __future__ import annotations
import streamlit as st
from components.styles import inject_custom_css
from components.graphics import (
    render_hero_banner,
    render_feature_preview_card,
    render_section_header,
    icon,
)

inject_custom_css()

# ── Header ──
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #F2EDE8 0%, #FAFAF8 50%, #F2EDE8 100%);
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    border: 1px solid #E8E0D8;
    position: relative;
    overflow: hidden;
">
    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); opacity:0.04;">
        <svg width="300" height="300" viewBox="0 0 300 300" fill="none">
            <circle cx="150" cy="150" r="140" stroke="#8B7355" stroke-width="1.5"/>
            <circle cx="150" cy="150" r="100" stroke="#8B7355" stroke-width="1"/>
            <circle cx="150" cy="150" r="60" stroke="#8B7355" stroke-width="0.75"/>
            <path d="M150 10 L150 290" stroke="#8B7355" stroke-width="0.5"/>
            <path d="M10 150 L290 150" stroke="#8B7355" stroke-width="0.5"/>
        </svg>
    </div>
    <div style="position:relative; z-index:1;">
        <div style="margin-bottom:1rem; opacity:0.3;">
            {icon("chart", 48, "#8B7355")}
        </div>
        <h1 style="margin:0 !important; font-size:2rem !important;">Reports</h1>
        <p style="color:#6B6156; margin:0.75rem auto 0; max-width:450px; line-height:1.5;">
            Comprehensive research reports with synthesized findings across all your discovery sessions.
        </p>
        <div style="
            display:inline-block;
            margin-top:1.25rem;
            padding:0.4rem 1rem;
            background:#F2EDE8;
            border-radius:999px;
            font-size:0.8rem;
            color:#8B7355;
            font-weight:600;
            letter-spacing:0.05em;
        ">COMING IN PHASE 5</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Feature Preview Cards ──
render_section_header("layers", "What Reports Will Include")

col1, col2, col3 = st.columns(3)
with col1:
    render_feature_preview_card(
        "document",
        "Executive Summary",
        "High-level overview of findings, key themes, and actionable recommendations."
    )
with col2:
    render_feature_preview_card(
        "users",
        "User Journeys",
        "Visual journey maps with multiple paths, confidence levels, and pain points."
    )
with col3:
    render_feature_preview_card(
        "warning",
        "Discrepancies",
        "Conflicts between users or against product context, with evidence from both sides."
    )

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)
with col4:
    render_feature_preview_card(
        "lightbulb",
        "Expectations",
        "User expectations tagged by persona, journey stage, and priority level."
    )
with col5:
    render_feature_preview_card(
        "target",
        "Pain Points",
        "Grouped by journey stage with severity ratings and supporting quotes."
    )
with col6:
    render_feature_preview_card(
        "chart",
        "Cross-Session Trends",
        "Aggregated insights, evolving journeys, and patterns across multiple sessions."
    )
