#!/usr/bin/env python3
"""
Calculate total portfolio value in Canadian dollars
"""

import json
from pathlib import Path

def main():
    # Load the latest holdings detailed file
    output_dir = Path("data/output")
    holdings_files = list(output_dir.glob("holdings_detailed_*.json"))
    
    if not holdings_files:
        print("No holdings files found")
        return
    
    latest_file = max(holdings_files, key=lambda f: f.stat().st_mtime)
    print(f"Loading: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        holdings_data = json.load(f)
    
    # Calculate total value in CAD
    total_cad = 0
    for holding in holdings_data:
        market_value_cad = holding.get('Market_Value_CAD', 0)
        if market_value_cad:
            total_cad += market_value_cad
    
    print(f"Total Portfolio Value in CAD: ${total_cad:,.2f}")
    print(f"Total Holdings: {len(holdings_data)}")
    
    # Also show breakdown by account type
    account_totals = {}
    for holding in holdings_data:
        account = holding.get('Account #', 'Unknown')
        market_value_cad = holding.get('Market_Value_CAD', 0)
        if account not in account_totals:
            account_totals[account] = 0
        account_totals[account] += market_value_cad
    
    print("\nBreakdown by Account:")
    for account, value in sorted(account_totals.items()):
        print(f"  {account}: ${value:,.2f}")

if __name__ == "__main__":
    main()
