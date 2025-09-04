#!/usr/bin/env python3
"""
Benefits Portal Data Extractor
Successfully extracts DC pension plan and RRSP amounts from Bell Benefits portal
Adapted for RBC_fiile_get project structure
"""

import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "data" / "benefits_extraction.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    logger.warning(f"No .env file found at {env_file}")

class BenefitsExtractor:
    """Extracts DC pension and RRSP amounts from Bell Benefits portal"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.base_url = "https://www.benefits-avantages.hroffice.com/account/login/MustAuthLogin?target=%2f#/"
        self.username = os.getenv('BENEFITS_USERNAME')
        self.password = os.getenv('BENEFITS_PASSWORD')
        
        if not self.username or not self.password:
            logger.error("Missing BENEFITS_USERNAME or BENEFITS_PASSWORD in environment variables")
            raise ValueError("Benefits credentials not configured in .env file")
    
    def create_driver(self):
        """Create Chrome driver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1200,800')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            logger.info("Chrome driver created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            return False
    
    def login(self):
        """Login to benefits portal"""
        try:
            logger.info("Navigating to benefits portal...")
            self.driver.get(self.base_url)
            time.sleep(5)
            
            # Click login link
            login_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[ng-click*='goToLogin']"))
            )
            login_link.click()
            time.sleep(3)
            
            # Fill username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='UserName']"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Fill password
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='Password']")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[id='signin-modal-submit']")
            login_button.click()
            
            # Wait for login to complete and page to load
            time.sleep(10)
            
            logger.info("Login completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def close_modal_if_present(self):
        """Close any modal popups that might be blocking the page"""
        try:
            # Look for close button in modal
            close_selectors = [
                ".modal-header .close",
                ".modal .close",
                "[ng-click*='close']",
                "button.close"
            ]
            
            for selector in close_selectors:
                try:
                    close_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if close_button.is_displayed():
                        close_button.click()
                        logger.info(f"Closed modal using selector: {selector}")
                        time.sleep(2)
                        break
                except:
                    continue
                    
            # Try pressing Escape key as backup
            from selenium.webdriver.common.keys import Keys
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(1)
            
        except Exception as e:
            logger.debug(f"Modal close attempt: {e}")
    
    def navigate_to_savings_section(self):
        """Navigate to the Savings & retirement section"""
        try:
            logger.info("Navigating to Savings & retirement section...")
            
            # Close any modal popups first
            self.close_modal_if_present()
            
            # Click on "Savings & retirement" in the top navigation
            # Use JavaScript to ensure we click the right element
            self.driver.execute_script("""
                var elements = document.querySelectorAll('a, button, span, div');
                for (var i = 0; i < elements.length; i++) {
                    var text = elements[i].textContent || elements[i].innerText || '';
                    if (text.includes('Savings & retirement')) {
                        elements[i].scrollIntoView();
                        elements[i].click();
                        break;
                    }
                }
            """)
            
            time.sleep(8)  # Wait for page to load
            
            # Close any new modals that appeared
            self.close_modal_if_present()
            
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to savings section: {e}")
            return False
    
    def parse_benefits_text(self, text_content):
        """Parse benefits text and extract amounts using proven logic"""
        
        lines = text_content.split('\n')
        
        total_savings = None
        dc_amount = None
        rrsp_amount = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for total savings
            if line == "Your total current balance is:":
                # Check next few lines for dollar amount
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('$'):
                        total_savings = next_line
                        logger.info(f"Found total savings: {total_savings}")
                        break
            
            # Look for DC pension
            elif line == "Your defined contribution (DC) pension plan":
                # Look ahead for "Your current balance is:"
                for j in range(i+1, min(i+15, len(lines))):
                    if lines[j].strip() == "Your current balance is:":
                        # Look for dollar amount after this
                        for k in range(j+1, min(j+5, len(lines))):
                            next_line = lines[k].strip()
                            if next_line.startswith('$'):
                                dc_amount = next_line
                                logger.info(f"Found DC Pension Plan: {dc_amount}")
                                break
                        break
            
            # Look for RRSP
            elif line == "Your RRSP":
                # Look ahead for "Your current balance is:"
                for j in range(i+1, min(i+15, len(lines))):
                    if lines[j].strip() == "Your current balance is:":
                        # Look for dollar amount after this
                        for k in range(j+1, min(j+5, len(lines))):
                            next_line = lines[k].strip()
                            if next_line.startswith('$'):
                                rrsp_amount = next_line
                                logger.info(f"Found RRSP: {rrsp_amount}")
                                break
                        break
        
        return total_savings, dc_amount, rrsp_amount
    
    def extract_balances_from_page(self):
        """Extract DC pension and RRSP balances from the current page"""
        try:
            logger.info("Extracting balance information from page...")
            
            # Extract all visible text
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Save page text for debugging
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            text_file = DATA_OUTPUT_DIR / f"benefits_page_text_{timestamp}.txt"
            with open(text_file, 'w') as f:
                f.write(body_text)
            logger.info(f"Page text saved: {text_file}")
            
            # Parse using proven logic
            total_savings, dc_amount, rrsp_amount = self.parse_benefits_text(body_text)
            
            return dc_amount, rrsp_amount, total_savings
            
        except Exception as e:
            logger.error(f"Error extracting balances: {e}")
            return None, None, None
    
    def extract_benefits_data(self):
        """Extract benefits data"""
        try:
            logger.info("Starting benefits data extraction...")
            
            # Navigate to savings section
            if not self.navigate_to_savings_section():
                logger.error("Failed to navigate to savings section")
                return None
            
            # Extract balances
            dc_amount, rrsp_amount, total_savings = self.extract_balances_from_page()
            
            extracted_data = {
                'dc_pension_plan': dc_amount,
                'rrsp': rrsp_amount,
                'total_savings': total_savings,
                'extraction_date': datetime.now().isoformat(),
                'source': 'benefits_portal_automation'
            }
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error in benefits extraction: {e}")
            return None
    
    def save_data(self, data, filename=None):
        """Save extracted data to JSON file in data/output directory"""
        if not data:
            logger.error("No data to save")
            return False
        
        if not filename:
            filename = f"benefits_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            filepath = DATA_OUTPUT_DIR / filename
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Benefits data saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def extract_benefits_complete(self):
        """Complete benefits extraction workflow"""
        try:
            # Create driver
            if not self.create_driver():
                return None
            
            # Login
            if not self.login():
                return None
            
            # Extract data
            data = self.extract_benefits_data()
            
            if data:
                # Save data
                filepath = self.save_data(data)
                if filepath:
                    logger.info("Benefits extraction completed successfully!")
                    return data, filepath
            
            logger.error("Benefits extraction failed")
            return None
            
        except Exception as e:
            logger.error(f"Error in complete extraction: {e}")
            return None
        
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function to run benefits extraction"""
    print("🏦 Starting Benefits Portal Data Extraction")
    print("=" * 60)
    
    # Check credentials
    username = os.getenv('BENEFITS_USERNAME')
    password = os.getenv('BENEFITS_PASSWORD')
    
    if not username or not password:
        print("❌ Missing benefits credentials in .env file")
        print("Please add to .env:")
        print("BENEFITS_USERNAME=your_benefits_username")
        print("BENEFITS_PASSWORD=your_benefits_password")
        return False
    
    print(f"✅ Found credentials for user: {username}")
    print()
    
    # Create extractor
    extractor = BenefitsExtractor(headless=True)
    
    # Extract data
    result = extractor.extract_benefits_complete()
    
    if result:
        data, filepath = result
        print("✅ Benefits extraction completed successfully!")
        print("📊 Extracted data:")
        print(f"  Total Savings: {data.get('total_savings', 'Not found')}")
        print(f"  DC Pension Plan: {data.get('dc_pension_plan', 'Not found')}")
        print(f"  RRSP: {data.get('rrsp', 'Not found')}")
        print(f"  Saved to: {filepath}")
        
        if data.get('dc_pension_plan') and data.get('rrsp'):
            print("🎉 Successfully extracted both benefit amounts!")
            
            # Calculate totals for verification
            try:
                dc_val = float(data['dc_pension_plan'].replace('$', '').replace(',', ''))
                rrsp_val = float(data['rrsp'].replace('$', '').replace(',', ''))
                calculated_total = dc_val + rrsp_val
                print(f"💰 DC + RRSP = ${calculated_total:,.2f}")
                
                if data.get('total_savings'):
                    total_val = float(data['total_savings'].replace('$', '').replace(',', ''))
                    print(f"📋 Portal total = ${total_val:,.2f}")
                    if abs(calculated_total - total_val) < 1:
                        print("✅ Totals match - extraction verified!")
                    else:
                        print("⚠️  Totals don't match - there may be additional accounts")
            except Exception as e:
                logger.debug(f"Total calculation error: {e}")
                
        return True
    else:
        print("❌ Benefits extraction failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)