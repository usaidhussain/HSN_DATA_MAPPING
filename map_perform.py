import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="HSN6 Dual Mapper", layout="wide")

# SESSION STATE FOR "RESTART"
if "clear_data" not in st.session_state:
    st.session_state.clear_data = False

def reset_state():
    st.session_state.clear_data = True

st.title("HSN6 Amazon Category Mapper — Exact & Partial Modes")

st.write("""
Upload Amazon and HSN Excel files.<br>
- <b>Exact Match Table:</b> Only exact match between a subcategory and HSN description.<br>
- <b>Partial Match Table:</b> Any subcategory is a substring of an HSN description.<br>
[Restart Button] will clear all and let you start over.
""", unsafe_allow_html=True)

col1, col2 = st.columns([7, 1])
with col2:
    if st.button("Restart App", use_container_width=True):
        reset_state()

if st.session_state.clear_data:
    st.experimental_rerun()

def normalize(text):
    return str(text).strip().lower() if pd.notnull(text) else ''

amazon_file = st.file_uploader("Upload Amazon Data (.xlsx)", type=['xlsx'], key='amazon_data')
hsn_file = st.file_uploader("Upload HSN Data (.xlsx)", type=['xlsx'], key='hsn_data')

if amazon_file and hsn_file:
    with st.spinner("Loading..."):
        amazon_df = pd.read_excel(amazon_file)
        hsn_df = pd.read_excel(hsn_file)

    # Validate columns
    required_amazon = ['Subcategory 2', 'Subcategory 3', 'Subcategory 4']
    required_hsn = ['HSN6', 'Description']
    for col in required_amazon:
        if col not in amazon_df.columns:
            st.error(f"Column missing: {col}")
            st.stop()
    for col in required_hsn:
        if col not in hsn_df.columns:
            st.error(f"Column missing: {col}")
            st.stop()

    # STEP 1: Build maps and lists for both modes
    # ------ Prepare HSN6 with leading zeros ------
    hsn_df = hsn_df[~hsn_df['HSN6'].isna()]  # Only rows with HSN6
    hsn_df['HSN6_code'] = hsn_df['HSN6'].astype(int).astype(str).str.zfill(6)
    hsn_df['Description_norm'] = hsn_df['Description'].map(normalize)
    hsn_map = dict(zip(hsn_df['Description_norm'], zip(hsn_df['HSN6_code'], hsn_df['Description'])))

    # ------ Exact Match: subcategory == HSN Description ------
    exact_matches = []
    N = len(amazon_df)
    progress = st.progress(0, text="Processing Exact Matches...")

    for idx, row in amazon_df.iterrows():
        found = False
        for subcat_col in ['Subcategory 4', 'Subcategory 3', 'Subcategory 2']:
            subcat_norm = normalize(row.get(subcat_col, ''))
            if subcat_norm in hsn_map:
                hsn6_code, hsn_desc = hsn_map[subcat_norm]
                updated_row = dict(row)
                updated_row['HSN6_code'] = hsn6_code
                updated_row['HSN_Description'] = hsn_desc
                updated_row['Matched On'] = subcat_col
                exact_matches.append(updated_row)
                found = True
                break  # Only need first in priority order
        # No match: do nothing
        if (idx + 1) % 25 == 0 or idx + 1 == N:
            frac = (idx + 1) / N
            progress.progress(frac, f"Processing Exact Matches... {int(frac * 100)}%")

    # STEP 2: Partial (Substring) Match Table — old way
    progress = st.progress(0, text="Processing Partial Matches...")
    partial_matches = []
    for idx, row in amazon_df.iterrows():
        matched = False
        for subcat_col in ['Subcategory 4', 'Subcategory 3', 'Subcategory 2']:
            subcat_norm = normalize(row.get(subcat_col, ''))
            if not subcat_norm or subcat_norm == 'nan':
                continue
            for _, hsn_row in hsn_df.iterrows():
                desc_norm = hsn_row['Description_norm']
                if subcat_norm in desc_norm:
                    updated_row = dict(row)
                    updated_row['HSN6_code'] = hsn_row['HSN6_code']
                    updated_row['HSN_Description'] = hsn_row['Description']
                    updated_row['Matched On'] = f"{subcat_col} (partial)"
                    partial_matches.append(updated_row)
                    matched = True
                    break  # first partial match per-priority column
            if matched:
                break
        if (idx + 1) % 25 == 0 or idx + 1 == N:
            frac = (idx + 1) / N
            progress.progress(frac, f"Processing Partial Matches... {int(frac * 100)}%")

    # STEP 3: OUTPUT AND DOWNLOAD
    st.header("1️⃣ Exact Matches Table")
    if exact_matches:
        exact_df = pd.DataFrame(exact_matches)
        st.success(f"{len(exact_df)} matched ({round(100 * len(exact_df)/N, 2)}%) — exact match between any subcategory and HSN description.")
        st.dataframe(exact_df, use_container_width=True, height=330)
        buf1 = io.BytesIO()
        exact_df.to_excel(buf1, index=False, engine='openpyxl')
        buf1.seek(0)
        st.download_button(
            label="Download Exact Matches (Excel)",
            data=buf1,
            file_name="amazon_hsn6_exact_matches.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No exact matches found.")

    st.header("2️⃣ Partial/Substring Matches Table (Old Style)")
    if partial_matches:
        partial_df = pd.DataFrame(partial_matches)
        st.info(f"{len(partial_df)} had a partial/substring match ({round(100 * len(partial_df)/N, 2)}%).")
        st.dataframe(partial_df, use_container_width=True, height=330)
        buf2 = io.BytesIO()
        partial_df.to_excel(buf2, index=False, engine='openpyxl')
        buf2.seek(0)
        st.download_button(
            label="Download Partial/Substring Matches (Excel)",
            data=buf2,
            file_name="amazon_hsn6_partial_matches.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No partial/substring matches found.")



