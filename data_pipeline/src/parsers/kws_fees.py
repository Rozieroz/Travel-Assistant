"""
kws_fees_parser.py – Parse KWS fee table from CSV.

The CSV has columns:
Category, Item/Sub-Category, EA Citizen Adult (Ksh), EA Citizen Child/Student (Ksh),
Kenya Resident Adult (Ksh), Kenya Resident Child/Student (Ksh),
Non-Resident Adult (USD), Non-Resident Child/Student (USD),
African Citizen Adult (USD), African Citizen Child/Student (USD)

We extract entry fees for parks (rows where Category is "PARK ENTRY").
"""
import csv
import re
from typing import Dict, Optional

# Approximate exchange rate USD to KES
USD_TO_KES = 100

# Mapping from KWS category names to list of park names (lowercase)
# This helps assign fees to specific locations when the row is a category.
CATEGORY_TO_PARKS = {
    "scenic parks": [
        "hell's gate national park",
        "mount longonot national park",
        # add others as needed
    ],
    "special interest": [
        "mwea national reserve",
        "ruma national park",
        "sibiloi national park",
        # etc.
    ],
    "marine protected areas": [
        "watamu marine national park",
        "kisite mpunguti marine national park",
        # etc.
    ],
    "nairobi package": [
        "nairobi national park"  # but this is a package including orphanage, so maybe we treat separately
    ],
    # Add more as needed
}

def normalize_name(name: str) -> str:
    """Lowercase and strip, remove extra spaces."""
    return re.sub(r'\s+', ' ', name.strip().lower())

def parse_kws_fees_csv(filepath: str) -> Dict[str, Dict[str, str]]:
    """
    Returns a dict mapping normalized park name to entry fee dict.
    Fee dict has keys: citizen, resident, non_resident (all in KES strings).
    """
    fees = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = row.get('Category', '').strip()
            if category != 'PARK ENTRY':
                continue
            item = row.get('Item/Sub-Category', '').strip()
            if not item:
                continue

            # Extract fees, convert to KES where needed
            citizen_adult = row.get('EA Citizen Adult (Ksh)', '').strip()
            resident_adult = row.get('Kenya Resident Adult (Ksh)', '').strip()
            non_resident_adult_usd = row.get('Non-Resident Adult (USD)', '').strip()

            # Convert to strings with KES
            citizen_str = f"KES {citizen_adult}" if citizen_adult else ""
            resident_str = f"KES {resident_adult}" if resident_adult else ""
            non_resident_kes = ""
            if non_resident_adult_usd:
                try:
                    usd_val = float(non_resident_adult_usd.replace(',', ''))
                    kes_val = int(usd_val * USD_TO_KES)
                    non_resident_kes = f"KES {kes_val}"
                except ValueError:
                    non_resident_kes = f"USD {non_resident_adult_usd} (approx KES {int(float(non_resident_adult_usd)*USD_TO_KES)})"

            fee_entry = {
                "citizen": citizen_str,
                "resident": resident_str,
                "non_resident": non_resident_kes
            }

            # Check if item is a specific park or a category
            item_lower = normalize_name(item)
            # Remove parenthetical like "(Hells Gate/Longonot/etc)"
            base_item = re.sub(r'\s*\(.*\)', '', item_lower).strip()

            # Specific parks we know: try to map directly
            # We'll also handle known categories via the mapping
            if base_item in ['amboseli', 'lake nakuru', 'amboseli & lake nakuru']:
                # Amboseli & Lake Nakuru are two separate parks but share same fee
                fees['amboseli national park'] = fee_entry
                fees['lake nakuru national park'] = fee_entry
            elif base_item == 'nairobi national park':
                fees['nairobi national park'] = fee_entry
            elif base_item == 'tsavo east':
                fees['tsavo east national park'] = fee_entry
            elif base_item == 'tsavo west':
                fees['tsavo west national park'] = fee_entry
            elif base_item == 'meru':
                fees['meru national park'] = fee_entry
            elif base_item == 'kora':
                fees['kora national park'] = fee_entry
            elif base_item == 'aberdare':
                fees['aberdare national park'] = fee_entry
            elif base_item == 'mt. kenya':
                fees['mount kenya national park'] = fee_entry
            elif base_item == 'scenic parks':
                for park in CATEGORY_TO_PARKS.get('scenic parks', []):
                    fees[park] = fee_entry
            elif base_item == 'special interest':
                for park in CATEGORY_TO_PARKS.get('special interest', []):
                    fees[park] = fee_entry
            elif base_item == 'marine protected areas':
                for park in CATEGORY_TO_PARKS.get('marine protected areas', []):
                    fees[park] = fee_entry
            elif base_item == 'nairobi package':
                # This is a package for Nairobi National Park + orphanage + walk.
                # We might store it as a note or separate, but for now assign to Nairobi National Park with a note.
                # We'll add a separate key for the package maybe.
                fees['nairobi national park package'] = fee_entry
            else:
                # Generic fallback: try to use the item as a park name
                # Remove "Park" etc.
                park_name = base_item
                if not park_name.endswith('park'):
                    park_name += ' national park'
                fees[park_name] = fee_entry

    return fees