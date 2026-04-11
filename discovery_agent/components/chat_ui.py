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
    """Render a chat interface with inline file attachment.

    Files are parsed and included as context in the user's next message.
    The file content is not stored — only used as conversation context.
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
            # Show a cleaner version for file messages
            content = msg.get("content", "")
            if content.startswith("[Attached:"):
                # Show just the attachment label, not the full content
                lines = content.split("\n", 3)
                st.markdown(lines[0])
                if len(lines) > 2:
                    with st.expander("View attached content", expanded=False):
                        st.markdown(lines[-1][:500] + ("..." if len(lines[-1]) > 500 else ""))
            else:
                st.markdown(content)

    # ── Input area: file attach + text input side by side ──
    if enable_file_upload:
        # Pending file in session state
        pending_file_key = f"pending_file_{session_key}"
        upload_key = f"file_upload_{session_key}"

        # File uploader — small, inline
        uploaded_file = st.file_uploader(
            "📎 Attach file",
            type=["md", "txt", "pdf", "docx", "doc", "csv", "json", "yaml", "yml"],
            key=upload_key,
            label_visibility="collapsed",
            help="Attach a file to include as context in your next message",
        )

        # Parse file when uploaded
        if uploaded_file is not None:
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.get(f"parsed_id_{session_key}") != file_id:
                from utils.file_parser import parse_uploaded_file
                file_content = parse_uploaded_file(uploaded_file)
                if file_content and not file_content.startswith("["):
                    if len(file_content) > 15000:
                        file_content = file_content[:15000] + "\n\n[... truncated ...]"
                    st.session_state[pending_file_key] = {
                        "name": uploaded_file.name,
                        "content": file_content,
                    }
                    st.session_state[f"parsed_id_{session_key}"] = file_id
                elif file_content.startswith("["):
                    st.warning(file_content)

        # Show pending file indicator
        pending = st.session_state.get(pending_file_key)
        if pending:
            st.markdown(
                f'<div style="background:#E8E3D8;border-radius:6px;padding:0.4rem 0.75rem;'
                f'margin-bottom:0.5rem;font-size:0.8rem;color:#3D3D35;display:inline-flex;'
                f'align-items:center;gap:0.4rem;">'
                f'📎 <strong>{pending["name"]}</strong> attached '
                f'<span style="color:#8C8878;">({len(pending["content"]):,} chars)</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Chat input
    if user_input := st.chat_input(placeholder, key=f"chat_input_{session_key}"):
        # Build the full message — text + any attached file
        pending = st.session_state.get(f"pending_file_{session_key}") if enable_file_upload else None

        if pending:
            full_content = (
                f"[Attached: **{pending['name']}**]\n\n"
                f"{user_input}\n\n"
                f"--- File Content: {pending['name']} ---\n"
                f"{pending['content']}\n"
                f"--- End File ---"
            )
            display_content = f"📎 **{pending['name']}** — {user_input}"
            # Clear the pending file
            del st.session_state[f"pending_file_{session_key}"]
            if f"parsed_id_{session_key}" in st.session_state:
                del st.session_state[f"parsed_id_{session_key}"]
        else:
            full_content = user_input
            display_content = user_input

        with st.chat_message("user"):
            st.markdown(display_content)

        messages.append({"role": "user", "content": full_content, "timestamp": _now()})
        st.session_state[session_key] = messages

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent_callback(messages)

        messages.append({"role": "assistant", "content": response, "timestamp": _now()})
        st.session_state[session_key] = messages

        st.rerun()
