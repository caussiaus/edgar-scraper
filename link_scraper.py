import requests
import pandas as pd
import os
import time
from datetime import datetime

# Directory to save the filings CSV for each company
save_directory = "links"
os.makedirs(save_directory, exist_ok=True)

# Log file to track CIKs with 404 errors or other issues
error_log_file = "error_log.txt"

# Function to log errors
def log_error(cik, status_code):
    with open(error_log_file, 'a') as log_file:
        log_file.write(f"CIK: {cik}, Status Code: {status_code}\n")

# Function to generate the URL for each filing
def generate_filing_url(cik, accession_number):
    accession_number_no_dashes = accession_number.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number_no_dashes}/{accession_number}-index.html"

# Function to retrieve Form 4 filings for a given CIK between November 15 and December 4
def get_form_4_urls_for_cik(cik):
    try:
        # Get company-specific filing metadata for the CIK
        filing_metadata = requests.get(
            f'https://data.sec.gov/submissions/CIK{cik}.json',
            headers={'User-Agent': 'caseyjussaume@gmail.com'}
        )
        time.sleep(1)  # Add a 1-second delay between requests to avoid rate-limiting

        # Check if the response was successful
        if filing_metadata.status_code != 200:
            print(f"Error: Failed to fetch filings for CIK {cik}. Status code: {filing_metadata.status_code}")
            log_error(cik, filing_metadata.status_code)  # Log the error
            return None

        # Parse recent filings
        recent_filings = filing_metadata.json().get('filings', {}).get('recent', {})

        # Convert recent filings metadata to DataFrame
        all_forms = pd.DataFrame.from_dict(recent_filings)

        # If there are no filings, return None
        if all_forms.empty:
            return None

        # Convert reportDate to datetime and filter for Form 4 filings between November 15 and December 4
        all_forms['reportDate'] = pd.to_datetime(all_forms['reportDate'], errors='coerce')
        start_date = datetime.strptime('2023-11-15', '%Y-%m-%d')
        end_date = datetime.strptime('2024-12-04', '%Y-%m-%d')
        filtered_forms = all_forms[
            (all_forms['form'] == '4', '10-K', '10-Q', 'S-1', 'S-3') &
            (all_forms['reportDate'] >= start_date) &
            (all_forms['reportDate'] <= end_date)
        ]

        # Generate URLs for filtered filings
        filtered_forms['url'] = filtered_forms['accessionNumber'].apply(lambda x: generate_filing_url(cik, x))

        return filtered_forms[['accessionNumber', 'form', 'reportDate', 'url']]

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving filings for CIK {cik}: {e}")
        log_error(cik, "RequestException")  # Log request exceptions
        return None

# Function to read CIKs from a text file (one CIK per line) and ensure they have leading zeros
def read_ciks_from_file(file_path):
    with open(file_path, 'r') as file:
        # Ensure all CIKs are 10 digits long by padding with leading zeros
        ciks = [line.strip().zfill(10) for line in file.readlines()]
    return ciks

# Function to retrieve Form 4 URLs for each CIK in the file and save to CSV
def get_form_4_urls_for_ciks(cik_file):
    # Read the CIKs from the text file
    ciks = read_ciks_from_file(cik_file)

    # Iterate through each CIK in the list
    for cik in ciks:
        print(f"Processing CIK: {cik}")

        # Retrieve Form 4 URLs for the current CIK
        filings = get_form_4_urls_for_cik(cik)

        # If filings were found, save them to a CSV file
        if filings is not None and not filings.empty:
            save_path = os.path.join(save_directory, f"CIK_{cik}_form_4_filings.csv")
            filings.to_csv(save_path, index=False)
            print(f"Saved Form 4 filings for CIK: {cik} to {save_path}")
        else:
            print(f"No Form 4 filings found for CIK: {cik} between November 15 and December 4")

        # Wait for 1 second between processing each company
        time.sleep(1)

# Example usage
cik_file = "C:\skibidi\economicsense\cdo\CIKs\GS.txt"  # Path to your CIK file
get_form_4_urls_for_ciks(cik_file)
