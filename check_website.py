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
    # initial_url = "https://www.citaconsular.es/"  # Or whatever your initial URL is
    initial_url = os.environ["INITIAL_URL"]
    search_text = os.environ['SEARCH_TEXT']
    # url = 'https://www.citaconsular.es/es/hosteds/widgetdefault/2533f04b1d3e818b66f175afc9c24cf63/#services'
    # initial_url = "https://www.exteriores.gob.es/Consulados/miami/es/ServiciosConsulares/Paginas/Ley-de-Memoria-Democr%C3%A1tica-supuesto-1A.aspx"
    # search_text = 'disponibles'


    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0
    })
    chrome_options.binary_location = '/usr/bin/google-chrome'

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Step 1: Navigate to initial page
        print(f"[{datetime.now()}] Accessing initial page: {initial_url}")
        driver.get(initial_url)
        time.sleep(3)  # Wait for page to load
        
        # Step 2: Find and click the link to the target page
        try:
            print("Looking for link to target page...")
            possible_link_selectors = [
    "//a[.//strong[contains(text(), 'ELEGIR FECHA Y HORA')]]",
    "//a[contains(., 'ELEGIR FECHA Y HORA')]",
    "//strong[contains(text(), 'ELEGIR FECHA Y HORA')]/parent::a",
    "//a[normalize-space()='ELEGIR FECHA Y HORA']",
    # Case insensitive version just in case
    "//a[translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='elegir fecha y hora']"            ]
            
            target_link = None
            for selector in possible_link_selectors:
                try:
                    target_link = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"Found target link using selector: {selector}")
                    break
                except:
                    continue
            
            if target_link:
                print("Clicking target link...")
                target_link.click()
                time.sleep(3)  # Wait for page load after click
            else:
                print("Could not find target link")
        except Exception as e:
            print(f"Error finding/clicking target link: {e}")
        
        # Handle JavaScript alert using JavaScript executor
        try:
            print("Attempting to handle JavaScript alert...")
            driver.execute_script("window.onbeforeunload = null;")
            driver.execute_script("window.alert = function() {};")
            driver.execute_script("window.confirm = function() {return true;};")
            time.sleep(2)
        except Exception as e:
            print(f"JavaScript alert handling error: {e}")
        
        # Look for and click the continue button
        try:
            continue_button = None
            possible_selectors = [
                "//button[contains(text(), 'Continue')]",
                "//input[@value='Continue']",
                "//a[contains(text(), 'Continue')]",
                "//button[contains(text(), 'continue')]",
                "//input[@type='submit']",
                "//button[contains(text(), 'Continuar')]",  # Added Spanish version
                "//input[@value='Continuar']"
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
                time.sleep(3)
        except Exception as e:
            print(f"Continue button handling error: {e}")
        
        try:
            print("Waiting for loading indicator to disappear...")
            # Try multiple possible loading indicator selectors
            loading_selectors = [
                "//div[contains(@class, 'loading')]",
                "//div[contains(@class, 'spinner')]",
                "//div[contains(@class, 'loader')]",
                "//div[contains(@class, 'progress')]",
                "//div[@role='progressbar']"
            ]
            
            for selector in loading_selectors:
                try:
                    WebDriverWait(driver, 15).until(
                        EC.invisibility_of_element_located((By.XPATH, selector))
                    )
                    print(f"Loading indicator disappeared (using selector: {selector})")
                    break
                except:
                    continue
            
            # Add a small additional wait to ensure everything is fully loaded
            time.sleep(2)
            
        except Exception as e:
            print(f"Error waiting for loading indicator: {e}")
        
        # Get the page source
        page_content = driver.page_source
        
        print(f"Final page title: {driver.title}")
        print(f"Page content: {page_content}")
        
        if search_text.lower() in page_content.lower():
            print(f"[{datetime.now()}] Found text: {search_text}")
        else:
            print(f"[{datetime.now()}] Text not found")
            print("First 1000 characters:", page_content)
            
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