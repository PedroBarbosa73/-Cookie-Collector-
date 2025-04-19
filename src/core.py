from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from .database import DatabaseManager
from .browsers.chrome.chrome_browser import ChromeBrowser
from .gui.controller import BrowserController
import time
import json
from enum import Enum
import os
import logging
import sys
import platform

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    BRAVE = "brave"
    OPERA = "opera"

class CookieCollector:
    def __init__(self, browser_type=BrowserType.CHROME):
        self.db = DatabaseManager()
        self.browser_type = browser_type
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Set up the WebDriver with appropriate options"""
        try:
            if self.browser_type in [BrowserType.CHROME, BrowserType.BRAVE, BrowserType.OPERA]:
                logger.info(f"Setting up {self.browser_type.value} browser...")
                options = ChromeOptions()
                
                # Updated Chrome options for better stability
                options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-infobars')
                options.add_argument('--disable-notifications')
                options.add_argument('--disable-popup-blocking')
                
                # Add user agent to avoid detection
                options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                
                if self.browser_type == BrowserType.BRAVE:
                    brave_path = self._find_brave_path()
                    if brave_path:
                        logger.info(f"Found Brave browser at: {brave_path}")
                        options.binary_location = brave_path
                    else:
                        logger.warning("Brave browser not found. Using Chrome instead.")
                
                elif self.browser_type == BrowserType.OPERA:
                    opera_path = self._find_opera_path()
                    if opera_path:
                        logger.info(f"Found Opera browser at: {opera_path}")
                        options.binary_location = opera_path
                    else:
                        logger.warning("Opera browser not found. Using Chrome instead.")
                
                try:
                    # Get the latest stable Chrome driver
                    driver_path = ChromeDriverManager().install()
                    logger.info(f"Using Chrome WebDriver at: {driver_path}")
                    
                    service = ChromeService(driver_path)
                    self.driver = webdriver.Chrome(service=service, options=options)
                    logger.info("Chrome WebDriver setup successful")
                except Exception as e:
                    logger.error(f"Error setting up Chrome WebDriver: {str(e)}")
                    raise
            
            elif self.browser_type == BrowserType.FIREFOX:
                logger.info("Setting up Firefox browser...")
                options = FirefoxOptions()
                options.add_argument('--headless')
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
                logger.info("Firefox WebDriver setup successful")
            
            elif self.browser_type == BrowserType.EDGE:
                logger.info("Setting up Edge browser...")
                options = EdgeOptions()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=options)
                logger.info("Edge WebDriver setup successful")
            
        except Exception as e:
            logger.error(f"Failed to set up WebDriver for {self.browser_type.value}: {str(e)}")
            raise
    
    def _find_brave_path(self):
        """Find Brave browser executable path"""
        possible_paths = [
            # Windows paths
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            # Linux paths
            "/usr/bin/brave-browser",
            "/usr/bin/brave",
            # macOS paths
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _find_opera_path(self):
        """Find Opera browser executable path"""
        possible_paths = [
            # Windows paths
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera\opera.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Opera\opera.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Opera\opera.exe"),
            # Linux paths
            "/usr/bin/opera",
            # macOS paths
            "/Applications/Opera.app/Contents/MacOS/Opera"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def handle_cookie_consent(self):
        """Attempt to handle common cookie consent popups"""
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
            
            # Save cookies to database
            self.db.save_cookies(url, cookies)
            logger.info("Saved cookies to database")
            
            return cookies
        except Exception as e:
            logger.error(f"Error collecting cookies for {url}: {str(e)}")
            return None
    
    def load_cookies(self, url):
        """Load previously saved cookies for a URL"""
        try:
            cookies = self.db.get_cookies(url)
            if cookies:
                logger.info(f"Loading {len(cookies)} cookies from database")
                self.driver.get(url)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        logger.warning(f"Failed to add cookie: {str(e)}")
                self.driver.refresh()
                return True
            logger.info("No cookies found in database")
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

def main():
    """Example usage"""
    url = "https://www.python.org"
    collector = CookieCollector(BrowserType.CHROME)
    try:
        cookies = collector.collect_cookies(url)
        if cookies:
            logger.info(f"Successfully collected {len(cookies)} cookies")
    finally:
        collector.close()

if __name__ == "__main__":
    main() 