#!/usr/bin/env python3
"""
Analyze USD holdings by account to prepare for dashboard enhancement
"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_usd_holdings():
    """Analyze USD holdings breakdown by account"""
    
    # Load comprehensive data
    output_dir = Path('data/output')
    corrected_files = list(output_dir.glob('comprehensive_holdings_dividends_cad_corrected_*.json'))
    
    if not corrected_files:
        print("No corrected comprehensive holdings files found!")
        return
    
    latest_file = max(corrected_files, key=lambda f: f.stat().st_mtime)
    print(f"Analyzing: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    holdings = data['holdings']
    
    print("\n=== USD HOLDINGS ANALYSIS BY ACCOUNT ===")
    
    # Analyze by account
    account_data = defaultdict(lambda: {
        'total_cad': 0,
        'usd_cad': 0,
        'usd_original': 0,
        'holdings_count': 0,
        'usd_holdings_count': 0
    })
    
    for holding in holdings:
        account = holding.get('Account_Number', 'Unknown')
        currency = holding.get('Currency', 'CAD')
        market_value_cad = holding.get('Market_Value_CAD', 0)
        market_value_usd = holding.get('Market_Value', 0)  # Original USD value
        
        account_data[account]['total_cad'] += market_value_cad
        account_data[account]['holdings_count'] += 1
        
        if currency == 'USD':
            account_data[account]['usd_cad'] += market_value_cad
            account_data[account]['usd_original'] += market_value_usd
            account_data[account]['usd_holdings_count'] += 1
    
    # Add cash balances
    cash_balances = data.get('cash_balances', [])
    for cash in cash_balances:
        if cash.get('Account_Type') != 'Benefits':  # RBC cash only
            account = cash.get('Account_Number', 'Unknown')
            amount_cad = cash.get('Amount_CAD', 0)
            account_data[account]['total_cad'] += amount_cad
            # Cash is always CAD, no USD cash balances
    
    # Add benefits accounts
    for cash in cash_balances:
        if cash.get('Account_Type') == 'Benefits':
            account_name = cash.get('Account_Name', 'Unknown')
            amount_cad = cash.get('Amount_CAD', 0)
            account_data[account_name] = {
                'total_cad': amount_cad,
                'usd_cad': 0,
                'usd_original': 0,
                'holdings_count': 1,
                'usd_holdings_count': 0
            }
    
    # Calculate totals
    total_portfolio_cad = sum(acc['total_cad'] for acc in account_data.values())
    total_usd_cad = sum(acc['usd_cad'] for acc in account_data.values())
    total_usd_original = sum(acc['usd_original'] for acc in account_data.values())
    
    print(f"\nPORTFOLIO TOTALS:")
    print(f"Total Portfolio (CAD): ${total_portfolio_cad:,.2f}")
    print(f"USD Holdings (CAD): ${total_usd_cad:,.2f}")
    print(f"USD Holdings (Original USD): ${total_usd_original:,.2f}")
    print(f"USD Percentage: {(total_usd_cad / total_portfolio_cad * 100):.1f}%")
    
    print(f"\nACCOUNT BREAKDOWN:")
    print(f"{'Account':<25} {'Total CAD':<12} {'USD CAD':<12} {'USD %':<8} {'Holdings':<8} {'USD Count':<10}")
    print("-" * 85)
    
    # Sort by total value
    sorted_accounts = sorted(account_data.items(), key=lambda x: x[1]['total_cad'], reverse=True)
    
    for account, data in sorted_accounts:
        usd_percentage = (data['usd_cad'] / data['total_cad'] * 100) if data['total_cad'] > 0 else 0
        
        print(f"{account:<25} "
              f"${data['total_cad']:>11,.0f} "
              f"${data['usd_cad']:>11,.0f} "
              f"{usd_percentage:>6.1f}% "
              f"{data['holdings_count']:>7} "
              f"{data['usd_holdings_count']:>9}")
    
    # Prepare data for dashboard
    print(f"\n=== DASHBOARD DATA STRUCTURE ===")
    dashboard_data = []
    
    for account, data in sorted_accounts:
        usd_percentage = (data['usd_cad'] / data['total_cad'] * 100) if data['total_cad'] > 0 else 0
        portfolio_percentage = (data['total_cad'] / total_portfolio_cad * 100)
        
        dashboard_data.append({
            'Account': account,
            'Total_CAD': data['total_cad'],
            'USD_CAD': data['usd_cad'],
            'USD_Original': data['usd_original'],
            'USD_Percentage': usd_percentage,
            'Portfolio_Percentage': portfolio_percentage,
            'Holdings_Count': data['holdings_count'],
            'USD_Holdings_Count': data['usd_holdings_count']
        })
    
    return dashboard_data, total_portfolio_cad

if __name__ == "__main__":
    dashboard_data, total_portfolio = analyze_usd_holdings()
