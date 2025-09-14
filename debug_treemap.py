#!/usr/bin/env python3
"""
Debug the treemap creation to show the duplication issue
"""

import json
from collections import defaultdict

def classify_holding(holding):
    """Copy of the classify_holding function from create_portfolio_buckets.py"""
    symbol = holding.get('Symbol', '').upper()
    name = holding.get('Name', '')
    sector = holding.get('Sector', 'Unknown')
    industry = holding.get('Industry', 'Unknown')
    product = holding.get('Product', 'Unknown')
    account_number = holding.get('Account_Number', '')
    account_name = holding.get('Account_Name', '')

    name_lower = name.lower()
    sector_lower = sector.lower()
    industry_lower = industry.lower()
    product_lower = product.lower()

    # Real Estate first
    if any(keyword in name_lower for keyword in ['reit', 'real estate', 'property']) or symbol in ['ZRE', 'O', 'REXR', 'STAG', 'NWH.UN', 'PMZ.UN']:
        return 'Real Estate'

    # Fixed Income second
    if any(keyword in name_lower for keyword in ['bond', 'treasury', 'corporate bond', 'government bond', 'note', 'debenture']) or symbol in ['HYG', 'ICSH', '5565652']:
        return 'Fixed Income'

    # Cash Equivalents third
    if any(keyword in name_lower for keyword in ['money market', 'cash management', 'short term', 'ultra short', 'high interest savings']) or symbol in ['CMR', 'MNY', 'HISU.U']:
        return 'Cash Alternatives'

    # Everything else goes to Equity
    return 'Equity'

