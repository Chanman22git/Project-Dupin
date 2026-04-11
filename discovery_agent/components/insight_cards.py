from __future__ import annotations
import streamlit as st
from components.graphics import icon, render_metric_card, COGNAC, PATINA, ALERT, SMOKE, CHARCOAL, COGNAC_LIGHT, FAINT, AGED_PAPER

# Type display config
INSIGHT_TYPE_CONFIG = {
    "pain_point": {"label": "Pain Point", "icon": "warning", "color": ALERT},
    "expectation": {"label": "Expectation", "icon": "lightbulb", "color": COGNAC},
    "workflow": {"label": "Workflow", "icon": "layers", "color": PATINA},
    "feature_request": {"label": "Feature Request", "icon": "plus", "color": COGNAC_LIGHT},
    "behavior_pattern": {"label": "Behavior", "icon": "users", "color": SMOKE},
    "user_journey_step": {"label": "Journey Step", "icon": "target", "color": PATINA},
}

PRIORITY_COLORS = {
    "critical": ALERT,
    "high": ALERT,
    "medium": COGNAC,
    "low": SMOKE,
}


def render_analysis_summary(counts):
    """Render metric cards summarizing analysis results."""
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("lightbulb", "Insights", counts.get("insights", 0), COGNAC)
    with c2:
        render_metric_card("warning", "Contradictions", counts.get("discrepancies", 0), ALERT)
    with c3:
        render_metric_card("target", "Journeys", counts.get("journeys", 0), PATINA)
    with c4:
        render_metric_card("users", "Expectations", counts.get("expectations", 0), COGNAC_LIGHT)
    with c5:
        render_metric_card("document", "New Leads", counts.get("context_improvements", 0), SMOKE)


