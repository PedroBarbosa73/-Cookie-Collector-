from chrome_browser import ChromeBrowser
from database import DatabaseManager
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_cookie_collection(test_url):
    """Test basic cookie collection functionality"""
    logger.info(f"\nTesting cookie collection for {test_url}")
    
    with ChromeBrowser() as browser:
        # Navigate to main page and wait for it to load
        browser.driver.get(test_url)
        time.sleep(5)  # Give more time for the page to load
        
        # Get initial cookies
        initial_cookies = browser.driver.get_cookies()
        logger.info(f"Initial cookies before login: {len(initial_cookies)}")
        
        # Visit different YouTube sections to get more cookies
        sections = [
            "/feed/trending",
            "/gaming",
            "/music",
            "/sports"
        ]
        
        for section in sections:
            try:
                browser.driver.get(test_url + section)
                time.sleep(3)  # Wait for page load
                
                # Try to interact with content
                videos = browser.driver.find_elements("css selector", "ytd-video-renderer")
                if videos:
                    # Click the first video
                    videos[0].click()
                    time.sleep(5)  # Wait for video to load
                    
                    # Try to interact with video (like, subscribe, etc.)
                    try:
                        like_button = browser.driver.find_element("css selector", "ytd-toggle-button-renderer")
                        like_button.click()
                        time.sleep(1)
                    except:
                        logger.info("Could not interact with video buttons")
            except Exception as e:
                logger.info(f"Error visiting section {section}: {str(e)}")
        
        # Collect all cookies after interactions
        cookies = browser.driver.get_cookies()
        
        if cookies:
            logger.info(f"Successfully collected {len(cookies)} cookies")
            for cookie in cookies:
                logger.info(f"Cookie: {cookie.get('name')} = {cookie.get('value')[:20]}...")
            
            # Save cookies to database
            db = DatabaseManager()
            try:
                db.save_cookies(test_url, cookies)
                logger.info("Cookies saved to database successfully")
            except Exception as e:
                logger.error(f"Failed to save cookies to database: {str(e)}")
            
            return cookies
        else:
            logger.warning("No cookies collected")
            return None

def test_cookie_persistence(test_url):
    """Test saving and loading cookies"""
    logger.info("\nTesting cookie persistence")
    db = DatabaseManager()
    
    # First collection
    cookies = test_cookie_collection(test_url)
    if not cookies:
        logger.error("Failed to collect cookies, skipping persistence test")
        return
    
    # Wait a bit
    time.sleep(2)
    
    # Try to load and use cookies
    with ChromeBrowser() as browser:
        try:
            # Get cookies from database
            stored_cookies = db.get_cookies(test_url)
            if not stored_cookies:
                logger.error("No cookies found in database")
                return
            
            logger.info(f"Retrieved {len(stored_cookies)} cookies from database")
            
            # Try to use the cookies
            if browser.load_cookies(test_url, stored_cookies):
                logger.info("Successfully loaded and applied cookies")
            else:
                logger.warning("Failed to load cookies")
        except Exception as e:
            logger.error(f"Error during cookie loading test: {str(e)}")

def main():
    logger.info("Starting Chrome cookie collector tests...")
    
    # Test with YouTube
    test_url = "https://www.youtube.com"
    
    # Run tests
    test_cookie_collection(test_url)
    test_cookie_persistence(test_url)
    
    logger.info("All Chrome tests completed!")

if __name__ == "__main__":
    main() 