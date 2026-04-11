from __future__ import annotations
import json
import time
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, DEFAULT_MAX_TOKENS, JSON_MAX_TOKENS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TRANSIENT_ERRORS = (
    anthropic.RateLimitError,
    anthropic.APIConnectionError,
    anthropic.InternalServerError,
)


class AgentError(Exception):
    """Raised when the agent cannot get a response after retries."""
    pass


def call_claude(system_prompt: str, messages: list[dict], max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    """Call Claude with automatic retry for transient errors."""
    last_error = None
    for attempt in range(2):
        try:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
            )
            return response.content[0].text
        except TRANSIENT_ERRORS as e:
            last_error = e
            if attempt == 0:
                time.sleep(2)
                continue
        except anthropic.AuthenticationError:
            raise AgentError(
                "API key is invalid or missing. Please check your ANTHROPIC_API_KEY configuration."
            )
        except anthropic.APIError as e:
            raise AgentError(f"API error: {str(e)}")

    raise AgentError(
        f"Dupin is temporarily unavailable. Please try again in a moment. ({type(last_error).__name__})"
    )


def call_claude_json(system_prompt: str, messages: list[dict]) -> dict:
    """Call Claude expecting a JSON response, with error handling."""
    response = call_claude(
        system_prompt + "\n\nRespond ONLY with valid JSON. No markdown, no explanation.",
        messages,
        max_tokens=JSON_MAX_TOKENS,
    )
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from the response if it's wrapped in markdown
        import re
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
        raise AgentError("Failed to parse the analysis response. Please try again.")
