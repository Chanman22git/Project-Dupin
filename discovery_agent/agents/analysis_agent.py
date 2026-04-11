from __future__ import annotations
import json
from agents.base import call_claude_json
from agents.prompts import build_analysis_prompt
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


def analyze_session(session_id):
    """Run full analysis on all completed interviews in a session.

    Returns a summary dict with counts of each type extracted.
    """
    session = DiscoverySessionDB.get(session_id)
    if not session:
        return {"error": "Session not found"}

    product_ctx = ProductContextDB.get(session["product_context_id"])
    if not product_ctx:
        return {"error": "Case not found"}

    conversations = ConversationDB.list_by_session(session_id)
    completed = [c for c in conversations if c.get("status") == "completed"]

    if not completed:
        return {"error": "No completed interviews to analyze"}

    # Build prompt and call Claude
    system_prompt = build_analysis_prompt(product_ctx, session, completed)
    messages = [
        {"role": "user", "content": "Analyze these interview transcripts and extract all findings."}
    ]

    try:
        results = call_claude_json(system_prompt, messages)
    except (json.JSONDecodeError, Exception) as e:
        return {"error": f"Analysis failed: {str(e)}"}

    # Store results
    counts = {
        "insights": 0,
        "discrepancies": 0,
        "journeys": 0,
        "expectations": 0,
        "context_improvements": 0,
    }

    # Store insights (pain points, workflows, feature requests, etc.)
    for insight in results.get("insights", []):
        InsightDB.create(
            discovery_session_id=session_id,
            type=insight.get("type", "pain_point"),
            title=insight.get("title", "Untitled"),
            description=insight.get("description", ""),
            evidence=insight.get("evidence", []),
            persona_tags=insight.get("persona_tags", []),
            journey_stage=insight.get("journey_stage"),
            priority=insight.get("priority", "medium"),
        )
        counts["insights"] += 1

    # Store discrepancies
    for disc in results.get("discrepancies", []):
        DiscrepancyDB.create(
            discovery_session_id=session_id,
            type=disc.get("type", "user_vs_user"),
            description=disc.get("description", ""),
            side_a=disc.get("side_a", {}),
            side_b=disc.get("side_b", {}),
            related_conversation_ids=disc.get("related_conversation_ids", []),
        )
        counts["discrepancies"] += 1

    # Store journeys
    for journey in results.get("journeys", []):
        UserJourneyDB.create(
            discovery_session_id=session_id,
            product_context_id=session["product_context_id"],
            journey_name=journey.get("journey_name", "Unnamed Journey"),
            persona=journey.get("persona", ""),
            stages=journey.get("stages", []),
            source_conversations=journey.get("source_conversations", []),
            confidence=journey.get("confidence", "low"),
            is_partial=journey.get("is_partial", True),
        )
        counts["journeys"] += 1

    # Store expectations
    for exp in results.get("expectations", []):
        ExpectationDB.create(
            discovery_session_id=session_id,
            product_context_id=session["product_context_id"],
            description=exp.get("description", ""),
            persona_tags=exp.get("persona_tags", []),
            journey_stage=exp.get("journey_stage"),
            priority=exp.get("priority", "medium"),
        )
        counts["expectations"] += 1

    # Store context improvements
    for imp in results.get("context_improvements", []):
        ContextImprovementDB.create(
            product_context_id=session["product_context_id"],
            discovery_session_id=session_id,
            suggestion_type=imp.get("suggestion_type", "new_info"),
            title=imp.get("title", "Untitled"),
            description=imp.get("description", ""),
            evidence=imp.get("evidence", []),
        )
        counts["context_improvements"] += 1

    return counts