# import streamlit as st
# import pandas as pd
# import io

# st.set_page_config(page_title="HSN6 Exact Mapper", layout="wide")

# def normalize(text):
#     return str(text).strip().lower() if pd.notnull(text) else ''

# st.title("HSN6 Category Mapper — Only Exact, Full Matches")

# st.write("Upload Amazon and HSN Excel files. Only exact equality between Subcategory X and HSN Description will produce a match. No partials, no substrings, no '000nan's.")

# amazon_file = st.file_uploader("Upload Amazon Data (.xlsx)", type=['xlsx'])
# hsn_file = st.file_uploader("Upload HSN Data (.xlsx)", type=['xlsx'])

# if amazon_file and hsn_file:
#     with st.spinner("Loading..."):
#         amazon_df = pd.read_excel(amazon_file)
#         hsn_df = pd.read_excel(hsn_file)

#     # Validate columns
#     required_amazon = ['Subcategory 2', 'Subcategory 3', 'Subcategory 4']
#     required_hsn = ['HSN6', 'Description']
#     for col in required_amazon:
#         if col not in amazon_df.columns:
#             st.error(f"Column missing: {col}")
#             st.stop()
#     for col in required_hsn:
#         if col not in hsn_df.columns:
#             st.error(f"Column missing: {col}")
#             st.stop()

#     # Build a {normalized description: (HSN6, raw_description)} map for lookups.
#     hsn_map = {}
#     for _, row in hsn_df.iterrows():
#         desc_norm = normalize(row['Description'])
#         # Ensure HSN6 is a 6-digit string, keeping leading zeros
#         hsn6_raw = row['HSN6']
#         if pd.isnull(hsn6_raw):
#             continue
#         hsn6_str = str(int(hsn6_raw)).zfill(6)
#         hsn_map[desc_norm] = (hsn6_str, row['Description'])

#     matched_rows = []
#     N = len(amazon_df)
#     progress = st.progress(0, text="Processing...")

#     for idx, row in amazon_df.iterrows():
#         found = False
#         for subcat_col in ['Subcategory 4', 'Subcategory 3', 'Subcategory 2']:
#             subcat_norm = normalize(row.get(subcat_col, ''))
#             if subcat_norm in hsn_map:
#                 hsn6_code, hsn_desc = hsn_map[subcat_norm]
#                 updated_row = dict(row)
#                 updated_row['HSN6_code'] = hsn6_code
#                 updated_row['HSN_Description'] = hsn_desc
#                 matched_rows.append(updated_row)
#                 found = True
#                 break  # Only need first in priority order
#         # If not found, don't add to matched_rows (so it won't be in output!)
#         if (idx+1)%25==0 or idx+1==N:
#             frac = (idx+1)/N
#             progress.progress(frac, f"Matching... {int(frac*100)}%")

#     if matched_rows:
#         result_df = pd.DataFrame(matched_rows)
#         st.success(f"Done! {len(result_df)} matched out of {N} rows.")
#         st.dataframe(result_df, use_container_width=True, height=450)

#         buf = io.BytesIO()
#         result_df.to_excel(buf, index=False, engine='openpyxl')
#         buf.seek(0)
#         st.download_button(
#             label="Download Matched Results (Only EXACT Matches)",
#             data=buf,
#             file_name="amazon_hsn6_exact_mapped.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )
#     else:
#         st.warning("No exact matches found.")


