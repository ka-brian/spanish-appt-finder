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
    chrome_options.add_argument('--headless=new')  # Using newer headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')  # Set a standard window size
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')  # Add a real user agent
    chrome_options.binary_location = '/usr/bin/google-chrome'
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"[{datetime.now()}] Accessing {url}")
        driver.get(url)
        
        # Wait for body to contain more than just empty content
        try:
            WebDriverWait(driver, 20).until(
                lambda x: len(x.find_element(By.TAG_NAME, "body").get_attribute("innerHTML").strip()) > 50
            )
        except Exception as e:
            print(f"Timeout waiting for content to load: {e}")
        
        # Additional wait to ensure dynamic content loads
        time.sleep(5)
        
        # Get the page source after JavaScript has rendered
        page_content = driver.page_source
        
        print(f"Final page title: {driver.title}")
        print(f"Page content length: {len(page_content)}")
        
        if search_text.lower() in page_content.lower():
            print(f"[{datetime.now()}] Found text: {search_text}")
            if 'DISCORD_WEBHOOK' in os.environ:
                requests.post(os.environ['DISCORD_WEBHOOK'], 
                    json={"content": f"Found text: {search_text} on {url}"})
        else:
            print(f"[{datetime.now()}] Text not found")
            print("First 1000 characters:", page_content[:1000])
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if driver is not None:
            try:
                # Take a screenshot before quitting
                driver.save_screenshot("page.png")
                print("Screenshot saved")
            except Exception as e:
                print(f"Screenshot error: {e}")
            driver.quit()

if __name__ == "__main__":
    check_website()