#!/usr/bin/env python3
"""
Check the total value in the most recent original holdings_detailed file
"""

import json
from pathlib import Path

def main():
    # Find the most recent original holdings_detailed file (not restructured)
    output_dir = Path('data/output')
    holdings_files = [f for f in output_dir.glob('holdings_detailed_*.json') 
                     if 'restructured' not in f.name and 'corrected' not in f.name and 'complete' not in f.name and 'final' not in f.name]
    
    if holdings_files:
        latest_file = max(holdings_files, key=lambda f: f.stat().st_mtime)
        print(f'Most recent original holdings file: {latest_file.name}')
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        # Calculate total
        total_value = sum(h.get('Market_Value_CAD', 0) for h in data)
        
        print(f'Total holdings: {len(data)}')
        print(f'Total value: ${total_value:,.2f}')
        
        # Show breakdown by account
        print(f'\nBreakdown by account:')
        account_totals = {}
        for h in data:
            account = h.get('Account', 'Unknown')
            if account not in account_totals:
                account_totals[account] = 0
            account_totals[account] += h.get('Market_Value_CAD', 0)
        
        for account, total in sorted(account_totals.items()):
            print(f'  {account}: ${total:,.2f}')
            
        # Check cash holdings
        cash_holdings = [h for h in data if h.get('Symbol') is None or h.get('Symbol') == '']
        cash_total = sum(h.get('Market_Value_CAD', 0) for h in cash_holdings)
        
        print(f'\nCash holdings: {len(cash_holdings)} (${cash_total:,.2f})')
        
        # Expected breakdown
        print(f'\nExpected breakdown:')
        print(f'  RBC Holdings: ~$2,600,000')
        print(f'  Cash (part of RBC): $283,676')
        print(f'  Benefits: $1,090,332')
        print(f'  Total Expected: $3,700,000')
        
        print(f'\nCurrent vs Expected:')
        print(f'  Current Total: ${total_value:,.2f}')
        print(f'  Expected Total: $3,700,000')
        print(f'  Difference: ${total_value - 3700000:,.2f}')
        
    else:
        print('No original holdings_detailed files found')

if __name__ == "__main__":
    main()
