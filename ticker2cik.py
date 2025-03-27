import json
import pandas as pd

# Paths to your files
ticker_file_path = r"C:\skibidi\FIAM\CIKs\spy500.txt"
mapping_file_path = r"C:\skibidi\FIAM\CIKs\mapping_table.txt"
output_file_path = r"C:\skibidi\FIAM\CIKs\mapped_408.csv"

# Step 1: Load the tickers from the txt file
with open(ticker_file_path, 'r') as file:
    tickers = [line.strip() for line in file.readlines()]

# Step 2: Load the mapping data from the JSON file
with open(mapping_file_path, 'r') as file:
    mapping_data = json.load(file)

# Step 3: Convert the mapping data to a pandas DataFrame
# Assuming the JSON format has "fields" and "data" keys
columns = mapping_data['fields']
data = mapping_data['data']

mapping_df = pd.DataFrame(data, columns=columns)

# Step 4: Filter the DataFrame to get rows where the ticker is in the tickers list
mapped_tickers = mapping_df[mapping_df['ticker'].isin(tickers)]

# Step 5: Save the results to a CSV file
mapped_tickers[['ticker', 'cik']].to_csv(output_file_path, index=False)

print(f"Mapped tickers to CIK saved to {output_file_path}")
