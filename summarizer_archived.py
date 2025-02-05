import os
from scholarly import scholarly
import requests
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Configuration for the generative model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 35,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the generative model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

# Prompt template for summarization
prompt = """
You are an experienced researcher who has been asked to summarize a research paper. The paper is about a certain topic, and you need to provide a summary of the key information. You must also cite some sentences if possible. The summary should be at least 500 words and at most 1000 words. The summary must contain the most necessary information and not any other irrelevant details. You must answer these questions:
1.Research Problem:
- What is the main objective of the study?
- What problem or question is the article trying to solve?
2.Hypothesis/Research Questions:
- What are the main hypotheses or research questions that the article poses?
3.Research Methods:
- What is the approach that the author used to solve the problem?
- What specific tools, data, and procedures were applied in the study?
4.Results:
- What are the important results obtained by the study?
- What specific data or information demonstrate those results?
5.Discussion & Analysis:
- What do the results mean in a broader context?
- What important conclusions does the author draw or provide?
6.Conclusion & Recommendations:
- What are the main conclusions of the paper?
- What are the recommendations for future research or practical applications?
7.Limitations:
- What are the limitations or unresolved issues in the study?
##Paper##
"""

# Function to search for relevant papers using Google Scholar
def search_papers(query, num_results=1):
    print(f"Searching for papers on '{query}' using Google Scholar...")
    try:
        # Perform the search
        search_query = scholarly.search_pubs(query)
        results = []
        count = 0
        
        while count < num_results:
            try:
                paper = next(search_query)
                # Extract metadata from the paper dictionary
                title = paper.get("bib", {}).get("title", "Unknown Title")
                url = paper.get("pub_url", None)  # Use "pub_url" instead of "url"
                citations = paper.get("num_citations", 0)  # Use "num_citations" instead of "citedby"
                year = paper.get("bib", {}).get("year", "Unknown Year")
                
                results.append({
                    "title": title,
                    "url": url,
                    "citations": citations,
                    "year": year
                })
                count += 1
            except StopIteration:
                break
        
        # Sort results by citations (popularity)
        results.sort(key=lambda x: x["citations"], reverse=True)
        return results
    except Exception as e:
        print(f"Error searching for papers: {str(e)}")
        return []

# Function to download a PDF from a URL
def download_pdf(url, title):
    response = requests.get(url)
    if response.status_code == 200:
        file_path = f"{title}.pdf"
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded PDF to '{file_path}'")
        return file_path
    else:
        print(f"Failed to download PDF: {response.status_code}")
        return None

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

# Function to generate a summary using the Gemini model
def summarize_text(paper_text, title, chat_history=None):
    try:
        # Use the Gemini model to generate a summary
        chat_session = model.start_chat(history=chat_history or [])
        response = chat_session.send_message([prompt, paper_text])
        summary = response.text
        return chat_session.history, summary
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return [], f"Error during summarization: {str(e)}"

# Function to process a single paper
def process_paper(title, url):
    try:
        # Download the PDF
        pdf_path = download_pdf(url, title)
        if not pdf_path:
            print(f"Skipping {title} due to failed download.")
            return

        # Extract text from the PDF
        paper_text = extract_text_from_pdf(pdf_path)
        if not paper_text:
            print(f"Skipping {title} due to failed text extraction.")
            os.remove(pdf_path)
            return

        # Summarize the paper
        _, summary = summarize_text(paper_text, title)

        # Remove the downloaded PDF
        os.remove(pdf_path)
        print(f"Processed and summarized '{title}'.")
        return summary
    except Exception as e:
        print(f"Error processing paper '{title}': {e}")
        return None

# Function to search and summarize multiple papers
def search_and_summarize(query):
    print(f"Starting search and summarize process for query: '{query}'")
    papers = search_papers(query)
    summaries = []
    for paper in papers:
        print(f"Processing paper: {paper['title']}")
        summary = process_paper(paper["title"], paper["url"])
        if summary:
            summaries.append({
                "title": paper["title"],
                "summary": summary
            })
    return summaries