from __future__ import annotations
import json
import streamlit as st
from database.models import ProductContextDB, DiscoverySessionDB, ContextImprovementDB
from agents.pm_agent import (
    get_context_agent_response,
    detect_save,
    extract_product_context,
    SAVE_MARKER,
)
from components.chat_ui import render_chat

ctx_id = st.session_state.get("selected_context_id")
if not ctx_id:
    st.warning("No product context selected.")
    if st.button("Go to Home"):
        st.switch_page("pages/1_Home.py")
    st.stop()

ctx = ProductContextDB.get(ctx_id)
if not ctx:
    st.error("Product context not found.")
    st.stop()

# --- Editable name ---
new_name = st.text_input("Context Name", value=ctx["name"], key=f"ctx_name_{ctx_id}")
if new_name != ctx["name"]:
    ProductContextDB.update(ctx_id, name=new_name)
    ctx["name"] = new_name

# --- Tabs ---
tab_overview, tab_sessions, tab_improvements = st.tabs(
    ["Overview", "Discovery Sessions", "Context Improvements"]
)

# ── Overview Tab ──
with tab_overview:
    col_display, col_chat = st.columns([1, 1])

    with col_display:
        st.subheader("Product Description")
        st.write(ctx.get("description") or "_Not defined yet. Chat with the assistant to set this up._")

        st.subheader("Documentation")
        st.write(ctx.get("documentation") or "_No documentation added yet._")

        st.subheader("Current State")
        st.write(ctx.get("current_state") or "_Not defined yet._")

    with col_chat:
        st.subheader("Setup Assistant")

        # Initialize chat history from DB
        chat_key = f"pm_context_chat_{ctx_id}"
        if chat_key not in st.session_state:
            saved = ctx.get("context_conversation_history", [])
            if isinstance(saved, str):
                saved = json.loads(saved) if saved else []
            st.session_state[chat_key] = saved

        def context_agent_callback(messages):
            raw_response = get_context_agent_response(messages, ctx)
            should_save, clean_response = detect_save(raw_response, SAVE_MARKER)

            if should_save:
                with st.spinner("Saving context..."):
                    # Include the clean response in extraction
                    full_messages = messages + [
                        {"role": "assistant", "content": clean_response}
                    ]
                    extracted = extract_product_context(full_messages)

                    update_kwargs = {}
                    for field in ["name", "description", "documentation", "current_state"]:
                        val = extracted.get(field)
                        if val and val != "null":
                            update_kwargs[field] = val

                    # Persist conversation history along with the save
                    update_kwargs["context_conversation_history"] = (
                        st.session_state[chat_key]
                        + [{"role": "assistant", "content": clean_response}]
                    )
                    ProductContextDB.update(ctx_id, **update_kwargs)

            return clean_response

        render_chat(
            session_key=chat_key,
            agent_callback=context_agent_callback,
            placeholder="Describe your product, paste docs, or say 'save this'...",
            initial_assistant_message=(
                "Hi! I'm here to help you define your product context. "
                "Tell me about the product you're researching — what is it, "
                "who uses it, and what does it currently do? You can also paste "
                "any documentation or specs you have."
            ),
        )

# ── Discovery Sessions Tab ──
with tab_sessions:
    sessions = DiscoverySessionDB.list_by_context(ctx_id)

    if st.button("+ Create New Discovery Session", type="primary"):
        new_session = DiscoverySessionDB.create(
            product_context_id=ctx_id,
            name="Untitled Session",
        )
        st.session_state["selected_session_id"] = new_session["id"]
        st.switch_page("pages/3_Discovery_Session.py")

    if not sessions:
        st.info("No discovery sessions yet.")
    else:
        for session in sessions:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    status_colors = {"draft": "grey", "active": "green", "completed": "blue"}
                    st.markdown(f"### {session['name']}")
                    st.caption(
                        f"Status: :{status_colors.get(session['status'], 'grey')}[{session['status']}]"
                        f" | Updated: {session['updated_at'][:10]}"
                    )
                    if session.get("objective"):
                        st.write(session["objective"][:150])
                with col2:
                    if st.button("Open", key=f"open_session_{session['id']}"):
                        st.session_state["selected_session_id"] = session["id"]
                        st.switch_page("pages/3_Discovery_Session.py")

# ── Context Improvements Tab ──
with tab_improvements:
    improvements = ContextImprovementDB.list_by_context(ctx_id)
    if not improvements:
        st.info("No context improvement suggestions yet. Run discovery sessions to generate them.")
    else:
        for imp in improvements:
            with st.container(border=True):
                st.markdown(f"**{imp['title']}** ({imp['suggestion_type']})")
                st.write(imp.get("description", ""))
                col1, col2, _ = st.columns([1, 1, 4])
                with col1:
                    if imp["status"] == "pending" and st.button("Accept", key=f"acc_{imp['id']}"):
                        ContextImprovementDB.update_status(imp["id"], "accepted")
                        st.rerun()
                with col2:
                    if imp["status"] == "pending" and st.button("Reject", key=f"rej_{imp['id']}"):
                        ContextImprovementDB.update_status(imp["id"], "rejected")
                        st.rerun()
