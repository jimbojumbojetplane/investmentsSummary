#!/usr/bin/env python3
"""
Investigate the source of the $30,838.04 missing amount
"""

import json
from pathlib import Path

def main():
    print("=== INVESTIGATING THE $30,838.04 MISSING AMOUNT ===")
    
    # Load the original holdings file
    output_dir = Path('data/output')
    original_files = [f for f in output_dir.glob('holdings_detailed_*.json') 
                     if 'restructured' not in f.name and 'corrected' not in f.name and 'complete' not in f.name and 'final' not in f.name and 'correct' not in f.name and 'proper' not in f.name and 'fixed' not in f.name]
    
    if not original_files:
        print("No original holdings files found!")
        return
    
    original_file = max(original_files, key=lambda f: f.stat().st_mtime)
    print(f'Analyzing: {original_file.name}')
    
    with open(original_file, 'r') as f:
        original_data = json.load(f)
    
    # Calculate original total
    original_total = sum(h.get('Market_Value_CAD', 0) for h in original_data)
    print(f'Original total: ${original_total:,.2f}')
    
    # Expected breakdown from user
    print(f'\n=== EXPECTED BREAKDOWN ===')
    print(f'RBC Holdings (less cash): ~$2,600,000')
    print(f'Cash balances: $283,676')
    print(f'Benefits: $1,090,332')
    print(f'Total Expected: $3,700,000')
    
    # What we actually have
    print(f'\n=== WHAT WE ACTUALLY HAVE ===')
    print(f'Original file total: ${original_total:,.2f}')
    print(f'Missing to reach $3.7M: ${3700000 - original_total:,.2f}')
    
    # Analyze what's in the original file
    print(f'\n=== DETAILED BREAKDOWN OF ORIGINAL FILE ===')
    
    # Check for benefits
    benefits_holdings = [h for h in original_data if 
                        'pension' in h.get('Name', '').lower() or 
                        'rrsp' in h.get('Name', '').lower() or
                        'benefit' in h.get('Name', '').lower()]
    
    benefits_total = sum(h.get('Market_Value_CAD', 0) for h in benefits_holdings)
    print(f'Benefits in original file: ${benefits_total:,.2f} ({len(benefits_holdings)} holdings)')
    for h in benefits_holdings:
        print(f'  - {h.get("Symbol", "No Symbol")} - {h.get("Name")} - ${h.get("Market_Value_CAD", 0):,.2f}')
    
    # Check for CASH symbols
    cash_symbols = [h for h in original_data if h.get('Symbol') == 'CASH']
    cash_symbols_total = sum(h.get('Market_Value_CAD', 0) for h in cash_symbols)
    print(f'CASH symbols in original file: ${cash_symbols_total:,.2f} ({len(cash_symbols)} holdings)')
    
    # Check for other holdings
    other_holdings = [h for h in original_data if h.get('Symbol') != 'CASH' and h not in benefits_holdings]
    other_total = sum(h.get('Market_Value_CAD', 0) for h in other_holdings)
    print(f'Other holdings: ${other_total:,.2f} ({len(other_holdings)} holdings)')
    
    # Verify the math
    calculated_total = benefits_total + cash_symbols_total + other_total
    print(f'\n=== VERIFICATION ===')
    print(f'Benefits: ${benefits_total:,.2f}')
    print(f'CASH symbols: ${cash_symbols_total:,.2f}')
    print(f'Other holdings: ${other_total:,.2f}')
    print(f'Calculated total: ${calculated_total:,.2f}')
    print(f'Original file total: ${original_total:,.2f}')
    print(f'Match: {abs(calculated_total - original_total) < 0.01}')
    
    # The real question: what should the benefits total be?
    print(f'\n=== BENEFITS ANALYSIS ===')
    print(f'Expected benefits total: $1,090,332')
    print(f'Actual benefits in file: ${benefits_total:,.2f}')
    print(f'Benefits difference: ${1090332 - benefits_total:,.2f}')
    
    # Check if the missing amount matches the benefits difference
    missing_amount = 3700000 - original_total
    benefits_difference = 1090332 - benefits_total
    print(f'Missing amount: ${missing_amount:,.2f}')
    print(f'Benefits difference: ${benefits_difference:,.2f}')
    
    if abs(missing_amount - benefits_difference) < 1000:
        print(f'✅ The missing amount matches the benefits difference!')
        print(f'This suggests the benefits data is incomplete in the original file.')
    else:
        print(f'❌ The missing amount does not match the benefits difference.')
        print(f'There might be other missing data or the benefits total is wrong.')

if __name__ == "__main__":
    main()
