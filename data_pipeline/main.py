"""
Main pipeline to build the knowledge base and vector store for Safari Scouts.
Steps:
1. Parse all raw data sources (Google Maps CSV, KWS CSV, Magical Kenya CSV, KWS fees PDF).
2. Enrich with manual data from manual_seed.json.
3. Convert to unified schema (partial).
4. Clean and normalize (standardize fees to KES, generate tags).
5. Enrich with KWS fees (match by name).
6. Save unified JSON.
7. Create chunks and build vector store.
8. Test retrieval with sample queries."""

import json
import os

# Import parsers and other modules
from src.parsers import google_maps, kws, magical_kenya, kws_fees
from src import cleaner, embedder, retriever

def parse_all_sources(raw_dir="data/raw"):
    all_raw = []
    for filename in os.listdir(raw_dir):
        if not filename.endswith('.csv'):
            continue
        filepath = os.path.join(raw_dir, filename)
        if filename.startswith('kws') and filename != 'kws_fees.csv':
            print(f"Parsing KWS file: {filename}")
            all_raw.extend(kws.parse_kws_csv(filepath))
        elif filename.startswith('magicalkenya'):
            print(f"Parsing Magical Kenya file: {filename}")
            all_raw.extend(magical_kenya.parse_magical_kenya_csv(filepath))
        elif filename == 'kws_fees.csv':
            # This is handled separately later
            continue
        else:
            print(f"Parsing Google Maps file: {filename}")
            all_raw.extend(google_maps.parse_google_maps_csv(filepath))
    return all_raw

def enrich_with_manual_data(raw_locations):
    manual_path = "data/manual_seed.json"
    if os.path.exists(manual_path):
        with open(manual_path, 'r') as f:
            manual = json.load(f)
        manual_dict = {loc['name'].lower(): loc for loc in manual}
        for loc in raw_locations:
            key = loc.get('name', '').lower()
            if key in manual_dict:
                loc.update(manual_dict[key])
    return raw_locations

def enrich_with_kws_fees(locations, fees_dict):
    """
    Update entry_fee for locations that match KWS fee entries.
    """
    for loc in locations:
        name = loc.get('name', '').lower().strip()
        # Try exact match
        if name in fees_dict:
            loc['entry_fee'] = fees_dict[name]
            continue
        # Try without "national park" or "national reserve"
        simplified = name.replace('national park', '').replace('national reserve', '').strip()
        if simplified in fees_dict:
            loc['entry_fee'] = fees_dict[simplified]
            continue
        # Try partial match
        for fee_name, fee in fees_dict.items():
            if fee_name in name or name in fee_name:
                loc['entry_fee'] = fee
                break
    return locations

def convert_to_schema(raw_locations):
    unified = []
    for raw in raw_locations:
        place_type = raw.get('place_type', '').lower()
        loc_type = 'park'
        if 'water park' in place_type:
            loc_type = 'park'
        elif 'amusement park' in place_type or 'theme park' in place_type:
            loc_type = 'park'
        elif 'national park' in place_type or 'national reserve' in place_type:
            loc_type = 'park'
        elif 'nature preserve' in place_type:
            loc_type = 'forest'
        elif 'mountain' in place_type:
            loc_type = 'mountain'

        loc = {
            "id": raw.get('name', '').lower().replace(' ', '-'),
            "name": raw.get('name', ''),
            "type": loc_type,
            "county": "",
            "region": raw.get('region', ''),
            "description": raw.get('description', ''),
            "climate": "",
            "best_time": "",
            "activities": [],
            "entry_fee": {
                "citizen": "",
                "resident": "",
                "non_resident": ""
            },
            "estimated_daily_cost": {
                "budget": "",
                "mid": "",
                "luxury": ""
            },
            "transport_options": [],
            "nearby_locations": [],
            "tags": raw.get('categories', []) if raw.get('categories') else []
        }

        if raw.get('description'):
            act_name = raw['description'][:50] + "..."
            loc['activities'].append({
                "name": act_name,
                "type": "adventure",
                "estimated_cost": ""
            })

        if raw.get('categories'):
            for cat in raw['categories']:
                if cat not in loc['tags']:
                    loc['tags'].append(cat)
                loc['activities'].append({
                    "name": f"Experience {cat}",
                    "type": _map_category_to_activity_type(cat),
                    "estimated_cost": ""
                })

        unified.append(loc)
    return unified

def _map_category_to_activity_type(cat):
    cat_low = cat.lower()
    if 'adventure' in cat_low:
        return 'adventure'
    if 'wildlife' in cat_low or 'safari' in cat_low:
        return 'wildlife'
    if 'culture' in cat_low or 'traditional' in cat_low:
        return 'cultural'
    if 'relax' in cat_low or 'beach' in cat_low:
        return 'relaxation'
    return 'adventure'

def run_pipeline():
    print("=== DAY 1: Building Knowledge Base ===")

    # 1. Parse all raw files (except kws_fees.csv)
    raw_locations = parse_all_sources()
    print(f"Parsed {len(raw_locations)} raw records.")

    # 2. Enrich with manual data
    raw_locations = enrich_with_manual_data(raw_locations)

    # 3. Convert to unified schema (partial)
    unified = convert_to_schema(raw_locations)

    # 4. Clean and normalize
    unified = cleaner.merge_sources([unified])
    unified = cleaner.deduplicate(unified)

    # 5. Enrich with KWS fees
    fees_path = "data/raw/kws_fees.csv"
    if os.path.exists(fees_path):
        print("Enriching with KWS fees...")
        fees_dict = kws_fees.parse_kws_fees_csv(fees_path)
        unified = enrich_with_kws_fees(unified, fees_dict)
    else:
        print("KWS fees CSV not found, skipping.")

    # 6. Generate tags (if not already)
    for loc in unified:
        loc = cleaner.normalize_fees(loc)
        if not loc['tags']:
            loc['tags'] = cleaner.generate_tags(loc)

    # 7. Save unified JSON
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/kenya_tourism.json", "w") as f:
        json.dump(unified, f, indent=2)
    print(f"Saved {len(unified)} locations to data/processed/kenya_tourism.json")

    # 8. Chunk and embed
    print("Creating chunks and building vector store...")
    chunks = embedder.load_and_chunk_all("data/processed/kenya_tourism.json")
    vectordb = embedder.build_vector_store(chunks, persist_dir="data/chroma_db")
    print(f"Vector store created with {vectordb._collection.count()} vectors.")

    # 9. Test retrieval
    print("\nTesting retrieval with sample query:")
    retriever.test_retriever("Where can I see elephants and what is the entry fee?")

if __name__ == "__main__":
    run_pipeline()