from __future__ import annotations
import re
from agents.base import call_claude
from agents.prompts import build_user_agent_prompt
from config import CONVERSATION_STATES

STATE_MARKER_PATTERN = re.compile(r"\[STATE:(\w+)\]\s*$")
COMPLETE_MARKER = "[CONVERSATION_COMPLETE]"


def _to_api_messages(messages):
    """Strip timestamps and extra fields, keep only role+content for the API."""
    return [{"role": m["role"], "content": m["content"]} for m in messages]


def _trim_history(messages, max_messages=50):
    """Keep first 2 messages (greeting context) and last N messages."""
    if len(messages) <= max_messages:
        return messages
    return messages[:2] + messages[-(max_messages - 2):]


def _count_user_messages(messages):
    """Count messages with role='user'."""
    return sum(1 for m in messages if m.get("role") == "user")


def extract_state_marker(response):
    """Extract state marker from response.
    Returns (state_or_None, clean_response)."""
    match = STATE_MARKER_PATTERN.search(response)
    if match:
        state = match.group(1)
        clean = STATE_MARKER_PATTERN.sub("", response).rstrip()
        if state in CONVERSATION_STATES:
            return state, clean
    return None, response


def detect_completion(response):
    """Check for completion marker.
    Returns (is_complete, clean_response)."""
    if COMPLETE_MARKER in response:
        clean = response.replace(COMPLETE_MARKER, "").strip()
        return True, clean
    return False, response


def extract_summary_from_response(response):
    """Extract the summary text from a SUMMARY state response."""
    return response.strip()


def infer_state_from_messages(messages):
    """Recover conversation state from stored messages.
    Scans from the end for the last state marker. Falls back to estimation."""
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            match = STATE_MARKER_PATTERN.search(msg.get("content", ""))
            if match and match.group(1) in CONVERSATION_STATES:
                return match.group(1)

    # Fallback: estimate from user message count
    user_count = _count_user_messages(messages)
    if user_count == 0:
        return "GREETING"
    elif user_count <= 2:
        return "ROLE_EXPLORATION"
    elif user_count <= 8:
        return "WORKFLOW_DEEP_DIVE"
    elif user_count <= 12:
        return "PAIN_POINTS"
    elif user_count <= 16:
        return "EXPECTATIONS"
    else:
        return "WRAP_UP"


def clean_messages_for_display(messages):
    """Strip state markers and completion markers from messages for UI display."""
    cleaned = []
    for msg in messages:
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            content = content.replace(COMPLETE_MARKER, "").strip()
            _, content = extract_state_marker(content)
            cleaned.append({**msg, "content": content})
        else:
            cleaned.append(msg)
    return cleaned


def get_user_agent_response(messages, product_context, session, link, conversation_state):
    """Get agent response for user discovery conversation.

    Args:
        messages: Full conversation history [{role, content, timestamp}].
        product_context: Product context dict from DB.
        session: Discovery session dict from DB.
        link: User session link dict from DB.
        conversation_state: Current conversation state string.

    Returns:
        Tuple of (clean_response, new_state, is_complete).
    """
    user_msg_count = _count_user_messages(messages)

    system_prompt = build_user_agent_prompt(
        product_context=product_context,
        session=session,
        link=link,
        conversation_state=conversation_state,
        user_message_count=user_msg_count,
    )

    api_messages = _to_api_messages(_trim_history(messages))
    raw_response = call_claude(system_prompt, api_messages)

    # Check for completion first
    is_complete, response = detect_completion(raw_response)

    # Extract state transition
    new_state, clean_response = extract_state_marker(response)
    if new_state is None:
        new_state = conversation_state  # Stay in current state

    return clean_response, new_state, is_complete
