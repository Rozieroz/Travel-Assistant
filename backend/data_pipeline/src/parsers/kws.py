import csv
from typing import List, Dict

def parse_kws_csv(filepath: str) -> List[Dict]:
    locations = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('title', '').strip()
            if not name:
                continue
            loc = {
                "name": name,
                "type": "park",
                "url": row.get('title href', ''),
                "image_url": row.get('item-image src', ''),
            }
            locations.append(loc)
    return locations