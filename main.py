import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote
import os
import hashlib
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def sanitize_filename(filename):
    # Replace special characters with underscores
    return re.sub(r'[\\/:*?"<>|]', '_', filename)

def download_pdf(url, destination_folder):
    # Retry mechanism with exponential backoff
    retry_strategy = Retry(
        total=3,  # Maximum number of retries
        backoff_factor=1,  # Exponential backoff factor
        status_forcelist=[500, 502, 503, 504],  # HTTP status codes to retry
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    with requests.Session() as session:
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        try:
            response = session.get(url)
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to {url}: {e}")
            return

    if response.status_code == 200:
        filename = os.path.basename(urlparse(url).path)
        hashed_filename = hashlib.md5(url.encode()).hexdigest()[:10]  # Using the first 10 characters of the hash
        file_path = os.path.join(destination_folder, f"{hashed_filename}.pdf")

        # Ensure the destination folder exists
        os.makedirs(destination_folder, exist_ok=True)

        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {url}")
    else:
        print(f"Failed to download: {url}")

def process_url(url, destination_folder):
    if not url:
        print("Skipping empty URL.")
        return

    download_pdf(url, destination_folder)

if __name__ == "__main__":
    input_file = "urls.txt"  # Replace with your input file containing URLs
    destination_folder = "pdf_downloads"  # Replace with your desired destination folder

    with open(input_file, 'r') as file:
        for line in file:
            url = line.strip()
            process_url(url, destination_folder)
