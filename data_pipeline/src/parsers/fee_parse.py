"""
parse_kws_pdf.py – Extract park entry fees from the KWS tariff PDF using tabula-py.
Saves a JSON mapping of park names to fees.
"""
import json
import re
import os
import csv
from typing import Dict

try:
    import tabula
except Exception:
    tabula = None

try:
    import pandas as pd
except Exception:
    pd = None

# Path to your PDF – adjust if needed
PDF_PATH = "../../data/raw/kws_fees.pdf"  # make sure this file exists

# Approximate USD to KES conversion (update to current rate)
USD_TO_KES = 130  # as of early 2025

# Mapping from KWS category names to list of actual park names (lowercase)
CATEGORY_TO_PARKS = {
    "scenic parks": [
        "hell's gate national park",
        "mount longonot national park",
        "mount longonot national park",  # duplicate? keep for clarity
    ],
    "special interest": [
        "mwea national reserve",
        "ruma national park",
        "sibiloi national park",
        "ndere island national park",
        "kiunga marine national reserve",
        # add others as needed
    ],
    "marine protected areas": [
        "watamu marine national park",
        "kisite mpunguti marine national park",
        "malindi marine national park",
        "mombasa marine national park",
    ],
    "nairobi package": [
        "nairobi national park"  # but note this is a package including orphanage
    ],
    # Add more based on your knowledge
}

def clean_fee_value(val) -> str:
    """Convert a cell value to a clean KES string."""
    if pd.isna(val) or val == '':
        return ""
    # Remove any non‑numeric characters except decimal point
    val_str = str(val).replace(',', '').strip()
    # Extract number
    match = re.search(r'(\d+(?:\.\d+)?)', val_str)
    if not match:
        return ""
    num = float(match.group(1))
    # Assume it's KES unless USD is explicitly mentioned (but we'll handle via column)
    return f"KES {int(num)}"

