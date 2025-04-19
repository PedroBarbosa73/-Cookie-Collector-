from src.browsers.chrome.chrome_browser import ChromeBrowser
import logging
import time
from selenium.common.exceptions import WebDriverException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_navigation(browser):
    """Test basic browser navigation"""
    logger.info("Testing basic browser navigation...")
    
    try:
        # Test navigation to YouTube
        test_url = "https://www.youtube.com"
        browser.driver.get(test_url)
        time.sleep(3)  # Wait for page load
        
        # Verify we're on YouTube
        current_url = browser.driver.current_url
        logger.info(f"Current URL: {current_url}")
        
        # Check if we can find some YouTube elements
        try:
            # Look for the YouTube logo
            logo = browser.driver.find_element("css selector", "ytd-logo")
            logger.info("Found YouTube logo - Navigation successful!")
        except Exception as e:
            logger.error(f"Could not find YouTube logo: {str(e)}")
    except WebDriverException as e:
        logger.error(f"Browser navigation test failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in navigation test: {str(e)}")

def test_cookie_handling(browser):
    """Test basic cookie handling"""
    logger.info("Testing cookie handling...")
    
    try:
        # Navigate to YouTube
        test_url = "https://www.youtube.com"
        browser.driver.get(test_url)
        time.sleep(3)
        
        # Get initial cookies
        cookies = browser.driver.get_cookies()
        logger.info(f"Found {len(cookies)} cookies")
        
        if cookies:
            # Print first few cookies as example
            for cookie in cookies[:3]:
                logger.info(f"Cookie: {cookie.get('name')} = {cookie.get('value')[:20]}...")
    except WebDriverException as e:
        logger.error(f"Browser cookie test failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in cookie test: {str(e)}")

def main():
    logger.info("Starting Chrome browser tests...")
    
    try:
        # Create a single browser instance for all tests
        with ChromeBrowser() as browser:
            # Run basic navigation test
            test_basic_navigation(browser)
            
            # Add a small delay between tests
            time.sleep(2)
            
            # Run cookie handling test
            test_cookie_handling(browser)
            
            logger.info("All Chrome tests completed!")
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")

if __name__ == "__main__":
    main() 