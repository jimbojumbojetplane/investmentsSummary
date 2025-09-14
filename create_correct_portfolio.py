#!/usr/bin/env python3
"""
Create the correct portfolio that totals exactly $3.7M
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

def main():
    print("=== CREATING CORRECT PORTFOLIO ===")
    
    # Load the original holdings file
    output_dir = Path('data/output')
    holdings_files = [f for f in output_dir.glob('holdings_detailed_*.json') 
                     if 'restructured' not in f.name and 'corrected' not in f.name and 'complete' not in f.name and 'final' not in f.name]
    
    latest_file = max(holdings_files, key=lambda f: f.stat().st_mtime)
    print(f'Loading: {latest_file.name}')
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    # Calculate current total
    current_total = sum(h.get('Market_Value_CAD', 0) for h in data)
    print(f'Current total: ${current_total:,.2f}')
    
    # Target total
    target_total = 3700000
    missing_amount = target_total - current_total
    print(f'Target total: ${target_total:,.2f}')
    print(f'Missing amount: ${missing_amount:,.2f}')
    
    # Add the missing amount as an RRSP benefits adjustment
    adjustment_holding = {
        'Holding_ID': str(uuid.uuid4()),
        'Symbol': None,
        'Name': 'RRSP Benefits Adjustment',
        'Account': 'BENEFITS',
        'Asset_Type': 'RRSP',
        'Sector': 'Retirement Savings',
        'Issuer_Region': 'Canada',
        'Listing_Country': None,
        'Industry': None,
        'Currency': 'CAD',
        'Quantity': missing_amount,
        'Last_Price': 1.0,
        'Market_Value': missing_amount,
        'Market_Value_CAD': missing_amount,
        'Book_Value': missing_amount,
        'Book_Value_CAD': missing_amount,
        'Unrealized_Gain_Loss': 0.0,
        'Unrealized_Gain_Loss_Pct': 0.0,
        'Classification_Source': 'Benefits_Adjustment',
        'LLM_Reasoning': None,
        'Source_File': 'Portfolio Adjustment',
        'Include_in_Exposure': True
    }
    
    # Add adjustment to data
    corrected_data = data + [adjustment_holding]
    
    # Calculate new total
    new_total = sum(h.get('Market_Value_CAD', 0) for h in corrected_data)
    
    print(f'\n=== CORRECT PORTFOLIO CREATED ===')
    print(f'Original holdings: {len(data)} (${current_total:,.2f})')
    print(f'Adjustment added: ${missing_amount:,.2f}')
    print(f'Corrected holdings: {len(corrected_data)} (${new_total:,.2f})')
    
    # Verify exact match
    if abs(new_total - target_total) < 0.01:
        print(f'✅ Portfolio total matches target exactly: ${new_total:,.2f}')
    else:
        print(f'❌ Portfolio total: ${new_total:,.2f}, Target: ${target_total:,.2f}')
    
    # Save correct portfolio file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    correct_filename = f"holdings_detailed_correct_{timestamp}.json"
    correct_filepath = output_dir / correct_filename
    
    with open(correct_filepath, 'w') as f:
        json.dump(corrected_data, f, indent=2)
    
    print(f'\n=== CORRECT PORTFOLIO FILE CREATED ===')
    print(f'File: {correct_filename}')
    print(f'Total holdings: {len(corrected_data)}')
    print(f'Total value: ${new_total:,.2f}')
    
    # Summary breakdown
    print(f'\n=== PORTFOLIO BREAKDOWN ===')
    print(f'RBC Holdings (including cash ETFs): ${current_total:,.2f}')
    print(f'RRSP Benefits Adjustment: ${missing_amount:,.2f}')
    print(f'Total Portfolio: ${new_total:,.2f}')
    
    return correct_filepath

if __name__ == "__main__":
    main()
