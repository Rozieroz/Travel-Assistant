"""
weaviate_retriever.py – Retrieve context from Weaviate for the RAG system.
Uses BM25 keyword search (no vectors required).
"""

import os
from typing import List, Dict, Any

import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth, AdditionalConfig, Timeout
from weaviate.classes.query import MetadataQuery

load_dotenv()


class WeaviateRetriever:
    def __init__(self):
        """Initialize connection to Weaviate Cloud."""
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv("WEAVIATE_URL"),
            auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
            skip_init_checks=True,  # Avoid gRPC timeout issues
            additional_config=AdditionalConfig(
                timeout=Timeout(init=10, query=30, insert=60)
            )
        )
        self.locations = self.client.collections.get("Location")

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for locations using BM25 keyword search.
        Returns a list of location objects with properties and relevance scores.
        """
        response = self.locations.query.bm25(
            query=query,
            query_properties=["name", "description", "activities", "tags"],
            limit=limit,
            return_metadata=MetadataQuery(score=True, explain_score=True),
            return_properties=[
                "name", "type", "county", "region", "description",
                "climate", "best_time", "activities",
                "entry_fee_citizen", "entry_fee_resident", "entry_fee_non_resident",
                "daily_cost_budget", "daily_cost_mid", "daily_cost_luxury",
                "transport_options", "nearby_locations", "tags"
            ]
        )

        results = []
        for obj in response.objects:
            result = {
                "name": obj.properties.get("name", ""),
                "type": obj.properties.get("type", ""),
                "county": obj.properties.get("county", ""),
                "region": obj.properties.get("region", ""),
                "description": obj.properties.get("description", ""),
                "climate": obj.properties.get("climate", ""),
                "best_time": obj.properties.get("best_time", ""),
                "activities": obj.properties.get("activities", []),
                "entry_fee": {
                    "citizen": obj.properties.get("entry_fee_citizen", ""),
                    "resident": obj.properties.get("entry_fee_resident", ""),
                    "non_resident": obj.properties.get("entry_fee_non_resident", ""),
                },
                "estimated_daily_cost": {
                    "budget": obj.properties.get("daily_cost_budget", ""),
                    "mid": obj.properties.get("daily_cost_mid", ""),
                    "luxury": obj.properties.get("daily_cost_luxury", ""),
                },
                "transport_options": obj.properties.get("transport_options", []),
                "nearby_locations": obj.properties.get("nearby_locations", []),
                "tags": obj.properties.get("tags", []),
                "score": obj.metadata.score if obj.metadata else None
            }
            results.append(result)

        return results

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results into a readable context string for the LLM."""
        contexts = []
        for i, r in enumerate(results, 1):
            # Format score separately
            score_str = f"{r['score']:.3f}" if r['score'] is not None else 'N/A'
            ctx = f"""
    --- Location {i} (relevance score: {score_str}) ---
    Name: {r['name']}
    Type: {r['type']}
    County: {r['county']}
    Region: {r['region']}
    Description: {r['description']}
    Climate: {r['climate']}
    Best time: {r['best_time']}
    Activities: {', '.join(r['activities']) if r['activities'] else 'Not specified'}
    Entry fees: Citizens {r['entry_fee']['citizen']}, Residents {r['entry_fee']['resident']}, Non-residents {r['entry_fee']['non_resident']}
    Daily costs (budget/mid/luxury): {r['estimated_daily_cost']['budget']} / {r['estimated_daily_cost']['mid']} / {r['estimated_daily_cost']['luxury']}
    Transport options: {', '.join(r['transport_options']) if r['transport_options'] else 'Not specified'}
    Nearby: {', '.join(r['nearby_locations']) if r['nearby_locations'] else 'None'}
    Tags: {', '.join(r['tags']) if r['tags'] else 'None'}
    """
            contexts.append(ctx)

        return "\n".join(contexts)

    def close(self):
        """Close the Weaviate connection."""
        self.client.close()