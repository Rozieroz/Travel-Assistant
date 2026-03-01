import csv
import re
from typing import List, Dict

def parse_magical_kenya_csv(filepath: str) -> List[Dict]:
    """
    Parses Magical Kenya CSV files. Handles two common formats:
    - One with background-image CSS (jet-listing-grid__item)
    - Another with plain region, name, link columns
    """
    locations = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Try to extract name from different possible columns
            name = (row.get('jet-listing-dynamic-link__link', '') or 
                    row.get('title', '') or 
                    row.get('', ''))  # fallback
            name = name.strip()
            if not name:
                continue

            # Try to get region
            region = None
            if '.jet-listing-grid__item' in row:
                # Extract region from background-image CSS? Not reliable.
                # leave region blank and fill manually later.
                pass
            elif 'Mombasa and South Coast' in row.values():
                # If the file has region as a separate column (like your last snippet)
                # The region might be the first column value
                first_key = list(row.keys())[0]
                region = row.get(first_key, '').strip()
                if region and ',' not in region and len(region) < 50:
                    # Likely a region name
                    pass
                else:
                    region = None

            # Categories/tags
            categories = []
            for col in row.keys():
                if 'elementor-post-info__terms-list-item' in col:
                    val = row[col].strip()
                    if val and val not in categories:
                        categories.append(val)

            loc = {
                "name": name,
                "type": _infer_type_from_categories(categories),
                "url": row.get('jet-listing-dynamic-link__link href', '') or row.get('title href', ''),
                "region": region,
                "categories": categories,
                "description": "",  # no description in these files
            }
            locations.append(loc)
    return locations

def _infer_type_from_categories(cats):
    if 'Adventure' in cats:
        return 'mountain'   # or  create a new type and refine later
    if 'Beach' in cats:
        return 'beach'
    return 'park'