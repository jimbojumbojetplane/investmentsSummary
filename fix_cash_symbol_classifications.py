#!/usr/bin/env python3
"""
Fix the CASH symbol holdings to be proper cash balances without symbols
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

def main():
    print("=== FIXING CASH SYMBOL CLASSIFICATIONS ===")
    
    # Load the original holdings file
    output_dir = Path('data/output')
    original_files = [f for f in output_dir.glob('holdings_detailed_*.json') 
                     if 'restructured' not in f.name and 'corrected' not in f.name and 'complete' not in f.name and 'final' not in f.name and 'correct' not in f.name and 'proper' not in f.name]
    
    if not original_files:
        print("No original holdings files found!")
        return
    
    original_file = max(original_files, key=lambda f: f.stat().st_mtime)
    print(f'Loading: {original_file.name}')
    
    with open(original_file, 'r') as f:
        original_data = json.load(f)
    
    # Calculate original total
    original_total = sum(h.get('Market_Value_CAD', 0) for h in original_data)
    print(f'Original total: ${original_total:,.2f}')
    
    # Separate CASH symbol holdings from other holdings
    cash_symbol_holdings = []
    other_holdings = []
    
    for h in original_data:
        if h.get('Symbol') == 'CASH':
            cash_symbol_holdings.append(h)
        else:
            other_holdings.append(h)
    
    print(f'CASH symbol holdings: {len(cash_symbol_holdings)}')
    print(f'Other holdings: {len(other_holdings)}')
    
    # Convert CASH symbol holdings to proper cash balances (no symbols)
    cash_balances = []
    for h in cash_symbol_holdings:
        # Determine currency based on account or amount
        # This is a heuristic - in reality we'd need to parse the CSV files properly
        currency = 'CAD'  # Default to CAD, could be enhanced
        
        cash_balance = {
            'Holding_ID': str(uuid.uuid4()),
            'Symbol': None,  # NO SYMBOL for cash balances
            'Name': 'Cash Balance',
            'Account': h.get('Account', 'Unknown'),
            'Asset_Type': f'Cash {currency}',  # Proper asset type
            'Sector': 'Cash & Equivalents',
            'Issuer_Region': 'Cash',
            'Listing_Country': None,
            'Industry': None,
            'Currency': currency,
            'Quantity': h.get('Market_Value_CAD', 0),
            'Last_Price': 1.0,
            'Market_Value': h.get('Market_Value_CAD', 0),
            'Market_Value_CAD': h.get('Market_Value_CAD', 0),
            'Book_Value': h.get('Market_Value_CAD', 0),
            'Book_Value_CAD': h.get('Market_Value_CAD', 0),
            'Unrealized_Gain_Loss': 0.0,
            'Unrealized_Gain_Loss_Pct': 0.0,
            'Classification_Source': 'RBC_CSV_Cash_Balance',
            'LLM_Reasoning': None,
            'Source_File': 'Original CSV Files',
            'Include_in_Exposure': True
        }
        cash_balances.append(cash_balance)
    
    # Combine other holdings with proper cash balances
    corrected_data = other_holdings + cash_balances
    
    # Calculate new total
    new_total = sum(h.get('Market_Value_CAD', 0) for h in corrected_data)
    
    print(f'\n=== CORRECTION COMPLETE ===')
    print(f'Original holdings: {len(original_data)} (${original_total:,.2f})')
    print(f'CASH symbols converted: {len(cash_symbol_holdings)}')
    print(f'Corrected holdings: {len(corrected_data)} (${new_total:,.2f})')
    
    # Verify against expected total
    expected_total = 3700000
    difference = abs(new_total - expected_total)
    if difference < 1000:  # Within $1000
        print(f'✅ Portfolio total matches expected $3.7M (within ${difference:,.2f})')
    else:
        print(f'❌ Portfolio total: ${new_total:,.2f}, Expected: ${expected_total:,.2f}, Difference: ${difference:,.2f}')
    
    # Save corrected file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    corrected_filename = f"holdings_detailed_fixed_{timestamp}.json"
    corrected_filepath = output_dir / corrected_filename
    
    with open(corrected_filepath, 'w') as f:
        json.dump(corrected_data, f, indent=2)
    
    print(f'\n=== CORRECTED FILE CREATED ===')
    print(f'File: {corrected_filename}')
    print(f'Total holdings: {len(corrected_data)}')
    print(f'Total value: ${new_total:,.2f}')
    
    # Show breakdown
    print(f'\n=== BREAKDOWN ===')
    other_total = sum(h.get('Market_Value_CAD', 0) for h in other_holdings)
    cash_total = sum(h.get('Market_Value_CAD', 0) for h in cash_balances)
    print(f'RBC Holdings (with symbols): ${other_total:,.2f}')
    print(f'Cash Balances (no symbols): ${cash_total:,.2f}')
    print(f'Total Portfolio: ${new_total:,.2f}')
    
    return corrected_filepath

if __name__ == "__main__":
    main()
