import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- CONFIGURATION FROM SECRETS ---
HRM_LOGIN_URL = "https://hrm.techlandbd.net/login"
# We fetch these from the cloud environment settings
EMAIL = os.environ.get('HRM_EMAIL')
PASSWORD = os.environ.get('HRM_PASSWORD')

def run_attendance():
    print("1. Launching Headless Browser...")
    chrome_options = Options()
    chrome_options.add_argument("--headless") # MANDATORY for cloud
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # --- LOGIN ---
        print("2. Logging in...")
        driver.get(HRM_LOGIN_URL)
        wait = WebDriverWait(driver, 20)

        wait.until(EC.presence_of_element_located((By.ID, "formData.email"))).send_keys(EMAIL)
        driver.find_element(By.ID, "formData.password").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # --- DASHBOARD ---
        print("3. Checking Dashboard...")
        time.sleep(5) 
        
        try:
            main_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Punch') or contains(text(), 'Clock')]")))
            main_btn.click()
        except:
            print("   Main button not found (Already done?).")
            return

        # --- POPUP ---
        print("4. Handling Popup...")
        time.sleep(3)
        popup_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-footer button.btn-warning")))
        
        driver.execute_script("arguments[0].click();", popup_btn)
        print("SUCCESS: Attendance Action Completed!")
        time.sleep(5)

    except Exception as e:
        print(f"ERROR: {e}")
        # We raise the error so GitHub knows it failed and sends you an email
        raise e 
    finally:
        driver.quit()

if __name__ == "__main__":
    run_attendance()
