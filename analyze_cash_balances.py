#!/usr/bin/env python3
"""
Analyze cash balances in the consolidated holdings data
"""

import json
import pandas as pd
from pathlib import Path

def analyze_cash_balances():
    """Analyze cash balances across all accounts"""
    
    # Load the most recent automated enriched data
    output_dir = Path('data/output')
    automated_files = list(output_dir.glob('consolidated_holdings_RBC_only_automated_enriched_*.json'))
    
    if not automated_files:
        print("No automated enriched files found!")
        return
    
    latest_file = max(automated_files, key=lambda f: f.stat().st_mtime)
    print(f"Analyzing cash balances from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    holdings_data = data.get('holdings', [])
    
    # Find all cash-related holdings
    cash_holdings = []
    
    for holding in holdings_data:
        symbol = holding.get('Symbol', '')
        name = holding.get('Name', '')
        asset_type = holding.get('Asset_Type', '')
        sector = holding.get('Sector', '')
        industry = holding.get('Industry', '')
        
        # Check if this is a cash-related holding
        is_cash = (
            'cash' in name.lower() or
            'money market' in name.lower() or
            symbol == 'CASH' or
            asset_type == 'Cash CAD' or
            asset_type == 'Cash USD' or
            sector == 'Money Market' or
            'cash' in asset_type.lower()
        )
        
        if is_cash:
            cash_holdings.append({
                'Account_Number': holding.get('Account_Number', ''),
                'Symbol': symbol,
                'Name': name,
                'Asset_Type': asset_type,
                'Sector': sector,
                'Industry': industry,
                'Market_Value_CAD': holding.get('Market_Value_CAD', 0),
                'Currency': holding.get('Currency', ''),
                'Source_File': holding.get('Source_File', '')
            })
    
    # Display results
    print(f"\n{'='*80}")
    print("CASH BALANCE ANALYSIS")
    print(f"{'='*80}")
    
    if not cash_holdings:
        print("No cash balances found in the data!")
        return
    
    print(f"Found {len(cash_holdings)} cash-related holdings:")
    print()
    
    total_cash_cad = 0
    account_summary = {}
    
    for i, cash in enumerate(cash_holdings, 1):
        print(f"{i}. Account: {cash['Account_Number']}")
        print(f"   Symbol: {cash['Symbol']}")
        print(f"   Name: {cash['Name']}")
        print(f"   Asset Type: {cash['Asset_Type']}")
        print(f"   Sector: {cash['Sector']}")
        print(f"   Industry: {cash['Industry']}")
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
    
    # Calculate percentage of total portfolio
    total_portfolio_value = sum(h.get('Market_Value_CAD', 0) for h in holdings_data)
    cash_percentage = (total_cash_cad / total_portfolio_value) * 100 if total_portfolio_value > 0 else 0
    
    print(f"Total Portfolio Value: ${total_portfolio_value:,.2f} CAD")
    print(f"Cash as % of Portfolio: {cash_percentage:.2f}%")
    
    # Check for any missing cash balances
    print(f"\n{'='*80}")
    print("VERIFICATION")
    print(f"{'='*80}")
    
    # Get all unique account numbers
    all_accounts = set(h.get('Account_Number', '') for h in holdings_data if h.get('Account_Number'))
    accounts_with_cash = set(cash['Account_Number'] for cash in cash_holdings)
    
    accounts_without_cash = all_accounts - accounts_with_cash
    
    if accounts_without_cash:
        print(f"Accounts WITHOUT cash balances: {sorted(accounts_without_cash)}")
    else:
        print("✅ All accounts have cash balances")
    
    print(f"\nAccounts with cash: {sorted(accounts_with_cash)}")
    print(f"Total accounts: {len(all_accounts)}")

if __name__ == "__main__":
    analyze_cash_balances()