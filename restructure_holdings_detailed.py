#!/usr/bin/env python3
"""
Restructure the existing holdings detailed file to follow proper data structure:
1. Separate cash balances from symbol holdings
2. Generate unique holding IDs
3. Fix industry classifications
4. Ensure proper asset type structure
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid

def load_existing_holdings():
    """Load the latest holdings detailed file"""
    output_dir = Path('data/output')
    holdings_files = list(output_dir.glob('holdings_detailed_*.json'))
    
    if not holdings_files:
        print("No holdings detailed files found")
        return []
    
    latest_file = max(holdings_files, key=lambda f: f.stat().st_mtime)
    print(f"Loading existing holdings from {latest_file.name}...")
    
    with open(latest_file, 'r') as f:
        holdings_data = json.load(f)
    
    print(f"Loaded {len(holdings_data)} holdings")
    return holdings_data

def restructure_holdings(holdings_list):
    """Restructure holdings to follow proper data structure"""
    restructured_holdings = []
    
    for holding in holdings_list:
        # Generate unique holding ID
        holding_id = str(uuid.uuid4())
        
        symbol = holding.get('Symbol', '')
        name = holding.get('Name', '')
        asset_type = holding.get('Asset_Type', '')
        sector = holding.get('Sector', 'Unknown')
        industry = holding.get('Industry', 'Unknown')
        
        # Determine if this should be a cash holding or symbol holding
        is_cash_holding = (
            symbol == 'CASH' and asset_type == 'Cash & Equivalents' or
            symbol in ['MNY', 'CMR', 'HISU.U'] and sector == 'Cash & Equivalents'
        )
        
        if is_cash_holding:
            # This is actual cash, not an ETF
            currency = holding.get('Currency', 'CAD')
            
            restructured_holding = {
                'Holding_ID': holding_id,
                'Symbol': None,  # Cash has no symbol
                'Name': f"{currency} Cash Balance",
                'Account_Number': holding.get('Account #', ''),
                'Asset_Type': f'Cash {currency}',
                'Sector': 'Cash & Equivalents',
                'Issuer_Region': 'Cash',
                'Listing_Country': 'Cash',
                'Industry': None,
                'Currency': currency,
                'Quantity': None,
                'Last_Price': 1.0,
                'Market_Value': holding.get('Market_Value_CAD', 0),
                'Market_Value_CAD': holding.get('Market_Value_CAD', 0),
                'Book_Value': holding.get('Book_Value_CAD', 0),
                'Book_Value_CAD': holding.get('Book_Value_CAD', 0),
                'Unrealized_Gain_Loss': holding.get('Unrealized_PnL_CAD', 0),
                'Unrealized_Gain_Loss_Pct': holding.get('Unrealized_PnL_CAD', 0),
                'Classification_Source': 'Cash_Balance',
                'LLM_Reasoning': f'Cash balance extracted from {currency} cash position',
                'Source_File': 'restructured'
            }
        else:
            # This is a symbol-based holding
            restructured_holding = {
                'Holding_ID': holding_id,
                'Symbol': symbol,
                'Name': name,
                'Account_Number': holding.get('Account #', ''),
                'Asset_Type': asset_type,
                'Sector': sector,
                'Issuer_Region': holding.get('Issuer_Region', 'Unknown'),
                'Listing_Country': holding.get('Listing_Country', 'Unknown'),
                'Industry': industry,
                'Currency': holding.get('Currency', 'CAD'),
                'Quantity': holding.get('Quantity', 0),
                'Last_Price': holding.get('Last Price', 0),
                'Market_Value': holding.get('Market_Value_CAD', 0),
                'Market_Value_CAD': holding.get('Market_Value_CAD', 0),
                'Book_Value': holding.get('Book_Value_CAD', 0),
                'Book_Value_CAD': holding.get('Book_Value_CAD', 0),
                'Unrealized_Gain_Loss': holding.get('Unrealized_PnL_CAD', 0),
                'Unrealized_Gain_Loss_Pct': holding.get('Unrealized_PnL_CAD', 0),
                'Classification_Source': holding.get('Classification_Source', 'Unknown'),
                'LLM_Reasoning': holding.get('LLM_Reasoning', ''),
                'Source_File': 'restructured'
            }
        
        restructured_holdings.append(restructured_holding)
    
    return restructured_holdings

def fix_industry_classifications(holdings_list):
    """Fix specific industry classifications based on business rules"""
    
    for holding in holdings_list:
        symbol = holding.get('Symbol', '')
        sector = holding.get('Sector', '')
        industry = holding.get('Industry', '')
        asset_type = holding.get('Asset_Type', '')
        
        # Fix Energy Midstream → Pipeline
        if sector == 'Energy (Midstream)':
            holding['Industry'] = 'Pipeline'
            holding['Classification_Source'] = 'Manual_Correction'
            holding['LLM_Reasoning'] = 'Energy midstream companies are classified as Pipeline industry'
        
        # Fix ETF Regional Equity → No Industry
        elif 'ETF' in asset_type and 'Regional' in sector:
            holding['Industry'] = None
            holding['Classification_Source'] = 'Manual_Correction'
            holding['LLM_Reasoning'] = 'ETF Regional Equity holdings do not have an industry classification'
        
        # Fix ARC → Energy (if misclassified)
        elif symbol == 'ARC' and sector != 'Energy':
            holding['Sector'] = 'Energy'
            holding['Industry'] = 'Oil & Gas Exploration'
            holding['Classification_Source'] = 'Manual_Correction'
            holding['LLM_Reasoning'] = 'ARC Resources is an energy company, not financials'
        
        # Fix CASH ETF → Proper ETF classification
        elif symbol == 'CASH' and holding.get('Symbol') is not None:
            holding['Asset_Type'] = 'ETF – Cash / Ultra-Short'
            holding['Issuer_Region'] = 'Canada'  # ETF issuer region
            holding['Listing_Country'] = 'Canada'
            holding['Industry'] = 'Cash Management ETF'
            holding['Classification_Source'] = 'Manual_Correction'
            holding['LLM_Reasoning'] = 'CASH is an ETF (Exchange-Traded Fund) that invests in cash equivalents'
    
    return holdings_list

def save_restructured_holdings(holdings_list):
    """Save the restructured holdings detailed file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/output/holdings_detailed_restructured_{timestamp}.json'
    
    # Add metadata
    output_data = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'total_holdings': len(holdings_list),
            'symbol_holdings': len([h for h in holdings_list if h['Symbol'] is not None]),
            'cash_holdings': len([h for h in holdings_list if h['Symbol'] is None]),
            'total_value_cad': sum(h['Market_Value_CAD'] for h in holdings_list)
        },
        'holdings': holdings_list
    }
    
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Saved {len(holdings_list)} restructured holdings to {filename}")
    return filename

