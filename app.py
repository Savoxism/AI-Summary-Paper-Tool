import os
import streamlit as st
from summarizer import *
from vector_db import search_similar_summaries

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
# Streamlit UI
st.set_page_config(page_title="Paper Summarizer", page_icon="📚")
st.title("📄 Paper Summarizer with Gemini")

# File Uploader
uploaded_file = st.file_uploader("Upload a research paper (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    # Save the uploaded file temporarily
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Extract the title from the file name
    title = os.path.splitext(uploaded_file.name)[0]
    
    # Display a loading spinner while summarizing
    with st.spinner("Summarizing the paper..."):
        chat_history, summary = summarize_text(file_path, title, st.session_state.chat_history)
        st.session_state.chat_history = chat_history  # Update the chat history
    
    os.remove(file_path)
    
    # Display the summary
    st.subheader("Summary")
    st.markdown(summary)

# Chat interface for follow-up questions
st.subheader("Ask Follow-Up Questions")
user_input = st.text_input("Enter your question:")

if user_input:
    chat_session = model.start_chat(history=st.session_state.chat_history)
    
    with st.spinner("Generating response..."):
        response = chat_session.send_message(user_input)
        st.session_state.chat_history = chat_session.history  # Update the chat history
    
    st.subheader("Response")
    st.markdown(response.text)

# Search for similar summaries
st.subheader("Search for Similar Summaries")
query = st.text_input("Enter a query to find similar summaries:")
if query:
    with st.spinner("Searching..."):
        results = search_similar_summaries(query, n_results=3)
        st.write("Similar Summaries:")
        for i, doc in enumerate(results["documents"][0]):
            st.markdown(f"**Result {i+1}:**")
            st.markdown(doc)
