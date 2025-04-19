from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from database import DatabaseManager

def test_youtube_experience():
    db = DatabaseManager()
    youtube_cookies = db.get_cookies("https://www.youtube.com")
    
    print("\n=== Testing YouTube Experience ===")
    
    # Setup Chrome options
    options = Options()
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--incognito')  # Start in incognito mode
    
    # Create driver
    driver = webdriver.Chrome(options=options)
    
    try:
        # First show YouTube without cookies
        print("\n1. Without Cookies (Fresh Session):")
        driver.get("https://www.youtube.com")
        time.sleep(5)  # Give time to observe
        print("- You should see the default YouTube homepage")
        print("- No personalized recommendations")
        print("- Not logged in")
        input("Press Enter to continue and see YouTube with your cookies...")
        
        # Now add the cookies and show YouTube with them
        print("\n2. Adding Your Cookies:")
        for cookie in youtube_cookies:
            try:
                if 'expiry' in cookie:
                    del cookie['expiry']  # Remove expiry to avoid timestamp issues
                driver.add_cookie(cookie)
            except Exception as e:
                continue
        
        # Refresh to apply cookies
        driver.refresh()
        time.sleep(5)  # Give time for page to load with cookies
        
        print("\nWith Your Cookies Applied:")
        print("- You should now see your personalized YouTube homepage")
        print("- Your preferences should be applied")
        print("- Your login status should be restored")
        print("\nObserve the differences in:")
        print("1. Recommended videos (personalized vs generic)")
        print("2. UI preferences (dark/light mode, language, etc.)")
        print("3. Login status")
        
        input("\nPress Enter to close the browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_youtube_experience() 