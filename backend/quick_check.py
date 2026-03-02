# quick_check.py
import weaviate
from weaviate.classes.init import Auth
import os
from dotenv import load_dotenv

load_dotenv()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
    skip_init_checks=True
)

locations = client.collections.get("Location")
count = locations.aggregate.over_all(total_count=True)
print(f"✅ Found {count.total_count} locations in Weaviate")

# Test a search
response = locations.query.near_text(query="safari park", limit=3)
print(f"\nSample search results:")
for obj in response.objects:
    print(f"- {obj.properties['name']}")
    
client.close()