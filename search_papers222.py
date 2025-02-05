import arxiv
from download_extract_pdf import download_pdf, extract_text_from_pdf
from summarize_text import summarize_text
from vector_db import store_summary_in_db
import os

def search_papers(query):
    """
    Fetch the 5 most relevant papers from arXiv.
    """
    print(f"Searching for the most relevant papers on '{query}' using arXiv...")
    try:
        # Perform the search and fetch the top 5 results
        search = arxiv.Search(
            query=query,
            max_results=20,  # Fetch the top 5 results
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending,
        )
        
        results = list(search.results())
        if results:
            papers = []
            for result in results:
                title = result.title
                url = result.pdf_url
                published_date = result.published.strftime("%Y-%m-%d")
                
                papers.append({
                    "title": title,
                    "url": url,
                    "published_date": published_date
                })
            
            print(f"Found {len(papers)} relevant papers.")
            return papers
        else:
            print("No relevant papers found.")
            return []
    except Exception as e:
        print(f"Error searching for papers: {str(e)}")
        return []

def process_paper(title, url):
    try:
        # Download the PDF
        pdf_path = download_pdf(url, title)
        if not pdf_path:
            print(f"Skipping {title} due to failed download.")
            return None
        
        # Extract text from the PDF
        paper_text = extract_text_from_pdf(pdf_path)
        if not paper_text:
            print(f"Skipping {title} due to failed text extraction.")
            return None
        
        # Summarize the paper
        summary = summarize_text(paper_text, title)
        
        # Store the summary in the vector database
        store_summary_in_db(title, summary)
        
        # Delete the downloaded PDF after processing
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"Deleted PDF: {pdf_path}")
        
        return summary
    except Exception as e:
        print(f"Error processing paper '{title}': {e}")
        return None

def search_and_summarize(query):
    papers = search_papers(query)
    summaries = []
    
    for paper in papers:
        summary = process_paper(paper["title"], paper["url"])
        if summary:
            summaries.append({
                "title": paper["title"],
                "summary": summary
            })
    
    return summaries