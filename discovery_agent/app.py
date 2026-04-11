import sys
import os

# Ensure the discovery_agent directory is on the Python path
# so relative imports work regardless of where Streamlit runs from
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _APP_DIR)

import streamlit as st
from database.db import init_db

st.set_page_config(
    page_title="Dupin",
    page_icon=os.path.join(_APP_DIR, "assets", "logo.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database on first run
init_db()

# Sidebar logo
logo_path = os.path.join(_APP_DIR, "assets", "logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=160)
    st.sidebar.markdown(
        '<p style="text-align:center; color:#8C8878; font-size:0.75rem; '
        'letter-spacing:0.12em; text-transform:uppercase; margin-top:-0.5rem;">Discovery Agent</p>',
        unsafe_allow_html=True,
    )
    st.sidebar.divider()

# Main landing — redirect to Home page
home = st.Page("pages/1_Home.py", title="Home", icon=":material/home:", default=True)
product_context = st.Page("pages/2_Product_Context.py", title="Product Context", icon=":material/description:")
discovery_session = st.Page("pages/3_Discovery_Session.py", title="Discovery Session", icon=":material/search:")
user_chat = st.Page("pages/4_User_Chat.py", title="User Chat", icon=":material/chat:")
reports = st.Page("pages/5_Reports.py", title="Reports", icon=":material/assessment:")

pg = st.navigation([home, product_context, discovery_session, user_chat, reports])
pg.run()
