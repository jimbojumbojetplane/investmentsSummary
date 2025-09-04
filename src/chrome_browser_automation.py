import asyncio
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from .config import config
from .utils import sanitize_filename, save_data

logger = logging.getLogger(__name__)

class RBCChromeAutomation:
    """Browser automation class for RBC Direct Investing using user's Chrome browser."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Download tracking - downloads go to ~/Downloads then move to data/input/downloaded_files
        self.downloads_folder = Path.home() / 'Downloads'
        self.project_root = Path(__file__).parent.parent
        self.data_input_dir = self.project_root / 'data' / 'input' / 'downloaded_files'
        self.data_input_dir.mkdir(parents=True, exist_ok=True)
        
        # Keep old session directory for backward compatibility
        self.session_dir = self.data_input_dir  # Point session_dir to new location
        
        self.downloaded_files: List[str] = []
        self.pending_downloads: Dict[str, asyncio.Future] = {}
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_browser()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_browser()
        
    async def start_browser(self):
        """Connect to user's existing Chrome browser."""
        self.playwright = await async_playwright().start()
        
        try:
            # Connect to user's Chrome browser via remote debugging
            self.browser = await self.playwright.chromium.connect_over_cdp("http://localhost:9222")
            logger.info("Connected to user's Chrome browser on port 9222")
            
            # Use the existing context (user's browser session)
            contexts = self.browser.contexts
            if contexts:
                self.context = contexts[0]
                logger.info(f"Using existing browser context with {len(self.context.pages)} pages")
            else:
                # Create new context if none exist
                self.context = await self.browser.new_context(accept_downloads=True)
                logger.info("Created new browser context")
            
            # Create a new page for our automation
            self.page = await self.context.new_page()
            
            # Set up download handling
            self.page.on('download', self._handle_download)
            
        except Exception as e:
            logger.error(f"Failed to connect to Chrome browser: {e}")
            logger.error("Make sure Chrome is running with: chrome --remote-debugging-port=9222")
            raise
    
    async def _handle_download(self, download):
        """Handle file downloads - save to Downloads then move to session directory."""
        try:
            filename = download.suggested_filename
            temp_path = self.downloads_folder / filename
            
            logger.info(f"📥 Download started: {filename}")
            
            # Save to user's Downloads folder first
            await download.save_as(temp_path)
            logger.info(f"✅ Download completed to: {temp_path}")
            
            # Move to session directory immediately
            session_path = self.session_dir / filename
            shutil.move(str(temp_path), str(session_path))
            logger.info(f"📁 Moved to session directory: {session_path}")
            
            self.downloaded_files.append(str(session_path))
            
        except Exception as e:
            logger.error(f"❌ Download/move failed: {e}")
    
    def move_existing_downloads_to_session(self):
        """Move any existing Holdings files from Downloads to session directory."""
        try:
            # Look for Holdings files from today
            today_pattern = "Holdings * September 3, 2025*.csv"
            existing_files = list(self.downloads_folder.glob(today_pattern))
            
            moved_count = 0
            for file_path in existing_files:
                try:
                    session_path = self.session_dir / file_path.name
                    shutil.move(str(file_path), str(session_path))
                    logger.info(f"📁 Moved existing file: {file_path.name}")
                    self.downloaded_files.append(str(session_path))
                    moved_count += 1
                except Exception as e:
                    logger.warning(f"Could not move {file_path.name}: {e}")
            
            if moved_count > 0:
                logger.info(f"📂 Moved {moved_count} existing files to session directory")
                
        except Exception as e:
            logger.error(f"Error moving existing downloads: {e}")
    
    async def close_browser(self):
        """Close browser resources."""
        if self.page:
            await self.page.close()
        # Don't close the browser or context since it's the user's Chrome
        if self.playwright:
            await self.playwright.stop()
    
    async def navigate_to_login(self):
        """Navigate to RBC login page."""
        url = "https://secure.royalbank.com/statics/login-service-ui/index#/full/signin?LANGUAGE=ENGLISH"
        logger.info(f"Navigating to login page: {url}")
        await self.page.goto(url)
        await asyncio.sleep(3)
        
    async def login(self, username: str, password: str):
        """Login to RBC Direct Investing."""
        logger.info("Starting login process")
        
        # Handle cookie dialog if present
        try:
            accept_cookies = await self.page.wait_for_selector("button:has-text('Accept All Cookies')", timeout=5000)
            if accept_cookies:
                await accept_cookies.click()
                await asyncio.sleep(2)
                logger.info("Accepted cookies")
        except:
            logger.info("No cookie dialog found")
        
        # Wait for and fill username - use correct selector
        username_selector = "#userName"
        try:
            await self.page.wait_for_selector(username_selector, timeout=15000)
            await self.page.fill(username_selector, username)
            logger.info("Filled username")
            
            # Press Enter to proceed to password page
            await self.page.keyboard.press("Enter")
            await asyncio.sleep(3)
            logger.info("Pressed Enter after username")
            
        except Exception as e:
            logger.error(f"Username step failed: {e}")
            raise
        
        # Wait for and fill password
        password_selector = "input[type='password']"
        try:
            await self.page.wait_for_selector(password_selector, timeout=15000)
            await self.page.fill(password_selector, password)
            logger.info("Filled password")
            
            # Press Enter to submit login
            await self.page.keyboard.press("Enter")
            await asyncio.sleep(5)
            logger.info("Pressed Enter after password")
            
        except Exception as e:
            logger.error(f"Password step failed: {e}")
            raise
        
        # Check if login was successful
        try:
            await self.page.wait_for_url("**/summary**", timeout=15000)
            logger.info("Login successful - reached summary page")
            return True
        except:
            current_url = self.page.url
            if "summary" in current_url or "account" in current_url or "overview" in current_url:
                logger.info(f"Login successful - URL indicates success: {current_url}")
                return True
            else:
                logger.error(f"Login may have failed - current URL: {current_url}")
                return False
    
    async def get_accounts(self):
        """Get list of investment accounts."""
        logger.info("Looking for investment accounts")
        
        # Wait for accounts to load
        await asyncio.sleep(3)
        
        # Look specifically for RBC Direct Investing links
        accounts = []
        try:
            # Find all links with "RBC Direct Investing" text (but not Practice Account)
            rbc_links = await self.page.query_selector_all("a:has-text('RBC Direct Investing')")
            
            for element in rbc_links:
                text = await element.text_content()
                href = await element.get_attribute('href')
                
                # Skip practice accounts and generic links - also handle URL-encoded format
                if text and href and 'Practice' not in text and ('AccountNo=' in href or 'AccountNo%3D' in href):
                    # Extract account number from URL (handle both encoded and decoded)
                    account_no = None
                    try:
                        if 'AccountNo=' in href:
                            account_no = href.split('AccountNo=')[1].split('&')[0]
                        elif 'AccountNo%3D' in href:
                            account_no = href.split('AccountNo%3D')[1].split('%26')[0]
                    except:
                        pass
                    
                    # Only include if we found an account number
                    if account_no:
                        accounts.append({
                            'text': text.strip(),
                            'href': href,
                            'element': element,
                            'account_number': account_no
                        })
            
        except Exception as e:
            logger.error(f"Error finding accounts: {e}")
        
        logger.info(f"Found {len(accounts)} accounts")
        return accounts
    
    async def export_holdings(self, account):
        """Export holdings for a specific account."""
        logger.info(f"Processing account: {account['text'][:50]}...")
        
        try:
            # Click on the account
            await account['element'].click()
            await asyncio.sleep(5)
            
            # Look for export button
            export_selectors = [
                "button:has-text('Export')",
                "a:has-text('Export')",
                "[data-testid*='export']",
                "button:has-text('Download')",
                ".export-button"
            ]
            
            exported = False
            for selector in export_selectors:
                try:
                    export_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if export_button:
                        await export_button.click()
                        await asyncio.sleep(3)
                        logger.info("Successfully clicked export button")
                        exported = True
                        break
                except:
                    continue
            
            if not exported:
                logger.warning("No export button found for holdings")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to export holdings: {e}")
            return False