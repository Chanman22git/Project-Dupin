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

IMPORTANT: When the user indicates they want to save what you've discussed (they say things like
"save this", "looks good", "that's it", "let's go with that", "save", "done", etc.),
include the marker {marker} at the very END of your response, after your conversational text.
Do NOT include this marker unless the user has clearly indicated readiness to save.
When you include the marker, also provide a brief confirmation of what you're saving."""


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
        current_state += f"\nCurrent description: {product_context['description']}"
    if product_context.get("documentation"):
        current_state += f"\nCurrent documentation: {product_context['documentation']}"
    if product_context.get("current_state"):
        current_state += f"\nCurrent product state: {product_context['current_state']}"

    system = PM_CONTEXT_SYSTEM_PROMPT
    if current_state:
        system += f"\n\nHere is what has been defined so far:{current_state}"
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
