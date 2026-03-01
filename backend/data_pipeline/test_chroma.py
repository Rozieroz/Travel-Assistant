import os
import chromadb
from pathlib import Path

chroma_dir = "data/chroma_db"
print(f"Checking Chroma DB at: {os.path.abspath(chroma_dir)}")

if not os.path.exists(chroma_dir):
    print("Directory does not exist!")
else:
    print("Directory exists. Contents:")
    for root, dirs, files in os.walk(chroma_dir):
        level = root.replace(chroma_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

# Connect to Chroma and list collections
client = chromadb.PersistentClient(path=chroma_dir)
collections = client.list_collections()
print(f"\nCollections in DB: {[c.name for c in collections]}")

for col in collections:
    count = col.count()
    print(f"Collection '{col.name}' has {count} documents.")
    if count > 0:
        sample = col.get(limit=1, include=["documents", "metadatas"])
        print("Sample document:", sample['documents'][0][:100] if sample['documents'] else "None")
        print("Sample metadata:", sample['metadatas'][0])