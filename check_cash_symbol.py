#!/usr/bin/env python3
"""
Check where CASH symbol holdings are classified in the corrected data
"""

import json
from pathlib import Path

def main():
    # Load the corrected file
    output_dir = Path('data/output')
    corrected_files = list(output_dir.glob('holdings_detailed_restructured_corrected_*.json'))
    if corrected_files:
        latest_file = max(corrected_files, key=lambda f: f.stat().st_mtime)
        print(f'Loading: {latest_file.name}')
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        holdings = data['holdings']
        
        # Find CASH symbol holdings
        cash_symbol_holdings = [h for h in holdings if h.get('Symbol') == 'CASH']
        print(f'\nCASH symbol holdings found: {len(cash_symbol_holdings)}')
        
        for i, holding in enumerate(cash_symbol_holdings):
            print(f'\nCASH Holding #{i+1}:')
            print(f'  Symbol: {holding.get("Symbol")}')
            print(f'  Name: {holding.get("Name")}')
            print(f'  Asset_Type: {holding.get("Asset_Type")}')
            print(f'  Sector: {holding.get("Sector")}')
            print(f'  Issuer_Region: {holding.get("Issuer_Region")}')
            print(f'  Currency: {holding.get("Currency")}')
            print(f'  Market_Value_CAD: ${holding.get("Market_Value_CAD", 0):,.2f}')
            print(f'  Classification_Source: {holding.get("Classification_Source")}')
            
        # Also check for any other cash-related symbols
        print(f'\n=== ALL CASH-RELATED SYMBOLS ===')
        cash_related = [h for h in holdings if 'cash' in h.get('Name', '').lower() or 
                       h.get('Symbol') in ['CMR', 'MNY', 'CASH']]
        
        print(f'Total cash-related holdings: {len(cash_related)}')
        for holding in cash_related:
            print(f'  {holding.get("Symbol")} - {holding.get("Name")} - {holding.get("Asset_Type")} - ${holding.get("Market_Value_CAD", 0):,.2f}')
            
        # Check actual cash balances (no symbol)
        print(f'\n=== ACTUAL CASH BALANCES (NO SYMBOL) ===')
        cash_balances = [h for h in holdings if h.get('Symbol') is None or h.get('Symbol') == '']
        print(f'Cash balance holdings: {len(cash_balances)}')
        for holding in cash_balances:
            print(f'  {holding.get("Asset_Type")} - {holding.get("Currency")} - ${holding.get("Market_Value_CAD", 0):,.2f}')
            
    else:
        print('No corrected files found')

if __name__ == "__main__":
    main()
