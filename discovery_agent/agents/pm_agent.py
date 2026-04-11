from __future__ import annotations
import json
from agents.base import call_claude, call_claude_json
from agents.prompts import (
    PM_CONTEXT_SYSTEM_PROMPT,
    PM_SESSION_SYSTEM_PROMPT,
    CONTEXT_EXTRACTION_PROMPT,
    SESSION_EXTRACTION_PROMPT,
)

SAVE_MARKER = "[SAVE_CONTEXT]"
SESSION_SAVE_MARKER = "[SAVE_SESSION]"

_SAVE_INSTRUCTION = """

SAVING BEHAVIOR:
After every response, assess whether you've gathered meaningful new information. If so,
include the marker {marker} at the very END of your response (the user won't see it).

Include the marker when:
- The user has shared substantive product details (description, users, features, docs)
- The user has provided or updated documentation, specs, or current state info
- The user confirms or corrects something you summarized
- The user says "save", "done", "looks good", etc.

Do NOT include the marker when:
- You're still asking clarifying questions and haven't received answers yet
- The user only said "hi" or gave a very brief non-informative reply
- You're in the middle of probing for more details

When you include the marker, naturally continue the conversation — ask what else to explore,
or suggest what to do next. Don't announce that you're saving."""


def _trim_history(messages: list[dict], max_messages: int = 40) -> list[dict]:
    """Truncate long conversation histories to stay within token limits."""
    if len(messages) <= max_messages:
        return messages
    return messages[:2] + messages[-(max_messages - 2):]


def _to_api_messages(messages: list[dict]) -> list[dict]:
    """Strip timestamps and extra fields, keep only role+content for the API."""
    return [{"role": m["role"], "content": m["content"]} for m in messages]


def detect_save(response: str, marker: str) -> tuple:
    """Check if the response contains a save marker.
    Returns (should_save, clean_response) with marker stripped."""
    if marker in response:
        clean = response.replace(marker, "").strip()
        return True, clean
    return False, response


def get_context_agent_response(messages: list[dict], product_context: dict) -> str:
    """Get a conversational response from the PM context setup agent."""
    current_state = ""
    if product_context.get("description"):
        current_state += f"\nSubject: {product_context['description']}"
    if product_context.get("documentation"):
        current_state += f"\nEvidence & Documentation: {product_context['documentation']}"
    if product_context.get("current_state"):
        current_state += f"\nCurrent State of Affairs: {product_context['current_state']}"

    # Include case history so Dupin can explain past decisions
    history = product_context.get("case_history", [])
    history_text = ""
    if history:
        recent = history[-10:]  # Last 10 entries
        history_lines = []
        for h in recent:
            history_lines.append(f"  [{h.get('timestamp', '')[:16]}] {h.get('source', 'PM')}: {h.get('action', '')} — {h.get('details', '')}")
        history_text = "\n\nCASE HISTORY (how the brief evolved — use this to answer questions about past decisions):\n" + "\n".join(history_lines)

    system = PM_CONTEXT_SYSTEM_PROMPT
    if current_state:
        system += f"\n\nCURRENT CASE BRIEF:{current_state}"
    if history_text:
        system += history_text
    system += _SAVE_INSTRUCTION.format(marker=SAVE_MARKER)

    api_messages = _to_api_messages(_trim_history(messages))
    return call_claude(system, api_messages)


def get_session_agent_response(messages: list[dict], session: dict, product_context: dict) -> str:
    """Get a conversational response from the PM session setup agent."""
    context_summary = ""
    if product_context.get("name"):
        context_summary += f"\nProduct: {product_context['name']}"
    if product_context.get("description"):
        context_summary += f"\nProduct description: {product_context['description'][:500]}"

    session_state = ""
    if session.get("objective"):
        session_state += f"\nCurrent objective: {session['objective']}"
    if session.get("scope"):
        session_state += f"\nCurrent scope: {session['scope']}"
    personas = session.get("target_personas", [])
    if personas:
        session_state += f"\nCurrent personas: {json.dumps(personas)}"
    behavior = session.get("agent_behavior", {})
    if behavior:
        session_state += f"\nCurrent agent behavior config: {json.dumps(behavior)}"

    system = PM_SESSION_SYSTEM_PROMPT
    if context_summary:
        system += f"\n\nPRODUCT CONTEXT:{context_summary}"
    if session_state:
        system += f"\n\nHere is what has been configured so far:{session_state}"
    system += _SAVE_INSTRUCTION.format(marker=SESSION_SAVE_MARKER)

    api_messages = _to_api_messages(_trim_history(messages))
    return call_claude(system, api_messages)


def extract_product_context(messages: list[dict]) -> dict:
    """Extract structured product context data from conversation history."""
    api_messages = _to_api_messages(messages)
    # Add the full conversation as a user message for the extraction call
    conversation_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in api_messages
    )
    extraction_messages = [
        {"role": "user", "content": f"Here is the conversation:\n\n{conversation_text}\n\nExtract the product context."}
    ]
    try:
        return call_claude_json(CONTEXT_EXTRACTION_PROMPT, extraction_messages)
    except (json.JSONDecodeError, Exception):
        return {}


def extract_session_config(messages: list[dict]) -> dict:
    """Extract structured session configuration from conversation history."""
    api_messages = _to_api_messages(messages)
    conversation_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in api_messages
    )
    extraction_messages = [
        {"role": "user", "content": f"Here is the conversation:\n\n{conversation_text}\n\nExtract the session configuration."}
    ]
    try:
        return call_claude_json(SESSION_EXTRACTION_PROMPT, extraction_messages)
    except (json.JSONDecodeError, Exception):
        return {}
