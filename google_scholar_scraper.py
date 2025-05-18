import re
import time
import argparse
import random
import bibtexparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

def extract_title(entry):
    """Extract clean title from a BibTeX entry."""
    if 'title' not in entry:
        return None
    
    title = entry['title']
    # Remove curly braces, which are common in BibTeX titles
    title = re.sub(r'{|}', '', title)
    # Remove special formatting like \textbackslash, etc.
    title = re.sub(r'\\[a-zA-Z]+', '', title)
    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def setup_webdriver(proxy_url=None):
    """Set up and return a configured Chrome WebDriver instance."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    
    # Add proxy if specified
    if proxy_url:
        chrome_options.add_argument(f'--proxy-server={proxy_url}')
    
    # Add user agent to mimic a regular browser
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Use ChromeDriverManager to automatically download and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def search_google_scholar(title, driver, max_retries=3):
    """Search Google Scholar for a paper by title using Selenium."""
    print(f"Searching for: {title}")
    
    for attempt in range(max_retries):
        # Construct the search URL
        search_query = title.replace(' ', '+')
        url = f"https://scholar.google.com/scholar?q={search_query}"
        
        # Navigate to the search URL
        driver.get(url)
        
        # Wait for the search results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".gs_ri"))
        )
        
        # Look for the first result
        results = driver.find_elements(By.CSS_SELECTOR, ".gs_ri")
        if not results:
            print("No results found")
            return None
        
        # Click on the cite button of the first result
        first_result = results[0]
        cite_button = first_result.find_element(By.CSS_SELECTOR, ".gs_or_cit.gs_or_btn.gs_nph")
        cite_button.click()
        
        # Wait for the citation popup to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".gs_citi"))
        )
        
        # Find and click on the BibTeX link
        bibtex_link = driver.find_element(By.XPATH, "//a[contains(text(), 'BibTeX')]")
        bibtex_link.click()
        
        # Wait for the BibTeX content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "pre"))
        )
        
        # Extract the BibTeX content
        bibtex_content = driver.find_element(By.TAG_NAME, "pre").text
        
        # Parse the BibTeX content
        bib_database = bibtexparser.loads(bibtex_content)
        if bib_database.entries:
            return bib_database.entries[0]
        
        return None

def main():
    parser = argparse.ArgumentParser(description='Scrape Google Scholar for BibTeX references')
    parser.add_argument('--input', type=str, default='reference.bib', help='Input BibTeX file')
    parser.add_argument('--output', type=str, default='google.bib', help='Output BibTeX file')
    parser.add_argument('--delay', type=float, default=3.0, help='Delay between requests (seconds)')
    parser.add_argument('--proxy', type=str, default="http://user-usslab2013:db2013@pr.roxlabs.cn:4600", help='Proxy URL (optional)')
    args = parser.parse_args()
    
    # Load the original BibTeX file
    with open(args.input, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f)
    
    # Create a new database for Google Scholar results
    google_db = BibDatabase()
    google_db.entries = []
    
    # Set up the WebDriver with or without proxy
    driver = setup_webdriver(args.proxy)
    
    try:
        # Process each entry
        for i, entry in enumerate(bib_database.entries):
            title = extract_title(entry)
            if not title:
                print(f"Skipping entry {i+1}: No title found")
                continue
            
            print(f"Processing entry {i+1}/{len(bib_database.entries)}: {title[:60]}...")
            
            # Search Google Scholar
            bibtex_entry = search_google_scholar(title, driver)
            
            # Add to database if found
            if bibtex_entry:
                google_db.entries.append(bibtex_entry)
                print(f"✓ Found and added to database")
            else:
                print(f"✗ Not found on Google Scholar")
            
            # Add delay between requests to avoid rate limiting
            if i < len(bib_database.entries) - 1:
                delay = args.delay * (1 + random.random() * 0.5)  # Add some randomness
                print(f"Waiting {delay:.2f} seconds before next request...")
                time.sleep(delay)
    
    finally:
        # Close the WebDriver
        driver.quit()
    
    # Write the Google Scholar results to a new file
    writer = BibTexWriter()
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(writer.write(google_db))
    
    print(f"\nDone! Retrieved {len(google_db.entries)} references out of {len(bib_database.entries)} entries.")
    print(f"Processed {len(bib_database.entries)} entries.")
    print(f"Found {len(google_db.entries)} entries on Google Scholar.")

if __name__ == "__main__":
    main()