import streamlit as st
from styles import load_css

# Import tab modules
from tabs import markets, ai_assistant, portfolio, settings, investments
from auth import render as auth_render  # Login/Signup module

# Page config
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
load_css()

# ---------- Helper Function ----------
def get_display_name(username):
    """
    Extract a friendly first name from the username.
    Example: 'hershkambli' -> 'Hersh'
    """
    first_name = username[:5]  # take first 5 letters as heuristic
    return first_name.capitalize()

# ---------- Initialize session state ----------
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ---------- Authentication ----------
if not st.session_state.logged_in:
    auth_render()  # Show login/signup page
    st.stop()      # Stop running the rest of the dashboard until logged in

# ---------- Top Header with Welcome + Logout ----------
header_col1, header_col2 = st.columns([6, 1])
with header_col1:
    display_name = get_display_name(st.session_state.user)
    st.markdown(f"## Welcome {display_name}")
with header_col2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.experimental_rerun()  # Refresh page to go back to login

st.markdown("---")  # Divider below header

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(["Budget", "Investments", "Markets", "Settings"])

with tab1:
    portfolio.render()

with tab2:
    investments.render()

with tab3:
    markets.render()

# Uncomment this when AI assistant is ready
# with tab4:
#     ai_assistant.render(api_key)

with tab4:
    settings.render()

