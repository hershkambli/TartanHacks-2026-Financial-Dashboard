import streamlit as st
from anthropic import Anthropic


def render(api_key):
    st.markdown("# AI Investment Assistant")
    st.caption("Get personalized investment advice powered by AI")
    st.markdown("---")

    question = st.text_area(
        "Ask anything about investing",
        placeholder="E.g., What's a good diversification strategy for tech stocks?",
        height=120,
        label_visibility="collapsed",
        key="ai_question"
    )

    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    with col1:
        ask_btn = st.button("Ask AI", type="primary", use_container_width=True)
    with col2:
        if st.button("Clear", use_container_width=True):
            st.rerun()

    if ask_btn and question:
        if not api_key:
            st.warning("⚠️ Please enter your Anthropic API key in the sidebar.")
        else:
            try:
                with st.spinner("Thinking..."):
                    client = Anthropic(api_key=api_key)

                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        messages=[{
                            "role": "user",
                            "content": f"You are a financial advisor. Answer this investment question concisely and professionally: {question}"
                        }]
                    )

                    st.markdown("---")
                    st.markdown("#### AI Response")
                    st.markdown(message.content[0].text)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")