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
    """Render a chat interface with inline file attachment."""
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
            content = msg.get("content", "")
            if "[Attached:" in content and "--- File Content:" in content:
                parts = content.split("--- File Content:", 1)
                header = parts[0].strip()
                st.markdown(header)
            else:
                st.markdown(content)

    # ── Attach + Input area ──
    if enable_file_upload:
        pending_file_key = f"pending_file_{session_key}"
        upload_key = f"file_upload_{session_key}"

        # Show pending file chip
        pending = st.session_state.get(pending_file_key)
        if pending:
            col_chip, col_remove = st.columns([5, 1])
            with col_chip:
                st.info(f"📎 **{pending['name']}** attached ({len(pending['content']):,} chars) — type your message below")
            with col_remove:
                if st.button("Remove", key=f"remove_file_{session_key}"):
                    del st.session_state[pending_file_key]
                    st.rerun()

        # File uploader with expander to keep it compact
        with st.expander("📎 Attach a file", expanded=False):
            uploaded_file = st.file_uploader(
                "Select file",
                type=["md", "txt", "pdf", "docx", "doc", "csv", "json", "yaml", "yml"],
                key=upload_key,
                label_visibility="collapsed",
            )

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
                        st.rerun()
                    elif file_content.startswith("["):
                        st.warning(file_content)
                        st.session_state[f"parsed_id_{session_key}"] = file_id

    # Chat input
    if user_input := st.chat_input(placeholder, key=f"chat_input_{session_key}"):
        pending = st.session_state.get(f"pending_file_{session_key}") if enable_file_upload else None

        if pending:
            full_content = (
                f"[Attached: **{pending['name']}**] {user_input}\n\n"
                f"--- File Content: {pending['name']} ---\n"
                f"{pending['content']}\n"
                f"--- End File ---"
            )
            display = f"📎 **{pending['name']}** — {user_input}"
            del st.session_state[f"pending_file_{session_key}"]
            if f"parsed_id_{session_key}" in st.session_state:
                del st.session_state[f"parsed_id_{session_key}"]
        else:
            full_content = user_input
            display = user_input

        with st.chat_message("user"):
            st.markdown(display)

        messages.append({"role": "user", "content": full_content, "timestamp": _now()})
        st.session_state[session_key] = messages

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent_callback(messages)

        messages.append({"role": "assistant", "content": response, "timestamp": _now()})
        st.session_state[session_key] = messages

        st.rerun()
