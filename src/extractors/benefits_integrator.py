#!/usr/bin/env python3
"""
Benefits Holdings Integrator
Integrates Bell Benefits portal data (DC pension plan and RRSP) as holdings entries 
into the combined holdings JSON file for dashboard integration
"""

import json
import os
import glob
from datetime import datetime
from pathlib import Path
import logging

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

# Configure logging
logger = logging.getLogger(__name__)

def find_latest_benefits_file():
    """Find the most recent benefits data file"""
    benefits_files = glob.glob(str(DATA_OUTPUT_DIR / "benefits_data_*.json"))
    if not benefits_files:
        logger.error(f"No benefits data files found in {DATA_OUTPUT_DIR}")
        return None
    
    # Sort by modification time, newest first
    benefits_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_file = benefits_files[0]
    logger.info(f"Found latest benefits file: {latest_file}")
    return latest_file

def find_latest_holdings_file():
    """Find the most recent combined holdings file"""
    holdings_files = glob.glob(str(DATA_OUTPUT_DIR / "holdings_combined_*.json"))
    
    if not holdings_files:
        logger.error(f"No combined holdings files found in {DATA_OUTPUT_DIR}")
        return None
    
    # Sort by modification time, newest first
    holdings_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_file = holdings_files[0]
    logger.info(f"Found latest holdings file: {latest_file}")
    return latest_file

def parse_dollar_amount(amount_str):
    """Parse dollar amount string to float"""
    if not amount_str:
        return 0.0
    
    try:
        # Remove $ and commas, convert to float
        clean_amount = amount_str.replace('$', '').replace(',', '')
        return float(clean_amount)
    except:
        return 0.0

def create_benefits_holdings_entries(benefits_data):
    """Convert benefits data into holdings format entries"""
    
    holdings_entries = []
    
    # Create DC Pension Plan entry
    if benefits_data.get('dc_pension_plan'):
        dc_amount = parse_dollar_amount(benefits_data['dc_pension_plan'])
        
        dc_entry = {
            "type": "current_holdings",
            "data": {
                "Account #": "BENEFITS01",  # Unique account identifier for benefits
                "Product": "DC Pension Plan",
                "Symbol": "DC-PENSION",
                "Name": "BELL DEFINED CONTRIBUTION PENSION PLAN",
                "Quantity": 1,  # Treat as single unit
                "Last Price": dc_amount,
                "Currency": "CAD",
                "Change $": 0,  # Benefits don't have daily changes
                "Change %": "N/A",
                "Total Book Cost": dc_amount,  # Assume book cost equals market value
                "Total Market Value": dc_amount,
                "Unrealized Gain/Loss $": 0,  # No gain/loss calculation for benefits
                "Unrealized Gain/Loss %": "N/A",
                "Average Cost": dc_amount,
                "Annual Dividend Amount $": None,
                "Dividend Ex Date": "",
                "Load Type": "",
                "RSP Eligibility": "",
                "Automatic Investment Plan": "",
                "DRIP Eligibility": "",
                "Coupon Rate": None,
                "Maturity Date": None,
                "Expiration Date": None,
                "Open Interest": None
            }
        }
        holdings_entries.append(dc_entry)
        logger.info(f"Created DC Pension Plan entry: ${dc_amount:,.2f}")
    
    # Create RRSP entry
    if benefits_data.get('rrsp'):
        rrsp_amount = parse_dollar_amount(benefits_data['rrsp'])
        
        rrsp_entry = {
            "type": "current_holdings",
            "data": {
                "Account #": "BENEFITS02",  # Unique account identifier for RRSP benefits
                "Product": "RRSP",
                "Symbol": "RRSP-BELL",
                "Name": "BELL REGISTERED RETIREMENT SAVINGS PLAN",
                "Quantity": 1,  # Treat as single unit
                "Last Price": rrsp_amount,
                "Currency": "CAD",
                "Change $": 0,  # Benefits don't have daily changes
                "Change %": "N/A",
                "Total Book Cost": rrsp_amount,  # Assume book cost equals market value
                "Total Market Value": rrsp_amount,
                "Unrealized Gain/Loss $": 0,  # No gain/loss calculation for benefits
                "Unrealized Gain/Loss %": "N/A",
                "Average Cost": rrsp_amount,
                "Annual Dividend Amount $": None,
                "Dividend Ex Date": "",
                "Load Type": "",
                "RSP Eligibility": "Yes",  # RRSP is RSP eligible
                "Automatic Investment Plan": "",
                "DRIP Eligibility": "",
                "Coupon Rate": None,
                "Maturity Date": None,
                "Expiration Date": None,
                "Open Interest": None
            }
        }
        holdings_entries.append(rrsp_entry)
        logger.info(f"Created RRSP entry: ${rrsp_amount:,.2f}")
    
    # Create Benefits Summary entry (similar to financial summary)
    if benefits_data.get('total_savings'):
        total_amount = parse_dollar_amount(benefits_data['total_savings'])
        
        summary_entry = {
            "type": "financial_summary",
            "data": {
                "Account #": "BENEFITS",
                "Currency": "CAD",
                "Cash": "0.00",
                "Investments": f"{total_amount:.2f}",
                "Total": f"{total_amount:.2f}",
                "Exchange Rate to CAD": "1",
                "Cash (CAD)": 0.0,
                "Investments (CAD)": total_amount,
                "Total (CAD)": total_amount
            }
        }
        holdings_entries.append(summary_entry)
        logger.info(f"Created Benefits Summary entry: ${total_amount:,.2f}")
    
    return holdings_entries

