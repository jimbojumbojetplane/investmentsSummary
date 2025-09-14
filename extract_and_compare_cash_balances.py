#!/usr/bin/env python3
"""
Extract cash balances from individual holdings files and compare to consolidated file
"""

import json
import pandas as pd
from pathlib import Path
import glob

def extract_cash_from_file(file_path):
    """Extract cash balances from a single holdings file"""
    print(f"\nAnalyzing: {Path(file_path).name}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    cash_balances = []
    
    for i, line in enumerate(lines):
        # Look for cash balance lines (usually contain "Cash Balance" or have empty symbol)
        if ('Cash Balance' in line or 
            (line.strip() and not line.startswith('"') and ',' in line)):
            
            # Try to parse CSV-like structure
            parts = line.strip().split(',')
            if len(parts) >= 8:  # Minimum expected columns
                try:
                    # Extract relevant fields
                    symbol = parts[0].strip('"') if parts[0].strip('"') else None
                    name = parts[1].strip('"') if len(parts) > 1 else ''
                    quantity = parts[2].strip('"') if len(parts) > 2 else '0'
                    last_price = parts[3].strip('"') if len(parts) > 3 else '0'
                    currency = parts[4].strip('"') if len(parts) > 4 else ''
                    book_value = parts[5].strip('"') if len(parts) > 5 else '0'
                    market_value = parts[6].strip('"') if len(parts) > 6 else '0'
                    
                    # Check if this looks like a cash balance
                    is_cash = (
                        symbol == '' or symbol is None or
                        'cash' in name.lower() or
                        'money market' in name.lower() or
                        symbol == 'CASH'
                    )
                    
                    if is_cash:
                        try:
                            market_value_num = float(market_value) if market_value else 0
                            book_value_num = float(book_value) if book_value else 0
                            quantity_num = float(quantity) if quantity else 0
                            last_price_num = float(last_price) if last_price else 0
                            
                            cash_balances.append({
                                'symbol': symbol,
                                'name': name,
                                'quantity': quantity_num,
                                'last_price': last_price_num,
                                'currency': currency,
                                'book_value': book_value_num,
                                'market_value': market_value_num,
                                'line_number': i + 1
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
            all_cash_balances[account_match] = []
            continue
        
        account_cad = 0
        account_usd = 0
        
        for i, cash in enumerate(cash_balances, 1):
            print(f"\nCash Balance {i}:")
            print(f"  Symbol: '{cash['symbol']}'")
            print(f"  Name: {cash['name']}")
            print(f"  Quantity: {cash['quantity']:,.2f}")
            print(f"  Last Price: ${cash['last_price']:,.2f}")
            print(f"  Currency: {cash['currency']}")
            print(f"  Book Value: ${cash['book_value']:,.2f}")
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
