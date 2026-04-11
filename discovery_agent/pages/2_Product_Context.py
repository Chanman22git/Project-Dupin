from __future__ import annotations
import json
import streamlit as st
from database.models import ProductContextDB, DiscoverySessionDB, ContextImprovementDB, ArtifactDB
from agents.base import AgentError
from agents.pm_agent import (
    get_context_agent_response,
    detect_save,
    extract_product_context,
    SAVE_MARKER,
)
from agents.artifact_agent import get_artifact_response, extract_artifact_content, ARTIFACT_READY
from components.chat_ui import render_chat
from components.styles import inject_custom_css
from components.graphics import (
    render_section_header,
    render_info_field,
    render_progress_ring,
    render_status_pill,
    render_empty_state,
    icon,
)
from components.guidance import render_page_guide, render_tab_guide
from components.artifact_viewer import render_artifact_card, render_artifact_preview
from utils.export import export_artifact_to_docx, export_artifact_to_pptx

inject_custom_css()

ctx_id = st.session_state.get("selected_context_id")
if not ctx_id:
    st.warning("No case selected.")
    if st.button("Go to Case Board"):
        st.switch_page("pages/1_Home.py")
    st.stop()

ctx = ProductContextDB.get(ctx_id)
if not ctx:
    st.error("Case not found.")
    st.stop()

# ── Header ──
col_name, col_back = st.columns([4, 1])
with col_name:
    new_name = st.text_input(
        "Case Name", value=ctx["name"], key=f"ctx_name_{ctx_id}", label_visibility="collapsed"
    )
    if new_name != ctx["name"]:
        ProductContextDB.update(ctx_id, name=new_name)
        ctx["name"] = new_name
with col_back:
    if st.button("< Case Board", use_container_width=True):
        st.switch_page("pages/1_Home.py")

render_page_guide(
    "Case File — Product Definition",
    "A <strong>Case</strong> is your product or initiative. Build the case brief by chatting with Dupin, "
    "then launch <strong>Investigations</strong> (focused research sessions) to interview users."
)

# ── Tabs ──
tab_overview, tab_investigations, tab_leads, tab_artifacts = st.tabs(
    ["Case Brief", "Investigations", "New Leads", "Artifacts"]
)

