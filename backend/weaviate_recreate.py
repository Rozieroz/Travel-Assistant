"""
weaviate_recreate.py – Recreate Location collection with available vectorizer.
"""

import weaviate
import json
from weaviate.classes.config import Property, DataType, Configure
from weaviate.classes.init import Auth
import os
import time
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

print(f"🔌 Connecting to Weaviate at: {WEAVIATE_URL}")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
    skip_init_checks=True,
)

print("✅ Connected to Weaviate Cloud")

# Delete old collection if it exists
if client.collections.exists("Location"):
    print("⚠️  Deleting existing Location collection...")
    client.collections.delete("Location")
    time.sleep(2)

print("🔄 Creating new Location collection with contextionary vectorizer...")

# Use text2vec-contextionary – built‑in, no API key needed
locations = client.collections.create(
    name="Location",
    description="Kenyan tourism and local spots",
    vectorizer_config=Configure.Vectorizer.text2vec_contextionary(),  # ⬅️ changed
    properties=[
        Property(name="name", data_type=DataType.TEXT),
        Property(name="type", data_type=DataType.TEXT),
        Property(name="county", data_type=DataType.TEXT),
        Property(name="region", data_type=DataType.TEXT),
        Property(name="description", data_type=DataType.TEXT),
        Property(name="climate", data_type=DataType.TEXT),
        Property(name="best_time", data_type=DataType.TEXT),
        Property(name="activities", data_type=DataType.TEXT_ARRAY),
        Property(name="entry_fee_citizen", data_type=DataType.TEXT),
        Property(name="entry_fee_resident", data_type=DataType.TEXT),
        Property(name="entry_fee_non_resident", data_type=DataType.TEXT),
        Property(name="daily_cost_budget", data_type=DataType.TEXT),
        Property(name="daily_cost_mid", data_type=DataType.TEXT),
        Property(name="daily_cost_luxury", data_type=DataType.TEXT),
        Property(name="transport_options", data_type=DataType.TEXT_ARRAY),
        Property(name="nearby_locations", data_type=DataType.TEXT_ARRAY),
        Property(name="tags", data_type=DataType.TEXT_ARRAY),
    ]
)

print("✅ Collection created with contextionary vectorizer")

# Load data
print("📂 Loading data from JSON...")
with open("data_pipeline/data/processed/kenya_tourism.json", "r") as f:
    locations_data = json.load(f)

print(f"📊 Found {len(locations_data)} locations")

# Insert in batches
batch_size = 50
successful = 0

for i in range(0, len(locations_data), batch_size):
    batch = locations_data[i:i+batch_size]
    print(f"📦 Importing batch {i//batch_size + 1}/{(len(locations_data)-1)//batch_size + 1}...")
    
    with locations.batch.fixed_size(batch_size=20) as batch_writer:
        for loc in batch:
            # Flatten activities to simple strings
            activities = []
            if loc.get("activities"):
                if isinstance(loc["activities"], list):
                    for act in loc["activities"]:
                        if isinstance(act, dict):
                            activities.append(act.get("name", ""))
                        elif isinstance(act, str):
                            activities.append(act)
            
            properties = {
                "name": loc.get("name", ""),
                "type": loc.get("type", ""),
                "county": loc.get("county", ""),
                "region": loc.get("region", ""),
                "description": loc.get("description", ""),
                "climate": loc.get("climate", ""),
                "best_time": loc.get("best_time", ""),
                "activities": activities,
                "entry_fee_citizen": loc.get("entry_fee", {}).get("citizen", ""),
                "entry_fee_resident": loc.get("entry_fee", {}).get("resident", ""),
                "entry_fee_non_resident": loc.get("entry_fee", {}).get("non_resident", ""),
                "daily_cost_budget": loc.get("estimated_daily_cost", {}).get("budget", ""),
                "daily_cost_mid": loc.get("estimated_daily_cost", {}).get("mid", ""),
                "daily_cost_luxury": loc.get("estimated_daily_cost", {}).get("luxury", ""),
                "transport_options": [str(t) for t in loc.get("transport_options", [])],
                "nearby_locations": loc.get("nearby_locations", []),
                "tags": loc.get("tags", []),
            }
            
            batch_writer.add_object(properties=properties, uuid=None)
            successful += 1
    
    time.sleep(1)

print(f"✅ Successfully imported {successful}/{len(locations_data)} locations")

# Test the search
print("\n🔍 Testing search with contextionary vectorizer...")
try:
    response = locations.query.near_text(query="safari park with elephants", limit=3)
    print(f"Found {len(response.objects)} results:")
    for obj in response.objects:
        print(f"  - {obj.properties['name']}")
except Exception as e:
    print(f"Search test failed: {e}")

client.close()
print("👋 Done!")