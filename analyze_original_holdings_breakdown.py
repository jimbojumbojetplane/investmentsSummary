#!/usr/bin/env python3
"""
Analyze the original holdings file to understand what's already included
"""

import json
from pathlib import Path

def main():
    print("=== ANALYZING ORIGINAL HOLDINGS BREAKDOWN ===")
    
    # Load the original holdings file
    output_dir = Path('data/output')
    original_files = [f for f in output_dir.glob('holdings_detailed_*.json') 
                     if 'restructured' not in f.name and 'corrected' not in f.name and 'complete' not in f.name and 'final' not in f.name and 'correct' not in f.name and 'proper' not in f.name]
    
    if not original_files:
        print("No original holdings files found!")
        return
    
    original_file = max(original_files, key=lambda f: f.stat().st_mtime)
    print(f'Analyzing: {original_file.name}')
    
    with open(original_file, 'r') as f:
        original_data = json.load(f)
    
    print(f'Total holdings: {len(original_data)}')
    
    # Analyze by asset type
    asset_types = {}
    for h in original_data:
        asset_type = h.get('Asset_Type', 'Unknown')
        if asset_type not in asset_types:
            asset_types[asset_type] = {'count': 0, 'total': 0, 'holdings': []}
        asset_types[asset_type]['count'] += 1
        asset_types[asset_type]['total'] += h.get('Market_Value_CAD', 0)
        asset_types[asset_type]['holdings'].append(h)
    
    print(f'\nBreakdown by Asset Type:')
    for asset_type, info in sorted(asset_types.items(), key=lambda x: x[1]['total'], reverse=True):
        print(f'  {asset_type}: {info["count"]} holdings, ${info["total"]:,.2f}')
        
        # Show details for large holdings
        if info['total'] > 100000:
            for h in info['holdings']:
                print(f'    - {h.get("Symbol", "No Symbol")} - {h.get("Name")} - ${h.get("Market_Value_CAD", 0):,.2f}')
    
    # Check for benefits/pension holdings
    print(f'\nBenefits/Pension holdings:')
    benefits_related = [h for h in original_data if 
                       'pension' in h.get('Name', '').lower() or 
                       'rrsp' in h.get('Name', '').lower() or
                       'benefit' in h.get('Name', '').lower() or
                       h.get('Asset_Type', '').lower() in ['pension', 'rrsp', 'benefits']]
    
    if benefits_related:
        for h in benefits_related:
            print(f'  {h.get("Symbol", "No Symbol")} - {h.get("Name")} - {h.get("Asset_Type")} - ${h.get("Market_Value_CAD", 0):,.2f}')
    else:
        print('  No benefits/pension holdings found')
    
    # Check for CASH symbol holdings
    print(f'\nCASH symbol holdings:')
    cash_symbols = [h for h in original_data if h.get('Symbol') == 'CASH']
    if cash_symbols:
        for h in cash_symbols:
            print(f'  {h.get("Symbol")} - {h.get("Name")} - {h.get("Asset_Type")} - ${h.get("Market_Value_CAD", 0):,.2f}')
    else:
        print('  No CASH symbol holdings found')
    
    # Calculate expected breakdown
    print(f'\nExpected breakdown:')
    print(f'  RBC Holdings (less cash): ~$2,600,000')
    print(f'  Cash balances: $283,676')
    print(f'  Benefits: $1,090,332')
    print(f'  Total Expected: $3,700,000')
    
    current_total = sum(h.get('Market_Value_CAD', 0) for h in original_data)
    print(f'\nCurrent vs Expected:')
    print(f'  Current Total: ${current_total:,.2f}')
    print(f'  Expected Total: $3,700,000')
    print(f'  Difference: ${current_total - 3700000:,.2f}')
    
    if current_total > 3700000:
        print(f'  ❌ Current total is HIGHER than expected')
        print(f'  This suggests benefits data is already included')
    else:
        print(f'  ❌ Current total is LOWER than expected')
        print(f'  This suggests cash balances or benefits are missing')

if __name__ == "__main__":
    main()
