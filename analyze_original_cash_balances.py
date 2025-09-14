#!/usr/bin/env python3
"""
Analyze cash balances from the original consolidated file
"""

import json
import pandas as pd
from pathlib import Path

def analyze_original_cash_balances():
    """Analyze cash balances from the original consolidated file"""
    
    file_path = "/Users/jgf/coding/RBC_fiile_get/data/output/consolidated_holdings_RBC_only_20250913_115744.json"
    
    print(f"Analyzing cash balances from: consolidated_holdings_RBC_only_20250913_115744.json")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Check metadata first
    metadata = data.get('metadata', {})
    print(f"\n{'='*80}")
    print("METADATA SUMMARY")
    print(f"{'='*80}")
    print(f"Total Holdings: {metadata.get('total_holdings', 0)}")
    print(f"Total Cash Balances: {metadata.get('total_cash_balances', 0)}")
    print(f"Total Accounts: {metadata.get('total_accounts', 0)}")
    print(f"Holdings Total CAD: ${metadata.get('holdings_total_cad', 0):,.2f}")
    print(f"Cash Total CAD: ${metadata.get('cash_total_cad', 0):,.2f}")
    print(f"Combined Total CAD: ${metadata.get('combined_total_cad', 0):,.2f}")
    
    holdings_data = data.get('holdings', [])
    
    # Find all cash-related holdings
    cash_holdings = []
    
    for holding in holdings_data:
        symbol = holding.get('Symbol')
        name = holding.get('Name', '')
        account = holding.get('Account_Number', '')
        
        # Check if this is a cash-related holding
        is_cash = (
            symbol is None or  # Cash balances often have null symbols
            'cash' in name.lower() or
            'money market' in name.lower() or
            symbol == 'CASH' or
            'Cash Balance' in name
        )
        
        if is_cash:
            cash_holdings.append({
                'Account_Number': account,
                'Symbol': symbol,
                'Name': name,
                'Market_Value_CAD': holding.get('Market_Value_CAD', 0),
                'Currency': holding.get('Currency', ''),
                'Source_File': holding.get('Source_File', '')
            })
    
    # Display results
    print(f"\n{'='*80}")
    print("CASH BALANCE ANALYSIS")
    print(f"{'='*80}")
    
    if not cash_holdings:
        print("No explicit cash balance holdings found!")
        print("Checking for cash-related ETFs...")
        
        # Check for cash-related ETFs
        cash_etfs = []
        for holding in holdings_data:
            symbol = holding.get('Symbol', '')
            name = holding.get('Name', '')
            
            if ('cash' in name.lower() or 
                'money market' in name.lower() or 
                symbol in ['CMR', 'MNY', 'CASH']):
                cash_etfs.append({
                    'Account_Number': holding.get('Account_Number', ''),
                    'Symbol': symbol,
                    'Name': name,
                    'Market_Value_CAD': holding.get('Market_Value_CAD', 0),
                    'Currency': holding.get('Currency', ''),
                    'Source_File': holding.get('Source_File', '')
                })
        
        if cash_etfs:
            print(f"Found {len(cash_etfs)} cash-related ETFs:")
            print()
            
            total_cash_cad = 0
            account_summary = {}
            
            for i, cash in enumerate(cash_etfs, 1):
                print(f"{i}. Account: {cash['Account_Number']}")
                print(f"   Symbol: {cash['Symbol']}")
                print(f"   Name: {cash['Name']}")
                print(f"   Market Value: ${cash['Market_Value_CAD']:,.2f} CAD")
                print(f"   Currency: {cash['Currency']}")
                print(f"   Source File: {cash['Source_File']}")
                print()
                
                total_cash_cad += cash['Market_Value_CAD']
                
                # Track by account
                account = cash['Account_Number']
                if account not in account_summary:
                    account_summary[account] = 0
                account_summary[account] += cash['Market_Value_CAD']
            
            print(f"{'='*80}")
            print("CASH ETF SUMMARY")
            print(f"{'='*80}")
            
            print("By Account:")
            for account, amount in account_summary.items():
                print(f"  Account {account}: ${amount:,.2f} CAD")
            
            print(f"\nTotal Cash ETFs: ${total_cash_cad:,.2f} CAD")
            
            # Compare with metadata
            metadata_cash = metadata.get('cash_total_cad', 0)
            print(f"Metadata Cash Total: ${metadata_cash:,.2f} CAD")
            
            if abs(total_cash_cad - metadata_cash) > 1:
                print(f"⚠️  DISCREPANCY: ETF cash ({total_cash_cad:,.2f}) vs Metadata cash ({metadata_cash:,.2f})")
            else:
                print("✅ Cash totals match metadata")
        
        else:
            print("No cash-related ETFs found either!")
    else:
        print(f"Found {len(cash_holdings)} explicit cash balance holdings:")
        print()
        
        total_cash_cad = 0
        account_summary = {}
        
        for i, cash in enumerate(cash_holdings, 1):
            print(f"{i}. Account: {cash['Account_Number']}")
            print(f"   Symbol: {cash['Symbol']}")
            print(f"   Name: {cash['Name']}")
            print(f"   Market Value: ${cash['Market_Value_CAD']:,.2f} CAD")
            print(f"   Currency: {cash['Currency']}")
            print(f"   Source File: {cash['Source_File']}")
            print()
            
            total_cash_cad += cash['Market_Value_CAD']
            
            # Track by account
            account = cash['Account_Number']
            if account not in account_summary:
                account_summary[account] = 0
            account_summary[account] += cash['Market_Value_CAD']
        
        print(f"{'='*80}")
        print("CASH BALANCE SUMMARY")
        print(f"{'='*80}")
        
        print("By Account:")
        for account, amount in account_summary.items():
            print(f"  Account {account}: ${amount:,.2f} CAD")
        
        print(f"\nTotal Cash Balance: ${total_cash_cad:,.2f} CAD")
    
    # Check account summaries
    print(f"\n{'='*80}")
    print("ACCOUNT SUMMARIES")
    print(f"{'='*80}")
    
    account_summaries = data.get('account_summaries', [])
    for account in account_summaries:
        account_num = account.get('Account_Number', '')
        total_cad = account.get('Combined_Total_CAD', 0)
        print(f"Account {account_num}: ${total_cad:,.2f} CAD")

if __name__ == "__main__":
    analyze_original_cash_balances()
