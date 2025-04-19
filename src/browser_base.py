from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrowserBase(ABC):
    def __init__(self):
        self.driver = None
    
    @abstractmethod
    def setup_driver(self):
        """Set up the WebDriver with browser-specific options"""
        pass
    
    def handle_cookie_consent(self):
        """Attempt to handle common cookie consent popups"""
        if not self.driver:
            raise Exception("Driver not initialized")
            
        common_selectors = [
            'button[id*="cookie"]',
            'button[id*="consent"]',
            'button[class*="cookie"]',
            'button[class*="consent"]',
            'button[data-testid*="cookie"]',
            'button[data-testid*="consent"]',
            'button:contains("Accept")',
            'button:contains("Allow")',
            'button:contains("Agree")'
        ]
        
        for selector in common_selectors:
            try:
                logger.debug(f"Trying to find cookie consent button with selector: {selector}")
                button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                button.click()
                logger.info("Successfully clicked cookie consent button")
                time.sleep(2)  # Wait for the popup to disappear
                return True
            except Exception:
                continue
        
        logger.info("No cookie consent button found or needed")
        return False
    
    def collect_cookies(self, url):
        """Visit a URL, handle cookie consent, and collect cookies"""
        if not self.driver:
            raise Exception("Driver not initialized")
            
        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)
            time.sleep(5)  # Initial wait for page load
            
            # Try to handle cookie consent
            self.handle_cookie_consent()
            
            # Wait for any dynamic content to load
            time.sleep(3)
            
            # Get all cookies
            cookies = self.driver.get_cookies()
            logger.info(f"Collected {len(cookies)} cookies")
            
            return cookies
        except Exception as e:
            logger.error(f"Error collecting cookies for {url}: {str(e)}")
            return None
    
    def load_cookies(self, url, cookies):
        """Load cookies for a URL"""
        if not self.driver:
            raise Exception("Driver not initialized")
            
        try:
            if cookies:
                logger.info(f"Loading {len(cookies)} cookies")
                self.driver.get(url)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        logger.warning(f"Failed to add cookie: {str(e)}")
                self.driver.refresh()
                return True
            logger.info("No cookies provided")
            return False
        except Exception as e:
            logger.error(f"Error loading cookies: {str(e)}")
            return False
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")
                
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close() 