from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from datetime import datetime
import time
import requests

def check_website():
    url = os.environ['WEBSITE_URL']
    search_text = os.environ['SEARCH_TEXT']
    
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.binary_location = '/usr/bin/google-chrome'
    
    driver = None
    try:
        # Initialize the driver with webdriver_manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"[{datetime.now()}] Accessing {url}")
        
        # Load the page
        driver.get(url)
        
        # Wait for 10 seconds to let everything load
        time.sleep(10)
        
        # Get the page source after JavaScript has rendered
        page_content = driver.page_source
        
        if search_text.lower() in page_content.lower():
            print(f"[{datetime.now()}] Found text: {search_text}")
            if 'DISCORD_WEBHOOK' in os.environ:
                requests.post(os.environ['DISCORD_WEBHOOK'], 
                    json={"content": f"Found text: {search_text} on {url}"})
        else:
            print(f"[{datetime.now()}] Text not found")
            print("Page content length:", len(page_content))
            print("First 1000 characters:", page_content[:1000])
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Chrome binary location: {chrome_options.binary_location}")
        # Print if Chrome exists
        if os.path.exists('/usr/bin/google-chrome'):
            print("Chrome binary exists at /usr/bin/google-chrome")
        else:
            print("Chrome binary not found at /usr/bin/google-chrome")
    finally:
        if driver is not None:
            driver.quit()

if __name__ == "__main__":
    check_website()