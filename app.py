import streamlit as st
from search_papers222 import search_papers, process_paper
from vector_db import search_similar_summaries
from summarize_text import model


# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(page_title="Paper Summarizer", page_icon="📚")
st.title("📄 Paper Summarizer with arXiv")

# Search for relevant papers
st.subheader("Search for Relevant Papers")
query = st.text_input("Enter the title or topic of a research paper:")
if st.button("Search"):
    if query:
        with st.spinner("Searching for relevant papers..."):
            papers = search_papers(query)
        
        if papers:
            st.success(f"Found {len(papers)} relevant papers.")
            
            # Display the list of papers and let the user choose one
            paper_titles = [paper["title"] for paper in papers]
            selected_title = st.selectbox("Select a paper to analyze:", paper_titles)
            
            # Find the selected paper
            selected_paper = next(paper for paper in papers if paper["title"] == selected_title)
            
            # Process the selected paper
            if st.button("Download and Summarize"):
                with st.spinner(f"Downloading and summarizing '{selected_title}'..."):
                    summary = process_paper(selected_paper["title"], selected_paper["url"])
                
                if summary:
                    st.success(f"Summary for '{selected_title}' generated successfully!")
                    st.markdown(f"**Title:** {selected_paper['title']}")
                    st.markdown(f"**Published Date:** {selected_paper['published_date']}")
                    st.markdown(f"**Summary:**\n{summary}")
                else:
                    st.error(f"Failed to process '{selected_title}'. Please try again.")
        else:
            st.error("No relevant papers found. Please refine your query.")

# Search for similar summaries
st.subheader("Search for Similar Summaries")
search_query = st.text_input("Enter a query to find similar summaries:")
if search_query:
    with st.spinner("Searching..."):
        results = search_similar_summaries(search_query, n_results=3)
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