# ═══════════════════════════════════════════════
# Case Brief Tab — Always Split: Evidence Board + Dupin Chat
# ═══════════════════════════════════════════════
with tab_overview:
    render_tab_guide(
        "The left panel shows everything Dupin knows about this case. "
        "Chat on the right to add details, ask questions, or update the brief. Changes are tracked."
    )

    # Chat state init
    chat_key = f"pm_context_chat_{ctx_id}"
    if chat_key not in st.session_state:
        saved = ctx.get("context_conversation_history", [])
        if isinstance(saved, str):
            saved = json.loads(saved) if saved else []
        st.session_state[chat_key] = saved

    def context_agent_callback(messages):
        try:
            raw_response = get_context_agent_response(messages, ctx)
        except (AgentError, Exception) as e:
            return f"I'm having a brief connection issue. Please try again. ({type(e).__name__})"
        _, clean_response = detect_save(raw_response, SAVE_MARKER)

        # Count user messages — auto-extract after every substantive exchange
        user_msg_count = sum(1 for m in messages if m.get("role") == "user")
        should_extract = user_msg_count >= 1  # Extract after every user message

        if should_extract:
            try:
                full_messages = messages + [
                    {"role": "assistant", "content": clean_response}
                ]
                extracted = extract_product_context(full_messages)
                update_kwargs = {}
                changes = []
                for field in ["name", "description", "documentation", "current_state"]:
                    val = extracted.get(field)
                    if val and val != "null" and val.strip():
                        old_val = ctx.get(field, "") or ""
                        if val != old_val:
                            update_kwargs[field] = val
                            field_label = {"description": "Subject", "documentation": "Evidence & Documentation",
                                           "current_state": "Current State", "name": "Case Name"}.get(field, field)
                            if old_val.strip():
                                changes.append(f"Updated {field_label}")
                            else:
                                changes.append(f"Added {field_label}")
                # Generate one-liner summary from whatever we know
                desc_val = update_kwargs.get("description", ctx.get("description", ""))
                state_val = update_kwargs.get("current_state", ctx.get("current_state", ""))
                if desc_val:
                    # Build a brief summary: first sentence of description, max 120 chars
                    first_sentence = desc_val.split(".")[0].strip()
                    if len(first_sentence) > 120:
                        first_sentence = first_sentence[:117] + "..."
                    update_kwargs["summary"] = first_sentence

                # Always save conversation history
                update_kwargs["context_conversation_history"] = (
                    st.session_state[chat_key]
                    + [{"role": "assistant", "content": clean_response}]
                )
                if update_kwargs:
                    ProductContextDB.update(ctx_id, **update_kwargs)
                for change in changes:
                    ProductContextDB.add_history_entry(ctx_id, change, clean_response[:150], "Dupin Assistant")
            except Exception:
                # Extraction failed — still save conversation history
                ProductContextDB.update(ctx_id, context_conversation_history=(
                    st.session_state[chat_key]
                    + [{"role": "assistant", "content": clean_response}]
                ))

        return clean_response

    col_evidence, col_chat = st.columns([1, 1], gap="large")

    # ── Left: Evidence Board (What We Know) ──
    with col_evidence:
        render_section_header("document", "What We Know")

        fields = ["description", "documentation", "current_state"]
        filled = sum(1 for f in fields if ctx.get(f))
        has_content = filled > 0

        if has_content:
            if ctx.get("description"):
                render_info_field("Subject", ctx["description"])
            if ctx.get("documentation"):
                render_info_field("Evidence & Documentation", ctx["documentation"])
            if ctx.get("current_state"):
                render_info_field("Current State of Affairs", ctx["current_state"])

            # Show case history
            history = ctx.get("case_history", [])
            if history:
                with st.expander(f"Case History ({len(history)} entries)", expanded=False):
                    for entry in reversed(history):
                        ts = entry.get("timestamp", "")[:16]
                        source = entry.get("source", "PM")
                        action = entry.get("action", "")
                        details = entry.get("details", "")
                        source_color = "#C4823A" if "Dupin" in source else "#5C7A6E" if "Investigation" in source else "#8C8878"
                        st.markdown(
                            f'<div style="border-left:3px solid {source_color};padding:0.4rem 0.75rem;'
                            f'margin-bottom:0.5rem;border-radius:0 4px 4px 0;">'
                            f'<div style="font-size:0.7rem;color:#B8B4A8;">{ts} · {source}</div>'
                            f'<div style="font-size:0.85rem;color:#3D3D35;font-weight:500;">{action}</div>'
                            f'<div style="font-size:0.8rem;color:#8C8878;margin-top:0.15rem;">{details[:120]}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
        else:
            render_empty_state(
                "document",
                "Nothing here yet",
                "Chat with Dupin on the right to start building the case brief. "
                "Information will appear here as you share it."
            )

    # ── Right: Dupin Chat ──
    with col_chat:
        render_section_header("chat", "Dupin Assistant")

        greeting = (
            "Welcome, detective. I'm Dupin, your discovery assistant.\n\n"
            if not has_content else
            "The case brief is taking shape. What else should I know? "
            "You can also ask me **why** something is in the brief \u2014 "
            "I remember how things evolved.\n\n"
        )
        if not has_content:
            greeting += (
                "Let's build the case brief. I'll ask you some questions and "
                "organize everything as we go. To start \u2014 **what product or "
                "initiative are you investigating?**"
            )

        render_chat(
            session_key=chat_key,
            agent_callback=context_agent_callback,
            placeholder="Tell Dupin about your product, or ask about past decisions...",
            initial_assistant_message=greeting,
        )

    st.divider()

# ═══════════════════════════════════════════════
# Investigations Tab
# ═══════════════════════════════════════════════
with tab_investigations:
    render_tab_guide("Each investigation is a focused research session — e.g., exploring onboarding, a specific feature, or a persona's workflow.")
    sessions = DiscoverySessionDB.list_by_context(ctx_id)

    col_hdr, col_btn = st.columns([3, 1])
    with col_hdr:
        render_section_header("magnifier", "Investigations")
    with col_btn:
        if st.button("+ New Investigation", type="primary", use_container_width=True):
            new_session = DiscoverySessionDB.create(
                product_context_id=ctx_id, name="Untitled Investigation"
            )
            st.session_state["selected_session_id"] = new_session["id"]
            st.switch_page("pages/3_Discovery_Session.py")

    if not sessions:
        render_empty_state(
            "magnifier",
            "No investigations opened yet",
            "Start an investigation to uncover user journeys and pain points.",
        )
    else:
        for session in sessions:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"#### {session['name']}")
                    if session.get("objective"):
                        st.markdown(
                            f'<p style="color:#8C8878; font-size:0.9rem;">{session["objective"][:150]}</p>',
                            unsafe_allow_html=True,
                        )
                with col2:
                    st.markdown(
                        f"<div style='margin-top:0.75rem;'>{render_status_pill(session['status'])}</div>",
                        unsafe_allow_html=True,
                    )
                with col3:
                    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
                    if st.button("Investigate", key=f"open_session_{session['id']}", use_container_width=True):
                        st.session_state["selected_session_id"] = session["id"]
                        st.switch_page("pages/3_Discovery_Session.py")

