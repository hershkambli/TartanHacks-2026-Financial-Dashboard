import os
import pickle
import streamlit as st

def render():
    st.header("AI-Powered Recommendations")
    st.write("Based on your financial profile and goals")

    # Path relative to this file
    script_dir = os.path.dirname(__file__)
    model_path = os.path.join(script_dir, "models", "risk_classifier.pkl")

    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            risk_model = pickle.load(f)
        st.success("Model loaded successfully!")
        st.write("Predicted risk: Moderate (dummy prediction)")
    else:
        st.warning(f"ML model not found at {model_path}. Showing dummy predictions.")
        st.write("Predicted risk: Moderate (dummy prediction)")

