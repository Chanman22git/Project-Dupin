from __future__ import annotations
import json
import streamlit as st
from database.models import (
    ProductContextDB,
    DiscoverySessionDB,
    ConversationDB,
    InsightDB,
    DiscrepancyDB,
    UserJourneyDB,
    ExpectationDB,
    ContextImprovementDB,
)
from agents.base import call_claude
from agents.prompts import REPORT_SUMMARY_PROMPT
from components.styles import inject_custom_css
from components.graphics import (
    render_section_header,
    render_metric_card,
    render_empty_state,
    icon,
    COGNAC, PATINA, ALERT, SMOKE, COGNAC_LIGHT,
)
from components.guidance import render_page_guide, render_tab_guide
from components.insight_cards import (
    render_insight_card,
    render_discrepancy_card,
    render_expectation_card,
)
from components.journey_visualizer import render_journey_map
from utils.export import generate_investigation_markdown, generate_case_markdown

inject_custom_css()

render_page_guide(
    "The Dossier — Research Reports",
    "View comprehensive findings from your investigations. Generate an <strong>Investigation Dossier</strong> "
    "for a single research session, or a <strong>Case Dossier</strong> that aggregates insights across all "
    "investigations in a case. Export as markdown for sharing."
)

# ── Mode Selector ──
dossier_mode = st.radio(
    "Dossier Type",
    options=["Investigation Dossier", "Case Dossier"],
    horizontal=True,
    label_visibility="collapsed",
)

cases = ProductContextDB.list_all()

if not cases:
    render_empty_state("folder", "No cases yet", "Open a case and run investigations to generate dossiers.")
    st.stop()

