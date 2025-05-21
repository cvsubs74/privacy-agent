# privacy_agent/utils/web_parser.py
import requests
from bs4 import BeautifulSoup

def fetch_url_content(url: str) -> str | None:
    """
    Fetches the HTML content from the given URL.

    Args:
        url: The URL to fetch.

    Returns:
        The HTML content as a string, or None if an error occurs.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def extract_text_from_html(html_content: str) -> str:
    """
    Extracts clean text content from HTML.

    Args:
        html_content: The HTML content as a string.

    Returns:
        The extracted plain text.
    """
    if not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text
        text = soup.get_text()

        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        print(f"Error extracting text from HTML: {e}")
        return ""

if __name__ == '__main__':
    # Example usage (for testing this module directly)
    test_url = "https://termly.io/html_document/website-privacy-policy-template-text-format/" # Example privacy policy
    print(f"Fetching content from: {test_url}")
    html = fetch_url_content(test_url)
    if html:
        print(f"Successfully fetched HTML (length: {len(html)} characters).")
        extracted_text = extract_text_from_html(html)
        print(f"\nExtracted Text (first 500 chars):\n{extracted_text[:500]}...")
        print(f"\nTotal extracted text length: {len(extracted_text)} characters.")
    else:
        print("Failed to fetch HTML.")
