import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import glob
import time

# Create request header to mimic a browser request
headers = {'User-Agent': "caseyjussaume@gmail.com"}

# Directory containing all CSV files with 10-K URLs
csv_directory = r"C:\skibidi\FIAM\to_scrape_folders\1_to_scrape"  # Path to your CSV files
save_directory = "10k_documents"  # Directory to save 10-K documents
os.makedirs(save_directory, exist_ok=True)

# Function to generate the URL for each filing's landing page
def generate_filing_url(cik, accession_number):
    accession_number_no_dashes = accession_number.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number_no_dashes}/{accession_number}-index.html"

# Function to get the direct 10-K document URL from the landing page
def get_10k_document_url(filing_url):
    try:
        response = requests.get(filing_url, headers=headers)
        time.sleep(0.1)  # Add a 0.1-second delay between requests
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the link to the main 10-K document (usually the first link or one labeled "10-K")
        document_link = None
        for row in soup.find_all('tr'):
            if "10-K" in row.text:  # Look for a row that mentions the 10-K form
                document_link = row.find('a')['href']
                break

        if document_link:
            return f"https://www.sec.gov{document_link}"  # Complete URL for the 10-K document
        else:
            print(f"No 10-K document found for {filing_url}")
            return None
    except Exception as e:
        print(f"Error retrieving 10-K document from {filing_url}: {e}")
        return None

# Download and save the 10-K document
def download_10k_document(doc_url, save_path):
    try:
        response = requests.get(doc_url, headers=headers)
        time.sleep(0.1)  # Add a 0.1-second delay between requests
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"10-K document saved to {save_path}")
        else:
            print(f"Failed to download 10-K document from {doc_url}")
    except Exception as e:
        print(f"Error downloading document: {e}")

# Process each CSV file in the directory
csv_files = glob.glob(os.path.join(csv_directory, "*.csv"))

for csv_file in csv_files:
    # Get the company's CIK from the CSV file name (assuming the CIK is part of the file name)
    company_cik = os.path.basename(csv_file).split("_")[1]

    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Iterate through each URL in the CSV file and download the 10-K documents
    for index, row in df.iterrows():
        filing_url = row['url']
        accession_number = row['accessionNumber']
        print(f"Processing filing for CIK: {company_cik}, Accession Number: {accession_number}")

        # Get the 10-K document URL from the landing page
        document_url = get_10k_document_url(filing_url)
        if document_url:
            # Define the path to save the 10-K document
            company_save_directory = os.path.join(save_directory, company_cik)
            os.makedirs(company_save_directory, exist_ok=True)  # Create a directory for each company based on CIK

            save_path = os.path.join(company_save_directory, f"{accession_number}.html")
            # Download the 10-K document
            download_10k_document(document_url, save_path)
