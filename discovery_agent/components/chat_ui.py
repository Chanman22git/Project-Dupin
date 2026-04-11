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
                # Show clean version for file messages
                parts = content.split("--- File Content:", 1)
                header = parts[0].strip()
                st.markdown(header)
            else:
                st.markdown(content)

    # ── Embedded attach + input area ──
    if enable_file_upload:
        pending_file_key = f"pending_file_{session_key}"
        upload_key = f"file_upload_{session_key}"

        # Pending file indicator (shows above input like a chat attachment chip)
        pending = st.session_state.get(pending_file_key)
        if pending:
            col_chip, col_remove = st.columns([5, 1])
            with col_chip:
                st.markdown(
                    f'<div style="background:#E8E3D8;border:1px solid #D0CAC0;border-radius:8px;'
                    f'padding:0.35rem 0.75rem;font-size:0.8rem;color:#3D3D35;display:inline-flex;'
                    f'align-items:center;gap:0.4rem;margin-bottom:0.25rem;">'
                    f'📎 <strong>{pending["name"]}</strong>'
                    f'<span style="color:#8C8878;margin-left:0.25rem;">{len(pending["content"]):,} chars</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with col_remove:
                if st.button("✕", key=f"remove_file_{session_key}", help="Remove attachment"):
                    del st.session_state[pending_file_key]
                    st.rerun()

        # Compact file uploader styled as a small attach button
        # Hide the default label and make it minimal
        st.markdown(
            """<style>
            div[data-testid="stFileUploader"] > section > button {
                font-size: 0.8rem !important;
                padding: 0.2rem 0.6rem !important;
                border-radius: 6px !important;
            }
            div[data-testid="stFileUploader"] > label { display: none !important; }
            div[data-testid="stFileUploader"] { margin-bottom: -0.5rem !important; }
            div[data-testid="stFileUploader"] > section {
                padding: 0 !important;
                border: none !important;
            }
            </style>""",
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "📎",
            type=["md", "txt", "pdf", "docx", "doc", "csv", "json", "yaml", "yml"],
            key=upload_key,
            label_visibility="collapsed",
        )

        # Parse when new file uploaded
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
            # Clear pending
            del st.session_state[f"pending_file_{session_key}"]
            if f"parsed_id_{session_key}" in st.session_state:
                del st.session_state[f"parsed_id_{session_key}"]
        else:
            full_content = user_input

        with st.chat_message("user"):
            if pending:
                st.markdown(f"📎 **{pending['name']}** — {user_input}")
            else:
                st.markdown(user_input)

        messages.append({"role": "user", "content": full_content, "timestamp": _now()})
        st.session_state[session_key] = messages

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent_callback(messages)

        messages.append({"role": "assistant", "content": response, "timestamp": _now()})
        st.session_state[session_key] = messages

        st.rerun()
