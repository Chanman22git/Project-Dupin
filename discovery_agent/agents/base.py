from __future__ import annotations
import json
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, DEFAULT_MAX_TOKENS, JSON_MAX_TOKENS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def call_claude(system_prompt: str, messages: list[dict], max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text


def call_claude_json(system_prompt: str, messages: list[dict]) -> dict:
    response = call_claude(
        system_prompt + "\n\nRespond ONLY with valid JSON. No markdown, no explanation.",
        messages,
        max_tokens=JSON_MAX_TOKENS,
    )
    return json.loads(response)
