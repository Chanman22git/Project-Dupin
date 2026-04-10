import streamlit as st
from database.models import ProductContextDB

st.title("Discovery Agent")
st.subheader("Product Contexts")

contexts = ProductContextDB.list_all()

if st.button("+ Create New Product Context", type="primary"):
    new_ctx = ProductContextDB.create(name="Untitled Product Context")
    st.session_state["selected_context_id"] = new_ctx["id"]
    st.switch_page("pages/2_Product_Context.py")

if not contexts:
    st.info("No product contexts yet. Create one to get started.")
else:
    for ctx in contexts:
        session_count = ProductContextDB.count_sessions(ctx["id"])
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {ctx['name']}")
                if ctx.get("description"):
                    st.caption(ctx["description"][:200] + ("..." if len(ctx.get("description", "")) > 200 else ""))
                st.caption(f"{session_count} session(s) | Updated: {ctx['updated_at'][:10]}")
            with col2:
                if st.button("Open", key=f"open_{ctx['id']}"):
                    st.session_state["selected_context_id"] = ctx["id"]
                    st.switch_page("pages/2_Product_Context.py")
                if st.button("Delete", key=f"del_{ctx['id']}", type="secondary"):
                    ProductContextDB.delete(ctx["id"])
                    st.rerun()
