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
HRM_LOGIN_URL = "https://hrm.techlandbd.net"
EMAIL = os.environ.get('HRM_EMAIL')
PASSWORD = os.environ.get('HRM_PASSWORD')

def run_attendance():
    print("1. Launching Headless Browser...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Standard User-Agent to prevent 403 errors
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        print("2. Navigating to Login Page...")
        driver.get(HRM_LOGIN_URL)
        wait = WebDriverWait(driver, 60)

        # Login
        print("3. Logging in...")
        wait.until(EC.presence_of_element_located((By.ID, "formData.email"))).send_keys(EMAIL)
        driver.find_element(By.ID, "formData.password").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        print("4. Checking Dashboard...")
        time.sleep(10) # Wait for dashboard load
        
        # --- NEW: ROBUST DASHBOARD CLICK LOGIC ---
        try:
            # Find the main button
            main_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Punch') or contains(text(), 'Clock')]")))
            
            # Attempt 1: Normal Click
            print("   Clicking Dashboard button (Attempt 1)...")
            main_btn.click()
            time.sleep(3)
            
            # Check if popup opened (look for modal-footer)
            # If finding the footer fails, it means the popup isn't open yet.
            if len(driver.find_elements(By.CSS_SELECTOR, ".modal-footer")) == 0:
                print("   Popup did not open. Trying Force Click (Attempt 2)...")
                driver.execute_script("arguments[0].click();", main_btn)
                time.sleep(3)
                
        except Exception as e:
            print("   ERROR: Could not find or click Dashboard button.")
            raise e

        # --- HANDLING POPUP ---
        print("5. Handling Popup...")
        
        # Wait for the orange button specifically
        # We use a broad selector first to catch any orange button in the modal
        popup_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-footer button.btn-warning")))
        
        print(f"   Found Confirmation Button: {popup_btn.text}")
        
        # Force click the final confirmation
        driver.execute_script("arguments[0].click();", popup_btn)
        print("SUCCESS: Attendance Action Completed!")
        
        # Wait a bit to ensure the server received it
        time.sleep(5)

    except Exception as e:
        print("\n--- ERROR DIAGNOSIS ---")
        print(f"Failed on page: {driver.title}")
        print(f"Error details: {e}")
        # Save a screenshot for debugging (Optional, visible in GitHub artifacts if configured)
        driver.save_screenshot("error_screenshot.png") 
        raise e 
    finally:
        driver.quit()

if __name__ == "__main__":
    run_attendance()
