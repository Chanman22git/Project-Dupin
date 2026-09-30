import sys
import os

# Ensure the discovery_agent directory is on the Python path
# so relative imports work regardless of where Streamlit runs from
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _APP_DIR)

import base64
import streamlit as st
from database.db import init_db


def _logo_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.set_page_config(
    page_title="Dupin",
    page_icon=os.path.join(_APP_DIR, "assets", "logo.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database on first run
init_db()

# Sidebar branding
logo_path = os.path.join(_APP_DIR, "assets", "logo.png")
if os.path.exists(logo_path):
    st.sidebar.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.75rem; padding:0.25rem 0 0.75rem 0;">
            <img src="data:image/png;base64,{_logo_base64(logo_path)}" width="48" height="48"
                 style="border-radius:8px; object-fit:cover;" />
            <div>
                <div style="font-family:'Playfair Display',serif; font-size:1.25rem; font-weight:700;
                     color:#3D3D35; line-height:1.2;">Dupin</div>
                <div style="font-family:'Inter',sans-serif; font-size:0.625rem; font-weight:500;
                     color:#8C8878; letter-spacing:0.12em; text-transform:uppercase;">Discovery Agent</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.divider()

# Pages
home = st.Page("pages/1_Home.py", title="Case Board", icon=":material/home:", default=True)
case_file = st.Page("pages/2_Product_Context.py", title="Case File", icon=":material/description:")
investigation = st.Page("pages/3_Discovery_Session.py", title="Investigation", icon=":material/search:")
interview = st.Page("pages/4_User_Chat.py", title="Interview", icon=":material/chat:")
reports = st.Page("pages/5_Reports.py", title="Dossier", icon=":material/assessment:")

# Interview links (BASE_URL?page=chat&token=...) must land on the Interview page,
# and interviewees must not reach the PM pages — so a token request only gets
# the Interview page registered, which makes it the page served at any path.
if st.query_params.get("token"):
    pg = st.navigation([interview], position="hidden")
else:
    pg = st.navigation([home, case_file, investigation, interview, reports])
pg.run()
