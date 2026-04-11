import streamlit as st


def render_page_guide(title, description):
    """Render a subtle contextual guidance bar at the top of a page."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, rgba(196,130,58,0.08) 0%, rgba(196,130,58,0.02) 100%);
        border-left: 3px solid #C4823A;
        border-radius: 0 6px 6px 0;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1.25rem;
    ">
        <div style="
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            font-weight: 600;
            color: #C4823A;
            letter-spacing: 0.04em;
            margin-bottom: 0.2rem;
        ">{title}</div>
        <div style="
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            color: #8C8878;
            line-height: 1.5;
        ">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def render_tab_guide(text):
    """Render a subtle one-line hint below a tab header."""
    st.markdown(f"""
    <div style="
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        color: #B8B4A8;
        margin-bottom: 1rem;
        font-style: italic;
    ">{text}</div>
    """, unsafe_allow_html=True)
