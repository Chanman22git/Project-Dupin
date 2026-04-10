import streamlit as st
from database.models import ProductContextDB, DiscoverySessionDB, ContextImprovementDB

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

st.title(ctx["name"])

# --- Tabs ---
tab_overview, tab_sessions, tab_improvements = st.tabs(["Overview", "Discovery Sessions", "Context Improvements"])

with tab_overview:
    st.subheader("Product Description")
    st.write(ctx.get("description") or "_No description yet. Use the chat below to define it._")

    st.subheader("Documentation")
    st.write(ctx.get("documentation") or "_No documentation added yet._")

    st.subheader("Current State")
    st.write(ctx.get("current_state") or "_Not defined yet._")

    st.divider()
    st.caption("Conversational context setup will be implemented in Phase 2.")

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
                    st.caption(f"Status: :{status_colors.get(session['status'], 'grey')}[{session['status']}] | Updated: {session['updated_at'][:10]}")
                    if session.get("objective"):
                        st.write(session["objective"][:150])
                with col2:
                    if st.button("Open", key=f"open_session_{session['id']}"):
                        st.session_state["selected_session_id"] = session["id"]
                        st.switch_page("pages/3_Discovery_Session.py")

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
