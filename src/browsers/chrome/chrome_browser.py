from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from ...browser_base import BrowserBase
import time
import logging
import os
import sys
import subprocess
import psutil
from typing import List, Dict

logger = logging.getLogger(__name__)

class ChromeBrowser(BrowserBase):
    def __init__(self, headless=False):
        super().__init__()
        self.chrome_process = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """Set up Chrome WebDriver with optimized settings"""
        try:
            logger.info("Setting up Chrome browser...")
            
            # Kill any existing Chrome instances
            self._kill_existing_chrome()
            
            # Create Chrome options
            options = ChromeOptions()
            
            # Common options for both modes
            options.add_argument('--enable-javascript')
            options.add_argument('--enable-cookies')
            options.add_argument('--start-maximized')
            
            # Get Chrome driver
            driver_manager = ChromeDriverManager()
            driver_path = driver_manager.install()
            
            # Ensure we're using the correct executable
            if sys.platform == 'win32':
                driver_dir = os.path.dirname(driver_path)
                if 'chromedriver-win32' in driver_dir:
                    driver_path = os.path.join(driver_dir, 'chromedriver.exe')
                logger.info(f"Using Chrome WebDriver path: {driver_path}")
            
            if self.headless:
                options.add_argument('--headless=new')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--window-size=1920,1080')
                
                # Create service
                service = ChromeService(executable_path=driver_path)
                
                # Initialize driver directly in headless mode
                self.driver = webdriver.Chrome(service=service, options=options)
                logger.info("Chrome WebDriver setup successful in headless mode")
                return
            
            # For non-headless mode, continue with remote debugging setup
            debug_port = 9222
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            user_data_dir = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
            
            # Start Chrome with remote debugging enabled
            chrome_cmd = [
                chrome_path,
                f"--remote-debugging-port={debug_port}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "about:blank"  # Start with a blank page
            ]
            
            logger.info("Starting Chrome with remote debugging...")
            self.chrome_process = subprocess.Popen(chrome_cmd)
            time.sleep(3)  # Give Chrome time to start
            
            # Add remote debugging option
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            
            # Create service
            service = ChromeService(executable_path=driver_path)
            
            # Initialize driver
            self.driver = webdriver.Chrome(service=service, options=options)
            logger.info("Chrome WebDriver setup successful")
            
        except Exception as e:
            logger.error(f"Failed to set up Chrome WebDriver: {str(e)}")
            self._cleanup()
            raise
    
    def _kill_existing_chrome(self):
        """Kill any existing Chrome processes"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'chrome.exe':
                    try:
                        proc.kill()
                    except:
                        pass
            time.sleep(2)  # Give processes time to close
        except:
            pass
    
    def _cleanup(self):
        """Clean up resources"""
        if self.chrome_process:
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait(timeout=5)
            except:
                pass
            self.chrome_process = None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self._cleanup()

    def get_cookies_from_url(self, url: str, wait_time: int = 3, progress_callback=None) -> List[Dict]:
        """Get cookies from a specific URL with proper waiting and error handling"""
        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)
            
            if progress_callback:
                progress_callback(0.5, f"Loading {url}")  # 50% progress after page starts loading
            
            # Wait for the page to load
            logger.info(f"Waiting {wait_time} seconds for page load")
            time.sleep(wait_time)  # Basic wait
            
            if progress_callback:
                progress_callback(0.8, f"Getting cookies from {url}")  # 80% progress before getting cookies
            
            # Get cookies
            cookies = self.driver.get_cookies()
            logger.info(f"Found {len(cookies)} cookies")
            
            if progress_callback:
                progress_callback(1.0, f"Completed {url}")  # 100% progress after getting cookies
            
            return cookies
            
        except Exception as e:
            logger.error(f"Error getting cookies from {url}: {str(e)}")
            raise 