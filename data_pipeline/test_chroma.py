import chromadb
from sentence_transformers import SentenceTransformer

# Load the same embedding model used in the pipeline
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Connect to your Chroma DB
client = chromadb.PersistentClient(path="data/chroma_db")
# Use the same collection name as the pipeline
collection = client.get_or_create_collection("tourism_locations")

query = "Where can I see elephants and what is the entry fee?"
query_emb = model.encode(query).tolist()

results = collection.query(query_embeddings=[query_emb], n_results=5)

print(f"\nQuery: {query}\n")
if results['documents'] and results['documents'][0]:
    for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"{i+1}. {doc[:200]}...")
        print(f"   metadata: {meta}\n")
else:
    print("No results found. Your vector store might be empty.")