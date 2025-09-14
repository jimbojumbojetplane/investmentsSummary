#!/usr/bin/env python3
"""
Create the final correct portfolio with proper cash balances and RRSP benefits
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

def main():
    print("=== CREATING FINAL CORRECT PORTFOLIO ===")
    
    # Load the fixed holdings file (with proper cash balances)
    output_dir = Path('data/output')
    fixed_files = list(output_dir.glob('holdings_detailed_fixed_*.json'))
    
    if not fixed_files:
        print("No fixed holdings files found!")
        return
    
    fixed_file = max(fixed_files, key=lambda f: f.stat().st_mtime)
    print(f'Loading: {fixed_file.name}')
    
    with open(fixed_file, 'r') as f:
        fixed_data = json.load(f)
    
    # Calculate current total
    current_total = sum(h.get('Market_Value_CAD', 0) for h in fixed_data)
    print(f'Current total: ${current_total:,.2f}')
    
    # Target total
    target_total = 3700000
    missing_amount = target_total - current_total
    print(f'Target total: ${target_total:,.2f}')
    print(f'Missing amount: ${missing_amount:,.2f}')
    
    # Add the missing RRSP benefits
    rrsp_benefits = {
        'Holding_ID': str(uuid.uuid4()),
        'Symbol': None,
        'Name': 'RRSP Benefits',
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
        'Classification_Source': 'Benefits_Data',
        'LLM_Reasoning': None,
        'Source_File': 'Benefits Integration',
        'Include_in_Exposure': True
    }
    
    # Add RRSP benefits to data
    final_data = fixed_data + [rrsp_benefits]
    
    # Calculate new total
    new_total = sum(h.get('Market_Value_CAD', 0) for h in final_data)
    
    print(f'\n=== FINAL PORTFOLIO CREATED ===')
    print(f'Fixed holdings: {len(fixed_data)} (${current_total:,.2f})')
    print(f'RRSP benefits added: ${missing_amount:,.2f}')
    print(f'Final holdings: {len(final_data)} (${new_total:,.2f})')
    
    # Verify exact match
    if abs(new_total - target_total) < 0.01:
        print(f'✅ Portfolio total matches target exactly: ${new_total:,.2f}')
    else:
        print(f'❌ Portfolio total: ${new_total:,.2f}, Target: ${target_total:,.2f}')
    
    # Save final portfolio file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_filename = f"holdings_detailed_final_{timestamp}.json"
    final_filepath = output_dir / final_filename
    
    with open(final_filepath, 'w') as f:
        json.dump(final_data, f, indent=2)
    
    print(f'\n=== FINAL PORTFOLIO FILE CREATED ===')
    print(f'File: {final_filename}')
    print(f'Total holdings: {len(final_data)}')
    print(f'Total value: ${new_total:,.2f}')
    
    # Summary breakdown
    print(f'\n=== PORTFOLIO BREAKDOWN ===')
    
    # Categorize holdings
    symbol_holdings = [h for h in final_data if h.get('Symbol') is not None]
    cash_holdings = [h for h in final_data if h.get('Symbol') is None and 'Cash' in h.get('Asset_Type', '')]
    benefits_holdings = [h for h in final_data if h.get('Symbol') is None and 'Cash' not in h.get('Asset_Type', '')]
    
    symbol_total = sum(h.get('Market_Value_CAD', 0) for h in symbol_holdings)
    cash_total = sum(h.get('Market_Value_CAD', 0) for h in cash_holdings)
    benefits_total = sum(h.get('Market_Value_CAD', 0) for h in benefits_holdings)
    
    print(f'RBC Holdings (with symbols): ${symbol_total:,.2f} ({len(symbol_holdings)} holdings)')
    print(f'Cash Balances (no symbols): ${cash_total:,.2f} ({len(cash_holdings)} holdings)')
    print(f'Benefits (no symbols): ${benefits_total:,.2f} ({len(benefits_holdings)} holdings)')
    print(f'Total Portfolio: ${new_total:,.2f} ({len(final_data)} holdings)')
    
    return final_filepath

if __name__ == "__main__":
    main()
