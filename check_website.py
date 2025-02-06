import requests
import os
from datetime import datetime

def check_website():
    url = os.environ['WEBSITE_URL']  # We'll set this in GitHub secrets
    search_text = os.environ['SEARCH_TEXT']
    
    try:
        response = requests.get(url)
        if search_text.lower() in response.text.lower():
            print(f"[{datetime.now()}] Found text: {search_text}")
            # If you want notifications, you could add Discord webhook or email here
            if 'DISCORD_WEBHOOK' in os.environ:
                requests.post(os.environ['DISCORD_WEBHOOK'], 
                    json={"content": f"Found text: {search_text} on {url}"})
        else:
            print(f"[{datetime.now()}] Text not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_website()