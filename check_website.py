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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def send_email_notification(found_text, screenshot_path=None):
    sender_email = os.environ.get('EMAIL_SENDER')
    sender_password = os.environ.get('EMAIL_PASSWORD')
    recipient_emails = os.environ.get('EMAIL_RECIPIENTS', '').split(',')    

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(recipient_emails)

    if not found_text:
        msg['Subject'] = "🎉 Alert: Spanish Consulate Appointments may be available!"
        body = f"The text '{os.environ.get('SEARCH_TEXT')}' was not found on the website at {datetime.now()}. This indicates appointments may be available. Check here to confirm {os.environ.get('INITIAL_URL')}\n\nPlease see the attached screenshot for verification."
    else:
        msg['Subject'] = "Website Check Update"
        body = f"Check completed at {datetime.now()}. The target text '{os.environ.get('SEARCH_TEXT')}' was found. This indicates appointments are not likely available.\n\nPlease see the attached screenshot for verification."
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach screenshot if available
    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', filename="appointment_page.png")
            # Add the image inline in the email body
            img.add_header('Content-ID', '<appointment_screenshot>')
            msg.attach(img)
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Email notification sent successfully to {len(recipient_emails)} recipients")
    except Exception as e:
        print(f"Failed to send email: {e}")

def capture_full_page_screenshot(driver, path):
    try:
        # Get the total height of the page
        total_height = driver.execute_script("return document.body.scrollHeight")
        # Set window size to capture everything
        driver.set_window_size(1920, total_height)
        time.sleep(1)  # Wait for any dynamic content to load
        # Take screenshot
        driver.save_screenshot(path)
        print(f"Full page screenshot saved to {path}")
        return True
    except Exception as e:
        print(f"Error capturing full page screenshot: {e}")
        return False

def check_website():
    search_text = "No hay horas disponibles."
    initial_url = "https://www.exteriores.gob.es/Consulados/miami/es/ServiciosConsulares/Paginas/Ley-de-Memoria-Democr%C3%A1tica-supuesto-1A.aspx"

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
        
        print(f"[{datetime.now()}] Accessing initial page: {initial_url}")
        driver.get(initial_url)
        time.sleep(3)
        
        try:
            print("Looking for link to target page...")
            possible_link_selectors = [
                "//a[.//strong[contains(text(), 'ELEGIR FECHA Y HORA')]]",
                "//a[contains(., 'ELEGIR FECHA Y HORA')]",
                "//strong[contains(text(), 'ELEGIR FECHA Y HORA')]/parent::a",
                "//a[normalize-space()='ELEGIR FECHA Y HORA']",
                "//a[translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='elegir fecha y hora']"
            ]
            
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
                time.sleep(3)
            else:
                print("Could not find target link")
        except Exception as e:
            print(f"Error finding/clicking target link: {e}")
        
        try:
            print("Handling JavaScript alerts...")
            driver.execute_script("window.onbeforeunload = null;")
            driver.execute_script("window.alert = function() {};")
            driver.execute_script("window.confirm = function() {return true;};")
            time.sleep(2)
        except Exception as e:
            print(f"JavaScript alert handling error: {e}")
        
        try:
            continue_button = None
            possible_selectors = [
                "//button[contains(text(), 'Continue')]",
                "//input[@value='Continue']",
                "//a[contains(text(), 'Continue')]",
                "//button[contains(text(), 'continue')]",
                "//input[@type='submit']",
                "//button[contains(text(), 'Continuar')]",
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
            
            time.sleep(2)
            
        except Exception as e:
            print(f"Error waiting for loading indicator: {e}")
        
        page_content = driver.page_source
        
        print(f"Final page title: {driver.title}")
        print(f"Page content length: {len(page_content)}")
        
        text_found = False
        if search_text.lower() in page_content.lower():
            print(f"[{datetime.now()}] Found text: {search_text}")
            text_found = True
        else:
            print(f"[{datetime.now()}] Text not found")
            print("First 1000 characters:", page_content[:1000])
            
        # Take a full page screenshot after all interactions are complete
        screenshot_path = "appointment_page.png"
        capture_full_page_screenshot(driver, screenshot_path)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if driver is not None:
            try:
                send_email_notification(text_found, screenshot_path)
            except Exception as e:
                print(f"Error sending email notification: {e}")
            driver.quit()

if __name__ == "__main__":
    check_website()