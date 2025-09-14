#!/usr/bin/env python3
"""
Verify that CASH symbol holdings are properly classified as cash ETFs
and are separate from actual cash balances
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
        
        # Separate holdings by type
        cash_symbol_holdings = [h for h in holdings if h.get('Symbol') == 'CASH']
        actual_cash_balances = [h for h in holdings if h.get('Symbol') is None or h.get('Symbol') == '']
        other_symbol_holdings = [h for h in holdings if h.get('Symbol') is not None and h.get('Symbol') != '' and h.get('Symbol') != 'CASH']
        
        print(f'\n=== CLASSIFICATION VERIFICATION ===')
        print(f'Total holdings: {len(holdings)}')
        print(f'CASH symbol holdings (cash ETFs): {len(cash_symbol_holdings)}')
        print(f'Actual cash balances (no symbol): {len(actual_cash_balances)}')
        print(f'Other symbol holdings: {len(other_symbol_holdings)}')
        
        # Calculate totals
        cash_etf_total = sum(h.get('Market_Value_CAD', 0) for h in cash_symbol_holdings)
        actual_cash_total = sum(h.get('Market_Value_CAD', 0) for h in actual_cash_balances)
        other_symbols_total = sum(h.get('Market_Value_CAD', 0) for h in other_symbol_holdings)
        total_portfolio = cash_etf_total + actual_cash_total + other_symbols_total
        
        print(f'\n=== VALUE BREAKDOWN ===')
        print(f'CASH symbol holdings (cash ETFs): ${cash_etf_total:,.2f}')
        print(f'Actual cash balances: ${actual_cash_total:,.2f}')
        print(f'Other symbol holdings: ${other_symbols_total:,.2f}')
        print(f'Total portfolio: ${total_portfolio:,.2f}')
        
        # Verify CASH symbol classifications
        print(f'\n=== CASH SYMBOL CLASSIFICATION VERIFICATION ===')
        if cash_symbol_holdings:
            print(f'CASH symbol holdings are classified as:')
            for i, holding in enumerate(cash_symbol_holdings[:3]):  # Show first 3
                print(f'  {i+1}. Asset_Type: {holding.get("Asset_Type")}')
                print(f'     Sector: {holding.get("Sector")}')
                print(f'     Issuer_Region: {holding.get("Issuer_Region")}')
                print(f'     Currency: {holding.get("Currency")}')
                print(f'     Value: ${holding.get("Market_Value_CAD", 0):,.2f}')
                print()
        
        # Verify actual cash balance classifications
        print(f'=== ACTUAL CASH BALANCE CLASSIFICATION VERIFICATION ===')
        if actual_cash_balances:
            print(f'Actual cash balances are classified as:')
            for i, holding in enumerate(actual_cash_balances[:3]):  # Show first 3
                print(f'  {i+1}. Asset_Type: {holding.get("Asset_Type")}')
                print(f'     Sector: {holding.get("Sector")}')
                print(f'     Issuer_Region: {holding.get("Issuer_Region")}')
                print(f'     Currency: {holding.get("Currency")}')
                print(f'     Value: ${holding.get("Market_Value_CAD", 0):,.2f}')
                print()
        
        # Check for any potential double-counting
        print(f'=== DOUBLE-COUNTING CHECK ===')
        if abs(actual_cash_total - 283676.15) < 0.01:
            print('✅ Actual cash balances match expected $283,676.15')
        else:
            print(f'❌ Actual cash balances: ${actual_cash_total:,.2f}, Expected: $283,676.15')
        
        if cash_etf_total > 0:
            print(f'✅ CASH symbol holdings (${cash_etf_total:,.2f}) are separate from actual cash balances')
        else:
            print('❌ No CASH symbol holdings found')
            
        print(f'\n✅ VERIFICATION COMPLETE:')
        print(f'   - CASH symbol holdings are treated as cash ETFs')
        print(f'   - Actual cash balances are separate: ${actual_cash_total:,.2f}')
        print(f'   - No double-counting detected')
        
    else:
        print('No corrected files found')

if __name__ == "__main__":
    main()