# ═══════════════════════════════════════════════
# New Leads Tab (Context Improvements)
# ═══════════════════════════════════════════════
with tab_leads:
    render_tab_guide("Leads are suggestions to update your case brief based on what Dupin uncovered during interviews.")
    render_section_header("lightbulb", "New Leads")
    improvements = ContextImprovementDB.list_by_context(ctx_id)

    if not improvements:
        render_empty_state(
            "lightbulb",
            "No new leads yet",
            "Conduct investigations and interviews to uncover leads.",
        )
    else:
        for imp in improvements:
            stype = imp.get("suggestion_type", "gap")
            st.markdown(
                f'<div class="improvement-card {stype}">',
                unsafe_allow_html=True,
            )
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{imp['title']}**")
                    st.markdown(
                        f'<span class="status-pill {stype}">{stype.replace("_", " ").title()}</span>',
                        unsafe_allow_html=True,
                    )
                    st.write(imp.get("description", ""))
                with col2:
                    if imp["status"] == "pending":
                        if st.button("Accept", key=f"acc_{imp['id']}"):
                            # Apply the lead to the case brief
                            stype = imp.get("suggestion_type", "new_info")
                            imp_title = imp.get("title", "")
                            imp_desc = imp.get("description", "")
                            lead_text = f"\n\n[From investigation] {imp_title}: {imp_desc}"

                            field_updated = ""
                            if stype in ("new_info", "gap"):
                                current = ctx.get("description", "") or ""
                                ProductContextDB.update(ctx_id, description=current + lead_text)
                                field_updated = "Subject"
                            elif stype == "correction":
                                current = ctx.get("current_state", "") or ""
                                ProductContextDB.update(ctx_id, current_state=current + lead_text)
                                field_updated = "Current State"
                            elif stype == "conflicting_assumption":
                                current = ctx.get("documentation", "") or ""
                                ProductContextDB.update(ctx_id, documentation=current + lead_text)
                                field_updated = "Evidence & Documentation"

                            # Log to case history
                            ProductContextDB.add_history_entry(
                                ctx_id,
                                f"Accepted lead: {imp_title}",
                                f"Added to {field_updated}. {imp_desc[:100]}",
                                source=f"Investigation Finding ({stype})",
                            )

                            ContextImprovementDB.update_status(imp["id"], "accepted")
                            st.rerun()
                        if st.button("Dismiss", key=f"rej_{imp['id']}"):
                            ContextImprovementDB.update_status(imp["id"], "rejected")
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# Artifacts Tab
# ═══════════════════════════════════════════════
with tab_artifacts:
    render_tab_guide(
        "Generate documents, flow diagrams, presentations, and other deliverables from your case knowledge. "
        "Chat with Dupin to describe what you want — iterate until it's right."
    )

    artifacts = ArtifactDB.list_by_context(ctx_id)
    creating_key = f"creating_artifact_{ctx_id}"
    viewing_key = f"viewing_artifact_{ctx_id}"

    # ── Creation Mode ──
    if st.session_state.get(creating_key):
        artifact_id = st.session_state[creating_key]
        artifact = ArtifactDB.get(artifact_id)

        if artifact:
            st.markdown(f"### Creating: {artifact.get('name', 'New Artifact')}")

            col_preview, col_chat = st.columns([1, 1], gap="large")

            with col_preview:
                render_section_header("document", "Live Preview")
                # Show latest content from session state if available
                preview_key = f"artifact_preview_{artifact_id}"
                preview_content = st.session_state.get(preview_key, artifact.get("content", ""))
                if preview_content:
                    temp_artifact = {**artifact, "content": preview_content}
                    render_artifact_preview(temp_artifact)
                else:
                    render_empty_state("document", "Preview will appear here",
                                       "Describe what you want to Dupin on the right.")

                # Save + Download buttons
                if preview_content:
                    col_save, col_dl, col_final = st.columns(3)
                    with col_save:
                        if st.button("Save Draft", key="save_draft", use_container_width=True):
                            ArtifactDB.update(artifact_id, content=preview_content)
                            st.success("Draft saved!")
                    with col_dl:
                        st.download_button(
                            "Download .md",
                            data=preview_content,
                            file_name=f"{artifact.get('name', 'artifact').replace(' ', '_').lower()}.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )
                    with col_final:
                        if st.button("Finalize & Close", type="primary", key="finalize",
                                     use_container_width=True):
                            ArtifactDB.update(artifact_id, content=preview_content, status="final")
                            ProductContextDB.add_history_entry(
                                ctx_id,
                                f"Created artifact: {artifact.get('name', '')}",
                                f"Type: {artifact.get('artifact_type', '')}",
                                "Dupin Artifact Generator",
                            )
                            del st.session_state[creating_key]
                            if preview_key in st.session_state:
                                del st.session_state[preview_key]
                            st.rerun()

                    # DOCX/PPTX export
                    atype = artifact.get("artifact_type", "document")
                    if atype in ("document", "markdown"):
                        docx_bytes = export_artifact_to_docx({**artifact, "content": preview_content})
                        if docx_bytes:
                            st.download_button(
                                "Download .docx", data=docx_bytes,
                                file_name=f"{artifact.get('name', 'artifact').replace(' ', '_').lower()}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="dl_docx",
                            )
                    elif atype == "presentation":
                        pptx_bytes = export_artifact_to_pptx({**artifact, "content": preview_content})
                        if pptx_bytes:
                            st.download_button(
                                "Download .pptx", data=pptx_bytes,
                                file_name=f"{artifact.get('name', 'artifact').replace(' ', '_').lower()}.pptx",
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                key="dl_pptx",
                            )

            with col_chat:
                render_section_header("chat", "Dupin Artifact Builder")

                art_chat_key = f"artifact_chat_{artifact_id}"
                if art_chat_key not in st.session_state:
                    saved_hist = artifact.get("conversation_history", [])
                    if isinstance(saved_hist, str):
                        saved_hist = json.loads(saved_hist) if saved_hist else []
                    st.session_state[art_chat_key] = saved_hist

                def artifact_callback(messages):
                    try:
                        clean_resp, art_content, is_ready = get_artifact_response(
                            messages=messages,
                            product_context=ctx,
                            artifact_type=artifact.get("artifact_type", "document"),
                            reference_artifact=None,
                        )
                    except (AgentError, Exception) as e:
                        return f"Connection issue. Please try again. ({type(e).__name__})"

                    # Update preview if content was generated
                    if art_content:
                        st.session_state[f"artifact_preview_{artifact_id}"] = art_content
                        ArtifactDB.update(artifact_id, content=art_content,
                                          conversation_history=st.session_state[art_chat_key])

                    return clean_resp

                atype_label = {"document": "document", "flowchart": "flow diagram",
                               "presentation": "presentation", "markdown": "markdown note"}
                render_chat(
                    session_key=art_chat_key,
                    agent_callback=artifact_callback,
                    placeholder=f"Describe the {atype_label.get(artifact.get('artifact_type', ''), 'artifact')} you want...",
                    initial_assistant_message=(
                        f"I'm ready to create a **{atype_label.get(artifact.get('artifact_type', ''), 'artifact')}** "
                        f"using everything I know about this case.\n\n"
                        f"What should it cover? Who's the audience? Any specific sections or format you need?"
                    ),
                )

            # Cancel button
            if st.button("Cancel", key="cancel_artifact"):
                ArtifactDB.delete(artifact_id)
                del st.session_state[creating_key]
                st.rerun()

    # ── Viewing Mode ──
    elif st.session_state.get(viewing_key):
        artifact_id = st.session_state[viewing_key]
        artifact = ArtifactDB.get(artifact_id)

        if artifact:
            col_back, _ = st.columns([1, 4])
            with col_back:
                if st.button("< Back to Artifacts"):
                    del st.session_state[viewing_key]
                    st.rerun()

            st.markdown(f"### {artifact.get('name', 'Untitled')}")
            render_artifact_preview(artifact)

            col_dl1, col_dl2, col_iterate = st.columns(3)
            with col_dl1:
                st.download_button(
                    "Download .md",
                    data=artifact.get("content", ""),
                    file_name=f"{artifact.get('name', 'artifact').replace(' ', '_').lower()}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key="view_dl_md",
                )
            with col_iterate:
                if st.button("Iterate on this", type="primary", use_container_width=True,
                             key="iterate_btn"):
                    # Create new artifact referencing this one
                    new_version = artifact.get("version", 1) + 1
                    new_art = ArtifactDB.create(
                        product_context_id=ctx_id,
                        name=f"{artifact.get('name', 'Untitled')} v{new_version}",
                        artifact_type=artifact.get("artifact_type", "document"),
                        content=artifact.get("content", ""),
                        parent_artifact_id=artifact["id"],
                        version=new_version,
                    )
                    st.session_state[creating_key] = new_art["id"]
                    if viewing_key in st.session_state:
                        del st.session_state[viewing_key]
                    st.rerun()

    # ── List Mode (default) ──
    else:
        col_hdr, col_btn = st.columns([3, 1])
        with col_hdr:
            render_section_header("folder", "Case Artifacts")
        with col_btn:
            if st.button("+ Generate Artifact", type="primary", use_container_width=True):
                st.session_state[f"show_artifact_form_{ctx_id}"] = True
                st.rerun()

        # New artifact form
        form_key = f"show_artifact_form_{ctx_id}"
        if st.session_state.get(form_key):
            with st.container(border=True):
                st.markdown("#### New Artifact")
                art_name = st.text_input("Name", value="", placeholder="e.g., PRD Summary, User Flow, Stakeholder Deck")
                art_type = st.selectbox("Type", ["document", "flowchart", "presentation", "markdown"],
                                        format_func=lambda x: {"document": "Document", "flowchart": "Flow Diagram",
                                                                "presentation": "Presentation", "markdown": "Markdown"}[x])

                # Reference existing artifact
                ref_artifact = None
                if artifacts:
                    ref_options = {"none": "Start fresh"} | {a["id"]: f"{a['name']} ({a['artifact_type']})" for a in artifacts}
                    ref_choice = st.selectbox("Reference existing artifact (optional)",
                                              options=list(ref_options.keys()),
                                              format_func=lambda x: ref_options[x])
                    if ref_choice != "none":
                        ref_artifact = ArtifactDB.get(ref_choice)

                col_create, col_cancel = st.columns(2)
                with col_create:
                    if st.button("Start Creating", type="primary", use_container_width=True,
                                 disabled=not art_name):
                        new_art = ArtifactDB.create(
                            product_context_id=ctx_id,
                            name=art_name,
                            artifact_type=art_type,
                            content=ref_artifact.get("content", "") if ref_artifact else "",
                            parent_artifact_id=ref_artifact["id"] if ref_artifact else None,
                        )
                        st.session_state[creating_key] = new_art["id"]
                        del st.session_state[form_key]
                        st.rerun()
                with col_cancel:
                    if st.button("Cancel", use_container_width=True, key="cancel_form"):
                        del st.session_state[form_key]
                        st.rerun()

        # Existing artifacts list
        if not artifacts:
            if not st.session_state.get(form_key):
                render_empty_state(
                    "folder",
                    "No artifacts yet",
                    "Generate documents, diagrams, or presentations from your case knowledge."
                )
        else:
            for art in artifacts:
                col_card, col_actions = st.columns([4, 1])
                with col_card:
                    render_artifact_card(art)
                with col_actions:
                    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
                    if st.button("View", key=f"view_{art['id']}", use_container_width=True):
                        st.session_state[viewing_key] = art["id"]
                        st.rerun()
                    if st.button("Delete", key=f"del_art_{art['id']}", use_container_width=True):
                        ArtifactDB.delete(art["id"])
                        st.rerun()
