import streamlit as st
import requests

# Configure this to your Replit Flask backend URL
FLASK_BACKEND_URL = "https://your-repl-name.username.repl.co"  # Change this!

def display_paper_info(paper_info):
    st.subheader(paper_info['title'])
    st.write(f"**Authors:** {', '.join(paper_info['authors'])}")
    st.write(f"**Published:** {paper_info['published']}")
    st.markdown("---")
    st.subheader("Abstract")
    st.write(paper_info['summary'])
    st.markdown(f"[Download PDF]({paper_info['pdf_url']})", unsafe_allow_html=True)

# Streamlit UI (unchanged from your original)
st.set_page_config(page_title="Research Assistant", layout="wide")
st.title("Research Assistant Chatbot")

user_input = st.text_input(
    "Ask a research question or enter a paper ID (e.g., 2401.12345):",
    placeholder="Your question or paper ID..."
)

if st.button("Submit") and user_input:
    with st.spinner("Processing your request..."):
        if any(c.isdigit() for c in user_input):
            # Call Flask backend for paper info
            response = requests.post(
                f"{FLASK_BACKEND_URL}/get_paper_content",
                json={"paper_id": user_input}
            )
            paper_info = response.json()
            
            if 'error' not in paper_info:
                display_paper_info(paper_info)
            else:
                st.error(paper_info['error'])
        else:
            # Call Flask backend for research assistant
            response = requests.post(
                f"{FLASK_BACKEND_URL}/research_assistant",
                json={"query": user_input}
            )
            result = response.json()
            
            st.subheader("Research Assistant Response")
            st.markdown(result.get('response', result.get('error', 'No response available')))

# API functions section
st.markdown("---")
st.subheader("API Functions")

with st.expander("Search Papers"):
    topic = st.text_input("Research topic:")
    max_results = st.number_input("Max results:", min_value=1, max_value=20, value=5)
    if st.button("Search Papers"):
        with st.spinner("Searching papers..."):
            response = requests.post(
                f"{FLASK_BACKEND_URL}/search_papers",
                json={"topic": topic, "max_results": max_results}
            )
            st.json(response.json())

with st.expander("Get Paper Content"):
    paper_id = st.text_input("Paper ID:")
    if st.button("Get Paper Content"):
        with st.spinner("Fetching paper..."):
            response = requests.post(
                f"{FLASK_BACKEND_URL}/get_paper_content",
                json={"paper_id": paper_id}
            )
            st.json(response.json())

with st.expander("Research Assistant API"):
    query = st.text_input("Research question:")
    if st.button("Ask Assistant"):
        with st.spinner("Generating response..."):
            response = requests.post(
                f"{FLASK_BACKEND_URL}/research_assistant",
                json={"query": query}
            )
            st.json(response.json())
