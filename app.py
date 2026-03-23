import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/query")

st.set_page_config(page_title="Governed RAG", page_icon="🔒")
st.title("🔒 Governed RAG Pipeline")
st.markdown("Ask a question. All queries are audited and PII is masked.")

user_id = st.text_input("User ID (for audit)", "demo_user")
question = st.text_input("Your question:")

if st.button("Ask"):
    if question and user_id:
        with st.spinner("Processing..."):
            try:
                response = requests.post(API_URL, json={"question": question, "user_id": user_id})
                if response.status_code == 200:
                    data = response.json()
                    st.write("**Answer:**", data["answer"])
                    st.write("**Audit ID:**", data["audit_id"])
                    with st.expander("See retrieved & masked context"):
                        for ctx in data.get("contexts", []):
                            st.write(ctx)
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")
    else:
        st.warning("Please enter both user ID and question.")