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
    # Add these options to handle alerts
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0
    })
    chrome_options.binary_location = '/usr/bin/google-chrome'
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"[{datetime.now()}] Accessing {url}")
        driver.get(url)
        
        # Handle JavaScript alert using JavaScript executor
        try:
            print("Attempting to handle JavaScript alert...")
            driver.execute_script("window.onbeforeunload = null;")
            driver.execute_script("window.alert = function() {};")
            driver.execute_script("window.confirm = function() {return true;};")
            time.sleep(2)  # Brief pause to let JS execute
        except Exception as e:
            print(f"JavaScript alert handling error: {e}")
        
        # Look for and click the continue button (try multiple possible selectors)
        try:
            # Wait for any of these possible continue button variations
            continue_button = None
            possible_selectors = [
                "//button[contains(text(), 'Continue')]",
                "//input[@value='Continue']",
                "//a[contains(text(), 'Continue')]",
                "//button[contains(text(), 'continue')]",
                "//input[@type='submit']"
            ]
            
            for selector in possible_selectors:
                try:
                    continue_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"Found continue button using selector: {selector}")
                    break
                except:
                    continue
            
            if continue_button:
                continue_button.click()
                print("Clicked continue button")
                time.sleep(3)  # Wait for page to load after clicking
        except Exception as e:
            print(f"Continue button handling error: {e}")
        
        # Wait for the page content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Get the page source
        page_content = driver.page_source
        
        print(f"Final page title: {driver.title}")
        print(f"Page content length: {len(page_content)}")
        
        if search_text.lower() in page_content.lower():
            print(f"[{datetime.now()}] Found text: {search_text}")
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