from sentence_transformers import SentenceTransformer
import chromadb

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(name="paper_summaries")

def generate_embedding(text):
    return embedding_model.encode(text).tolist()

def store_summary_in_db(title, summary):
    try:
        embedding = generate_embedding(summary) # document emnbedding
        collection.add(
            documents=[summary],
            metadatas=[{"title": title}],
            ids=[title],
            embeddings=[embedding]
        )     
        
        return f"Summary for '{title}' successfully stored in the database."
    except Exception as e:
        print(f"Error storing summary in the database: {str(e)}")
        raise ValueError(f"Failed to store summary for '{title}'. Error: {str(e)}")

def search_similar_summaries(query, n_results=3):
    query_embedding = generate_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results