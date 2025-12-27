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
    
    # --- IMPORTANT: HEADLESS MUST BE ON FOR GITHUB ACTIONS ---
    chrome_options.add_argument("--headless") 
    
    # Standard Cloud Settings
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
        
        # --- ROBUST POPUP CLICKING LOOP ---
        popup_visible = False
        
        # Try 3 times to open the popup
        for attempt in range(1, 4):
            print(f"   Attempt {attempt}: Clicking Dashboard Punch Button...")
            
            try:
                # 1. Find and Click the Dashboard Button
                main_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Punch') or contains(text(), 'Clock')]")))
                driver.execute_script("arguments[0].click();", main_btn) 
                
                # 2. Wait for animation
                time.sleep(3)
                
                # 3. Check if the ORANGE button is VISIBLE
                orange_btns = driver.find_elements(By.CSS_SELECTOR, ".modal-footer button.btn-warning")
                
                # We check if it exists AND is displayed (visible to the eye)
                if len(orange_btns) > 0 and orange_btns[0].is_displayed():
                    print("   Popup opened successfully!")
                    popup_visible = True
                    break 
                else:
                    print("   Popup not visible yet. Retrying...")
                    
            except Exception as e:
                print(f"   Error during attempt {attempt}: {e}")
                time.sleep(2)

        if not popup_visible:
            raise Exception("Failed to open popup after 3 attempts.")

        # --- HANDLING POPUP ---
        print("5. Confirming Attendance...")
        
        # Find the button again to be safe
        confirm_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-footer button.btn-warning")))
        
        print(f"   Clicking: {confirm_btn.text}")
        driver.execute_script("arguments[0].click();", confirm_btn)
        
        print("SUCCESS: Attendance Action Completed!")
        time.sleep(5)

    except Exception as e:
        print("\n--- ERROR DIAGNOSIS ---")
        # Check if driver is still alive before asking for title
        try:
            print(f"Failed on page: {driver.title}")
        except:
            print("Failed (Browser crashed or closed)")
        print(f"Error details: {e}")
        raise e 
    finally:
        driver.quit()

if __name__ == "__main__":
    run_attendance()