# ═══════════════════════════════════════════════
# Investigation Dossier
# ═══════════════════════════════════════════════
if dossier_mode == "Investigation Dossier":
    # Selectors
    col_case, col_inv = st.columns(2)

    with col_case:
        case_names = {c["id"]: c["name"] for c in cases}
        selected_case_id = st.selectbox(
            "Select Case",
            options=list(case_names.keys()),
            format_func=lambda x: case_names[x],
        )

    investigations = DiscoverySessionDB.list_by_context(selected_case_id)
    if not investigations:
        render_empty_state("magnifier", "No investigations in this case yet")
        st.stop()

    with col_inv:
        inv_names = {s["id"]: s["name"] for s in investigations}
        selected_inv_id = st.selectbox(
            "Select Investigation",
            options=list(inv_names.keys()),
            format_func=lambda x: inv_names[x],
        )

    session = DiscoverySessionDB.get(selected_inv_id)
    product_ctx = ProductContextDB.get(selected_case_id)

    # Load data
    insights = InsightDB.list_by_session(selected_inv_id)
    discrepancies = DiscrepancyDB.list_by_session(selected_inv_id)
    journeys = UserJourneyDB.list_by_session(selected_inv_id)
    expectations = ExpectationDB.list_by_session(selected_inv_id)
    conversations = ConversationDB.list_by_session(selected_inv_id)
    completed = [c for c in conversations if c.get("status") == "completed"]

    has_data = insights or discrepancies or journeys or expectations

    if not has_data:
        render_empty_state(
            "magnifier",
            "No analysis data for this investigation",
            f"{len(completed)} completed interview(s). Go to the Investigation page and click 'Analyze Interviews' first.",
        )
        st.stop()

    st.divider()

    # ── Header ──
    st.markdown(f"""
    <div style="margin-bottom:1rem;">
        <h2 style="margin-bottom:0.25rem !important;">{session.get('name', '')}</h2>
        <p style="color:#8C8878 !important; font-size:0.9rem;">
            {session.get('objective', '')} | {len(completed)} interview(s) analyzed
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Download ──
    col_dl, _ = st.columns([1, 3])
    with col_dl:
        md_content = generate_investigation_markdown(selected_inv_id)
        st.download_button(
            "Download Dossier (.md)",
            data=md_content,
            file_name=f"dossier_{session.get('name', 'report').replace(' ', '_').lower()}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # ── Executive Summary ──
    render_section_header("document", "Executive Summary")

    summary_key = f"exec_summary_{selected_inv_id}"
    if summary_key not in st.session_state:
        # Generate summary via Claude
        findings_text = json.dumps({
            "objective": session.get("objective", ""),
            "scope": session.get("scope", ""),
            "interviews_completed": len(completed),
            "pain_points": [{"title": i["title"], "priority": i["priority"], "description": i["description"]}
                           for i in insights if i.get("type") == "pain_point"],
            "key_insights": [{"title": i["title"], "type": i["type"]}
                            for i in insights if i.get("type") != "pain_point"][:5],
            "journeys": [{"name": j["journey_name"], "confidence": j["confidence"],
                         "stages": len(j.get("stages", []))} for j in journeys],
            "expectations_count": len(expectations),
            "discrepancies_count": len(discrepancies),
        }, indent=2)

        try:
            summary = call_claude(
                REPORT_SUMMARY_PROMPT,
                [{"role": "user", "content": f"Investigation findings:\n{findings_text}"}],
            )
            st.session_state[summary_key] = summary
        except Exception:
            st.session_state[summary_key] = "Executive summary could not be generated."

    st.markdown(
        f'<div style="font-size:0.95rem;color:#3D3D35;line-height:1.75;padding:0.5rem 0;">'
        f'{st.session_state[summary_key]}</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Metrics ──
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("lightbulb", "Insights", len(insights), COGNAC)
    with m2:
        render_metric_card("target", "Journeys", len(journeys), PATINA)
    with m3:
        render_metric_card("users", "Expectations", len(expectations), COGNAC_LIGHT)
    with m4:
        render_metric_card("warning", "Contradictions", len(discrepancies), ALERT)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    # ── Sections ──
    report_tabs = st.tabs(["Journeys", "Pain Points", "Expectations", "Contradictions", "Key Quotes"])

    with report_tabs[0]:
        render_tab_guide("User journey maps extracted from interviews.")
        if journeys:
            for j in journeys:
                render_journey_map(j)
        else:
            render_empty_state("target", "No journeys mapped")

    with report_tabs[1]:
        render_tab_guide("Pain points grouped by severity.")
        pain_points = [i for i in insights if i.get("type") == "pain_point"]
        other = [i for i in insights if i.get("type") != "pain_point"]
        if pain_points:
            for p in sorted(pain_points, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("priority"), 1)):
                render_insight_card(p)
        if other:
            st.divider()
            render_section_header("layers", "Other Insights")
            for o in other:
                render_insight_card(o)
        if not pain_points and not other:
            render_empty_state("lightbulb", "No insights extracted")

    with report_tabs[2]:
        render_tab_guide("What users want, ranked by priority.")
        if expectations:
            for exp in sorted(expectations, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("priority"), 2)):
                render_expectation_card(exp)
        else:
            render_empty_state("users", "No expectations captured")

    with report_tabs[3]:
        render_tab_guide("Conflicting information found across interviews or against the case brief.")
        if discrepancies:
            for d in discrepancies:
                render_discrepancy_card(d)
        else:
            render_empty_state("warning", "No contradictions found")

    with report_tabs[4]:
        render_tab_guide("Notable quotes from interview evidence.")
        quotes_found = False
        for ins in insights:
            for e in ins.get("evidence", []):
                quote = e.get("quote", str(e)) if isinstance(e, dict) else str(e)
                if quote:
                    quotes_found = True
                    st.markdown(f"""
                    <div style="border-left:3px solid {COGNAC};padding:0.5rem 0.75rem;
                                margin-bottom:0.5rem;background:#FAF8F5;border-radius:0 6px 6px 0;">
                        <div style="font-size:0.9rem;color:#3D3D35;font-style:italic;line-height:1.5;">
                            "{quote}"
                        </div>
                        <div style="font-size:0.75rem;color:#8C8878;margin-top:0.25rem;">
                            Re: {ins.get('title', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        if not quotes_found:
            render_empty_state("chat", "No quotes extracted from evidence")


# ═══════════════════════════════════════════════
# Case Dossier (Cross-Investigation)
# ═══════════════════════════════════════════════
else:
    case_names = {c["id"]: c["name"] for c in cases}
    selected_case_id = st.selectbox(
        "Select Case",
        options=list(case_names.keys()),
        format_func=lambda x: case_names[x],
    )

    product_ctx = ProductContextDB.get(selected_case_id)
    investigations = DiscoverySessionDB.list_by_context(selected_case_id)

    if not investigations:
        render_empty_state("magnifier", "No investigations in this case yet")
        st.stop()

    # Aggregate all data across investigations
    all_insights = []
    all_discrepancies = []
    all_journeys = []
    all_expectations = []
    total_interviews = 0

    for inv in investigations:
        sid = inv["id"]
        all_insights.extend(InsightDB.list_by_session(sid))
        all_discrepancies.extend(DiscrepancyDB.list_by_session(sid))
        all_journeys.extend(UserJourneyDB.list_by_session(sid))
        all_expectations.extend(ExpectationDB.list_by_session(sid))
        convs = ConversationDB.list_by_session(sid)
        total_interviews += sum(1 for c in convs if c.get("status") == "completed")

    has_data = all_insights or all_discrepancies or all_journeys or all_expectations

    if not has_data:
        render_empty_state(
            "folder",
            "No analysis data across investigations",
            "Run interviews and analyze them to populate the case dossier.",
        )
        st.stop()

    st.divider()

    # ── Header ──
    st.markdown(f"""
    <div style="margin-bottom:1rem;">
        <h2 style="margin-bottom:0.25rem !important;">Case Dossier: {product_ctx.get('name', '')}</h2>
        <p style="color:#8C8878 !important; font-size:0.9rem;">
            {len(investigations)} investigation(s) | {total_interviews} interview(s) analyzed
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Download ──
    col_dl, _ = st.columns([1, 3])
    with col_dl:
        md_content = generate_case_markdown(selected_case_id)
        st.download_button(
            "Download Case Dossier (.md)",
            data=md_content,
            file_name=f"case_dossier_{product_ctx.get('name', 'case').replace(' ', '_').lower()}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # ── Metrics ──
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_metric_card("magnifier", "Investigations", len(investigations), COGNAC)
    with m2:
        render_metric_card("lightbulb", "Insights", len(all_insights), COGNAC_LIGHT)
    with m3:
        render_metric_card("target", "Journeys", len(all_journeys), PATINA)
    with m4:
        render_metric_card("users", "Expectations", len(all_expectations), SMOKE)
    with m5:
        render_metric_card("warning", "Contradictions", len(all_discrepancies), ALERT)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    # ── Investigations Overview ──
    render_section_header("magnifier", "Investigations")
    for inv in investigations:
        inv_insights = [i for i in all_insights if i.get("discovery_session_id") == inv["id"]]
        status = inv.get("status", "draft")
        st.markdown(f"""
        <div style="background:#FAF8F5;border:1px solid #D0CAC0;border-radius:8px;
                    padding:0.75rem 1rem;margin-bottom:0.5rem;display:flex;
                    justify-content:space-between;align-items:center;">
            <div>
                <span style="font-weight:600;color:#3D3D35;">{inv.get('name', '')}</span>
                <span style="color:#8C8878;font-size:0.85rem;margin-left:0.5rem;">{inv.get('objective', '')[:80]}</span>
            </div>
            <div style="display:flex;gap:0.75rem;align-items:center;">
                <span style="font-size:0.8rem;color:#C4823A;font-weight:600;">{len(inv_insights)} insights</span>
                <span class="status-pill {status}">{status.title()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Aggregated Sections ──
    case_tabs = st.tabs(["All Journeys", "Pain Points", "Expectations", "Contradictions", "New Leads"])

    with case_tabs[0]:
        render_tab_guide("All user journeys mapped across investigations.")
        if all_journeys:
            for j in all_journeys:
                render_journey_map(j)
        else:
            render_empty_state("target", "No journeys mapped across investigations")

    with case_tabs[1]:
        render_tab_guide("All pain points aggregated and sorted by severity.")
        pain_points = [i for i in all_insights if i.get("type") == "pain_point"]
        if pain_points:
            for p in sorted(pain_points, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("priority"), 1)):
                render_insight_card(p)
        else:
            render_empty_state("warning", "No pain points found across investigations")

    with case_tabs[2]:
        render_tab_guide("User expectations from all investigations, ranked by priority.")
        if all_expectations:
            for exp in sorted(all_expectations, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("priority"), 2)):
                render_expectation_card(exp)
        else:
            render_empty_state("users", "No expectations captured")

    with case_tabs[3]:
        render_tab_guide("All contradictions found across interviews and investigations.")
        if all_discrepancies:
            for d in all_discrepancies:
                render_discrepancy_card(d)
        else:
            render_empty_state("warning", "No contradictions found")

    with case_tabs[4]:
        render_tab_guide("Suggestions for updating the case brief based on investigation findings.")
        improvements = ContextImprovementDB.list_by_context(selected_case_id)
        if improvements:
            for imp in improvements:
                stype = imp.get("suggestion_type", "gap")
                st.markdown(f'<div class="improvement-card {stype}">', unsafe_allow_html=True)
                with st.container():
                    st.markdown(f"**{imp.get('title', '')}**")
                    st.markdown(
                        f'<span class="status-pill {stype}">{stype.replace("_", " ").title()}</span>',
                        unsafe_allow_html=True,
                    )
                    st.write(imp.get("description", ""))
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            render_empty_state("lightbulb", "No new leads from investigations")
