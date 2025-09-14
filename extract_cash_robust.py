#!/usr/bin/env python3
"""
Extract cash balances from individual holdings files with robust parsing
"""

import json
import re
from pathlib import Path
import glob

def extract_cash_from_file(file_path):
    """Extract cash balances from a single holdings file"""
    print(f"\nAnalyzing: {Path(file_path).name}")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    lines = content.split('\n')
    cash_balances = []
    
    # Look for cash balance sections
    in_cash_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check if we're entering a cash balance section
        if ('Currency,Cash' in line or 
            'Cash Balance' in line or
            'Cash' in line and 'Investments' in line):
            in_cash_section = True
            continue
        
        # Skip empty lines and headers
        if not line or line.startswith('"') or 'Account:' in line or 'Balances as of' in line:
            continue
        
        # If we're in cash section, try to parse cash data
        if in_cash_section:
            # Look for lines that might contain cash balances
            if ',' in line and not line.startswith('Currency'):
                parts = [part.strip().strip('"') for part in line.split(',')]
                
                if len(parts) >= 4:
                    try:
                        currency = parts[0] if parts[0] else 'CAD'
                        cash_value = float(parts[1]) if parts[1] else 0
                        investments = float(parts[2]) if parts[2] else 0
                        total = float(parts[3]) if parts[3] else 0
                        
                        # Only include if there's actual cash
                        if cash_value > 0:
                            cash_balances.append({
                                'currency': currency,
                                'cash_value': cash_value,
                                'investments': investments,
                                'total': total,
                                'line_number': i + 1,
                                'type': 'Cash Balance'
                            })
                    except ValueError:
                        continue
        
        # Also look for individual cash entries (like CMR, MNY, etc.)
        if ',' in line and len(line.split(',')) >= 6:
            parts = [part.strip().strip('"') for part in line.split(',')]
            
            if len(parts) >= 6:
                symbol = parts[0] if parts[0] else ''
                name = parts[1] if len(parts) > 1 else ''
                
                # Check if this is a cash-related ETF
                is_cash_etf = (
                    'cash' in name.lower() or
                    'money market' in name.lower() or
                    symbol in ['CMR', 'MNY', 'CASH'] or
                    'purpose cash' in name.lower()
                )
                
                if is_cash_etf:
                    try:
                        quantity = float(parts[2]) if parts[2] else 0
                        last_price = float(parts[3]) if parts[3] else 0
                        currency = parts[4] if len(parts) > 4 else 'CAD'
                        market_value = float(parts[6]) if len(parts) > 6 and parts[6] else 0
                        
                        cash_balances.append({
                            'symbol': symbol,
                            'name': name,
                            'quantity': quantity,
                            'last_price': last_price,
                            'currency': currency,
                            'market_value': market_value,
                            'line_number': i + 1,
                            'type': 'Cash ETF'
                        })
                    except ValueError:
                        continue
    
    return cash_balances