def integrate_benefits_into_holdings(benefits_file, holdings_file):
    """Integrate benefits data into holdings file"""
    
    try:
        # Load benefits data
        with open(benefits_file, 'r') as f:
            benefits_data = json.load(f)
        
        logger.info(f"Loaded benefits data from {benefits_file}")
        
        # Load existing holdings data
        with open(holdings_file, 'r') as f:
            holdings_data = json.load(f)
        
        logger.info(f"Loaded {len(holdings_data)} existing holdings entries")
        
        # Create benefits holdings entries
        benefits_entries = create_benefits_holdings_entries(benefits_data)
        
        # Remove any existing benefits entries (to avoid duplicates)
        filtered_holdings = []
        for entry in holdings_data:
            account_num = entry.get('data', {}).get('Account #', '')
            if not account_num.startswith('BENEFITS'):
                filtered_holdings.append(entry)
            else:
                logger.info(f"Removed existing benefits entry: {account_num}")
        
        # Add benefits entries at the beginning (so they appear first)
        integrated_holdings = benefits_entries + filtered_holdings
        
        # Create backup of original file
        backup_filename = holdings_file.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(backup_filename, 'w') as f:
            json.dump(holdings_data, f, indent=2)
        logger.info(f"Backup created: {backup_filename}")
        
        # Save integrated holdings back to original file
        with open(holdings_file, 'w') as f:
            json.dump(integrated_holdings, f, indent=2)
        
        logger.info(f"Updated holdings file: {holdings_file}")
        
        # Print summary
        total_entries = len(integrated_holdings)
        benefits_count = len(benefits_entries)
        holdings_count = len(filtered_holdings)
        
        print("✅ Benefits integration completed successfully!")
        print(f"📊 Integration summary:")
        print(f"  Benefits entries added: {benefits_count}")
        print(f"  Original holdings entries: {holdings_count}")
        print(f"  Total entries: {total_entries}")
        print(f"  Updated file: {holdings_file}")
        
        return holdings_file
        
    except Exception as e:
        logger.error(f"Error integrating benefits into holdings: {e}")
        return None

def integrate_benefits_data():
    """Main function to integrate benefits data into holdings"""
    print("🔗 Starting Benefits Holdings Integration")
    print("=" * 60)
    
    # Find latest files
    benefits_file = find_latest_benefits_file()
    if not benefits_file:
        print("❌ No benefits data file found")
        return False
    
    holdings_file = find_latest_holdings_file()
    if not holdings_file:
        print("❌ No holdings data file found")
        return False
    
    print(f"📄 Benefits file: {Path(benefits_file).name}")
    print(f"📄 Holdings file: {Path(holdings_file).name}")
    print()
    
    # Integrate benefits into holdings
    result = integrate_benefits_into_holdings(benefits_file, holdings_file)
    
    if result:
        print("🎉 Benefits successfully integrated into holdings!")
        print("💡 Benefits data will now appear in the RBC dashboard")
        return True
    else:
        print("❌ Benefits integration failed")
        return False

if __name__ == "__main__":
    success = integrate_benefits_data()
    exit(0 if success else 1)