#!/usr/bin/env python3
"""
Debug the grouping logic to show exactly what's happening
"""

import json
from collections import defaultdict

def debug_grouping():
    # Load comprehensive data
    with open('data/output/comprehensive_holdings_with_etf_dividends_20250913_150846.json', 'r') as f:
        data = json.load(f)

    print('🚨 PROBLEM IDENTIFIED - DASHBOARD GROUPING LOGIC ISSUES')
    print('=' * 80)

    # Simulate the dashboard's apply_correct_grouping function
    buckets = {
        'DC Pension': {'value': 0, 'count': 0, 'holdings': []},
        'RRSP': {'value': 0, 'count': 0, 'holdings': []},
        'Equity': {'value': 0, 'count': 0, 'holdings': []},
        'Fixed Income': {'value': 0, 'count': 0, 'holdings': []},
        'Cash & Cash Equivalents': {'value': 0, 'count': 0, 'holdings': []},
        'Real Estate': {'value': 0, 'count': 0, 'holdings': []}
    }
    
    print('💰 STEP 1: PROCESSING CASH BALANCES')
    cash_balances = data.get('cash_balances', [])
    
    for cash in cash_balances:
        account_name = cash.get('Account_Name', 'Unknown')
        account_type = cash.get('Account_Type', 'Unknown')
        value = cash.get('Amount_CAD', 0)
        
        if account_type == 'Benefits':
            if 'DC Pension' in account_name or 'DC' in account_name:
                buckets['DC Pension']['value'] += value
                buckets['DC Pension']['count'] += 1
                buckets['DC Pension']['holdings'].append(cash)
                print(f'   ✅ DC Pension: {account_name} → ${value:,.0f}')
            elif 'RSP' in account_name or 'RRSP' in account_name:
                buckets['RRSP']['value'] += value
                buckets['RRSP']['count'] += 1
                buckets['RRSP']['holdings'].append(cash)
                print(f'   ✅ RRSP: {account_name} → ${value:,.0f}')
        else:
            # RBC cash - goes to Cash & Cash Equivalents
            buckets['Cash & Cash Equivalents']['value'] += value
            buckets['Cash & Cash Equivalents']['count'] += 1
            buckets['Cash & Cash Equivalents']['holdings'].append(cash)
            print(f'   ✅ RBC Cash: ${value:,.0f}')
    
    print()
    print('📊 STEP 2: PROCESSING HOLDINGS')
    holdings = data['holdings']
    
    for holding in holdings:
        symbol = holding.get('Symbol', '')
        name = holding.get('Name', '')
        value = holding.get('Market_Value_CAD', 0)
        name_lower = name.lower()
        
        # RULE 1: Real Estate - REITs and real estate ETFs (check first)
        if any(keyword in name_lower for keyword in ['reit', 'real estate', 'property']) or symbol in ['ZRE', 'O', 'REXR', 'STAG', 'NWH.UN', 'PMZ.UN']:
            buckets['Real Estate']['value'] += value
            buckets['Real Estate']['count'] += 1
            buckets['Real Estate']['holdings'].append(holding)
            print(f'   ✅ Real Estate: {symbol:6s} {name[:30]:30s} → ${value:8,.0f}')
            continue
        
        # RULE 2: Fixed Income - Bonds and bond ETFs
        if any(keyword in name_lower for keyword in ['bond', 'treasury', 'corporate bond', 'government bond', 'note', 'debenture']) or symbol in ['HYG', 'ICSH', '5565652']:
            buckets['Fixed Income']['value'] += value
            buckets['Fixed Income']['count'] += 1
            buckets['Fixed Income']['holdings'].append(holding)
            print(f'   ✅ Fixed Income: {symbol:6s} {name[:30]:30s} → ${value:8,.0f}')
            continue
        
        # RULE 3: Cash Equivalents - Money market and cash equivalent ETFs
        if any(keyword in name_lower for keyword in ['money market', 'cash management', 'short term', 'ultra short', 'high interest savings']) or symbol in ['CMR', 'MNY', 'HISU.U']:
            buckets['Cash & Cash Equivalents']['value'] += value
            buckets['Cash & Cash Equivalents']['count'] += 1
            buckets['Cash & Cash Equivalents']['holdings'].append(holding)
            print(f'   ✅ Cash Equivalents: {symbol:6s} {name[:30]:30s} → ${value:8,.0f}')
            continue
        
        # RULE 4: Everything else goes to Equity
        buckets['Equity']['value'] += value
        buckets['Equity']['count'] += 1
        buckets['Equity']['holdings'].append(holding)
        print(f'   ✅ Equity: {symbol:6s} {name[:30]:30s} → ${value:8,.0f}')
    
    print()
    print('🎯 FINAL BUCKET TOTALS:')
    total_value = sum(bucket['value'] for bucket in buckets.values())
    for bucket_name, bucket_info in buckets.items():
        if bucket_info['value'] > 0:
            percentage = (bucket_info['value'] / total_value * 100)
            print(f'{bucket_name:25s} {bucket_info["count"]:3d} holdings ${bucket_info["value"]:10,.0f} ({percentage:5.1f}%)')

    print(f'{"TOTAL PORTFOLIO":25s} ${total_value:10,.0f} (100.0%)')
    
    print()
    print('🔍 DETAILED HOLDINGS BY BUCKET:')
    for bucket_name, bucket_info in buckets.items():
        if bucket_info['holdings']:
            print(f'\n📦 {bucket_name.upper()}:')
            for holding in bucket_info['holdings']:
                symbol = holding.get('Symbol', 'N/A')
                name = holding.get('Name', holding.get('Account_Name', ''))
                value = holding.get('Market_Value_CAD', holding.get('Amount_CAD', 0))
                print(f'   {symbol:6s} {name[:50]:50s} ${value:8,.0f}')

if __name__ == "__main__":
    debug_grouping()
