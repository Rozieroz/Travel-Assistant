"""
cleaner.py – Data cleaning and normalization module.

Purpose:
- Remove duplicate locations based on name.
- Convert currency amounts to KES (if given in USD).
- Standardise string formats.
- Generate tags from activities, description, and type.
- Merge data from multiple sources.
"""
import re
from typing import List, Dict, Any

def convert_to_kes(amount_str: str) -> str:
    """
    Convert a string like "USD 60" to "KES 6000" (approx rate 100).
    If already in KES, leave unchanged.
    If no currency or unknown, return as is.
    """
    if not amount_str:
        return amount_str
    # Match patterns like "USD 60", "USD60", "$60", "60 USD", etc.
    # Simplified: look for 3-letter currency code followed by number, or number followed by code.
    match = re.search(r'(?i)(?:USD|KSH|KES?)\s*(\d+(?:,\d+)?(?:\.\d+)?)', amount_str)
    if match:
        value_str = match.group(1).replace(',', '')
        try:
            value = float(value_str)
        except ValueError:
            return amount_str
        # Assume it's USD – convert
        value_kes = int(value * 100)  # approximate
        return f"KES {value_kes}"
    # Check if it might be just a number (assume KES)
    match = re.search(r'(\d+(?:,\d+)?(?:\.\d+)?)', amount_str)
    if match and 'USD' not in amount_str and '$' not in amount_str:
        return f"KES {match.group(1)}"
    return amount_str

def normalize_fees(location: Dict[str, Any]) -> Dict[str, Any]:
    """Apply KES conversion to all fee and cost fields."""
    # Entry fees
    if 'entry_fee' in location and isinstance(location['entry_fee'], dict):
        for k in ['citizen', 'resident', 'non_resident']:
            if k in location['entry_fee']:
                location['entry_fee'][k] = convert_to_kes(location['entry_fee'][k])
    # Daily costs
    if 'estimated_daily_cost' in location and isinstance(location['estimated_daily_cost'], dict):
        for k in ['budget', 'mid', 'luxury']:
            if k in location['estimated_daily_cost']:
                location['estimated_daily_cost'][k] = convert_to_kes(location['estimated_daily_cost'][k])
    # Transport costs (if present)
    if 'transport_options' in location and isinstance(location['transport_options'], list):
        for opt in location['transport_options']:
            if 'estimated_cost' in opt:
                opt['estimated_cost'] = convert_to_kes(opt['estimated_cost'])
    # Activity costs
    if 'activities' in location and isinstance(location['activities'], list):
        for act in location['activities']:
            if 'estimated_cost' in act:
                act['estimated_cost'] = convert_to_kes(act['estimated_cost'])
    return location

def generate_tags(location: Dict[str, Any]) -> List[str]:
    """
    Create a list of tags from type, activities, and description.
    Tags are lowercased and duplicates removed.
    """
    tags = set()
    # Add type
    if location.get('type'):
        tags.add(location['type'].lower())
    # Add region
    if location.get('region'):
        tags.add(location['region'].lower())
    # Add from activities
    activities = location.get('activities', [])
    for act in activities:
        if isinstance(act, dict):
            # Activity type field
            if act.get('type'):
                tags.add(act['type'].lower())
            # Activity name might contain keywords
            name = act.get('name', '').lower()
            for keyword in ['safari', 'hike', 'beach', 'culture', 'museum', 'game', 'bird']:
                if keyword in name:
                    tags.add(keyword)
        elif isinstance(act, str):
            # If activities are strings, split by common delimiters? Simpler: add whole as tag? Not ideal.
            # We'll just add keywords from the string.
            for keyword in ['safari', 'hike', 'beach', 'culture', 'museum', 'game', 'bird']:
                if keyword in act.lower():
                    tags.add(keyword)
    # Add from description
    desc = location.get('description', '').lower()
    for keyword in ['family', 'kids', 'adventure', 'relax', 'wildlife', 'nature', 'city']:
        if keyword in desc:
            tags.add(keyword)
    return list(tags)

def deduplicate(locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicates based on name (case‑insensitive).
    The first occurrence with a non‑empty name is kept.
    """
    seen = {}
    unique = []
    for loc in locations:
        name = loc.get('name', '').strip().lower()
        if not name:
            continue
        if name not in seen:
            seen[name] = True
            unique.append(loc)
    return unique

def merge_sources(lists_of_locations: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merge multiple lists of location dicts, updating existing entries with new data.
    Locations are matched by lowercase name.
    """
    merged = {}
    for lst in lists_of_locations:
        for loc in lst:
            name = loc.get('name', '').strip().lower()
            if not name:
                continue
            if name not in merged:
                merged[name] = loc.copy()
            else:
                # Update existing with non‑empty values from new
                existing = merged[name]
                for key, value in loc.items():
                    if value and (key not in existing or not existing[key]):
                        existing[key] = value
    return list(merged.values())