def render_insight_card(insight):
    """Render a single insight card with type badge, priority, and evidence."""
    itype = insight.get("type", "pain_point")
    config = INSIGHT_TYPE_CONFIG.get(itype, INSIGHT_TYPE_CONFIG["pain_point"])
    priority = insight.get("priority", "medium")
    p_color = PRIORITY_COLORS.get(priority, SMOKE)

    evidence = insight.get("evidence", [])
    persona_tags = insight.get("persona_tags", [])
    stage = insight.get("journey_stage", "")

    # Tags HTML
    tags_html = ""
    if persona_tags:
        tags_html += " ".join(
            f'<span style="background:{AGED_PAPER};color:{SMOKE};padding:0.15rem 0.5rem;'
            f'border-radius:9999px;font-size:0.7rem;font-weight:500;">{t}</span>'
            for t in persona_tags
        )
    if stage:
        tags_html += (
            f' <span style="background:{AGED_PAPER};color:{PATINA};padding:0.15rem 0.5rem;'
            f'border-radius:9999px;font-size:0.7rem;font-weight:500;">{stage}</span>'
        )

    # Evidence HTML
    evidence_html = ""
    if evidence:
        quotes = evidence[:2]  # Show max 2 quotes
        for e in quotes:
            quote = e.get("quote", str(e)) if isinstance(e, dict) else str(e)
            evidence_html += (
                f'<div style="border-left:2px solid {COGNAC};padding-left:0.75rem;'
                f'margin:0.4rem 0;font-size:0.85rem;color:{SMOKE};font-style:italic;">'
                f'"{quote}"</div>'
            )

    st.markdown(f"""
    <div style="background:#FAF8F5;border:1px solid #D0CAC0;border-radius:10px;
                padding:1rem 1.25rem;margin-bottom:0.75rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <div style="display:flex;align-items:center;gap:0.5rem;">
                {icon(config["icon"], 16, config["color"])}
                <span style="font-size:0.7rem;font-weight:600;color:{config['color']};
                      text-transform:uppercase;letter-spacing:0.08em;">{config["label"]}</span>
            </div>
            <span style="font-size:0.65rem;font-weight:600;color:{p_color};
                  text-transform:uppercase;letter-spacing:0.08em;
                  background:rgba(0,0,0,0.04);padding:0.15rem 0.5rem;border-radius:9999px;">
                {priority}
            </span>
        </div>
        <div style="font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;
                    color:{CHARCOAL};margin-bottom:0.35rem;">{insight.get("title", "")}</div>
        <div style="font-size:0.9rem;color:{SMOKE};line-height:1.5;margin-bottom:0.5rem;">
            {insight.get("description", "")}
        </div>
        {evidence_html}
        <div style="margin-top:0.5rem;display:flex;gap:0.4rem;flex-wrap:wrap;">{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)


def render_discrepancy_card(disc):
    """Render a two-sided contradiction card."""
    dtype = disc.get("type", "user_vs_user")
    type_label = "Witness vs Witness" if dtype == "user_vs_user" else "Witness vs Case Brief"
    type_color = COGNAC if dtype == "user_vs_user" else ALERT

    side_a = disc.get("side_a", {})
    side_b = disc.get("side_b", {})

    st.markdown(f"""
    <div style="background:#FAF8F5;border:1px solid #D0CAC0;border-radius:10px;
                padding:1rem 1.25rem;margin-bottom:0.75rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
            {icon("warning", 16, type_color)}
            <span style="font-size:0.7rem;font-weight:600;color:{type_color};
                  text-transform:uppercase;letter-spacing:0.08em;">{type_label}</span>
        </div>
        <div style="font-size:0.9rem;color:{CHARCOAL};margin-bottom:0.75rem;line-height:1.5;">
            {disc.get("description", "")}
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
            <div style="background:{AGED_PAPER};border-radius:6px;padding:0.75rem;">
                <div style="font-size:0.7rem;font-weight:600;color:{SMOKE};text-transform:uppercase;
                      letter-spacing:0.08em;margin-bottom:0.3rem;">Side A: {side_a.get("source", "")}</div>
                <div style="font-size:0.85rem;color:{CHARCOAL};font-style:italic;">
                    "{side_a.get("claim", "")}"
                </div>
            </div>
            <div style="background:{AGED_PAPER};border-radius:6px;padding:0.75rem;">
                <div style="font-size:0.7rem;font-weight:600;color:{SMOKE};text-transform:uppercase;
                      letter-spacing:0.08em;margin-bottom:0.3rem;">Side B: {side_b.get("source", "")}</div>
                <div style="font-size:0.85rem;color:{CHARCOAL};font-style:italic;">
                    "{side_b.get("claim", "")}"
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_journey_card(journey):
    """Render a user journey as a horizontal stage flow."""
    confidence = journey.get("confidence", "low")
    conf_color = PATINA if confidence == "high" else COGNAC if confidence == "medium" else SMOKE
    is_partial = journey.get("is_partial", False)
    stages = journey.get("stages", [])

    # Build stages HTML
    stages_html = ""
    for i, stage in enumerate(stages):
        name = stage.get("stage_name", f"Step {i+1}")
        desc = stage.get("description", "")
        pains = stage.get("pain_points", [])
        pain_dots = f' <span style="color:{ALERT};">{"!" * len(pains)}</span>' if pains else ""

        stages_html += f"""
        <div style="flex:1;text-align:center;padding:0.5rem;">
            <div style="width:28px;height:28px;border-radius:50%;background:{COGNAC};color:white;
                        display:inline-flex;align-items:center;justify-content:center;
                        font-size:0.75rem;font-weight:600;">{i+1}</div>
            <div style="font-size:0.8rem;font-weight:600;color:{CHARCOAL};margin-top:0.3rem;">
                {name}{pain_dots}
            </div>
            <div style="font-size:0.75rem;color:{SMOKE};margin-top:0.15rem;">{desc[:60]}</div>
        </div>
        """
        if i < len(stages) - 1:
            stages_html += f'<div style="display:flex;align-items:center;color:{FAINT};font-size:1.2rem;">→</div>'

    partial_badge = (
        f'<span style="font-size:0.65rem;background:{AGED_PAPER};color:{SMOKE};'
        f'padding:0.15rem 0.5rem;border-radius:9999px;font-weight:500;">Partial</span>'
        if is_partial else ""
    )

    st.markdown(f"""
    <div style="background:#FAF8F5;border:1px solid #D0CAC0;border-radius:10px;
                padding:1rem 1.25rem;margin-bottom:0.75rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
            <div>
                <span style="font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;
                      color:{CHARCOAL};">{journey.get("journey_name", "")}</span>
                <span style="font-size:0.8rem;color:{SMOKE};margin-left:0.5rem;">
                    {journey.get("persona", "")}
                </span>
            </div>
            <div style="display:flex;gap:0.4rem;align-items:center;">
                {partial_badge}
                <span style="font-size:0.65rem;font-weight:600;color:{conf_color};
                      text-transform:uppercase;letter-spacing:0.08em;
                      background:rgba(0,0,0,0.04);padding:0.15rem 0.5rem;border-radius:9999px;">
                    {confidence} confidence
                </span>
            </div>
        </div>
        <div style="display:flex;align-items:flex-start;overflow-x:auto;gap:0;">
            {stages_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_expectation_card(expectation):
    """Render an expectation card with persona tags and priority."""
    priority = expectation.get("priority", "medium")
    p_color = PRIORITY_COLORS.get(priority, SMOKE)
    personas = expectation.get("persona_tags", [])
    stage = expectation.get("journey_stage", "")
    freq = expectation.get("frequency", 1)

    tags = ""
    for p in personas:
        tags += (
            f'<span style="background:{AGED_PAPER};color:{SMOKE};padding:0.15rem 0.5rem;'
            f'border-radius:9999px;font-size:0.7rem;font-weight:500;">{p}</span> '
        )

    freq_html = ""
    if freq > 1:
        freq_html = (
            f'<span style="font-size:0.7rem;color:{PATINA};font-weight:600;">'
            f'{freq} witnesses mentioned this</span>'
        )

    st.markdown(f"""
    <div style="background:#FAF8F5;border:1px solid #D0CAC0;border-radius:10px;
                padding:1rem 1.25rem;margin-bottom:0.75rem;
                border-left:3px solid {p_color};">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
            <span style="font-size:0.65rem;font-weight:600;color:{p_color};
                  text-transform:uppercase;letter-spacing:0.08em;">{priority} priority</span>
            {freq_html}
        </div>
        <div style="font-size:0.9rem;color:{CHARCOAL};line-height:1.5;margin-bottom:0.5rem;">
            {expectation.get("description", "")}
        </div>
        <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
            {tags}
            {'<span style="background:' + AGED_PAPER + ';color:' + PATINA + ';padding:0.15rem 0.5rem;border-radius:9999px;font-size:0.7rem;font-weight:500;">' + stage + '</span>' if stage else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)
