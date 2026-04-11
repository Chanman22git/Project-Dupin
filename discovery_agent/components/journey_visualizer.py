from __future__ import annotations
import streamlit as st
from components.graphics import (
    icon, COGNAC, COGNAC_LIGHT, PATINA, ALERT, SMOKE, CHARCOAL,
    FAINT, AGED_PAPER, BORDER, NEUTRAL_50,
)


def render_journey_map(journey):
    """Render a full-width journey map with stage cards, pain points, and metadata."""
    stages = journey.get("stages", [])
    confidence = journey.get("confidence", "low")
    is_partial = journey.get("is_partial", False)
    persona = journey.get("persona", "")

    conf_color = PATINA if confidence == "high" else COGNAC if confidence == "medium" else SMOKE

    # Header
    partial_badge = (
        f'<span style="font-size:0.625rem;background:{AGED_PAPER};color:{SMOKE};'
        f'padding:0.2rem 0.6rem;border-radius:9999px;font-weight:500;'
        f'letter-spacing:0.08em;text-transform:uppercase;">Partial Journey</span>'
        if is_partial else ""
    )

    st.markdown(f"""
    <div style="background:{NEUTRAL_50};border:1px solid {BORDER};border-radius:10px;
                padding:1.25rem 1.5rem;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
            <div style="display:flex;align-items:center;gap:0.5rem;">
                {icon("target", 20, COGNAC)}
                <span style="font-family:'Playfair Display',serif;font-size:1.15rem;font-weight:700;
                      color:{CHARCOAL};">{journey.get("journey_name", "Unnamed Journey")}</span>
                <span style="font-size:0.85rem;color:{SMOKE};margin-left:0.25rem;">{persona}</span>
            </div>
            <div style="display:flex;gap:0.5rem;align-items:center;">
                {partial_badge}
                <span style="font-size:0.625rem;font-weight:600;color:{conf_color};
                      text-transform:uppercase;letter-spacing:0.08em;
                      background:rgba(0,0,0,0.04);padding:0.2rem 0.6rem;border-radius:9999px;">
                    {confidence} confidence
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Stages as connected cards
    if stages:
        stages_html = '<div style="display:flex;align-items:stretch;gap:0;overflow-x:auto;padding-bottom:0.5rem;">'
        for i, stage in enumerate(stages):
            name = stage.get("stage_name", f"Step {i+1}")
            desc = stage.get("description", "")
            actions = stage.get("actions", [])
            pains = stage.get("pain_points", [])
            emotions = stage.get("emotions", [])
            touchpoints = stage.get("touchpoints", [])

            # Actions list
            actions_html = ""
            if actions:
                items = "".join(
                    f'<li style="font-size:0.75rem;color:{SMOKE};margin:0.15rem 0;">{a}</li>'
                    for a in actions[:3]
                )
                actions_html = f'<ul style="padding-left:1rem;margin:0.3rem 0;">{items}</ul>'

            # Pain points
            pains_html = ""
            if pains:
                for p in pains[:2]:
                    pains_html += (
                        f'<div style="font-size:0.7rem;color:{ALERT};margin-top:0.2rem;">'
                        f'{icon("warning", 10, ALERT)} {p}</div>'
                    )

            # Touchpoints
            touch_html = ""
            if touchpoints:
                chips = " ".join(
                    f'<span style="font-size:0.6rem;background:{AGED_PAPER};color:{SMOKE};'
                    f'padding:0.1rem 0.4rem;border-radius:9999px;">{t}</span>'
                    for t in touchpoints[:3]
                )
                touch_html = f'<div style="margin-top:0.3rem;">{chips}</div>'

            # Emotions
            emotion_html = ""
            if emotions:
                emotion_html = (
                    f'<div style="font-size:0.7rem;color:{COGNAC_LIGHT};margin-top:0.2rem;font-style:italic;">'
                    f'{", ".join(emotions[:2])}</div>'
                )

            stages_html += f"""
            <div style="flex:1;min-width:160px;max-width:240px;">
                <div style="background:white;border:1px solid {BORDER};border-radius:8px;
                            padding:0.75rem;height:100%;position:relative;">
                    <div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.4rem;">
                        <div style="width:24px;height:24px;border-radius:50%;background:{COGNAC};color:white;
                                    display:flex;align-items:center;justify-content:center;
                                    font-size:0.7rem;font-weight:600;flex-shrink:0;">{i+1}</div>
                        <div style="font-size:0.8rem;font-weight:600;color:{CHARCOAL};">{name}</div>
                    </div>
                    <div style="font-size:0.75rem;color:{SMOKE};line-height:1.4;">{desc[:100]}</div>
                    {actions_html}
                    {touch_html}
                    {emotion_html}
                    {pains_html}
                </div>
            </div>
            """
            if i < len(stages) - 1:
                stages_html += (
                    f'<div style="display:flex;align-items:center;padding:0 0.25rem;'
                    f'color:{FAINT};font-size:1.5rem;flex-shrink:0;">→</div>'
                )

        stages_html += '</div>'
        st.markdown(stages_html, unsafe_allow_html=True)

    # Close container
    st.markdown("</div>", unsafe_allow_html=True)
