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
    enable_file_upload: bool = True,
):
    """Render a reusable chat interface with optional file upload.

    Args:
        session_key: st.session_state key where message history (list of dicts) is stored.
        agent_callback: Callable that takes list[dict] messages and returns str response.
        placeholder: Placeholder text for the chat input.
        initial_assistant_message: Optional greeting shown if history is empty.
        enable_file_upload: Whether to show the file upload button above the chat.
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

    # File upload area
    if enable_file_upload:
        upload_key = f"file_upload_{session_key}"
        uploaded_file = st.file_uploader(
            "Attach a file",
            type=["md", "txt", "pdf", "docx", "doc", "csv", "json", "yaml", "yml"],
            key=upload_key,
            label_visibility="collapsed",
            help="Attach .md, .txt, .pdf, .docx, .csv, .json, or .yaml files",
        )

        if uploaded_file is not None:
            # Check if we already processed this file (avoid re-processing on rerun)
            processed_key = f"processed_file_{session_key}"
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.get(processed_key) != file_id:
                from utils.file_parser import parse_uploaded_file
                file_content = parse_uploaded_file(uploaded_file)

                if file_content and not file_content.startswith("["):
                    # Truncate very large files
                    if len(file_content) > 15000:
                        file_content = file_content[:15000] + "\n\n[... truncated, file too large to include fully ...]"

                    # Add as user message with file context
                    file_msg = (
                        f"I'm attaching a file: **{uploaded_file.name}**\n\n"
                        f"---\n{file_content}\n---"
                    )
                    with st.chat_message("user"):
                        st.markdown(f"Attached: **{uploaded_file.name}** ({len(file_content):,} chars)")

                    messages.append({"role": "user", "content": file_msg, "timestamp": _now()})
                    st.session_state[session_key] = messages
                    st.session_state[processed_key] = file_id

                    # Get agent response
                    with st.chat_message("assistant"):
                        with st.spinner("Reading file..."):
                            response = agent_callback(messages)

                    messages.append({"role": "assistant", "content": response, "timestamp": _now()})
                    st.session_state[session_key] = messages
                    st.rerun()
                elif file_content.startswith("["):
                    st.warning(file_content)
                    st.session_state[processed_key] = file_id

    # Handle text input
    if user_input := st.chat_input(placeholder, key=f"chat_input_{session_key}"):
        with st.chat_message("user"):
            st.markdown(user_input)

        messages.append({"role": "user", "content": user_input, "timestamp": _now()})
        st.session_state[session_key] = messages

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent_callback(messages)

        messages.append({"role": "assistant", "content": response, "timestamp": _now()})
        st.session_state[session_key] = messages

        st.rerun()
