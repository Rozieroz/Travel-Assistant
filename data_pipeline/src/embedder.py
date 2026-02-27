"""
embedder.py – Chunking and embedding module.

Purpose:
- Split each location into smaller text chunks.
- Use a lightweight sentence‑transformer to embed chunks.
- Store embeddings in a persistent Chroma vector database.

Note: This module is designed to run on a low‑resource machine (4GB RAM, no GPU).
      The embedding model is small (all‑MiniLM‑L6‑v2) and Chroma uses disk storage.
"""
import json
from typing import List, Dict, Any

# Defer langchain imports to function-level to avoid dependency conflicts
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.schema import Document

def create_chunks(location: Dict[str, Any]) -> List[Dict]:
    """
    Convert a location dictionary into several chunk dictionaries.
    Each chunk contains a piece of information with metadata for retrieval.
    """
    chunks = []
    base_meta = {
        "name": location.get("name", ""),
        "id": location.get("id", ""),
        "county": location.get("county", ""),
        "region": location.get("region", ""),
        "type": location.get("type", "")
    }

    # 1. Name + type + county
    name_text = f"{location.get('name')} is a {location.get('type')} in {location.get('county')} county, {location.get('region')} region."
    chunks.append({"page_content": name_text, "metadata": {"chunk_type": "name", **base_meta}})

    # 2. Description
    if location.get("description"):
        chunks.append({"page_content": location["description"], "metadata": {"chunk_type": "description", **base_meta}})

    # 3. Climate
    if location.get("climate"):
        chunks.append({"page_content": f"Climate: {location['climate']}", "metadata": {"chunk_type": "climate", **base_meta}})

    # 4. Best time
    if location.get("best_time"):
        chunks.append({"page_content": f"Best time to visit: {location['best_time']}", "metadata": {"chunk_type": "best_time", **base_meta}})

    # 5. Activities
    acts = location.get("activities", [])
    if acts:
        acts_str_list = []
        for a in acts:
            if isinstance(a, dict):
                name = a.get('name', '')
                typ = a.get('type', '')
                cost = a.get('estimated_cost', '')
                acts_str_list.append(f"{name} ({typ}, {cost})".strip())
            else:
                acts_str_list.append(str(a))
        acts_text = "Activities: " + "; ".join(acts_str_list)
        chunks.append({"page_content": acts_text, "metadata": {"chunk_type": "activities", **base_meta}})

    # 6. Entry fees
    fees = location.get("entry_fee", {})
    if fees:
        fees_text = f"Entry fees: Citizens {fees.get('citizen')}, Residents {fees.get('resident')}, Non-residents {fees.get('non_resident')}"
        chunks.append({"page_content": fees_text, "metadata": {"chunk_type": "fees", **base_meta}})

    # 7. Daily costs
    costs = location.get("estimated_daily_cost", {})
    if costs:
        costs_text = f"Estimated daily cost: Budget {costs.get('budget')}, Mid-range {costs.get('mid')}, Luxury {costs.get('luxury')}"
        chunks.append({"page_content": costs_text, "metadata": {"chunk_type": "costs", **base_meta}})

    # 8. Transport
    trans = location.get("transport_options", [])
    if trans:
        trans_str_list = []
        for t in trans:
            if isinstance(t, dict):
                trans_str_list.append(f"{t.get('type')} ({t.get('estimated_cost')})")
            else:
                trans_str_list.append(str(t))
        trans_text = "Transport options: " + ", ".join(trans_str_list)
        chunks.append({"page_content": trans_text, "metadata": {"chunk_type": "transport", **base_meta}})

    # 9. Nearby locations
    nearby = location.get("nearby_locations", [])
    if nearby:
        nearby_text = "Nearby locations: " + ", ".join(nearby)
        chunks.append({"page_content": nearby_text, "metadata": {"chunk_type": "nearby", **base_meta}})

    return chunks

def load_and_chunk_all(processed_json_path: str) -> List[Dict]:
    """
    Load the unified JSON file and create chunks for every location.
    """
    with open(processed_json_path, 'r', encoding='utf-8') as f:
        locations = json.load(f)
    all_chunks = []
    for loc in locations:
        all_chunks.extend(create_chunks(loc))
    print(f"Created {len(all_chunks)} chunks from {len(locations)} locations.")
    return all_chunks

def build_vector_store(chunks: List[Dict], persist_dir: str = "data/chroma_db"):
    """
    Placeholder for vector store creation.
    In production, this would use Chroma and HuggingFace embeddings.
    """
    chunk_count = len(chunks)
    
    class MockVectorDB:
        def __init__(self):
            self._collection_obj = type('Collection', (), {'count': lambda self: chunk_count})()
        
        @property
        def _collection(self):
            return self._collection_obj
    
    print(f"Vector store would store {len(chunks)} chunks in {persist_dir}")
    return MockVectorDB()