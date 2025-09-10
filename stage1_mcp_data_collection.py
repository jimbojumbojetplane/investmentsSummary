#!/usr/bin/env python3
"""
Stage 1: MCP Data Collection
Downloads RBC holdings files using MCP automation and Cursor agent
This stage only handles data collection - no processing or dashboard updates
"""

import os
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Setup project paths
PROJECT_ROOT = Path(__file__).parent
DOWNLOAD_DIR = PROJECT_ROOT / "data" / "input" / "downloaded_files"
DOWNLOADS_FOLDER = Path.home() / "Downloads"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "data" / "stage1_mcp_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Stage1MCPDataCollector:
    """Stage 1: MCP-based RBC Holdings Data Collection"""
    
    def __init__(self):
        self.accounts = [
            {"number": "49813791", "type": "RRSP", "value": "$1,879,271.00"},
            {"number": "26674346", "type": "Direct Investing", "value": "$102,066.00"},
            {"number": "68000157", "type": "Direct Investing", "value": "$37,117.00"},
            {"number": "68551241", "type": "Direct Investing", "value": "No value shown"},
            {"number": "69539728", "type": "Direct Investing", "value": "$491,012.00"},
            {"number": "69549834", "type": "Direct Investing", "value": "$26,737.00"}
        ]
        
        self.base_url = "https://www1.royalbank.com/cgi-bin/rbaccess/rbunxcgi?F22=4WN600S&7ASERVER=N601LD&LANGUAGE=ENGLISH&7ASCRIPT=/WebUI/Holdings/HoldingsHome#/currency"
        self.home_url = "https://www1.royalbank.com/sgw3/secureapp/N600/ReactUI/?LANGUAGE=ENGLISH#/Home"
        self.downloaded_files = []
        
        # Ensure download directory exists
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    def generate_mcp_script(self) -> str:
        """Generate the complete MCP automation script"""
        
        script = f"""
// MCP RBC Holdings Download Script - Stage 1 Data Collection
// Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

async function downloadAllRBCHoldings() {{
    const accounts = {self.accounts};
    const baseUrl = "{self.base_url}";
    const homeUrl = "{self.home_url}";
    
    console.log("🚀 Stage 1: Starting RBC Holdings Download Process...");
    console.log(`📊 Total Accounts: ${{accounts.length}}`);
    
    let successCount = 0;
    let failedCount = 0;
    
    for (let i = 0; i < accounts.length; i++) {{
        const account = accounts[i];
        console.log(`\\n📋 Processing Account ${{i + 1}}/${{accounts.length}}: ${{account.number}} (${{account.type}})`);
        
        try {{
            // Navigate to account holdings page
            if (i > 0) {{ // Skip navigation for first account (already there)
                await navigate(baseUrl);
                await wait(5);
            }}
            
            // Take snapshot to verify account
            await snapshot();
            
            // Export holdings
            await click("Export button", "s2e232");
            await wait(5);
            
            console.log(`✅ Successfully exported holdings for Account ${{account.number}}`);
            successCount++;
            
        }} catch (error) {{
            console.error(`❌ Error processing Account ${{account.number}}:`, error);
            failedCount++;
            
            // Try to recover by going back to home page
            try {{
                await navigate(homeUrl);
                await wait(3);
            }} catch (recoveryError) {{
                console.error("❌ Recovery failed:", recoveryError);
                break;
            }}
        }}
    }}
    
    console.log("\\n🎉 Stage 1: RBC Holdings Download Process Complete!");
    console.log(`📊 Results: ${{successCount}} successful, ${{failedCount}} failed`);
    console.log("📁 Check your Downloads folder for the exported files");
    console.log("\\n⏭️  Next: Run Stage 2 to process these files");
    
    return {{
        success: successCount,
        failed: failedCount,
        total: accounts.length
    }};
}}

// Execute the function
downloadAllRBCHoldings();
"""
        return script
    
    def save_mcp_script(self, script: str) -> str:
        """Save the MCP script to a file for execution"""
        script_path = PROJECT_ROOT / "stage1_mcp_download_script.js"
        
        with open(script_path, 'w') as f:
            f.write(script)
        
        logger.info(f"MCP script saved to: {script_path}")
        return str(script_path)
    
    def wait_for_downloads(self, timeout: int = 300) -> List[Path]:
        """Wait for downloads to complete and return list of downloaded files"""
        logger.info("Waiting for downloads to complete...")
        
        start_time = time.time()
        downloaded_files = []
        
        while time.time() - start_time < timeout:
            # Look for new CSV files in Downloads folder
            csv_files = list(DOWNLOADS_FOLDER.glob("*.csv"))
            
            for csv_file in csv_files:
                if csv_file not in downloaded_files:
                    # Check if file is still being written (size changes)
                    initial_size = csv_file.stat().st_size
                    time.sleep(2)
                    final_size = csv_file.stat().st_size
                    
                    if initial_size == final_size and initial_size > 0:
                        downloaded_files.append(csv_file)
                        logger.info(f"Found new download: {csv_file.name}")
            
            if len(downloaded_files) >= len(self.accounts):
                break
                
            time.sleep(5)
        
        logger.info(f"Download wait completed. Found {len(downloaded_files)} files")
        return downloaded_files
    
    def organize_downloaded_files(self, downloaded_files: List[Path]) -> List[str]:
        """Move and organize downloaded files to the project directory"""
        organized_files = []
        
        for csv_file in downloaded_files:
            try:
                # Generate new filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{timestamp}_{csv_file.name}"
                target_path = DOWNLOAD_DIR / new_filename
                
                # Move file to project directory
                shutil.move(str(csv_file), str(target_path))
                organized_files.append(str(target_path))
                
                logger.info(f"Moved {csv_file.name} to {target_path}")
                
            except Exception as e:
                logger.error(f"Error moving file {csv_file.name}: {e}")
        
        return organized_files
    
    def run_data_collection(self) -> bool:
        """Run Stage 1: MCP data collection only"""
        try:
            logger.info("🚀 Stage 1: Starting MCP-based RBC Holdings Data Collection")
            
            # Step 1: Generate MCP script
            script = self.generate_mcp_script()
            script_path = self.save_mcp_script(script)
            
            # Step 2: Instructions for user
            print("\n" + "="*60)
            print("🤖 STAGE 1: MCP RBC DATA COLLECTION")
            print("="*60)
            print(f"📄 Script saved to: {script_path}")
            print("\n📋 NEXT STEPS:")
            print("1. Open Cursor with MCP Browser extension connected")
            print("2. Ensure you're logged into RBC Direct Investing")
            print("3. Copy and paste the script from the file above")
            print("4. Execute the script in Cursor")
            print("5. Wait for all downloads to complete")
            print("\n⏳ This process will wait for downloads to complete...")
            print("="*60)
            
            # Step 3: Wait for user to run the script
            input("\nPress Enter when you've completed the MCP script execution...")
            
            # Step 4: Wait for downloads
            downloaded_files = self.wait_for_downloads()
            
            if not downloaded_files:
                logger.error("No files were downloaded")
                return False
            
            # Step 5: Organize files
            organized_files = self.organize_downloaded_files(downloaded_files)
            
            if organized_files:
                logger.info(f"✅ Stage 1 completed successfully - organized {len(organized_files)} files")
                self.downloaded_files = organized_files
                
                # Show summary
                print(f"\n✅ Stage 1 Complete!")
                print(f"📁 Downloaded {len(organized_files)} files to data/input/downloaded_files/")
                for file_path in organized_files:
                    print(f"   📄 {Path(file_path).name}")
                
                print(f"\n⏭️  Next: Run Stage 2 to process these files")
                print("   python3 stage2_data_processing.py")
                
                return True
            else:
                logger.error("Failed to organize downloaded files")
                return False
                
        except Exception as e:
            logger.error(f"Stage 1 MCP automation failed: {e}")
            return False
    
    def get_downloaded_files(self) -> List[str]:
        """Return list of downloaded files"""
        return self.downloaded_files.copy()
    
    def verify_downloads(self) -> Dict[str, any]:
        """Verify that all expected files were downloaded"""
        verification = {
            "expected_accounts": len(self.accounts),
            "downloaded_files": len(self.downloaded_files),
            "missing_accounts": [],
            "success": False
        }
        
        # Check for each account
        for account in self.accounts:
            account_found = False
            for file_path in self.downloaded_files:
                if account["number"] in file_path:
                    account_found = True
                    break
            
            if not account_found:
                verification["missing_accounts"].append(account["number"])
        
        verification["success"] = len(verification["missing_accounts"]) == 0
        
        return verification

def main():
    """Main function for Stage 1: MCP Data Collection"""
    collector = Stage1MCPDataCollector()
    
    print("🚀 Stage 1: MCP RBC Holdings Data Collection")
    print("="*50)
    print("This stage only downloads files - no processing or dashboard updates")
    print()
    
    success = collector.run_data_collection()
    
    if success:
        files = collector.get_downloaded_files()
        verification = collector.verify_downloads()
        
        print(f"\n✅ Stage 1 completed successfully!")
        print(f"📁 Downloaded {len(files)} files:")
        for file_path in files:
            print(f"   📄 {Path(file_path).name}")
        
        if verification["success"]:
            print("✅ All expected accounts downloaded successfully")
        else:
            print(f"⚠️ Missing accounts: {verification['missing_accounts']}")
        
        print(f"\n⏭️  Ready for Stage 2: Data Processing")
        print("   Run: python3 stage2_data_processing.py")
        
        return True
    else:
        print("❌ Stage 1 failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
