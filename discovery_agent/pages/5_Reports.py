from __future__ import annotations
import streamlit as st
from components.styles import inject_custom_css
from components.graphics import (
    render_feature_preview_card,
    render_section_header,
    icon,
)
from components.guidance import render_page_guide

inject_custom_css()

render_page_guide(
    "Dossier — Research Reports",
    "The Dossier compiles all findings from your investigations into actionable reports: "
    "user journey maps, pain point analysis, expectation rankings, and cross-case patterns."
)

# ── Header ──
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #E8E3D8 0%, #F0EDE6 50%, #E8E3D8 100%);
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    border: 1px solid #D0CAC0;
    position: relative;
    overflow: hidden;
">
    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); opacity:0.04;">
        <svg width="300" height="300" viewBox="0 0 300 300" fill="none">
            <circle cx="150" cy="150" r="140" stroke="#C4823A" stroke-width="1.5"/>
            <circle cx="150" cy="150" r="100" stroke="#C4823A" stroke-width="1"/>
            <circle cx="150" cy="150" r="60" stroke="#C4823A" stroke-width="0.75"/>
            <path d="M150 10 L150 290" stroke="#C4823A" stroke-width="0.5"/>
            <path d="M10 150 L290 150" stroke="#C4823A" stroke-width="0.5"/>
        </svg>
    </div>
    <div style="position:relative; z-index:1;">
        <div style="margin-bottom:1rem; opacity:0.3;">
            {icon("chart", 48, "#C4823A")}
        </div>
        <h1 style="margin:0 !important; font-size:2rem !important;">The Dossier</h1>
        <p style="color:#8C8878; margin:0.75rem auto 0; max-width:450px; line-height:1.5;">
            Compiled findings, synthesized evidence, and investigative conclusions across all your cases.
        </p>
        <div style="
            display:inline-block;
            margin-top:1.25rem;
            padding:0.4rem 1rem;
            background:#E8E3D8;
            border-radius:999px;
            font-size:0.8rem;
            color:#C4823A;
            font-weight:600;
            letter-spacing:0.05em;
        ">COMING IN PHASE 5</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Feature Preview Cards ──
render_section_header("layers", "What the Dossier Will Contain")

col1, col2, col3 = st.columns(3)
with col1:
    render_feature_preview_card(
        "document",
        "Case Summary",
        "High-level findings, key themes, and actionable recommendations from the investigation."
    )
with col2:
    render_feature_preview_card(
        "users",
        "Witness Journeys",
        "Visual journey maps with multiple paths, confidence levels, and pain points."
    )
with col3:
    render_feature_preview_card(
        "warning",
        "Contradictions",
        "Conflicting testimony between witnesses, with evidence from both sides."
    )

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)
with col4:
    render_feature_preview_card(
        "lightbulb",
        "Expectations",
        "What witnesses want, tagged by persona, journey stage, and priority level."
    )
with col5:
    render_feature_preview_card(
        "target",
        "Pain Points",
        "Frustrations grouped by journey stage with severity ratings and supporting quotes."
    )
with col6:
    render_feature_preview_card(
        "chart",
        "Cross-Case Patterns",
        "Aggregated clues, evolving journeys, and patterns across multiple investigations."
    )
