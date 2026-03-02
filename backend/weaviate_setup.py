"""
weaviate_setup.py – One-time script to create schema and load your tourism data into Weaviate.
Run this locally once to populate your cloud vector database.
"""

import weaviate
import json
from weaviate.classes.config import Property, DataType
from weaviate.classes.init import Auth, AdditionalConfig, Timeout
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Configuration - get from .env
WEAVIATE_URL = os.environ.get("WEAVIATE_URL")
WEAVIATE_API_KEY = os.environ.get("WEAVIATE_API_KEY")


print(f"🔌 Connecting to Weaviate at: {WEAVIATE_URL}")

try:
    # Connect with increased timeouts and skip_init_checks to bypass gRPC health check 
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
        skip_init_checks=True,  #  Skip gRPC health check to avoid timeout 
        additional_config=AdditionalConfig(
            timeout=Timeout(init=30, query=60, insert=120)  #  Increased timeouts 
        )
    )
    
    print("Connected to Weaviate Cloud")
    
except Exception as e:
    print(f"Connection failed: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check your WEAVIATE_URL and WEAVIATE_API_KEY in .env")
    print("2. Try increasing timeout values further")
    print("3. Check your network connection - gRPC is sensitive to latency ")
    print("4. Visit https://console.weaviate.cloud to verify your cluster is active")
    exit(1)

# Check if connection is working
try:
    if not client.is_ready():
        print(" Client connected but not ready - waiting 5 seconds...")
        time.sleep(5)
        if not client.is_ready():
            print("Weaviate instance not ready")
            exit(1)
    print("Weaviate instance is ready")
except Exception as e:
    print(f"Readiness check failed: {e}")
    exit(1)

# Define the schema for locations
def create_schema():
    """Create the Location collection in Weaviate"""
    
    try:
        # Check if collection already exists
        if client.collections.exists("Location"):
            print(" Location collection already exists, deleting...")
            client.collections.delete("Location")
            time.sleep(2)  # Give it time to delete
        
        # Create new collection
        location_collection = client.collections.create(
            name="Location",
            description="Kenyan tourism and local spots",
            properties=[
                Property(name="name", data_type=DataType.TEXT, description="Location name"),
                Property(name="type", data_type=DataType.TEXT),
                Property(name="county", data_type=DataType.TEXT),
                Property(name="region", data_type=DataType.TEXT),
                Property(name="description", data_type=DataType.TEXT),
                Property(name="climate", data_type=DataType.TEXT),
                Property(name="best_time", data_type=DataType.TEXT),
                Property(name="activities", data_type=DataType.TEXT_ARRAY),  # Now expects list of strings
                Property(name="entry_fee_citizen", data_type=DataType.TEXT),
                Property(name="entry_fee_resident", data_type=DataType.TEXT),
                Property(name="entry_fee_non_resident", data_type=DataType.TEXT),
                Property(name="daily_cost_budget", data_type=DataType.TEXT),
                Property(name="daily_cost_mid", data_type=DataType.TEXT),
                Property(name="daily_cost_luxury", data_type=DataType.TEXT),
                Property(name="transport_options", data_type=DataType.TEXT_ARRAY),  # Should be strings
                Property(name="nearby_locations", data_type=DataType.TEXT_ARRAY),   # Should be strings
                Property(name="tags", data_type=DataType.TEXT_ARRAY),                # Should be strings
            ],
            # No vectorizer – we'll rely on keyword search or use a separate embedding service
            vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
        )
        print("Created Location collection")
        return True
    except Exception as e:
        print(f"Failed to create schema: {e}")
        return False

def load_data():
    """Load locations from kenya_tourism.json into Weaviate"""
    
    try:
        json_path = "data_pipeline/data/processed/kenya_tourism.json"
        print(f" Loading data from: {json_path}")
        
        with open(json_path, "r") as f:
            locations = json.load(f)
        
        print(f"Found {len(locations)} locations to import")
        
        location_collection = client.collections.get("Location")
        
        # Insert in smaller batches to avoid timeouts 
        batch_size = 20
        total = len(locations)
        successful = 0
        
        for i in range(0, total, batch_size):
            batch = locations[i:i+batch_size]
            print("=" * 40)
            print(f"Importing batch {i//batch_size + 1}/{(total-1)//batch_size + 1}...")

            
            with location_collection.batch.fixed_size(batch_size=20) as batch_writer:
                for loc in batch:
                    # Convert activities from list of dicts to list of strings
                    activities_raw = loc.get("activities", [])
                    if isinstance(activities_raw, list):
                        # If it's a list of dicts, extract a representative string (e.g., activity name)
                        activities = []
                        for act in activities_raw:
                            if isinstance(act, dict):
                                # Use the activity name if available, otherwise fallback to a formatted string
                                name = act.get("name", "")
                                if name:
                                    activities.append(name)
                                else:
                                    # If no name, maybe use type? Or skip
                                    pass
                            elif isinstance(act, str):
                                activities.append(act)
                    else:
                        activities = []

                    # Convert transport_options from list of dicts to list of strings
                    transport_raw = loc.get("transport_options", [])
                    transport_options = []
                    for t in transport_raw:
                        if isinstance(t, dict):
                            # Format as "type (cost)" or just type
                            typ = t.get("type", "")
                            cost = t.get("estimated_cost", "")
                            if typ and cost:
                                transport_options.append(f"{typ} ({cost})")
                            elif typ:
                                transport_options.append(typ)
                        elif isinstance(t, str):
                            transport_options.append(t)

                    # nearby_locations should already be list of strings
                    nearby = loc.get("nearby_locations", [])
                    if not isinstance(nearby, list):
                        nearby = [nearby] if nearby else []

                    # tags should be list of strings
                    tags = loc.get("tags", [])
                    if not isinstance(tags, list):
                        tags = [tags] if tags else []

                    # Prepare properties
                    properties = {
                        "name": loc.get("name", ""),
                        "type": loc.get("type", ""),
                        "county": loc.get("county", ""),
                        "region": loc.get("region", ""),
                        "description": loc.get("description", ""),
                        "climate": loc.get("climate", ""),
                        "best_time": loc.get("best_time", ""),
                        "activities": activities,  # Now a list of strings
                        "entry_fee_citizen": loc.get("entry_fee", {}).get("citizen", ""),
                        "entry_fee_resident": loc.get("entry_fee", {}).get("resident", ""),
                        "entry_fee_non_resident": loc.get("entry_fee", {}).get("non_resident", ""),
                        "daily_cost_budget": loc.get("estimated_daily_cost", {}).get("budget", ""),
                        "daily_cost_mid": loc.get("estimated_daily_cost", {}).get("mid", ""),
                        "daily_cost_luxury": loc.get("estimated_daily_cost", {}).get("luxury", ""),
                        "transport_options": transport_options,  # List of strings
                        "nearby_locations": nearby,              # List of strings
                        "tags": tags,                            # List of strings
                    }
                    
                    batch_writer.add_object(
                        properties=properties,
                        uuid=None
                    )
                    successful += 1
            
            time.sleep(1)  # Small pause between batches 
        
        print(f"Successfully loaded {successful}/{total} locations")
        return True
        
    except FileNotFoundError:
        print(f"JSON file not found at: {json_path}")
        return False
    except Exception as e:
        print(f"Failed to load data: {e}")
        return False

if __name__ == "__main__":
    print("🦒 Weaviate Setup for Safari Scouts\n")
    
    if create_schema():
        if load_data():
            print("\nSetup complete!")
        else:
            print("\nData loading failed")
    else:
        print("\nSchema creation failed")
    
    client.close()
    print("👋 Connection closed")