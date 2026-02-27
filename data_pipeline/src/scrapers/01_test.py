import pdfplumber
import pandas as pd

def extract_kws_fees_with_plumber(pdf_path):
    all_data = []
    with pdfplumber.open(pdf_path) as pdf:
        # Fee tables usually start after page 2
        for page in pdf.pages[2:]: 
            tables = page.extract_tables()
            for table in tables:
                # KWS tables are wide; we convert to DataFrame for easier cleaning
                df = pd.DataFrame(table)
                # Filter for rows that actually look like park data
                # (e.g., row has a name and at least 3 numbers)
                all_data.append(df)
    
    final_df = pd.concat(all_data)
    return final_df

# Example call (using local file is safer for heavy parsing)
# df = extract_kws_fees_with_plumber("kws_fees_2026.pdf")