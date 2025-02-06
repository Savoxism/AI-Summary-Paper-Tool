import streamlit as st
from searcher import search_papers, process_paper
from vector_db import search_similar_summaries
from summarizer import model

# Initialize session state for chat history and selected paper
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_paper" not in st.session_state:
    st.session_state.selected_paper = None
if "papers" not in st.session_state:
    st.session_state.papers = []

st.set_page_config(page_title="Paper Summarizer", page_icon="📚")
st.title("📄 Paper Summarizer with arXiv")

# Search for relevant papers
st.subheader("Search for Relevant Papers")
query = st.text_input("Enter the title or topic of a research paper:")
if st.button("Search"):
    if query:
        with st.spinner("Searching for relevant papers..."):
            st.session_state.papers = search_papers(query)  # Store papers in session state
        
        if st.session_state.papers:
            st.success(f"Found {len(st.session_state.papers)} relevant papers.")
        else:
            st.error("No relevant papers found. Please refine your query.")

# Display the dropdown only if papers are found
if st.session_state.papers:
    paper_titles = [paper["title"] for paper in st.session_state.papers]
    selected_title = st.selectbox("Select a paper to analyze:", paper_titles)

    # Update the selected_paper in session state when the user selects a new paper
    if st.session_state.selected_paper is None or st.session_state.selected_paper["title"] != selected_title:
        st.session_state.selected_paper = next(paper for paper in st.session_state.papers if paper["title"] == selected_title)
        st.success(f"Selected paper: {st.session_state.selected_paper['title']}")

# If a paper has been selected, allow the user to download and summarize it
if st.session_state.selected_paper:
    selected_paper = st.session_state.selected_paper

    if st.button("Download and Summarize"):
        with st.spinner(f"Downloading and summarizing '{selected_paper['title']}'..."):
            summary = process_paper(selected_paper["title"], selected_paper["url"])
        
        if summary:
            st.success(f"Summary for '{selected_paper['title']}' generated successfully!")
            st.markdown(f"**Title:** {selected_paper['title']}")
            st.markdown(f"**Author:** {', '.join(selected_paper['authors'])}")
            st.markdown(f"**Published Date:** {selected_paper['published_date']}")
            st.markdown(f"**Summary:**\n{summary}")
        else:
            st.error(f"Failed to process '{selected_paper['title']}'. Please try again.")

# Search for similar summaries
st.subheader("Search for Similar Summaries")
search_query = st.text_input("Enter a query to find similar summaries:")
if search_query:
    with st.spinner("Searching..."):
        results = search_similar_summaries(search_query, n_results=1)
        st.write("Similar Summaries:")
        for i, doc in enumerate(results["documents"][0]):
            st.markdown(f"**Result {i+1}:**")
            st.markdown(doc)

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