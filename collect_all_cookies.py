from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from database import DatabaseManager
from config import TARGET_WEBSITES

def setup_chrome():
    """Setup Chrome with remote debugging"""
    options = Options()
    options.add_argument('--remote-debugging-port=9222')
    return webdriver.Chrome(options=options)

def collect_cookies_from_website(driver, website_name, website_info):
    """Collect cookies from a specific website"""
    print(f"\nCollecting cookies from {website_name.upper()}...")
    print(f"URL: {website_info['url']}")
    print(f"Description: {website_info['description']}")
    
    try:
        # Visit the website
        driver.get(website_info['url'])
        
        # Wait for page to load and cookies to be set
        time.sleep(5)
        
        # Get all cookies
        cookies = driver.get_cookies()
        
        # Count cookies by security attributes
        secure_cookies = sum(1 for c in cookies if c.get('secure', False))
        httponly_cookies = sum(1 for c in cookies if c.get('httpOnly', False))
        
        print(f"Found {len(cookies)} cookies:")
        print(f"- Secure cookies: {secure_cookies}")
        print(f"- HTTPOnly cookies: {httponly_cookies}")
        
        # Save cookies to database
        db = DatabaseManager()
        db.save_cookies(website_info['url'], cookies)
        print("✓ Cookies saved successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error collecting cookies from {website_name}: {str(e)}")
        return False

def main():
    print("=== Multi-Website Cookie Collector ===")
    
    # Initialize Chrome
    driver = setup_chrome()
    
    try:
        successful_sites = 0
        total_sites = len(TARGET_WEBSITES)
        
        # Collect cookies from each website
        for site_name, site_info in TARGET_WEBSITES.items():
            if collect_cookies_from_website(driver, site_name, site_info):
                successful_sites += 1
            print("-" * 50)
        
        # Summary
        print("\n=== Collection Summary ===")
        print(f"Successfully collected cookies from {successful_sites} out of {total_sites} websites")
        
        if successful_sites < total_sites:
            print("\nNote: For websites requiring login, make sure you're logged in")
            print("through your main Chrome browser before running this script.")
        
    finally:
        driver.quit()
        print("\nBrowser closed. Cookie collection complete!")

if __name__ == "__main__":
    main() 