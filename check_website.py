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
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.binary_location = '/usr/bin/google-chrome'
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"[{datetime.now()}] Accessing {url}")
        driver.get(url)
        
        # Wait for alert and accept it
        try:
            print("Waiting for alert...")
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"Alert text: {alert.text}")
            alert.accept()
            print("Alert accepted")
        except Exception as e:
            print(f"Alert handling error: {e}")
        
        # Wait for content after alert
        time.sleep(5)  # Give page time to load after alert
        
        # Get the page source
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
                driver.save_screenshot("page.png")
                print("Screenshot saved")
            except Exception as e:
                print(f"Screenshot error: {e}")
            driver.quit()

if __name__ == "__main__":
    check_website()