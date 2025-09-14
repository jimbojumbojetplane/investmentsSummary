#!/usr/bin/env python3
"""
Analyze what's in the original holdings file to understand the breakdown
"""

import json
from pathlib import Path

def main():
    # Load the original holdings file
    output_dir = Path('data/output')
    holdings_files = [f for f in output_dir.glob('holdings_detailed_*.json') 
                     if 'restructured' not in f.name and 'corrected' not in f.name and 'complete' not in f.name and 'final' not in f.name]
    
    latest_file = max(holdings_files, key=lambda f: f.stat().st_mtime)
    print(f'Analyzing: {latest_file.name}')
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    print(f'Total holdings: {len(data)}')
    
    # Analyze by asset type
    asset_types = {}
    for h in data:
        asset_type = h.get('Asset_Type', 'Unknown')
        if asset_type not in asset_types:
            asset_types[asset_type] = {'count': 0, 'total': 0}
        asset_types[asset_type]['count'] += 1
        asset_types[asset_type]['total'] += h.get('Market_Value_CAD', 0)
    
    print(f'\nBreakdown by Asset Type:')
    for asset_type, info in sorted(asset_types.items(), key=lambda x: x[1]['total'], reverse=True):
        print(f'  {asset_type}: {info["count"]} holdings, ${info["total"]:,.2f}')
    
    # Check for cash-related holdings
    print(f'\nCash-related holdings:')
    cash_related = [h for h in data if 'cash' in h.get('Name', '').lower() or 
                   h.get('Asset_Type', '').lower() in ['cash', 'cash cad', 'cash usd'] or
                   h.get('Symbol') in ['CASH', 'CMR', 'MNY']]
    
    for h in cash_related:
        print(f'  {h.get("Symbol", "No Symbol")} - {h.get("Name")} - {h.get("Asset_Type")} - ${h.get("Market_Value_CAD", 0):,.2f}')
    
    # Check for benefits/pension holdings
    print(f'\nBenefits/Pension holdings:')
    benefits_related = [h for h in data if 'pension' in h.get('Name', '').lower() or 
                       'rrsp' in h.get('Name', '').lower() or
                       'benefit' in h.get('Name', '').lower() or
                       h.get('Asset_Type', '').lower() in ['pension', 'rrsp', 'benefits']]
    
    for h in benefits_related:
        print(f'  {h.get("Symbol", "No Symbol")} - {h.get("Name")} - {h.get("Asset_Type")} - ${h.get("Market_Value_CAD", 0):,.2f}')
    
    # Check accounts
    print(f'\nAccount breakdown:')
    accounts = {}
    for h in data:
        account = h.get('Account', 'Unknown')
        if account not in accounts:
            accounts[account] = {'count': 0, 'total': 0}
        accounts[account]['count'] += 1
        accounts[account]['total'] += h.get('Market_Value_CAD', 0)
    
    for account, info in sorted(accounts.items(), key=lambda x: x[1]['total'], reverse=True):
        print(f'  {account}: {info["count"]} holdings, ${info["total"]:,.2f}')
    
    # Total analysis
    total_value = sum(h.get('Market_Value_CAD', 0) for h in data)
    print(f'\nTotal Analysis:')
    print(f'  Current total: ${total_value:,.2f}')
    print(f'  Expected total: $3,700,000')
    print(f'  Difference: ${total_value - 3700000:,.2f}')
    
    if total_value > 3700000:
        print(f'  ❌ Current total is HIGHER than expected')
        print(f'  This suggests benefits data is already included')
    else:
        print(f'  ❌ Current total is LOWER than expected')
        print(f'  This suggests cash balances or benefits are missing')

if __name__ == "__main__":
    main()
