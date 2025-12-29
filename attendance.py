import os
import time
from datetime import datetime
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
    print("1. Launching Cloud Browser...")
    
    chrome_options = Options()
    # --- STEALTH SETTINGS FOR CLOUD ---
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Fake a real User Agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # HIDE SELENIUM (Critical for avoiding 404/403 blocks)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

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
        print("   Looking for 'Punch' buttons...")
        # Recursively find any button containing "Punch" or "Clock"
        candidates = driver.find_elements(By.XPATH, "//button[descendant-or-self::*[contains(text(), 'Punch') or contains(text(), 'Clock')]]")
        
        # Fallback if no <button> tags found
        if not candidates:
            candidates = driver.find_elements(By.XPATH, "//a[contains(text(), 'Punch') or contains(text(), 'Clock')]")

        popup_opened = False
        
        # Try clicking candidates one by one until popup opens
        for btn in candidates:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(3)
                
                # Check if popup appeared
                if driver.find_elements(By.CSS_SELECTOR, ".modal-footer"):
                    print("      SUCCESS: Popup detected!")
                    popup_opened = True
                    break 
            except: 
                pass

        if not popup_opened:
            raise Exception("Popup never opened. Could not find valid Punch button.")

        # --- HANDLING POPUP ---
        print("5. Confirming Attendance...")
        
        # Find the button that is NOT 'Cancel'
        final_xpath = "//div[contains(@class, 'modal-footer')]//button[not(contains(text(), 'Cancel'))]"
        confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, final_xpath)))
        
        # --- SAFETY CHECK (PREVENTS ACCIDENTAL CLOCK-OUT) ---
        btn_text = confirm_btn.text.lower()
        
        # Server is UTC, so add 6 hours for Bangladesh Time
        bd_hour = datetime.now().hour + 6 
        if bd_hour >= 24: bd_hour -= 24
        
        print(f"   Action: '{confirm_btn.text}' | Est BD Hour: {bd_hour}:00")

        # Morning Rule (Before 2 PM): Only allow "In"
        if bd_hour < 14 and "out" in btn_text:
            print("⚠️ STOP: It is Morning but button says 'Out'. You are already clocked in.")
            return

        # Evening Rule (After 2 PM): Only allow "Out"
        elif bd_hour >= 14 and "in" in btn_text:
            print("⚠️ STOP: It is Evening but button says 'In'. Preventing accidental new shift.")
            return

        # Click the button
        driver.execute_script("arguments[0].click();", confirm_btn)
        print("SUCCESS: Action Completed!")
        time.sleep(5)

    except Exception as e:
        print(f"\n--- ERROR: {e}")
        # Print page title to debug blocks
        try:
            print(f"Page Title: {driver.title}") 
        except:
            pass
        raise e 
    finally:
        driver.quit()

if __name__ == "__main__":
    run_attendance()