def extract_park_fees() -> Dict[str, Dict[str, str]]:
    """
    Returns dict: {normalized_park_name: {"citizen": str, "resident": str, "non_resident": str}}
    """
    # Prefer PDF parsing via tabula if available; otherwise fall back to CSV file
    tables = []
    if tabula is not None and os.path.exists(PDF_PATH):
        try:
            tables = tabula.read_pdf(PDF_PATH, pages='all', multiple_tables=True, pandas_options={'header': None})
        except Exception as e:
            print(f"Warning: tabula failed to read PDF ({e}), will try CSV fallback")

    # CSV fallback path
    csv_path = os.path.join(os.path.dirname(PDF_PATH), 'kws_fee.csv')
    if not tables:
        if os.path.exists(csv_path):
            print(f"Using CSV fallback: {csv_path}")
            # If pandas is available, create a DataFrame for compatibility
            if pd is not None:
                df = pd.read_csv(csv_path)
                tables = [df]
            else:
                # create a simple list-of-dicts table to iterate below
                with open(csv_path, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                # wrap rows in a minimal object with .columns and iterrows()
                class SimpleTable(list):
                    def __init__(self, rows):
                        super().__init__(rows)
                        self.columns = list(rows[0].keys()) if rows else []
                    def iterrows(self):
                        for i, row in enumerate(self):
                            yield i, row
                tables = [SimpleTable(rows)]
        else:
            raise FileNotFoundError(f"No PDF or CSV fee source found at {PDF_PATH} or {csv_path}")

    park_fees = {}

    for df in tables:
        # Convert to string to avoid dtype issues where possible
        if pd is not None and hasattr(df, 'astype'):
            try:
                df = df.astype(str)
            except Exception:
                pass
        # Look for a table that contains "PARK CATEGORY" in the first few cells
        found = False
        for col in df.columns:
            if df[col].str.contains('PARK CATEGORY', case=False, na=False).any():
                found = True
                break
        if not found:
            continue

        # Now we have the park fees table. Its exact structure may vary.
        # We'll assume:
        # - First column: Park category (e.g., "Amboseli & Lake Nakuru")
        # - Next columns: East African Citizen (Adult, Child), Kenya Resident (Adult, Child),
        #   Non‑Resident (Adult, Child in USD), African Citizen (Adult, Child in USD)
        # We'll take the Adult fees for simplicity.

        # Try to find the header row (where column names appear)
        header_row_idx = None
        # Find header row robustly; handle both pandas DataFrame rows and simple dict rows
        for i, row in (df.iterrows() if hasattr(df, 'iterrows') else enumerate(df)):
            # Build a safe string representation of the row for matching
            if isinstance(row, dict):
                row_vals = [str(v) for v in row.values()]
            else:
                # pandas Series or list-like
                row_vals = [str(v) for v in (row.values if hasattr(row, 'values') else row)]
            row_str = ' '.join(row_vals).lower()
            if 'east african citizen' in row_str and 'kenya resident' in row_str:
                header_row_idx = i
                break

        if header_row_idx is None:
            # If we can't find a header, assume first row is header
            header_row_idx = 0

        # Set the header
        df.columns = df.iloc[header_row_idx]
        df = df.iloc[header_row_idx+1:].reset_index(drop=True)

        # Now iterate over rows
        for idx, row in df.iterrows():
            park_category = str(row.iloc[0]).strip()
            if pd.isna(park_category) or park_category == '':
                continue

            # Try to locate columns by partial matching
            citizen_adult_col = None
            resident_adult_col = None
            non_resident_adult_col = None

            for col in df.columns:
                col_lower = str(col).lower()
                if 'east african citizen' in col_lower and ('adult' in col_lower or 'child' not in col_lower):
                    citizen_adult_col = col
                elif 'kenya resident' in col_lower and ('adult' in col_lower or 'child' not in col_lower):
                    resident_adult_col = col
                elif 'non-resident' in col_lower and ('adult' in col_lower or 'child' not in col_lower):
                    non_resident_adult_col = col

            # Fallback: if we didn't find exact, use the second, fourth, sixth columns
            if not citizen_adult_col and len(df.columns) >= 2:
                citizen_adult_col = df.columns[1]
            if not resident_adult_col and len(df.columns) >= 4:
                resident_adult_col = df.columns[3]
            if not non_resident_adult_col and len(df.columns) >= 6:
                non_resident_adult_col = df.columns[5]

            # Extract values
            citizen_val = row[citizen_adult_col] if citizen_adult_col else ""
            resident_val = row[resident_adult_col] if resident_adult_col else ""
            non_resident_val = row[non_resident_adult_col] if non_resident_adult_col else ""

            # Clean and convert non_resident from USD to KES
            citizen_kes = clean_fee_value(citizen_val)
            resident_kes = clean_fee_value(resident_val)

            non_resident_kes = ""
            if non_resident_val:
                # Try to extract USD number
                usd_match = re.search(r'(\d+(?:\.\d+)?)', str(non_resident_val))
                if usd_match:
                    usd = float(usd_match.group(1))
                    non_resident_kes = f"KES {int(usd * USD_TO_KES)}"
                else:
                    non_resident_kes = clean_fee_value(non_resident_val)  # fallback

            fee_entry = {
                "citizen": citizen_kes,
                "resident": resident_kes,
                "non_resident": non_resident_kes
            }

            # Map park category to actual park names
            park_category_lower = park_category.lower()
            if 'amboseli' in park_category_lower and 'nakuru' in park_category_lower:
                park_fees['amboseli national park'] = fee_entry
                park_fees['lake nakuru national park'] = fee_entry
            elif 'nairobi national park' in park_category_lower:
                park_fees['nairobi national park'] = fee_entry
            elif 'tsavo east' in park_category_lower:
                park_fees['tsavo east national park'] = fee_entry
            elif 'tsavo west' in park_category_lower:
                park_fees['tsavo west national park'] = fee_entry
            elif 'meru' in park_category_lower:
                park_fees['meru national park'] = fee_entry
            elif 'kora' in park_category_lower:
                park_fees['kora national park'] = fee_entry
            elif 'aberdare' in park_category_lower:
                park_fees['aberdare national park'] = fee_entry
            elif 'mt. kenya' in park_category_lower:
                park_fees['mount kenya national park'] = fee_entry
            elif 'scenic parks' in park_category_lower:
                for p in CATEGORY_TO_PARKS.get('scenic parks', []):
                    park_fees[p] = fee_entry
            elif 'special interest' in park_category_lower:
                for p in CATEGORY_TO_PARKS.get('special interest', []):
                    park_fees[p] = fee_entry
            elif 'marine protected areas' in park_category_lower:
                for p in CATEGORY_TO_PARKS.get('marine protected areas', []):
                    park_fees[p] = fee_entry
            elif 'nairobi package' in park_category_lower:
                # This is a package; maybe store separately or note
                park_fees['nairobi national park package'] = fee_entry
            else:
                # Fallback: treat as a direct park name
                # Remove extra words like "Park" to match
                simple_name = re.sub(r'\s*\(.*\)', '', park_category_lower).strip()
                if not simple_name.endswith('national park'):
                    simple_name += ' national park'
                park_fees[simple_name] = fee_entry

    return park_fees

def save_fees_to_json(fees: Dict, output_path: str = "../../data/processed/kws_fees.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(fees, f, indent=2)

if __name__ == "__main__":
    fees = extract_park_fees()
    save_fees_to_json(fees)
    print(f"Extracted fees for {len(fees)} parks.")