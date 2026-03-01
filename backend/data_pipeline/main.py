"""
main.py – Orchestrates the Day 1 data pipeline.

Steps:
1. Parse all raw CSV files (Google Maps, KWS parks, Magical Kenya).
2. Enrich with manually curated data (manual_seed.json).
3. Apply official KWS entry fees from PDF-extracted JSON.
4. Convert raw records to unified schema.
5. Clean, normalize, deduplicate.
6. Save unified JSON.
7. Chunk and embed into Chroma vector store.
8. Test retrieval.
"""
import json
import os
from src.parsers import google_maps, kws, magical_kenya, fee_parse
from src import cleaner, embedder, retriever

# ============== Helper functions ==============

def parse_all_sources(raw_dir="data/raw"):
    """Scan raw_dir for CSV files and parse them according to their names."""
    all_raw = []
    for filename in os.listdir(raw_dir):
        if not filename.endswith('.csv'):
            continue
        filepath = os.path.join(raw_dir, filename)
        # Decide parser based on filename
        if filename.startswith('kws') and not filename.startswith('kws_fees'):
            print(f"Parsing KWS file: {filename}")
            all_raw.extend(kws.parse_kws_csv(filepath))
        elif filename.startswith('magical_kenya'):
            print(f"Parsing Magical Kenya file: {filename}")
            all_raw.extend(magical_kenya.parse_magical_kenya_csv(filepath))
        else:
            #  Google Maps CSVs
            print(f"Parsing Google Maps file: {filename}")
            all_raw.extend(google_maps.parse_google_maps_csv(filepath))
    return all_raw

def enrich_with_manual_data(raw_locations, manual_path="data/manual_seed.json"):
    """Merge manually curated data into raw locations."""
    if os.path.exists(manual_path):
        with open(manual_path, 'r') as f:
            manual = json.load(f)
        manual_dict = {loc['name'].lower(): loc for loc in manual}
        for loc in raw_locations:
            key = loc.get('name', '').lower()
            if key in manual_dict:
                loc.update(manual_dict[key])
    return raw_locations

def apply_kws_fees(locations, fees_path="data/processed/kws_fees.json"):
    """
    Update entry_fee for locations that match KWS fee entries.
    Fees dict keys are lowercase park names.
    """
    if not os.path.exists(fees_path):
        print("KWS fees file not found. Skipping.")
        return locations

    with open(fees_path, 'r') as f:
        fees = json.load(f)

    # Normalise fees keys (they are already lowercase, but ensure)
    fees_lower = {k.lower(): v for k, v in fees.items()}

    for loc in locations:
        name_lower = loc.get('name', '').lower()
        if not name_lower:
            continue

        # Direct match
        if name_lower in fees_lower:
            loc['entry_fee'] = fees_lower[name_lower]
            continue

        # Try without common suffixes
        base = (name_lower
                .replace(' national park', '')
                .replace(' national reserve', '')
                .replace(' forest', '')
                .replace(' marine park', '')
                .strip())
        # Check if base matches any fee key
        for fee_key in fees_lower:
            if base in fee_key or fee_key in name_lower:
                loc['entry_fee'] = fees_lower[fee_key]
                break
    return locations

def convert_to_schema(raw_locations):
    """Map raw fields to the unified schema (with placeholders)."""
    unified = []
    for raw in raw_locations:
        # Determine a more specific type from place_type (Google Maps) or category
        place_type = raw.get('place_type', '').lower()
        loc_type = 'park'  # default
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
        elif 'beach' in place_type:
            loc_type = 'beach'

        loc = {
            "id": raw.get('name', '').lower().replace(' ', '-'),
            "name": raw.get('name', ''),
            "type": loc_type,
            "county": raw.get('county', ''),
            "region": raw.get('region', ''),
            "description": raw.get('description', ''),
            "climate": raw.get('climate', ''),
            "best_time": raw.get('best_time', ''),
            "activities": [],
            "entry_fee": {
                "citizen": "",
                "resident": "",
                "non_resident": ""
            },
            "estimated_daily_cost": {
                "budget": raw.get('daily_budget', ''),
                "mid": raw.get('daily_mid', ''),
                "luxury": raw.get('daily_luxury', '')
            },
            "transport_options": [],
            "nearby_locations": [],
            "tags": raw.get('categories', []) if raw.get('categories') else []
        }

        # If we have a review snippet, use it as a basic activity
        if raw.get('description'):
            act_name = raw['description'][:50] + "..."
            loc['activities'].append({
                "name": act_name,
                "type": "adventure",
                "estimated_cost": ""
            })

        # If we have categories from Magical Kenya, add as tags and activities
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

# ============== Main pipeline ==============

def run_pipeline():
    print("=== DAY 1: Building Knowledge Base ===")

    # 1. Parse all raw CSV files
    raw_locations = parse_all_sources()
    print(f"Parsed {len(raw_locations)} raw records.")

    # 2. Enrich with manual seed data
    raw_locations = enrich_with_manual_data(raw_locations)
    print("Enriched with manual data.")

    # 3. Apply KWS entry fees from PDF-extracted JSON
    raw_locations = apply_kws_fees(raw_locations)
    print("Applied KWS entry fees.")

    # 4. Convert to unified schema
    unified = convert_to_schema(raw_locations)

    # 5. Clean and normalize
    unified = cleaner.merge_sources([unified])  # merge duplicates
    unified = cleaner.deduplicate(unified)
    for loc in unified:
        loc = cleaner.normalize_fees(loc)
        # Generate tags if missing
        if not loc['tags']:
            loc['tags'] = cleaner.generate_tags(loc)

    # 6. Save unified JSON
    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/kenya_tourism.json"
    with open(output_path, "w") as f:
        json.dump(unified, f, indent=2)
    print(f"Saved {len(unified)} locations to {output_path}")

    # 7. Chunk and embed
    print("Creating chunks and building vector store...")
    chunks = embedder.load_and_chunk_all(output_path)
    vectordb = embedder.build_vector_store(chunks, persist_dir="data/chroma_db")
    print(f"Vector store created with {vectordb._collection.count()} vectors.")

    # 8. Test retrieval
    print("\nTesting retrieval with sample query:")
    retriever.test_retriever("Where can I see elephants and what is the entry fee?")

if __name__ == "__main__":
    run_pipeline()