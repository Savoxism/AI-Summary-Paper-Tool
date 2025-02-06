from arxiv import Search, Client
import arxiv
from downloader import download_pdf, extract_text_from_pdf
from summarizer import summarize_text
from vector_db import store_summary_in_db
import os

def search_papers(query):
    print(f"Searching for the most relevant papers on '{query}' using arXiv...")
    try:
        search = Search(
            query=f"ti:{query}",
            max_results=5,  # Fetch the top 5 results
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending,
        )
        
        client = Client()
        results = list(client.results(search))
        if results:
            papers = []
            for result in results:
                title = result.title
                url = result.pdf_url
                published_date = result.published.strftime("%Y-%m-%d")
                authors_raw = result.authors
                author_names = [author.name for author in authors_raw]
                # authors = ", ".join(author_names)
                
                papers.append({
                    "title": title,
                    "url": url,
                    "published_date": published_date,
                    "authors": author_names,
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
        pdf_path = download_pdf(url, title)
        if not pdf_path:
            print(f"Skipping {title} due to failed download.")
            return None
        
        paper_text = extract_text_from_pdf(pdf_path)
        if not paper_text:
            print(f"Skipping {title} due to failed text extraction.")
            return None
        
        summary = summarize_text(paper_text, title)
        
        store_summary_in_db(title, summary)
        
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"Deleted PDF: {pdf_path}")
        
        return summary
    except Exception as e:
        print(f"Error processing paper '{title}': {e}")
        return None


# DEBUG
papers = search_papers("attention is all you need")
for paper in papers:
    print("Title:", paper["title"])
    print("URL:", paper["url"])
    print("Published Date:", paper["published_date"])
    print("Authors:", ", ".join(paper["authors"]))  # Join author names into a single string
    print("-" * 40)