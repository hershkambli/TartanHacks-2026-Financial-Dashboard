import streamlit as st


def load_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Pure black background */
        .stApp {
            background-color: #000000;
        }

        /* Clean typography */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #ffffff;
        }

        h1 { font-size: 2rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem; }
        h2 { font-size: 1.5rem; font-weight: 600; color: #ffffff; }
        h3 { font-size: 1.2rem; font-weight: 600; color: #cccccc; }

        /* Clean container */
        .main {
            padding: 2rem 3rem;
        }

        .block-container {
            padding: 1rem 0;
            max-width: 1400px;
        }

        /* Minimal tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background: transparent;
            border-bottom: 1px solid #333333;
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border: none;
            padding: 16px 24px;
            color: #666666;
            font-weight: 500;
            font-size: 15px;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #ffffff;
        }

        .stTabs [aria-selected="true"] {
            color: #ffffff;
            border-bottom: 2px solid #ffffff;
        }

        /* Clean metrics */
        [data-testid="stMetricValue"] {
            font-size: 36px;
            font-weight: 700;
            color: #ffffff;
        }

        [data-testid="stMetricLabel"] {
            font-size: 12px;
            font-weight: 500;
            color: #999999;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0a0a0a;
            border-right: 1px solid #222222;
            padding: 2rem 1rem;
        }

        /* Simple buttons */
        .stButton button {
            background: #1a1a1a;
            color: #ffffff;
            border: 1px solid #333333;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            transition: all 0.2s;
        }

        .stButton button:hover {
            background: #2a2a2a;
            border-color: #555555;
        }

        .stButton button[kind="primary"] {
            background: #ffffff;
            color: #000000;
            border: none;
        }

        .stButton button[kind="primary"]:hover {
            background: #e0e0e0;
        }

        /* Clean inputs */
        .stTextInput input, .stTextArea textarea, .stNumberInput input {
            background: #0a0a0a;
            border: 1px solid #333333;
            border-radius: 6px;
            color: #ffffff;
            padding: 8px 12px;
        }

        .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
            border-color: #666666;
            box-shadow: none;
        }

        .stSelectbox [data-baseweb="select"] {
            background: #0a0a0a;
            border: 1px solid #333333;
        }

        /* Caption */
        .stCaption {
            color: #666666;
            font-size: 14px;
        }

        /* Alerts */
        .stSuccess { background: #0a2a0a; border-left: 3px solid #00ff00; color: #00ff00; }
        .stInfo { background: #0a0a2a; border-left: 3px solid #0080ff; color: #0080ff; }
        .stWarning { background: #2a2a0a; border-left: 3px solid #ffaa00; color: #ffaa00; }
        .stError { background: #2a0a0a; border-left: 3px solid #ff0000; color: #ff0000; }

        /* Dataframe */
        .dataframe {
            background: #000000;
            color: #ffffff;
            border: 1px solid #222222;
        }

        .dataframe thead th {
            background: #0a0a0a;
            color: #999999;
            font-weight: 600;
            border-bottom: 1px solid #333333;
        }

        .dataframe tbody tr:hover {
            background: #0a0a0a;
        }

        /* Remove extras */
        hr { border-color: #222222; }
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)