def debug_treemap_creation():
    # Load comprehensive data
    with open('data/output/comprehensive_holdings_with_etf_dividends_20250913_150846.json', 'r') as f:
        data = json.load(f)

    print('🚨 DEBUGGING TREEMAP CREATION - FINDING DUPLICATION ISSUES')
    print('=' * 80)

    # Apply correct grouping logic
    buckets = {
        'DC Pension': {'value': 0, 'count': 0, 'holdings': []},
        'RRSP': {'value': 0, 'count': 0, 'holdings': []},
        'Equity': {'value': 0, 'count': 0, 'holdings': []},
        'Fixed Income': {'value': 0, 'count': 0, 'holdings': []},
        'Cash & Cash Equivalents': {'value': 0, 'count': 0, 'holdings': []},
        'Real Estate': {'value': 0, 'count': 0, 'holdings': []}
    }
    
    # Process cash balances first (for DC Pension and RRSP)
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
            elif 'RSP' in account_name or 'RRSP' in account_name:
                buckets['RRSP']['value'] += value
                buckets['RRSP']['count'] += 1
                buckets['RRSP']['holdings'].append(cash)
        else:
            # RBC cash - goes to Cash & Cash Equivalents
            buckets['Cash & Cash Equivalents']['value'] += value
            buckets['Cash & Cash Equivalents']['count'] += 1
            buckets['Cash & Cash Equivalents']['holdings'].append(cash)
    
    # Process holdings with correct filtering logic
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
            continue
        
        # RULE 2: Fixed Income - Bonds and bond ETFs
        if any(keyword in name_lower for keyword in ['bond', 'treasury', 'corporate bond', 'government bond', 'note', 'debenture']) or symbol in ['HYG', 'ICSH', '5565652']:
            buckets['Fixed Income']['value'] += value
            buckets['Fixed Income']['count'] += 1
            buckets['Fixed Income']['holdings'].append(holding)
            continue
        
        # RULE 3: Cash Equivalents - Money market and cash equivalent ETFs
        if any(keyword in name_lower for keyword in ['money market', 'cash management', 'short term', 'ultra short', 'high interest savings']) or symbol in ['CMR', 'MNY', 'HISU.U']:
            buckets['Cash & Cash Equivalents']['value'] += value
            buckets['Cash & Cash Equivalents']['count'] += 1
            buckets['Cash & Cash Equivalents']['holdings'].append(holding)
            continue
        
        # RULE 4: Everything else goes to Equity
        buckets['Equity']['value'] += value
        buckets['Equity']['count'] += 1
        buckets['Equity']['holdings'].append(holding)

    print('📊 STEP 1: CREATING TREEMAP DATA')
    tree_data = []
    
    # Add DC Pension as its own group
    print('\n🔍 DC PENSION TREEMAP ENTRIES:')
    if buckets['DC Pension']['value'] > 0:
        # Add group level
        group_entry = {
            'Group': 'DC Pension',
            'SubGroup': 'DC Pension',
            'Holding': 'DC Pension Plan',
            'Value': buckets['DC Pension']['value'],
            'Level': 'Group'
        }
        tree_data.append(group_entry)
        print(f'   GROUP: {group_entry}')
        
        # Add individual holdings
        for holding in buckets['DC Pension']['holdings']:
            symbol = holding.get('Symbol', 'N/A')
            name = holding.get('Name', holding.get('Account_Name', ''))
            value = holding.get('Market_Value_CAD', holding.get('Amount_CAD', 0))
            
            holding_entry = {
                'Group': 'DC Pension',
                'SubGroup': 'DC Pension',
                'Holding': f"{symbol} - {name[:30]}",
                'Value': value,
                'Level': 'Holding'
            }
            tree_data.append(holding_entry)
            print(f'   HOLDING: {holding_entry}')
    
    # Add RRSP as its own group
    print('\n🔍 RRSP TREEMAP ENTRIES:')
    if buckets['RRSP']['value'] > 0:
        # Add group level
        group_entry = {
            'Group': 'RRSP',
            'SubGroup': 'RRSP',
            'Holding': 'RRSP Account',
            'Value': buckets['RRSP']['value'],
            'Level': 'Group'
        }
        tree_data.append(group_entry)
        print(f'   GROUP: {group_entry}')
        
        # Add individual holdings
        for holding in buckets['RRSP']['holdings']:
            symbol = holding.get('Symbol', 'N/A')
            name = holding.get('Name', holding.get('Account_Name', ''))
            value = holding.get('Market_Value_CAD', holding.get('Amount_CAD', 0))
            
            holding_entry = {
                'Group': 'RRSP',
                'SubGroup': 'RRSP',
                'Holding': f"{symbol} - {name[:30]}",
                'Value': value,
                'Level': 'Holding'
            }
            tree_data.append(holding_entry)
            print(f'   HOLDING: {holding_entry}')
    
    # Add Equity with sub-categories
    print('\n🔍 EQUITY TREEMAP ENTRIES:')
    equity_subcategories = defaultdict(lambda: {'value': 0, 'holdings': []})
    
    for holding in buckets['Equity']['holdings']:
        bucket = classify_holding(holding)
        value = holding.get('Market_Value_CAD', 0)
        
        # Map to equity sub-categories
        if bucket.startswith('Sector Equity -'):
            subcategory = bucket.replace('Sector Equity - ', '')
        elif bucket.startswith('Broad Market Equity'):
            subcategory = bucket.replace('Broad Market Equity - ', 'Broad Market ')
        elif bucket == 'Dividend Focused Equity':
            subcategory = 'Dividend Focused'
        elif bucket == 'Regional Equity':
            subcategory = 'Regional'
        else:
            subcategory = 'Other Equity'
        
        equity_subcategories[subcategory]['value'] += value
        equity_subcategories[subcategory]['holdings'].append(holding)
    
    # Add equity subcategories to tree data
    for subcategory, info in equity_subcategories.items():
        if info['value'] > 0:
            # Add subgroup level
            subgroup_entry = {
                'Group': 'Equity',
                'SubGroup': subcategory,
                'Holding': subcategory,
                'Value': info['value'],
                'Level': 'SubGroup'
            }
            tree_data.append(subgroup_entry)
            print(f'   SUBGROUP: {subgroup_entry}')
            
            # Add individual holdings
            for holding in info['holdings']:
                symbol = holding.get('Symbol', 'N/A')
                name = holding.get('Name', '')
                value = holding.get('Market_Value_CAD', 0)
                
                holding_entry = {
                    'Group': 'Equity',
                    'SubGroup': subcategory,
                    'Holding': f"{symbol} - {name[:30]}",
                    'Value': value,
                    'Level': 'Holding'
                }
                tree_data.append(holding_entry)
                print(f'   HOLDING: {holding_entry}')
    
    print(f'\n🎯 TOTAL TREEMAP ENTRIES: {len(tree_data)}')
    
    # Show the issue: multiple levels for the same data
    print('\n🚨 DUPLICATION ISSUE IDENTIFIED:')
    print('The treemap is creating:')
    print('1. GROUP level entries (e.g., "DC Pension Plan")')
    print('2. HOLDING level entries (e.g., individual holdings within DC Pension)')
    print('3. SUBGROUP level entries (e.g., "Technology" under Equity)')
    print('4. HOLDING level entries under subgroups')
    print('\nThis creates multiple boxes in the treemap instead of clean aggregated buckets!')

if __name__ == "__main__":
    debug_treemap_creation()
