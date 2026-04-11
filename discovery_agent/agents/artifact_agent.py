from __future__ import annotations
import re
from agents.base import call_claude, AgentError
from agents.prompts import build_artifact_prompt

ARTIFACT_START = "[ARTIFACT_START]"
ARTIFACT_END = "[ARTIFACT_END]"
ARTIFACT_READY = "[ARTIFACT_READY]"


def _to_api_messages(messages):
    return [{"role": m["role"], "content": m["content"]} for m in messages]


def _trim_history(messages, max_messages=40):
    if len(messages) <= max_messages:
        return messages
    return messages[:2] + messages[-(max_messages - 2):]


def _build_case_context(product_context):
    """Build a text summary of everything known about the case."""
    parts = []
    if product_context.get("name"):
        parts.append(f"Case: {product_context['name']}")
    if product_context.get("description"):
        parts.append(f"Subject: {product_context['description']}")
    if product_context.get("documentation"):
        parts.append(f"Evidence & Documentation: {product_context['documentation']}")
    if product_context.get("current_state"):
        parts.append(f"Current State: {product_context['current_state']}")
    return "\n".join(parts) if parts else "No case details available yet."


def extract_artifact_content(response):
    """Extract content between [ARTIFACT_START] and [ARTIFACT_END] markers.
    Returns (content, clean_response) where clean_response has markers stripped."""
    pattern = re.compile(
        re.escape(ARTIFACT_START) + r"(.*?)" + re.escape(ARTIFACT_END),
        re.DOTALL,
    )
    match = pattern.search(response)
    if match:
        content = match.group(1).strip()
        # Clean the response for display — remove markers but keep conversational text
        clean = response[:match.start()].strip()
        after = response[match.end():].strip()
        if after:
            clean = clean + "\n\n" + after if clean else after
        clean = clean.replace(ARTIFACT_READY, "").strip()
        return content, clean
    # No markers found — return empty content, full response
    return "", response.replace(ARTIFACT_READY, "").strip()


def detect_artifact_ready(response):
    """Check if the PM has approved and artifact is ready to save."""
    is_ready = ARTIFACT_READY in response
    clean = response.replace(ARTIFACT_READY, "").strip()
    return is_ready, clean


def get_artifact_response(messages, product_context, artifact_type,
                          reference_artifact=None):
    """Get Dupin's response for artifact generation/refinement.

    Returns (clean_response, artifact_content, is_ready).
    - clean_response: conversational text to display in chat
    - artifact_content: extracted content for preview (empty if none generated yet)
    - is_ready: True if PM approved and artifact is finalized
    """
    case_context = _build_case_context(product_context)
    system_prompt = build_artifact_prompt(case_context, artifact_type, reference_artifact)

    api_messages = _to_api_messages(_trim_history(messages))
    raw_response = call_claude(system_prompt, api_messages, max_tokens=8192)

    is_ready, response = detect_artifact_ready(raw_response)
    artifact_content, clean_response = extract_artifact_content(response)

    return clean_response, artifact_content, is_ready
