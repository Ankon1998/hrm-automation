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

        print(f"   Found {len(candidates)} potential buttons. Testing them one by one...")

        popup_opened = False

        for index, btn in enumerate(candidates):
            try:
                print(f"   [Candidate {index+1}] Text: '{btn.text}'")
                driver.execute_script("arguments[0].scrollIntoView();", btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", btn)
                print("      Clicked. Waiting for popup...")
                time.sleep(3)

                # Check if Popup appeared
                modals = driver.find_elements(By.CSS_SELECTOR, ".modal-footer")
                if len(modals) > 0 and modals[0].is_displayed():
                    print("      SUCCESS: Popup detected!")
                    popup_opened = True
                    break 
                else:
                    print("      No popup. Trying next candidate...")
            
            except Exception as e:
                print(f"      Failed to click candidate {index+1}: {e}")

        if not popup_opened:
            raise Exception("Tried all buttons, but popup never opened.")

        # --- HANDLING POPUP (FIXED SECTION) ---
        print("5. Confirming Attendance...")
        
        # OLD LOGIC (Failed): looked for .btn-warning (Orange only)
        # NEW LOGIC (Robust): Looks for the button in the footer that is NOT 'Cancel'
        
        # This XPath says: "Find a button inside .modal-footer that does NOT contain the text 'Cancel'"
        final_xpath = "//div[contains(@class, 'modal-footer')]//button[not(contains(text(), 'Cancel'))]"
        
        confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, final_xpath)))
        
        print(f"   Found Final Button: '{confirm_btn.text}' (Color/Class doesn't matter now)")
        driver.execute_script("arguments[0].click();", confirm_btn)
        
        print("SUCCESS: Attendance Action Completed!")
        time.sleep(5)

    except Exception as e:
        print("\n--- ERROR DIAGNOSIS ---")
        try:
            print(f"Current Page Title: {driver.title}")
        except:
            pass
        print(f"Error details: {e}")
        raise e 
    finally:
        driver.quit()

if __name__ == "__main__":
    run_attendance()
