from typing import Dict, List
from ..browsers.chrome.chrome_browser import ChromeBrowser
from selenium.common.exceptions import WebDriverException
from ..database import DatabaseManager
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrowserController:
    def __init__(self):
        self.browser = None
        self.current_settings = None
        self.db_manager = DatabaseManager()
        
    def initialize_browser(self, settings: Dict):
        """Initialize the selected browser with given settings."""
        self.current_settings = settings
        browser_type = settings["browser"]
        
        try:
            if browser_type == "chrome":
                self.browser = ChromeBrowser(headless=settings["headless"])
            elif browser_type == "firefox":
                # TODO: Add Firefox implementation
                raise NotImplementedError("Firefox support coming soon!")
            elif browser_type == "edge":
                # TODO: Add Edge implementation
                raise NotImplementedError("Edge support coming soon!")
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
            
            return True, "Browser initialized successfully"
        except WebDriverException as e:
            return False, f"Failed to initialize browser: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def collect_cookies(self, urls: List[str], callback=None) -> Dict:
        """
        Collect cookies from the specified URLs.
        
        Args:
            urls: List of URLs to collect cookies from
            callback: Optional callback function to update progress
            
        Returns:
            Dictionary containing results for each URL
        """
        results = {}
        total_urls = len(urls)
        
        try:
            for i, url in enumerate(urls):
                # Calculate base progress for this URL (each URL takes up 1/total_urls of the progress bar)
                base_progress = (i / total_urls) * 100
                
                if callback:
                    callback(base_progress, total_urls, f"Starting {url}")
                
                try:
                    # Add http:// if not present
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    
                    # Create a progress callback for this specific URL
                    def url_progress_callback(progress_fraction, message):
                        if callback:
                            # Calculate overall progress:
                            # base_progress + (progress_fraction * (100/total_urls))
                            overall_progress = base_progress + (progress_fraction * (100/total_urls))
                            callback(overall_progress, total_urls, message)
                    
                    # Get cookies using the new method with progress reporting
                    cookies = self.browser.get_cookies_from_url(
                        url, 
                        self.current_settings["wait_time"],
                        progress_callback=url_progress_callback
                    )
                    
                    # Save to database if requested
                    if self.current_settings["save_cookies"]:
                        try:
                            self.db_manager.save_cookies(url, cookies)
                            logger.info(f"Saved {len(cookies)} cookies for {url} to database")
                        except Exception as e:
                            logger.error(f"Failed to save cookies to database for {url}: {str(e)}")
                    
                    results[url] = {
                        "success": True,
                        "cookies": cookies,
                        "count": len(cookies)
                    }
                    
                except Exception as e:
                    logger.error(f"Failed to collect cookies from {url}: {str(e)}")
                    results[url] = {
                        "success": False,
                        "error": str(e),
                        "cookies": [],
                        "count": 0
                    }
            
            if callback:
                callback(100, total_urls, "Collection completed")
            
            return True, results
            
        except Exception as e:
            logger.error(f"Collection failed: {str(e)}")
            return False, f"Collection failed: {str(e)}"
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}") 