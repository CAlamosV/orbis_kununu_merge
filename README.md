This repo processes data from Orbis and Kununu to facilitate a merge based on company names.
It was developed for Caldwell, Haegele, and Heining (2024). "Firm Pay and Worker Search." (*Working Paper*).

The data-cleaning process is as follows:

### Loading and Cleaning Data

1. **Loading and Preprocessing Orbis Data:**
   - **Rename Columns:** The Orbis dataset columns are renamed according to `orbis_column_map`.
   - **Clean Employee Data:** Employee numbers are converted to numeric format using `clean_employee_data`.
   - **Preprocess Company Names:** Company names are cleaned by removing special characters, excess whitespace, and converting to lowercase with `preprocess_company_name`.
   - **Filter by Company Size:** Companies with fewer than 30 employees are filtered out.
   - **Remove Duplicates:** Duplicate company names are dropped, retaining only the first instance.

2. **Loading and Preprocessing Kununu Data:**
   - **Sort by Reviews:** The Kununu dataset is sorted by `firm_name` and `total_reviews_num`, with companies having the most reviews prioritized.
   - **Remove Duplicates:** Duplicates are removed based on `firm_name`, keeping the record with the highest review count.
   - **Rename Columns:** Columns are renamed using `kununu_column_map`.
   - **Filter by Reviews:** Companies with fewer than 10 reviews are excluded.
   - **Preprocess Company Names:** Company names are cleaned similarly to the Orbis dataset.

3. **Sequence of Matching Steps:**
   - **Exact Match:** An initial attempt to find exact matches between Orbis and Kununu company names.
   - **Standardize Abbreviations:** Abbreviations in company names are standardized.
   - **Remove Umlauts:** Umlauts in German company names are converted to their English equivalents.
   - **Remove Suffixes:** Common suffixes like "GmbH" are removed.
   - **Remove Common Words:** Frequently appearing words are removed from company names.

### Matching Remaining Firms Using Fuzzy Merge

Calculating and filtering fuzzy similarity scores between company names in the Orbis and Kununu datasets, then preparing DataFrame with the best matches for further verification:

1. **Calculate Similarity Scores:**
   - **Compute Fuzzy Similarity:** Calculate similarity scores between Orbis and Kununu company names using the `fuzz.QRatio` scorer.
   - **Filter by Threshold:** Only matches with a similarity score of 90 or higher are retained.

2. **Create DataFrame for Best Matches:**
   - **Create DataFrame:** Include these columns: `Original Orbis Name`, `Original Kununu Name`, `Similarity Score`, `Orbis Name (after preprocessing)`, `Kununu Name (after preprocessing)`, `Orbis ID`, `Kununu ID`, `NACE Code`, `Employees`, and `City`.
   - **Sort Matches:** The DataFrame is sorted by similarity score (in descending order) and then by Kununu ID (in ascending order).

3. **Translate Kununu Names:**
   - **Translate to English:** The `Original Kununu Name` is translated to English using the `translate_text` function to assist in verifying matches.
