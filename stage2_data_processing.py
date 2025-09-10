#!/usr/bin/env python3
"""
Stage 2: Data Processing and Dashboard Update
Processes CSV files from Stage 1, integrates benefits data, and updates the dashboard
This stage handles all data processing and GitHub updates
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Setup project paths
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT / "src"))

# Import our modules
from src.extractors.direct_csv_parser import process_csv_files
from src.extractors.benefits_extractor import BenefitsExtractor
from src.extractors.benefits_integrator import integrate_benefits_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "data" / "stage2_data_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_input_files():
    """Check if CSV files are available from Stage 1"""
    input_dir = PROJECT_ROOT / "data" / "input" / "downloaded_files"
    
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return False
    
    csv_files = list(input_dir.glob("*.csv"))
    
    if not csv_files:
        logger.error("No CSV files found in input directory")
        print("❌ No CSV files found in data/input/downloaded_files/")
        print("💡 Run Stage 1 first: python3 stage1_mcp_data_collection.py")
        return False
    
    logger.info(f"Found {len(csv_files)} CSV files in input directory")
    print(f"✅ Found {len(csv_files)} CSV files from Stage 1:")
    for csv_file in csv_files:
        print(f"   📄 {csv_file.name}")
    
    return True

def process_rbc_data():
    """Step 1: Process RBC CSV files into JSON"""
    print("\n📊 Step 1: Processing RBC Data")
    print("=" * 50)
    
    try:
        process_csv_files()
        print("✅ RBC data processing completed successfully")
        logger.info("RBC data processing completed")
        return True
    except Exception as e:
        print(f"❌ Error processing RBC data: {e}")
        logger.error(f"RBC data processing error: {e}")
        return False

def run_benefits_automation():
    """Step 2: Run Benefits portal data collection (optional)"""
    print("\n🏢 Step 2: Benefits Portal Data Collection (Optional)")
    print("=" * 50)
    
    try:
        # Check if benefits credentials are available
        if not os.getenv('BENEFITS_USERNAME') or not os.getenv('BENEFITS_PASSWORD'):
            print("⚠️  Benefits credentials not found in .env file")
            print("Skipping benefits extraction...")
            logger.warning("Benefits credentials not configured, skipping")
            return False
        
        print("🤖 Starting benefits data extraction...")
        extractor = BenefitsExtractor(headless=True)
        result = extractor.extract_benefits_complete()
        
        if result:
            data, filepath = result
            print("✅ Benefits data collection completed successfully")
            logger.info(f"Benefits extraction completed: {filepath}")
            return True
        else:
            print("❌ Benefits data collection failed")
            logger.error("Benefits extraction failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running benefits automation: {e}")
        logger.error(f"Benefits automation error: {e}")
        return False

def integrate_all_data():
    """Step 3: Integrate benefits data into holdings"""
    print("\n🔗 Step 3: Integrating All Data")
    print("=" * 50)
    
    try:
        success = integrate_benefits_data()
        if success:
            print("✅ Data integration completed successfully")
            logger.info("Data integration completed")
            return True
        else:
            print("❌ Data integration failed")
            logger.error("Data integration failed")
            return False
    except Exception as e:
        print(f"❌ Error integrating data: {e}")
        logger.error(f"Data integration error: {e}")
        return False

def push_to_github():
    """Step 4: Push updated data to GitHub"""
    print("\n📤 Step 4: Pushing to GitHub")
    print("=" * 50)
    
    try:
        # Check if there are changes to commit
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              cwd=PROJECT_ROOT, capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("ℹ️  No changes to commit - data is already up to date")
            return True
        
        # Add the updated holdings file and any relevant app changes
        subprocess.run(['git', 'add', 'data/output/holdings_combined_*.json', 'app.py', 'src/'], 
                      cwd=PROJECT_ROOT, check=True)
        
        # Create commit message
        commit_msg = f"""Update portfolio data - {datetime.now().strftime('%Y-%m-%d %H:%M')}

Automated update includes:
- RBC holdings via MCP automation (Stage 1)
- Data processing and integration (Stage 2)
- Bell Benefits integration (DC Pension + RRSP)
- Complete portfolio value: Updated via two-stage workflow

🤖 Generated with MCP + Cursor Agent (Stage 1) + Python Processing (Stage 2)

Co-Authored-By: MCP Automation <mcp@cursor.ai>"""
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_msg], 
                      cwd=PROJECT_ROOT, check=True)
        
        # Push to GitHub
        subprocess.run(['git', 'push'], cwd=PROJECT_ROOT, check=True)
        
        print("✅ Successfully pushed updates to GitHub")
        logger.info("GitHub push completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        logger.error(f"GitHub push failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error pushing to GitHub: {e}")
        logger.error(f"GitHub push error: {e}")
        return False

def show_dashboard_info():
    """Show information about accessing the updated dashboard"""
    print("\n🌐 Dashboard Access")
    print("=" * 50)
    
    # Check if we have the final data file
    data_dir = PROJECT_ROOT / "data" / "output"
    json_files = list(data_dir.glob("holdings_combined_*.json"))
    
    if json_files:
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        print(f"📄 Latest data file: {latest_file.name}")
        print(f"📅 Last updated: {datetime.fromtimestamp(latest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🚀 To view your updated portfolio:")
    print("   streamlit run app.py")
    print("\n💡 The dashboard will automatically load the latest data file")

def main():
    """Main function for Stage 2: Data Processing and Dashboard Update"""
    print("🚀 Stage 2: Data Processing and Dashboard Update")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if input files are available
    if not check_input_files():
        return False
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Process RBC Data
    if process_rbc_data():
        success_count += 1
    
    # Step 2: Benefits Data Collection (optional)
    benefits_success = run_benefits_automation()
    if benefits_success:
        success_count += 1
    
    # Step 3: Integrate Data (only if we have benefits data)
    integration_success = False
    if benefits_success and integrate_all_data():
        success_count += 1
        integration_success = True
    elif not benefits_success:
        # If no benefits, still count RBC processing as complete
        success_count += 1
        integration_success = True
        print("\n🔗 Step 3: Data Integration")
        print("=" * 50)
        print("⚠️  No benefits data to integrate, RBC data is ready for dashboard")
    
    # Step 4: Push to GitHub (if data processing was successful)
    if integration_success and push_to_github():
        success_count += 1
    
    print(f"\n📊 Stage 2 Summary")
    print("=" * 60)
    print(f"Completed: {success_count}/{total_steps} steps")
    
    if success_count >= 2:  # At least RBC processing and data integration
        print("✅ Stage 2 completed successfully!")
        print("🎯 Your portfolio data is ready for the dashboard")
        
        show_dashboard_info()
        
        return True
    else:
        print("❌ Stage 2 failed - insufficient steps completed")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    exit(0 if success else 1)
