from __future__ import annotations
import streamlit as st
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def render_chat(
    session_key: str,
    agent_callback,
    placeholder: str = "Type your message...",
    initial_assistant_message: str = None,
):
    """Render a reusable chat interface.

    Args:
        session_key: st.session_state key where message history (list of dicts) is stored.
        agent_callback: Callable that takes list[dict] messages and returns str response.
        placeholder: Placeholder text for the chat input.
        initial_assistant_message: Optional greeting shown if history is empty.
    """
    # Initialize with greeting if history is empty
    if session_key in st.session_state and not st.session_state[session_key]:
        if initial_assistant_message:
            st.session_state[session_key] = [
                {"role": "assistant", "content": initial_assistant_message, "timestamp": _now()}
            ]

    messages = st.session_state.get(session_key, [])

    # Render existing messages
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle new input
    if user_input := st.chat_input(placeholder, key=f"chat_input_{session_key}"):
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Append user message to history
        messages.append({"role": "user", "content": user_input, "timestamp": _now()})
        st.session_state[session_key] = messages

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent_callback(messages)

        # Append assistant response
        messages.append({"role": "assistant", "content": response, "timestamp": _now()})
        st.session_state[session_key] = messages

        st.rerun()