def analyze_all_files():
    """Analyze all holdings files"""
    
    # Get all holdings CSV files
    holdings_files = glob.glob('data/input/downloaded_files/Holdings *.csv')
    
    print("="*100)
    print("CASH BALANCE EXTRACTION FROM INDIVIDUAL FILES")
    print("="*100)
    
    all_cash_balances = {}
    total_cad = 0
    total_usd = 0
    usd_to_cad_rate = 1.35  # Approximate exchange rate
    
    for file_path in holdings_files:
        file_name = Path(file_path).name
        account_match = file_name.split()[1]  # Extract account number from filename
        
        print(f"\n{'='*80}")
        print(f"ACCOUNT: {account_match}")
        print(f"FILE: {file_name}")
        print(f"{'='*80}")
        
        cash_balances = extract_cash_from_file(file_path)
        
        if not cash_balances:
            print("No cash balances found in this file")
            all_cash_balances[account_match] = {
                'cash_balances': [],
                'cad_total': 0,
                'usd_total': 0,
                'total_cad_value': 0
            }
            continue
        
        account_cad = 0
        account_usd = 0
        
        for i, cash in enumerate(cash_balances, 1):
            print(f"\nCash Entry {i} ({cash['type']}):")
            
            if cash['type'] == 'Cash Balance':
                print(f"  Currency: {cash['currency']}")
                print(f"  Cash Value: ${cash['cash_value']:,.2f}")
                print(f"  Investments: ${cash['investments']:,.2f}")
                print(f"  Total: ${cash['total']:,.2f}")
                print(f"  Line: {cash['line_number']}")
                
                if cash['currency'] == 'CAD':
                    account_cad += cash['cash_value']
                elif cash['currency'] == 'USD':
                    account_usd += cash['cash_value']
                    
            elif cash['type'] == 'Cash ETF':
                print(f"  Symbol: '{cash['symbol']}'")
                print(f"  Name: {cash['name']}")
                print(f"  Quantity: {cash['quantity']:,.2f}")
                print(f"  Last Price: ${cash['last_price']:,.2f}")
                print(f"  Currency: {cash['currency']}")
                print(f"  Market Value: ${cash['market_value']:,.2f}")
                print(f"  Line: {cash['line_number']}")
                
                if cash['currency'] == 'CAD':
                    account_cad += cash['market_value']
                elif cash['currency'] == 'USD':
                    account_usd += cash['market_value']
        
        usd_in_cad = account_usd * usd_to_cad_rate
        total_account_value = account_cad + usd_in_cad
        
        print(f"\n--- ACCOUNT {account_match} SUMMARY ---")
        print(f"CAD Cash: ${account_cad:,.2f}")
        print(f"USD Cash: ${account_usd:,.2f}")
        print(f"USD in CAD (rate {usd_to_cad_rate}): ${usd_in_cad:,.2f}")
        print(f"Total Account Cash: ${total_account_value:,.2f} CAD")
        
        all_cash_balances[account_match] = {
            'cash_balances': cash_balances,
            'cad_total': account_cad,
            'usd_total': account_usd,
            'total_cad_value': total_account_value
        }
        
        total_cad += account_cad
        total_usd += account_usd
    
    print(f"\n{'='*100}")
    print("TOTAL SUMMARY FROM ALL FILES")
    print(f"{'='*100}")
    
    total_usd_in_cad = total_usd * usd_to_cad_rate
    grand_total = total_cad + total_usd_in_cad
    
    print(f"Total CAD Cash: ${total_cad:,.2f}")
    print(f"Total USD Cash: ${total_usd:,.2f}")
    print(f"USD in CAD: ${total_usd_in_cad:,.2f}")
    print(f"GRAND TOTAL CASH: ${grand_total:,.2f} CAD")
    
    # Compare with consolidated file
    print(f"\n{'='*100}")
    print("COMPARISON WITH CONSOLIDATED FILE")
    print(f"{'='*100}")
    
    consolidated_file = "data/output/consolidated_holdings_RBC_only_20250913_115744.json"
    
    if Path(consolidated_file).exists():
        with open(consolidated_file, 'r') as f:
            consolidated_data = json.load(f)
        
        metadata = consolidated_data.get('metadata', {})
        consolidated_cash = metadata.get('cash_total_cad', 0)
        
        print(f"Individual Files Total: ${grand_total:,.2f} CAD")
        print(f"Consolidated File Claims: ${consolidated_cash:,.2f} CAD")
        
        difference = grand_total - consolidated_cash
        if abs(difference) < 1:
            print("✅ MATCH: Individual files match consolidated file")
        else:
            print(f"⚠️  DISCREPANCY: ${difference:,.2f} CAD difference")
            if difference > 0:
                print(f"   Individual files have ${difference:,.2f} MORE cash")
            else:
                print(f"   Consolidated file claims ${abs(difference):,.2f} MORE cash")
    
    # Show detailed breakdown by account
    print(f"\n{'='*100}")
    print("DETAILED ACCOUNT BREAKDOWN")
    print(f"{'='*100}")
    
    for account, data in all_cash_balances.items():
        if data['cash_balances']:
            print(f"\nAccount {account}:")
            print(f"  CAD: ${data['cad_total']:,.2f}")
            print(f"  USD: ${data['usd_total']:,.2f}")
            print(f"  Total: ${data['total_cad_value']:,.2f} CAD")
            print(f"  Cash entries: {len(data['cash_balances'])}")
        else:
            print(f"\nAccount {account}: No cash balances found")

if __name__ == "__main__":
    analyze_all_files()
