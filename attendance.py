import os
import time
from datetime import datetime # <--- NEW IMPORT
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- CONFIGURATION ---
HRM_LOGIN_URL = "https://hrm.techlandbd.net"
EMAIL = os.environ.get('HRM_EMAIL')
PASSWORD = os.environ.get('HRM_PASSWORD')

def run_attendance():
    print("1. Launching Browser...")
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        print("2. Navigating to Login Page...")
        driver.get(HRM_LOGIN_URL)
        wait = WebDriverWait(driver, 30)

        # Login
        print("3. Logging in...")
        wait.until(EC.presence_of_element_located((By.ID, "formData.email"))).send_keys(EMAIL)
        driver.find_element(By.ID, "formData.password").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        print("4. Checking Dashboard...")
        time.sleep(10) 

        # --- SMART BUTTON FINDER ---
        print("   Looking for any clickable 'Punch' or 'Clock' elements...")
        candidates = driver.find_elements(By.XPATH, "//button[descendant-or-self::*[contains(text(), 'Punch') or contains(text(), 'Clock')]]")
        if len(candidates) == 0:
            candidates = driver.find_elements(By.XPATH, "//a[contains(text(), 'Punch') or contains(text(), 'Clock')]")

        popup_opened = False
        for index, btn in enumerate(candidates):
            try:
                driver.execute_script("arguments[0].scrollIntoView();", btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(3)

                modals = driver.find_elements(By.CSS_SELECTOR, ".modal-footer")
                if len(modals) > 0 and modals[0].is_displayed():
                    print("      SUCCESS: Popup detected!")
                    popup_opened = True
                    break 
            except:
                pass

        if not popup_opened:
            raise Exception("Tried all buttons, but popup never opened.")

        # --- HANDLING POPUP ---
        print("5. Confirming Attendance...")
        
        # Find the Action Button (Not Cancel)
        final_xpath = "//div[contains(@class, 'modal-footer')]//button[not(contains(text(), 'Cancel'))]"
        confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, final_xpath)))
        
        # --- 🛡️ SAFETY LOGIC START 🛡️ ---
        btn_text = confirm_btn.text.lower()
        current_hour = datetime.now().hour # Gets current hour (0-23)
        
        print(f"   Detected Button Action: '{confirm_btn.text}'")
        print(f"   Current Hour: {current_hour}:00")

        # RULE 1: MORNING (Before 2 PM / 14:00)
        # If it's morning, we expect to see "In". If we see "Out", STOP.
        if current_hour < 14:
            if "out" in btn_text:
                print("⚠️ SAFETY STOP: It is Morning, but button says 'Punch Out'. You are already clocked in.")
                return # Stops the script here

        # RULE 2: EVENING (After 2 PM / 14:00)
        # If it's evening, we expect to see "Out". If we see "In", STOP.
        else:
            if "in" in btn_text:
                print("⚠️ SAFETY STOP: It is Evening, but button says 'Punch In'. Preventing accidental new shift.")
                return # Stops the script here
        # --- 🛡️ SAFETY LOGIC END 🛡️ ---

        print(f"   Safety Check Passed. Clicking...")
        driver.execute_script("arguments[0].click();", confirm_btn)
        
        print("SUCCESS: Attendance Action Completed!")
        time.sleep(5)

    except Exception as e:
        print(f"\n--- ERROR: {e}")
        raise e 
    finally:
        driver.quit()

if __name__ == "__main__":
    run_attendance()
