import requests
import os
from datetime import datetime
import time
from urllib.parse import urlparse

def check_website():
    url = os.environ['WEBSITE_URL']
    search_text = os.environ['SEARCH_TEXT']
    
    # Headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
    }
    
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        # Get the domain for the Referer header
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        headers['Referer'] = domain
        
        print(f"[{datetime.now()}] Accessing {url}")
        
        # Make the request
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Check if we got actual content
        content = response.text
        print(f"Content length: {len(content)}")
        
        if search_text.lower() in content.lower():
            print(f"[{datetime.now()}] Found text: {search_text}")
            if 'DISCORD_WEBHOOK' in os.environ:
                requests.post(os.environ['DISCORD_WEBHOOK'], 
                    json={"content": f"Found text: {search_text} on {url}"})
        else:
            print(f"[{datetime.now()}] Text not found")
            print("First 1000 characters:", content[:1000])
            
        # Save the response content for debugging
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_website()