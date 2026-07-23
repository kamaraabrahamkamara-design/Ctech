import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def keep_app_awake():
    # Your target Streamlit application URL
    url = "https://jizehlnj8zf7gmk8tjavwq.streamlit.app/"

    print(f"Navigating to {url}...")
    
    # Configure headless Chrome for GitHub Actions execution
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        # Give the Streamlit wrapper page 20 seconds to load completely
        time.sleep(20) 
        
        # Check if the 'Wake App' button exists on the screen
        # It handles both potential text indicators ("back up" or "Wake")
        wake_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'back up') or contains(text(), 'Wake')]")
        
        if wake_buttons:
            print("App was sleeping! Clicking the wake button...")
            wake_buttons[0].click()
            # Wait 30 seconds for the cloud container to successfully spin up
            time.sleep(30)
            print("App wake command sent successfully.")
        else:
            print("App is already awake. Active WebSocket session registered.")
            
    except Exception as e:
        print(f"An error occurred during execution: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    keep_app_awake()
