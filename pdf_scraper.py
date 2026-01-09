#!/usr/bin/env python3
"""
PDF Scraper Tool
Downloads all PDF files linked on a given webpage.
Works on both Windows and macOS.
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def create_download_folder(folder_name="Downloaded_PDFs"):
    """Create the download folder if it doesn't exist."""
    # Get the script's directory for cross-platform compatibility
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_path = os.path.join(script_dir, folder_name)
    
    os.makedirs(download_path, exist_ok=True)
    print(f"📁 Download folder: {download_path}")
    return download_path


def get_pdf_links(url):
    """
    Fetch the webpage and extract all PDF links.
    Handles both absolute and relative URLs.
    """
    print(f"🔍 Fetching page: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error fetching page: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    pdf_links = set()  # Use set to avoid duplicates
    
    # Find all anchor tags with href
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Check if the link points to a PDF
        if href.lower().endswith('.pdf'):
            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(url, href)
            pdf_links.add(absolute_url)
    
    print(f"📄 Found {len(pdf_links)} PDF link(s)")
    return list(pdf_links)


def get_filename_from_url(url):
    """Extract a safe filename from the URL."""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    
    # If no filename found, generate one
    if not filename:
        filename = "document.pdf"
    
    # Ensure it ends with .pdf
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    
    return filename


def download_pdf(url, download_path):
    """Download a single PDF file."""
    filename = get_filename_from_url(url)
    filepath = os.path.join(download_path, filename)
    
    # Handle duplicate filenames
    counter = 1
    original_filepath = filepath
    while os.path.exists(filepath):
        name, ext = os.path.splitext(original_filepath)
        filepath = f"{name}_{counter}{ext}"
        counter += 1
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print(f"⬇️  Downloading: {filename}")
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath)
        print(f"✅ Saved: {os.path.basename(filepath)} ({file_size / 1024:.1f} KB)")
        return True
        
    except requests.RequestException as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False


def scrape_pdfs(url):
    """Main function to scrape and download all PDFs from a URL."""
    print("=" * 60)
    print("🔗 PDF Scraper Tool")
    print("=" * 60)
    
    # Create download folder
    download_path = create_download_folder()
    
    # Get all PDF links
    pdf_links = get_pdf_links(url)
    
    if not pdf_links:
        print("⚠️  No PDF links found on the page.")
        print("   This might happen if:")
        print("   - The page uses JavaScript to load links (try Selenium version)")
        print("   - There are no PDF links on this page")
        print("   - The page requires authentication")
        return
    
    # Download each PDF
    print("-" * 60)
    successful = 0
    failed = 0
    
    for pdf_url in pdf_links:
        if download_pdf(pdf_url, download_path):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("-" * 60)
    print(f"📊 Summary: {successful} downloaded, {failed} failed")
    print(f"📁 Files saved to: {download_path}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = input("Enter the website URL: ").strip()
    
    if not target_url:
        print("❌ No URL provided. Exiting.")
        sys.exit(1)
    
    # Add https:// if no protocol specified
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    scrape_pdfs(target_url)
