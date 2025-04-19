from cookie_collector import CookieCollector, BrowserType
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_single_browser(browser_type, test_url):
    """Test cookie collection with a single browser"""
    logger.info(f"Testing with {browser_type.value} browser...")
    collector = None
    
    try:
        collector = CookieCollector(browser_type)
        
        # Try to collect cookies
        logger.info(f"Collecting cookies from {test_url}")
        cookies = collector.collect_cookies(test_url)
        
        if cookies:
            logger.info(f"Successfully collected {len(cookies)} cookies")
            for cookie in cookies:
                logger.info(f"Cookie: {cookie.get('name')} = {cookie.get('value')[:20]}...")
            
            # Test loading cookies back
            logger.info("Testing cookie loading...")
            if collector.load_cookies(test_url):
                logger.info("Successfully loaded cookies")
            else:
                logger.warning("Failed to load cookies")
        else:
            logger.warning("No cookies collected")
            
    except Exception as e:
        logger.error(f"Error with {browser_type.value}: {str(e)}")
        return False
    finally:
        if collector:
            try:
                collector.close()
                logger.info(f"Finished testing {browser_type.value}")
            except Exception as e:
                logger.error(f"Error closing {browser_type.value} browser: {str(e)}")
        time.sleep(2)  # Wait between browser tests
    
    return True

def test_cookie_persistence(test_url, browser_type=BrowserType.FIREFOX):
    """Test if cookies are properly saved and retrieved from database"""
    logger.info("\nTesting cookie persistence...")
    collector = None
    cookies1 = None
    
    try:
        # First collection
        collector = CookieCollector(browser_type)
        logger.info("First collection - storing cookies")
        cookies1 = collector.collect_cookies(test_url)
        
        if cookies1:
            logger.info(f"Collected {len(cookies1)} cookies")
            
            # Close and create new collector
            collector.close()
            collector = None
            time.sleep(2)
            
            logger.info("Second collection - retrieving stored cookies")
            collector = CookieCollector(browser_type)
            cookies2 = collector.get_cookies(test_url)
            
            if cookies2:
                logger.info(f"Retrieved {len(cookies2)} cookies from database")
                if len(cookies1) == len(cookies2):
                    logger.info("Cookie count matches!")
                else:
                    logger.warning("Warning: Cookie count mismatch!")
            else:
                logger.warning("No cookies retrieved from database")
        else:
            logger.warning("No cookies collected in first attempt")
            
    except Exception as e:
        logger.error(f"Error during persistence test: {str(e)}")
    finally:
        if collector:
            try:
                collector.close()
            except Exception as e:
                logger.error(f"Error closing browser during persistence test: {str(e)}")

def main():
    logger.info("Starting cookie collector tests...")
    
    test_url = "https://www.python.org"  # A safe website to test
    
    # Test with Firefox first
    if test_single_browser(BrowserType.FIREFOX, test_url):
        # If Firefox works, test persistence
        test_cookie_persistence(test_url)
        
        # Then test other browsers
        for browser_type in [BrowserType.CHROME, BrowserType.BRAVE]:
            test_single_browser(browser_type, test_url)
    else:
        logger.error("Firefox test failed, skipping other tests")
    
    logger.info("All tests completed!")

if __name__ == "__main__":
    main() 