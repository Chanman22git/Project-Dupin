import streamlit as st
from database.db import init_db

st.set_page_config(
    page_title="Discovery Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database on first run
init_db()

# Main landing — redirect to Home page
home = st.Page("pages/1_Home.py", title="Home", icon=":material/home:", default=True)
product_context = st.Page("pages/2_Product_Context.py", title="Product Context", icon=":material/description:")
discovery_session = st.Page("pages/3_Discovery_Session.py", title="Discovery Session", icon=":material/search:")
user_chat = st.Page("pages/4_User_Chat.py", title="User Chat", icon=":material/chat:")
reports = st.Page("pages/5_Reports.py", title="Reports", icon=":material/assessment:")

pg = st.navigation([home, product_context, discovery_session, user_chat, reports])
pg.run()
