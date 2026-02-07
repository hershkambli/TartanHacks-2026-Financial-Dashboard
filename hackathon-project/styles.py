import streamlit as st


def load_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .stApp {
            background-color: #000000;
        }

        * {
            font-family: 'Inter', sans-serif;
            color: #ffffff;
        }

        h1 { 
            font-size: 1.8rem; 
            font-weight: 600; 
            color: #ffffff; 
            margin-bottom: 0.3rem;
        }

        h2 { 
            font-size: 1.3rem; 
            font-weight: 600; 
            color: #ffffff; 
        }

        h3 { 
            font-size: 1.1rem; 
            font-weight: 600; 
            color: #cccccc; 
        }

        .main {
            padding: 1.5rem 2.5rem;
        }

        .block-container {
            padding: 0.5rem 0;
            max-width: 1400px;
        }

        /* Tabs with colors */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: transparent;
            border-bottom: none;
        }

        .stTabs [data-baseweb="tab"] {
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            padding: 12px 20px;
            color: #888888;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.2s;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: #2a2a2a;
            color: #ffffff;
        }

        /* Portfolio tab - Blue */
        .stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: #ffffff;
            border-color: #3b82f6;
        }

        /* Markets tab - Green */
        .stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: #ffffff;
            border-color: #10b981;
        }

        /* AI Assistant tab - Purple */
        .stTabs [data-baseweb="tab"]:nth-child(3)[aria-selected="true"] {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: #ffffff;
            border-color: #8b5cf6;
        }

        /* Settings tab - Orange */
        .stTabs [data-baseweb="tab"]:nth-child(4)[aria-selected="true"] {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: #ffffff;
            border-color: #f59e0b;
        }

        [data-testid="stMetricValue"] {
            font-size: 32px;
            font-weight: 600;
            color: #ffffff;
        }

        [data-testid="stMetricLabel"] {
            font-size: 11px;
            font-weight: 500;
            color: #888888;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        [data-testid="stSidebar"] {
            background-color: #0a0a0a;
            border-right: 1px solid #1a1a1a;
            padding: 1.5rem 1rem;
        }

        /* ALL BUTTONS - darker theme */
        .stButton button {
            background: #2a2a2a !important;
            color: #ffffff !important;
            border: 1px solid #3a3a3a !important;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.15s;
        }

        .stButton button:hover {
            background: #3a3a3a !important;
            border-color: #4a4a4a !important;
        }

        /* Primary buttons - slightly lighter but not white */
        .stButton button[kind="primary"] {
            background: #3a3a3a !important;
            color: #ffffff !important;
            border: 1px solid #4a4a4a !important;
        }

        .stButton button[kind="primary"]:hover {
            background: #4a4a4a !important;
        }

        .stTextInput input, .stTextArea textarea, .stNumberInput input {
            background: #0a0a0a;
            border: 1px solid #2a2a2a;
            border-radius: 6px;
            color: #ffffff;
            padding: 7px 11px;
            font-size: 14px;
        }

        .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
            border-color: #4a4a4a;
            box-shadow: none;
        }

        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: #555555;
        }

        .stSelectbox [data-baseweb="select"] {
            background: #0a0a0a;
            border: 1px solid #2a2a2a;
        }

        .stCaption {
            color: #666666;
            font-size: 13px;
        }

        .stSuccess { 
            background: #0a2a0a; 
            border-left: 3px solid #00cc00; 
            color: #00cc00; 
        }

        .stInfo { 
            background: #0a0a2a; 
            border-left: 3px solid #0066ff; 
            color: #0066ff; 
        }

        .stWarning { 
            background: #2a2a0a; 
            border-left: 3px solid #ff9900; 
            color: #ff9900; 
        }

        .stError { 
            background: #2a0a0a; 
            border-left: 3px solid #ff0000; 
            color: #ff0000; 
        }

        .dataframe {
            background: #000000;
            color: #ffffff;
            border: 1px solid #1a1a1a;
            font-size: 13px;
        }

        .dataframe thead th {
            background: #0a0a0a;
            color: #888888;
            font-weight: 600;
            border-bottom: 1px solid #2a2a2a;
            font-size: 12px;
        }

        .dataframe tbody tr:hover {
            background: #0a0a0a;
        }

        .streamlit-expanderHeader {
            background: #0a0a0a;
            border: 1px solid #2a2a2a;
            border-radius: 6px;
            color: #ffffff;
            font-size: 14px;
        }

        .streamlit-expanderHeader:hover {
            background: #1a1a1a;
        }

        hr { 
            border-color: #1a1a1a; 
            margin: 1.5rem 0;
        }

        #MainMenu, footer, header { 
            visibility: hidden; 
        }
        </style>
    """, unsafe_allow_html=True)