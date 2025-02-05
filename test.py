from scholarly import scholarly

def search_papers(query):
    print(f"Searching for the most relevant paper on '{query}' using Google Scholar...")
    # Perform the search and fetch the first result
    search_query = scholarly.search_pubs(query)
    first_paper = next(search_query, None)  # Get the first result
    
    if first_paper:
        title = first_paper.get("bib", {}).get("title", "Unknown Title")
        url = first_paper.get("pub_url", None)
        citations = first_paper.get("num_citations", 0)
        year = first_paper.get("bib", {}).get("year", "Unknown Year")
        
        print(f"Found the most relevant paper: {title}")
        return [{
            "title": title,
            "url": url,
            "citations": citations,
            "year": year
        }]
    else:
        print("No relevant papers found.")
        return []
    
search_papers("machine learning")