import pandas as pd
from fuzzywuzzy import fuzz  # Install this package if fuzzy matching needed

# Load files
amazon_df = pd.read_excel('Amazon_map.xlsx')    # update file paths
hsn_df = pd.read_excel('Hsn_08-map.xlsx')

# Normalize text columns for matching
def normalize(val):
    return str(val).strip().lower() if pd.notnull(val) else ''

hsn_df['Description_clean'] = hsn_df['Description'].apply(normalize)

def find_best_hsn(row, hsn_df):
    for col in ['Subcategory 4', 'Subcategory 3', 'Subcategory 2']:
        search_val = normalize(row.get(col, ''))
        if search_val:
            for _, hsn_row in hsn_df.iterrows():
                if search_val in hsn_row['Description_clean']:
                    return hsn_row['HSN8'], hsn_row['Description']
    return None, None

# Apply matching and store results
amazon_df[['HSN8_code', 'HSN_Description']] = amazon_df.apply(
    lambda row: pd.Series(find_best_hsn(row, hsn_df)),
    axis=1
)

# Save results
amazon_df.to_excel('amazon_hsn_mapped.xlsx', index=False)