def main():
    """Main function to restructure holdings detailed file"""
    print("=== Restructuring Holdings Detailed File ===")
    
    # Load existing holdings
    print("\n1. Loading Existing Holdings...")
    existing_holdings = load_existing_holdings()
    
    if not existing_holdings:
        print("No existing holdings found!")
        return
    
    # Restructure holdings
    print("\n2. Restructuring Holdings...")
    restructured_holdings = restructure_holdings(existing_holdings)
    
    # Fix industry classifications
    print("\n3. Fixing Industry Classifications...")
    final_holdings = fix_industry_classifications(restructured_holdings)
    
    # Save results
    print("\n4. Saving Results...")
    filename = save_restructured_holdings(final_holdings)
    
    print(f"\n✅ Complete! Created restructured holdings detailed file: {filename}")
    
    # Summary
    symbol_count = len([h for h in final_holdings if h['Symbol'] is not None])
    cash_count = len([h for h in final_holdings if h['Symbol'] is None])
    total_value = sum(h['Market_Value_CAD'] for h in final_holdings)
    
    print(f"\nSummary:")
    print(f"- Symbol Holdings: {symbol_count}")
    print(f"- Cash Holdings: {cash_count}")
    print(f"- Total Value (CAD): ${total_value:,.2f}")
    
    # Show breakdown by asset type
    print(f"\nBreakdown by Asset Type:")
    asset_types = {}
    for holding in final_holdings:
        asset_type = holding['Asset_Type']
        if asset_type not in asset_types:
            asset_types[asset_type] = 0
        asset_types[asset_type] += holding['Market_Value_CAD']
    
    for asset_type, value in sorted(asset_types.items(), key=lambda x: x[1], reverse=True):
        print(f"- {asset_type}: ${value:,.2f}")

if __name__ == "__main__":
    main()
