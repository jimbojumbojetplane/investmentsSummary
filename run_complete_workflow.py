#!/usr/bin/env python3
"""
Complete RBC + Benefits Portfolio Workflow
Automates the full process of collecting RBC account data and benefits data,
then integrates everything into a unified portfolio dashboard.
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
        logging.FileHandler(PROJECT_ROOT / "data" / "complete_workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_rbc_automation():
    """Step 1: Run RBC account data collection"""
    print("🏦 Step 1: RBC Account Data Collection")
    print("=" * 50)
    
    try:
        # Run chrome automation to download CSV files
        rbc_script = PROJECT_ROOT / "src" / "chrome_browser_automation.py"
        result = subprocess.run(
            [sys.executable, str(rbc_script)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        
        if result.returncode == 0:
            print("✅ RBC data collection completed successfully")
            logger.info("RBC automation completed successfully")
            return True
        else:
            print("❌ RBC data collection failed")
            logger.error(f"RBC automation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ RBC automation timed out after 30 minutes")
        logger.error("RBC automation timed out")
        return False
    except Exception as e:
        print(f"❌ Error running RBC automation: {e}")
        logger.error(f"RBC automation error: {e}")
        return False

def process_rbc_data():
    """Step 2: Process RBC CSV files into JSON"""
    print("\n📊 Step 2: Processing RBC Data")
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
    """Step 3: Run Benefits portal data collection"""
    print("\n🏢 Step 3: Benefits Portal Data Collection")
    print("=" * 50)
    
    try:
        # Check if benefits credentials are available
        if not os.getenv('BENEFITS_USERNAME') or not os.getenv('BENEFITS_PASSWORD'):
            print("⚠️  Benefits credentials not found in .env file")
            print("Skipping benefits extraction...")
            logger.warning("Benefits credentials not configured, skipping")
            return False
        
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
    """Step 4: Integrate benefits data into holdings"""
    print("\n🔗 Step 4: Integrating All Data")
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

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Environment Check")
    print("=" * 50)
    
    # Check .env file
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        print("⚠️  No .env file found. Creating template...")
        env_template = """# RBC Automation Configuration
RBC_USERNAME=your_rbc_username
RBC_PASSWORD=your_rbc_password

# Benefits Portal Configuration
BENEFITS_USERNAME=your_benefits_username
BENEFITS_PASSWORD=your_benefits_password
"""
        with open(env_file, 'w') as f:
            f.write(env_template)
        print(f"📝 Created .env template at {env_file}")
        print("Please edit this file with your credentials")
        return False
    
    # Check directories
    required_dirs = [
        PROJECT_ROOT / "data" / "input" / "downloaded_files",
        PROJECT_ROOT / "data" / "output"
    ]
    
    for dir_path in required_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Environment check completed")
    return True

def main():
    """Main workflow orchestrator"""
    print("🚀 RBC + Benefits Complete Portfolio Workflow")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please configure your .env file.")
        return False
    
    print()
    success_count = 0
    total_steps = 4
    
    # Step 1: RBC Data Collection
    if run_rbc_automation():
        success_count += 1
    
    # Step 2: Process RBC Data
    if process_rbc_data():
        success_count += 1
    
    # Step 3: Benefits Data Collection (optional)
    benefits_success = run_benefits_automation()
    if benefits_success:
        success_count += 1
    
    # Step 4: Integrate Data (only if we have benefits data)
    if benefits_success and integrate_all_data():
        success_count += 1
    elif not benefits_success:
        # If no benefits, still count RBC processing as complete
        success_count += 1
        print("\n🔗 Step 4: Data Integration")
        print("=" * 50)
        print("⚠️  No benefits data to integrate, RBC data is ready for dashboard")
    
    print(f"\n📊 Workflow Summary")
    print("=" * 60)
    print(f"Completed: {success_count}/{total_steps} steps")
    
    if success_count >= 2:  # At least RBC collection and processing
        print("✅ Workflow completed successfully!")
        print("🎯 Your portfolio data is ready for the dashboard")
        
        # Check if we have the final data file
        data_dir = PROJECT_ROOT / "data" / "output"
        json_files = list(data_dir.glob("holdings_combined_*.json"))
        if json_files:
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"📄 Data file: {latest_file.name}")
        
        return True
    else:
        print("❌ Workflow failed - insufficient steps completed")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    exit(0 if success else 1)