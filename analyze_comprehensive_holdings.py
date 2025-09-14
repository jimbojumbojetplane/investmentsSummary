#!/usr/bin/env python3
"""
Analyze comprehensive holdings data with multiple summary levels
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

def load_comprehensive_holdings():
    """Load the most recent comprehensive holdings file"""
    output_dir = Path('data/output')
    comp_files = list(output_dir.glob('comprehensive_holdings_RBC_and_Benefits_*.json'))
    
    if not comp_files:
        raise FileNotFoundError("No comprehensive holdings files found!")
    
    latest_file = max(comp_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Loading comprehensive holdings from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def analyze_by_account_type():
    """Analyze holdings by account type (RBC vs Benefits)"""
    print("\n=== ANALYSIS BY ACCOUNT TYPE ===")
    
    data = load_comprehensive_holdings()
    
    # Separate RBC and Benefits accounts
    rbc_accounts = [acc for acc in data['cash_balances'] if acc.get('Account_Type') != 'Benefits']
    benefits_accounts = [acc for acc in data['cash_balances'] if acc.get('Account_Type') == 'Benefits']
    
    print(f"🏦 RBC Accounts ({len(rbc_accounts)}):")
    rbc_total = 0
    for acc in rbc_accounts:
        print(f"   Account {acc['Account_Number']}: {acc['Currency']} ${acc['Amount']:,.2f} (CAD: ${acc['Amount_CAD']:,.2f})")
        rbc_total += acc['Amount_CAD']
    
    print(f"   RBC Total: ${rbc_total:,.2f} CAD")
    
    print(f"\n🏛️ Benefits Accounts ({len(benefits_accounts)}):")
    benefits_total = 0
    for acc in benefits_accounts:
        print(f"   {acc['Account_Name']}: ${acc['Amount']:,.2f} CAD")
        benefits_total += acc['Amount_CAD']
    
    print(f"   Benefits Total: ${benefits_total:,.2f} CAD")
    print(f"\n💰 Combined Cash Total: ${rbc_total + benefits_total:,.2f} CAD")

def analyze_holdings_by_sector():
    """Analyze holdings by sector"""
    print("\n=== ANALYSIS BY SECTOR ===")
    
    data = load_comprehensive_holdings()
    
    sector_summary = defaultdict(lambda: {'count': 0, 'total_value': 0, 'holdings': []})
    
    for holding in data['holdings']:
        sector = holding.get('Sector', 'Unknown')
        value = holding.get('Market_Value_CAD', 0)
        
        sector_summary[sector]['count'] += 1
        sector_summary[sector]['total_value'] += value
        sector_summary[sector]['holdings'].append({
            'symbol': holding.get('Symbol', ''),
            'name': holding.get('Name', ''),
            'value': value
        })
    
    # Sort by total value
    sorted_sectors = sorted(sector_summary.items(), key=lambda x: x[1]['total_value'], reverse=True)
    
    for sector, info in sorted_sectors:
        print(f"\n📊 {sector}:")
        print(f"   Holdings: {info['count']}")
        print(f"   Total Value: ${info['total_value']:,.2f} CAD")
        print(f"   Top Holdings:")
        # Show top 3 holdings in this sector
        top_holdings = sorted(info['holdings'], key=lambda x: x['value'], reverse=True)[:3]
        for holding in top_holdings:
            print(f"     {holding['symbol']}: ${holding['value']:,.2f} CAD")

def analyze_holdings_by_asset_type():
    """Analyze holdings by asset type"""
    print("\n=== ANALYSIS BY ASSET TYPE ===")
    
    data = load_comprehensive_holdings()
    
    asset_summary = defaultdict(lambda: {'count': 0, 'total_value': 0})
    
    for holding in data['holdings']:
        asset_type = holding.get('Asset_Type', 'Unknown')
        value = holding.get('Market_Value_CAD', 0)
        
        asset_summary[asset_type]['count'] += 1
        asset_summary[asset_type]['total_value'] += value
    
    # Sort by total value
    sorted_assets = sorted(asset_summary.items(), key=lambda x: x[1]['total_value'], reverse=True)
    
    for asset_type, info in sorted_assets:
        print(f"📈 {asset_type}: {info['count']} holdings, ${info['total_value']:,.2f} CAD")

def analyze_currency_breakdown():
    """Analyze holdings by currency"""
    print("\n=== ANALYSIS BY CURRENCY ===")
    
    data = load_comprehensive_holdings()
    
    currency_summary = defaultdict(lambda: {'holdings': 0, 'cash': 0, 'total': 0})
    
    # Analyze holdings
    for holding in data['holdings']:
        currency = holding.get('Currency', 'Unknown')
        value = holding.get('Market_Value_CAD', 0)
        currency_summary[currency]['holdings'] += value
        currency_summary[currency]['total'] += value
    
    # Analyze cash balances
    for cash in data['cash_balances']:
        currency = cash.get('Currency', 'Unknown')
        value = cash.get('Amount_CAD', 0)
        currency_summary[currency]['cash'] += value
        currency_summary[currency]['total'] += value
    
    # Sort by total value
    sorted_currencies = sorted(currency_summary.items(), key=lambda x: x[1]['total'], reverse=True)
    
    for currency, info in sorted_currencies:
        print(f"💱 {currency}:")
        print(f"   Holdings: ${info['holdings']:,.2f} CAD")
        print(f"   Cash: ${info['cash']:,.2f} CAD")
        print(f"   Total: ${info['total']:,.2f} CAD")

def show_portfolio_summary():
    """Show overall portfolio summary"""
    print("\n=== PORTFOLIO SUMMARY ===")
    
    data = load_comprehensive_holdings()
    metadata = data['metadata']
    
    print(f"📊 Portfolio Overview:")
    print(f"   Total Holdings: {metadata['total_rbc_holdings']}")
    print(f"   Total Cash/Benefits Accounts: {metadata['total_rbc_cash_balances'] + metadata['total_benefits_accounts']}")
    print(f"   RBC Holdings Value: ${metadata['rbc_holdings_total_cad']:,.2f} CAD")
    print(f"   RBC Cash: ${metadata['rbc_cash_total_cad']:,.2f} CAD")
    print(f"   Benefits: ${metadata['benefits_total_cad']:,.2f} CAD")
    print(f"   Total Portfolio Value: ${metadata['total_portfolio_value_cad']:,.2f} CAD")
    
    # Calculate percentages
    total_value = metadata['total_portfolio_value_cad']
    holdings_pct = (metadata['rbc_holdings_total_cad'] / total_value) * 100
    cash_pct = (metadata['combined_cash_total_cad'] / total_value) * 100
    benefits_pct = (metadata['benefits_total_cad'] / total_value) * 100
    
    print(f"\n📈 Portfolio Allocation:")
    print(f"   Holdings: {holdings_pct:.1f}%")
    print(f"   Cash: {cash_pct:.1f}%")
    print(f"   Benefits: {benefits_pct:.1f}%")

if __name__ == "__main__":
    show_portfolio_summary()
    analyze_by_account_type()
    analyze_holdings_by_asset_type()
    analyze_holdings_by_sector()
    analyze_currency_breakdown()
