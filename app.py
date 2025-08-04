import streamlit as st
import pandas as pd
from io import BytesIO

st.title("🧾 Sub-Category to HSN Code Mapper")

# Upload files
amazon_file = st.file_uploader("📤 Upload Amazon Category Excel", type="xlsx")
hsn_file = st.file_uploader("📥 Upload HSN Full List Excel", type="xlsx")

if amazon_file and hsn_file:
    amazon_df = pd.read_excel(amazon_file)
    hsn_df = pd.read_excel(hsn_file)

    st.subheader("📋 Amazon Categories")
    st.dataframe(amazon_df.head())

    st.subheader("📋 HSN Data")
    st.dataframe(hsn_df.head())

    # Convert all to lowercase for case-insensitive matching
    for col in ['Subcategory 1', 'Subcategory 2', 'Subcategory 3', 'Subcategory 4']:
        amazon_df[col] = amazon_df[col].astype(str).str.lower()

    # Assuming the HSN description is in a column named 'Description'
    hsn_df['Description'] = hsn_df['Description'].astype(str).str.lower()

    # Function to find matching HSN6
    def find_hsn(row):
        for val in [row['Subcategory 1'], row['Subcategory 2'], row['Subcategory 3'], row['Subcategory 4']]:
            matches = hsn_df[hsn_df['Description'].str.contains(val, na=False)]
            if not matches.empty:
                return matches.iloc[0]['HSN6']  # take first match
        return "No Match"

    st.info("⏳ Matching categories with HSN descriptions...")
    amazon_df['Matched HSN6'] = amazon_df.apply(find_hsn, axis=1)
    st.success("✅ Done!")

    st.subheader("✅ Final Mapped Output")
    final_df = amazon_df[['Subcategory 1', 'Subcategory 2', 'Subcategory 3', 'Subcategory 4', 'Matched HSN6']]
    st.dataframe(final_df)

    # Download Button
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    st.download_button(
        label="📥 Download Final Mapped Excel",
        data=to_excel(final_df),
        file_name="final_hsn_mapped.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )




# import streamlit as st
# import pandas as pd
# from io import BytesIO
# from rapidfuzz import process, fuzz

# st.set_page_config(page_title="Amazon to HSN Mapper", layout="wide")

# st.title("🧠 Amazon Category to HSN Code Mapper")
# st.markdown("Upload Amazon category data and ITC HSN data to get a matched file with HSN6 codes.")

# # Upload Files
# amazon_file = st.file_uploader("📤 Upload Amazon Categories Excel", type=["xlsx"])
# hsn_file = st.file_uploader("📥 Upload ITC HSN Data Excel", type=["xlsx"])

# if amazon_file and hsn_file:
#     # Load Data
#     amazon_df = pd.read_excel(amazon_file)
#     hsn_df = pd.read_excel(hsn_file)

#     st.subheader("🔍 Preview: Amazon Categories")
#     st.dataframe(amazon_df.head())

#     st.subheader("🔍 Preview: ITC HSN Data")
#     st.dataframe(hsn_df.head())

#     # Step 1: Create 'full_category_path'
#     cat_cols = [col for col in amazon_df.columns if "cat" in col.lower()]
#     amazon_df["full_category_path"] = amazon_df[cat_cols].fillna('').agg(' > '.join, axis=1).str.strip(" >")

#     # Step 2: Create 'hsn_description_full'
#     hsn_cols = [col for col in hsn_df.columns if hsn_df[col].dtype == "object"]
#     hsn_df['hsn_description_full'] = hsn_df[hsn_cols].fillna('').agg(' > '.join, axis=1).str.strip(" >")

#     # Step 3: Fuzzy Matching
#     def match_category(row):
#         match, score, idx = process.extractOne(
#             row['full_category_path'], 
#             hsn_df['hsn_description_full'], 
#             scorer=fuzz.token_set_ratio
#         )
#         return pd.Series([match, score, hsn_df.iloc[idx]['HSN6'] if score >= 75 else "No Match"])

#     st.info("⏳ Matching categories... this may take a moment.")
#     amazon_df[['matched_hsn_desc', 'match_score', 'HSN6']] = amazon_df.apply(match_category, axis=1)

#     st.success("✅ Matching Complete!")

#     # Filter for matches above threshold
#     filtered_df = amazon_df[amazon_df['match_score'] >= 75]

#     st.subheader("📋 Mapped Data (≥ 75% Match)")
#     st.dataframe(filtered_df)

#     # Download Button
#     def to_excel(df):
#         output = BytesIO()
#         with pd.ExcelWriter(output, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False)
#         return output.getvalue()

#     st.download_button(
#         label="📥 Download Matched File as Excel",
#         data=to_excel(filtered_df),
#         file_name="amazon_to_hsn_mapping.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )
