"""
Generic parser for Google Maps CSV exports.
Assumes columns with class names like: hfpxzc href, qBF1Pd, MW4etd, UY7F9, W4Efsd, ...
"""
import csv
from typing import List, Dict

def parse_google_maps_csv(filepath: str) -> List[Dict]:
    """
    Reads any Google Maps CSV and returns a list of raw location dicts.
    """
    locations = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip empty rows
            if not row.get('qBF1Pd', '').strip():
                continue

            loc = {
                "name": row.get('qBF1Pd', '').strip(),
                "rating": row.get('MW4etd', ''),
                "reviews": row.get('UY7F9', ''),
                "place_type": row.get('W4Efsd', ''),          # e.g., "Amusement park"
                "address": row.get('W4Efsd 3', ''),           # approximate
                "hours_status": row.get('W4Efsd 4', ''),      # "Closed" or "Open"
                "hours": row.get('W4Efsd 5', ''),             # "· Opens 9 AM Thu"
                "image_url": row.get('FQ2IWe src', ''),
                "description": _extract_review_snippet(row),
                "url": row.get('hfpxzc href', ''),
                "phone": row.get('UsdlK', ''),                # if present
                "website": row.get('lcr4fd href', ''),        # if present
            }
            locations.append(loc)
    return locations

def _extract_review_snippet(row: Dict) -> str:
    """Combine review snippet columns (ah5Ghc, ah5Ghc 2, ...) into one string."""
    parts = []
    for i in range(1, 10):  # up to ah5Ghc 9
        col = f'ah5Ghc {i}' if i > 1 else 'ah5Ghc'
        if col in row and row[col]:
            text = row[col].strip('"').strip()
            if text:
                parts.append(text)
    return ' '.join(parts)