import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from .config import config
from .utils import sanitize_filename, save_data

logger = logging.getLogger(__name__)

class RBCAutomation:
    """Browser automation class for RBC Direct Investing."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Download tracking
        self.download_dir = Path(__file__).parent.parent / 'downloads' / 'session_files'
        self.download_dir.mkdir(parents=True, exist_ok=True)
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
        """Initialize and start the browser."""
        self.playwright = await async_playwright().start()
        
        # Force NON-INCOGNITO browser with persistent profile
        import tempfile
        import os
        
        # Create persistent user data directory
        user_data_dir = os.path.join(tempfile.gettempdir(), 'rbc_automation_profile')
        os.makedirs(user_data_dir, exist_ok=True)
        
        self.browser = await self.playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=config.browser_config['headless'],
            accept_downloads=True
            # downloads_path is NOT a valid parameter here - this was the bug!
        )
        
        # For persistent context, browser IS the context
        self.context = self.browser
        
        # Get the existing page or create a new one
        pages = self.browser.pages
        if pages:
            self.page = pages[0]  # Use existing page
        else:
            self.page = await self.browser.new_page()  # Create new page
        
        await self.context.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Set up download event handler
        self.page.on('download', self._handle_download)
        
        self.page.set_default_timeout(config.browser_config['timeout'])
        
        logger.info("Browser started successfully with download tracking")
        
    async def close_browser(self):
        """Close browser and cleanup resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        logger.info("Browser closed successfully")
    
    async def _handle_download(self, download):
        """Handle download events and save files to our directory."""
        try:
            # Log ALL download information
            logger.info(f"🔍 DOWNLOAD DETECTED:")
            logger.info(f"   Suggested filename: {download.suggested_filename}")
            logger.info(f"   Download URL: {download.url}")
            
            # Get the default download path FIRST
            default_path = await download.path()
            logger.info(f"   Default download path: {default_path}")
            
            # Generate filename with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            suggested_filename = download.suggested_filename
            filename = f"{timestamp}_{suggested_filename}"
            
            # Save to our download directory
            file_path = self.download_dir / filename
            await download.save_as(str(file_path))
            
            self.downloaded_files.append(str(file_path))
            logger.info(f"✅ Download saved to OUR directory: {file_path}")
            logger.info(f"   File size: {file_path.stat().st_size} bytes")
            
            # ALSO log where it would have gone by default
            if default_path:
                logger.info(f"   Original location would have been: {default_path}")
            
            # Mark any pending downloads as complete
            if suggested_filename in self.pending_downloads:
                self.pending_downloads[suggested_filename].set_result(str(file_path))
                del self.pending_downloads[suggested_filename]
                
        except Exception as e:
            logger.error(f"Download handler error: {e}")
            logger.error(f"   This might tell us where the file actually went")
    
    async def _wait_for_download(self, expected_filename_pattern: str = "", timeout: int = 15) -> str:
        """Wait for a download to complete and return the file path."""
        try:
            # Create a future for this download
            download_future = asyncio.Future()
            self.pending_downloads[expected_filename_pattern] = download_future
            
            # Wait for the download to complete
            file_path = await asyncio.wait_for(download_future, timeout=timeout)
            return file_path
            
        except asyncio.TimeoutError:
            logger.warning(f"Download timeout after {timeout} seconds")
            return ""
        except Exception as e:
            logger.error(f"Download wait error: {e}")
            return ""
    
    def get_downloaded_files(self) -> List[str]:
        """Return list of all downloaded files in this session."""
        return self.downloaded_files.copy()
        
    async def login(self) -> bool:
        """Login to RBC Direct Investing."""
        try:
            logger.info("Navigating to RBC login page")
            await self.page.goto(config.login_url)
            
            await self.page.wait_for_load_state('networkidle')
            
            # Add delay for page to fully render
            await asyncio.sleep(3)
            
            # Take a screenshot to see what we're working with
            await self.page.screenshot(path="page_loaded.png", full_page=True)
            
            # Get all input elements on the page for debugging
            all_inputs = await self.page.query_selector_all('input')
            logger.info(f"Found {len(all_inputs)} input elements on page")
            
            for i, input_element in enumerate(all_inputs):
                try:
                    input_id = await input_element.get_attribute('id')
                    input_name = await input_element.get_attribute('name')
                    input_type = await input_element.get_attribute('type')
                    input_placeholder = await input_element.get_attribute('placeholder')
                    logger.info(f"Input {i}: id='{input_id}', name='{input_name}', type='{input_type}', placeholder='{input_placeholder}'")
                except:
                    pass
            
            # Wait for login form to load - try multiple selectors
            try:
                await self.page.wait_for_selector('input[id="K1"], input[name="K1"], input[name="username"], input[type="text"]', timeout=5000)
            except Exception as e:
                logger.warning(f"Primary selectors not found: {e}")
                # Try waiting for any input field
                await self.page.wait_for_selector('input', timeout=10000)
            
            logger.info("Filling login credentials")
            # Try multiple possible selectors for RBC login form based on discovered fields
            username_selectors = [
                'input[id="userName"]',
                'input[id="K1"]',
                'input[name="K1"]',
                'input[data-cy="username"]',
                'input[name="username"]',
                'input[placeholder*="username" i]',
                'input[placeholder*="card" i]',
                'input[type="text"]:first-of-type'
            ]
            
            password_selectors = [
                'input[id="password"]',
                'input[id="Q1"]',
                'input[name="Q1"]',
                'input[data-cy="password"]',
                'input[type="password"]',
                'input[name="password"]',
                'input[placeholder*="password" i]'
            ]
            
            # Fill username
            username_filled = False
            for selector in username_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        # Click to focus and ensure element is interactive
                        await element.click()
                        await asyncio.sleep(0.5)
                        await element.fill(config.username)
                        logger.info(f"Username filled using selector: {selector}")
                        username_filled = True
                        break
                except Exception as e:
                    logger.debug(f"Failed to fill username with {selector}: {e}")
                    continue
            
            if not username_filled:
                logger.error("Could not find username field")
                await self.page.screenshot(path="debug_no_username.png")
                return False
            
            # After filling username, press Enter or click continue to proceed to password step
            username_element = await self.page.query_selector('input[id="userName"]')
            if username_element:
                await username_element.press('Enter')
                logger.info("Pressed Enter after username entry")
                
            # Wait for page to transition and password field to appear
            await asyncio.sleep(2)
            
            # Look for Continue or Next button and click it
            continue_buttons = [
                'button:has-text("Continue")',
                'button:has-text("Next")',  
                'input[type="submit"]',
                'button[type="submit"]',
                '[data-automation="continue"]'
            ]
            
            for button_selector in continue_buttons:
                try:
                    button = await self.page.query_selector(button_selector)
                    if button and await button.is_visible():
                        await button.click()
                        logger.info(f"Clicked continue button: {button_selector}")
                        break
                except:
                    continue
            
            # Wait for password page to load
            await asyncio.sleep(3)
            
            # Re-scan for inputs after username entry
            all_inputs_after = await self.page.query_selector_all('input')
            logger.info(f"Found {len(all_inputs_after)} input elements after username entry")
            
            # Take another screenshot to see the password page
            await self.page.screenshot(path="password_page.png", full_page=True)
            
            # Fill password
            password_filled = False
            for selector in password_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        # Check if element is visible
                        is_visible = await element.is_visible()
                        if is_visible:
                            await element.click()
                            await asyncio.sleep(0.5)
                            await element.fill(config.password)
                            logger.info(f"Password filled using selector: {selector}")
                            password_filled = True
                            break
                        else:
                            logger.debug(f"Password field {selector} exists but not visible")
                except Exception as e:
                    logger.debug(f"Failed to fill password with {selector}: {e}")
                    continue
            
            if not password_filled:
                logger.error("Could not find password field")
                await self.page.screenshot(path="debug_no_password.png")
                return False
            
            logger.info("Submitting login form")
            # Try multiple possible submit button selectors
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Sign In")',
                'button:has-text("Continue")',
                'button:has-text("Submit")',
                '[data-cy="submit"]',
                '.submit-button'
            ]
            
            submitted = False
            for selector in submit_selectors:
                try:
                    submit_button = await self.page.query_selector(selector)
                    if submit_button and await submit_button.is_visible():
                        await submit_button.click()
                        logger.info(f"Clicked submit button: {selector}")
                        submitted = True
                        break
                except:
                    continue
            
            if not submitted:
                # Try pressing Enter on password field as fallback
                password_element = await self.page.query_selector('input[id="password"]')
                if password_element:
                    await password_element.press('Enter')
                    logger.info("Pressed Enter on password field to submit")
            
            # Wait for navigation after login - give more time for processing
            try:
                await asyncio.sleep(5)  # Give time for processing
                await self.page.wait_for_load_state('networkidle', timeout=30000)
            except Exception as e:
                logger.warning(f"Wait for navigation error: {e}")
            
            # Take a screenshot after login attempt
            await self.page.screenshot(path="after_login_attempt.png", full_page=True)
            
            # Check current URL and page content
            current_url = self.page.url.lower()
            logger.info(f"Current URL after login attempt: {current_url}")
            
            # Check for error messages on the page
            error_selectors = [
                '.error-message', 
                '.alert-danger', 
                '[data-error]',
                'div:has-text("invalid")',
                'div:has-text("incorrect")',
                'div:has-text("error")'
            ]
            
            for selector in error_selectors:
                try:
                    error_element = await self.page.query_selector(selector)
                    if error_element and await error_element.is_visible():
                        error_text = await error_element.inner_text()
                        logger.error(f"Login error found: {error_text}")
                        break
                except:
                    continue
            
            # Check for successful login by looking for various indicators
            if any(indicator in current_url for indicator in ['dashboard', 'accounts', 'portfolio', 'main', 'home', 'summary']):
                logger.info("Login successful - redirected to main area")
                return True
            elif 'signin' in current_url:
                logger.error(f"Login failed - still on signin page: {self.page.url}")
                return False  
            else:
                # Unknown page, let's check if we can find account-related elements
                account_indicators = [
                    'a:has-text("Accounts")',
                    'a:has-text("Portfolio")', 
                    'div:has-text("Balance")',
                    'nav[role="navigation"]'
                ]
                
                for selector in account_indicators:
                    try:
                        element = await self.page.query_selector(selector)
                        if element:
                            logger.info(f"Login appears successful - found account indicator: {selector}")
                            return True
                    except:
                        continue
                
                logger.error(f"Login status unclear - current URL: {self.page.url}")
                return False
                
        except Exception as e:
            logger.error(f"Login failed with error: {str(e)}")
            return False
            
    async def navigate_to_accounts(self) -> bool:
        """Navigate to the accounts/portfolio section."""
        try:
            logger.info("Navigating to accounts section")
            
            accounts_link = await self.page.query_selector('a[href*="accounts"]')
            if accounts_link:
                await accounts_link.click()
            else:
                await self.page.click('text="Accounts"')
                
            await self.page.wait_for_load_state('networkidle')
            
            logger.info("Successfully navigated to accounts section")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to accounts: {str(e)}")
            return False
            
    async def get_account_list(self) -> List[Dict]:
        """Get list of investment accounts."""
        try:
            logger.info("Retrieving account list")
            
            accounts = []
            
            account_elements = await self.page.query_selector_all('.account-item, .account-row, [data-account-number]')
            
            for element in account_elements:
                account_number = await element.get_attribute('data-account-number')
                if not account_number:
                    account_text = await element.inner_text()
                    account_number = account_text.split()[0] if account_text else 'Unknown'
                    
                account_name = await element.inner_text()
                
                accounts.append({
                    'number': account_number,
                    'name': account_name.strip(),
                    'element': element
                })
                
            logger.info(f"Found {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            logger.error(f"Failed to get account list: {str(e)}")
            return []
            
    async def download_holdings(self, account_number: str) -> str:
        """Download holdings data for a specific account with enhanced tracking."""
        try:
            logger.info(f"Downloading holdings for account {account_number}")
            
            # Navigate to holdings page (assuming we're already on the account)
            holdings_tab = await self.page.query_selector('text="Holdings"')
            if holdings_tab:
                await holdings_tab.click()
                await self.page.wait_for_load_state('networkidle')
            
            export_button = await self.page.query_selector('button:has-text("Export"), a:has-text("Export"), [data-export]')
            if export_button:
                logger.info("Found export button, initiating download...")
                
                # Click export and wait for download
                await export_button.click()
                
                # Wait for download with timeout
                await asyncio.sleep(3)  # Give time for download to start
                
                # Check if we captured a download
                if self.downloaded_files:
                    latest_file = self.downloaded_files[-1]
                    logger.info(f"✅ Holdings downloaded: {latest_file}")
                    return latest_file
                else:
                    logger.warning("No download captured via event handler")
                    return ""
            else:
                logger.warning("Export button not found, trying alternative method")
                return await self._scrape_holdings_data(account_number)
                
        except Exception as e:
            logger.error(f"Failed to download holdings for {account_number}: {str(e)}")
            return ""
            
    async def download_transactions(self, account_number: str, date_range: str = "90d") -> str:
        """Download transaction data for a specific account with enhanced tracking."""
        try:
            logger.info(f"Downloading transactions for account {account_number}")
            
            transactions_tab = await self.page.query_selector('a[href*="transactions"], text="Transactions"')
            if transactions_tab:
                await transactions_tab.click()
                await self.page.wait_for_load_state('networkidle')
            
            date_filter = await self.page.query_selector('select[name="dateRange"], [data-date-range]')
            if date_filter:
                await date_filter.select_option(value=date_range)
                await self.page.wait_for_load_state('networkidle')
            
            export_button = await self.page.query_selector('button:has-text("Export"), a:has-text("Export"), [data-export]')
            if export_button:
                logger.info("Found export button, initiating download...")
                
                # Click export and wait for download
                await export_button.click()
                
                # Wait for download with timeout
                await asyncio.sleep(3)  # Give time for download to start
                
                # Check if we captured a download
                if self.downloaded_files:
                    latest_file = self.downloaded_files[-1]
                    logger.info(f"✅ Transactions downloaded: {latest_file}")
                    return latest_file
                else:
                    logger.warning("No download captured via event handler")
                    return ""
            else:
                logger.warning("Export button not found, trying alternative method")
                return await self._scrape_transaction_data(account_number)
                
        except Exception as e:
            logger.error(f"Failed to download transactions for {account_number}: {str(e)}")
            return ""
            
    async def _scrape_holdings_data(self, account_number: str) -> str:
        """Scrape holdings data when export is not available."""
        try:
            logger.info(f"Scraping holdings data for account {account_number}")
            
            holdings_table = await self.page.query_selector('table.holdings, .holdings-table, [data-holdings]')
            if not holdings_table:
                logger.error("Holdings table not found")
                return ""
            
            rows = await holdings_table.query_selector_all('tr')
            holdings_data = []
            
            for row in rows:
                cells = await row.query_selector_all('td, th')
                row_data = []
                for cell in cells:
                    text = await cell.inner_text()
                    row_data.append(text.strip())
                holdings_data.append(row_data)
            
            filename = f"holdings_{account_number}_{sanitize_filename()}.csv"
            return save_data(holdings_data, filename)
            
        except Exception as e:
            logger.error(f"Failed to scrape holdings data: {str(e)}")
            return ""
            
    async def _scrape_transaction_data(self, account_number: str) -> str:
        """Scrape transaction data when export is not available."""
        try:
            logger.info(f"Scraping transaction data for account {account_number}")
            
            transactions_table = await self.page.query_selector('table.transactions, .transactions-table, [data-transactions]')
            if not transactions_table:
                logger.error("Transactions table not found")
                return ""
            
            rows = await transactions_table.query_selector_all('tr')
            transaction_data = []
            
            for row in rows:
                cells = await row.query_selector_all('td, th')
                row_data = []
                for cell in cells:
                    text = await cell.inner_text()
                    row_data.append(text.strip())
                transaction_data.append(row_data)
            
            filename = f"transactions_{account_number}_{sanitize_filename()}.csv"
            return save_data(transaction_data, filename)
            
        except Exception as e:
            logger.error(f"Failed to scrape transaction data: {str(e)}")
            return ""
            
    async def logout(self):
        """Logout from RBC Direct Investing."""
        try:
            logger.info("Logging out")
            
            logout_button = await self.page.query_selector('a:has-text("Logout"), button:has-text("Sign Out"), [data-logout]')
            if logout_button:
                await logout_button.click()
                await self.page.wait_for_load_state('networkidle')
                
            logger.info("Logout successful")
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            
    async def run_full_export(self) -> List[str]:
        """Run complete export process for all accounts."""
        downloaded_files = []
        
        try:
            if not await self.login():
                raise Exception("Login failed")
                
            if not await self.navigate_to_accounts():
                raise Exception("Failed to navigate to accounts")
                
            accounts = await self.get_account_list()
            if not accounts:
                raise Exception("No accounts found")
                
            for account in accounts:
                account_number = account['number']
                
                holdings_file = await self.download_holdings(account_number)
                if holdings_file:
                    downloaded_files.append(holdings_file)
                    
                transactions_file = await self.download_transactions(account_number)
                if transactions_file:
                    downloaded_files.append(transactions_file)
                    
            await self.logout()
            
        except Exception as e:
            logger.error(f"Full export failed: {str(e)}")
            raise
            
        return downloaded_files