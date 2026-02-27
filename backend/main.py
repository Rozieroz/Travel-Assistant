import json
import os
from src.scrapers import google_maps, kws_parser, magical_kenya_parser
from src import cleaner, embedder, retriever

def parse_all_sources():
    """Parse all raw CSV files and return list of raw location dicts."""
    all_raw = []

    # Google Maps amusement parks
    if os.path.exists("data/raw/google_maps_amusement.csv"):
        all_raw.extend(google_maps.parse_google_maps_csv("data/raw/google_maps_amusement.csv"))

    # Google Maps national parks/reserves
    if os.path.exists("data/raw/reserves_kenya.csv"):
        all_raw.extend(google_maps.parse_google_maps_csv("data/raw/reserves_kenya.csv"))

    # KWS parks
    if os.path.exists("data/raw/kws.csv"):
        all_raw.extend(kws_parser.parse_kws_csv("data/raw/kws.csv"))

    # Magical Kenya parks
    if os.path.exists("data/raw/magicalkenya_places.csv"):
        all_raw.extend(magical_kenya_parser.parse_magical_kenya_csv("data/raw/magicalkenya_places.csv"))


    # Magical Kenya destinations (cities, beaches, mountains)
    if os.path.exists("data/raw/magicalkenya.csv"):
        all_raw.extend(magical_kenya_parser.parse_magical_kenya_csv("data/raw/magicalkenya.csv"))

    # fun indoor
    if os.path.exists("data/raw/indoor.csv"):
        all_raw.extend(magical_kenya_parser.parse_magical_kenya_csv("data/raw/indoor.csv"))


    return all_raw

def enrich_with_manual_data(raw_locations):
    """
    Load manual seed and merge with parsed data.
    Manual seed should contain full records for key locations.
    For locations not in manual seed, we keep parsed data with missing fields.
    """
    manual_path = "data/manual_seed.json"
    if os.path.exists(manual_path):
        with open(manual_path, 'r') as f:
            manual = json.load(f)
        # Merge: if name matches, update parsed with manual fields
        manual_dict = {loc['name'].lower(): loc for loc in manual}
        for loc in raw_locations:
            key = loc['name'].lower()
            if key in manual_dict:
                loc.update(manual_dict[key])
    return raw_locations

def convert_to_schema(raw_locations):
    """
    Convert raw dicts to the unified schema (with placeholders).
    This is a best-effort mapping.
    """
    unified = []
    for raw in raw_locations:
        # Start with empty template
        loc = {
            "id": raw.get('name', '').lower().replace(' ', '-'),
            "name": raw.get('name', ''),
            "type": raw.get('type', 'park'),
            "county": raw.get('county', ''),
            "region": raw.get('region', ''),
            "description": raw.get('description', raw.get('description', '')),
            "climate": raw.get('climate', ''),
            "best_time": raw.get('best_time', ''),
            "activities": [],  # need to parse from review snippets or categories
            "entry_fee": {
                "citizen": raw.get('entry_fee_citizen', ''),
                "resident": raw.get('entry_fee_resident', ''),
                "non_resident": raw.get('entry_fee_non_resident', '')
            },
            "estimated_daily_cost": {
                "budget": raw.get('daily_budget', ''),
                "mid": raw.get('daily_mid', ''),
                "luxury": raw.get('daily_luxury', '')
            },
            "transport_options": [],
            "nearby_locations": [],
            "tags": []
        }

        # If we have review snippets, try to create an activity list
        if raw.get('description'):
            # This is simplistic; you might want to use NLP to extract activities
            loc['activities'] = [{"name": raw['description'][:50], "type": "adventure", "estimated_cost": ""}]

        # If we have categories from Magical Kenya, use as tags
        if raw.get('categories'):
            loc['tags'] = raw['categories']

        unified.append(loc)
    return unified

def run_pipeline():
    print("=== DAY 1: Building Knowledge Base ===")

    # 1. Parse all raw sources
    raw_locations = parse_all_sources()
    print(f"Parsed {len(raw_locations)} raw records.")

    # 2. Enrich with manual data
    raw_locations = enrich_with_manual_data(raw_locations)

    # 3. Convert to unified schema
    unified = convert_to_schema(raw_locations)

    # 4. Clean and normalize
    unified = cleaner.merge_sources([unified])  # merge duplicates within same list
    unified = cleaner.deduplicate(unified)
    for loc in unified:
        loc = cleaner.normalize_fees(loc)
        loc['tags'] = cleaner.generate_tags(loc)

    # 5. Save unified JSON
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/kenya_tourism.json", "w") as f:
        json.dump(unified, f, indent=2)
    print(f"Saved {len(unified)} locations to data/processed/kenya_tourism.json")

    # 6. Chunk and embed
    print("Creating chunks and building vector store...")
    chunks = embedder.load_and_chunk_all("data/processed/kenya_tourism.json")
    vectordb = embedder.build_vector_store(chunks, persist_dir="data/chroma_db")
    print(f"Vector store created with {vectordb._collection.count()} vectors.")

    # 7. Test retrieval
    print("\nTesting retrieval with sample query:")
    retriever.test_retriever("Where can I take kids for fun activities?")

if __name__ == "__main__":
    run_pipeline()