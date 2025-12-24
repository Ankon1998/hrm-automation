import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- CONFIGURATION ---
HRM_LOGIN_URL = "https://hrm.techlandbd.net/login"
EMAIL = os.environ.get('HRM_EMAIL')
PASSWORD = os.environ.get('HRM_PASSWORD')

def run_attendance():
    print("1. Launching Headless Browser...")
    
    # --- FIX 1: ADD FAKE USER-AGENT ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # This line makes the bot look like a real Windows 10 Laptop
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        print("2. Navigating to Login Page...")
        driver.get(HRM_LOGIN_URL)
        
        # --- DEBUG: Print the Page Title ---
        # This tells us if we are on the right page or a "Access Denied" page
        print(f"   Page Title found: {driver.title}")
        
        # --- FIX 2: INCREASE TIMEOUT TO 60 SECONDS ---
        wait = WebDriverWait(driver, 60)

        print("3. Logging in...")
        # Check for Email Field
        email_field = wait.until(EC.presence_of_element_located((By.ID, "formData.email")))
        email_field.clear()
        email_field.send_keys(EMAIL)
        
        driver.find_element(By.ID, "formData.password").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        print("4. Checking Dashboard...")
        # Wait specifically for the URL to change or the dashboard to load
        time.sleep(10) 
        
        try:
            # Look for the punch button
            main_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Punch') or contains(text(), 'Clock')]")))
            main_btn.click()
            print("   Dashboard button clicked.")
        except:
            print("   Main button not found. (Maybe already punched in/out?)")
            return

        print("5. Handling Popup...")
        time.sleep(5)
        
        # Look for the orange button in the modal footer
        popup_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-footer button.btn-warning")))
        
        driver.execute_script("arguments[0].click();", popup_btn)
        print("SUCCESS: Attendance Action Completed!")
        time.sleep(5)

    except Exception as e:
        print("\n--- ERROR DIAGNOSIS ---")
        print(f"Failed on page: {driver.title}")
        print(f"Error details: {e}")
        # This will fail the job in GitHub so you get an email
        raise e 
    finally:
        driver.quit()

if __name__ == "__main__":
    run_attendance()
