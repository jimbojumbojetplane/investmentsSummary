#!/usr/bin/env python3
"""
Create comprehensive holdings file combining RBC holdings and benefits accounts
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
import pandas as pd

def load_latest_enriched_holdings():
    """Load the most recent enriched RBC holdings"""
    output_dir = Path('data/output')
    enriched_files = list(output_dir.glob('consolidated_holdings_RBC_only_automated_enriched_*.json'))
    
    if not enriched_files:
        raise FileNotFoundError("No enriched RBC holdings files found!")
    
    latest_file = max(enriched_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Loading RBC holdings from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def load_benefits_data():
    """Load the benefits data"""
    output_dir = Path('data/output')
    benefits_files = list(output_dir.glob('benefits_data_*.json'))
    
    if not benefits_files:
        raise FileNotFoundError("No benefits data files found!")
    
    latest_file = max(benefits_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Loading benefits data from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def create_benefits_accounts(benefits_data):
    """Create benefits account entries in the same format as RBC cash balances"""
    benefits_accounts = []
    
    # Helper function to parse currency amount
    def parse_amount(amount_str):
        """Parse amount string like '$674,025.96' to float"""
        return float(amount_str.replace('$', '').replace(',', ''))
    
    # Create DC Pension account
    if 'dc_pension_plan' in benefits_data:
        dc_amount = parse_amount(benefits_data['dc_pension_plan'])
        benefits_accounts.append({
            'Cash_ID': str(uuid.uuid4()),
            'Account_Number': 'BENEFITS_DC_PENSION',
            'Currency': 'CAD',
            'Amount': dc_amount,
            'Amount_CAD': dc_amount,
            'Exchange_Rate': 1.0,
            'Source_File': 'DC Pension Plan',
            'Account_Type': 'Benefits',
            'Account_Name': 'DC Pension Plan'
        })
    
    # Create RRSP account
    if 'rrsp' in benefits_data:
        rrsp_amount = parse_amount(benefits_data['rrsp'])
        benefits_accounts.append({
            'Cash_ID': str(uuid.uuid4()),
            'Account_Number': 'BENEFITS_RRSP',
            'Currency': 'CAD',
            'Amount': rrsp_amount,
            'Amount_CAD': rrsp_amount,
            'Exchange_Rate': 1.0,
            'Source_File': 'RRSP',
            'Account_Type': 'Benefits',
            'Account_Name': 'RRSP'
        })
    
    return benefits_accounts

def create_comprehensive_holdings():
    """Create comprehensive holdings file with RBC + Benefits"""
    print("=== CREATING COMPREHENSIVE HOLDINGS ===")
    
    # Load data
    rbc_data = load_latest_enriched_holdings()
    benefits_data = load_benefits_data()
    
    # Create benefits accounts
    benefits_accounts = create_benefits_accounts(benefits_data)
    
    # Calculate totals
    rbc_cash_total = rbc_data['metadata']['cash_total_cad']
    benefits_total = sum(acc['Amount_CAD'] for acc in benefits_accounts)
    combined_cash_total = rbc_cash_total + benefits_total
    
    rbc_holdings_total = rbc_data['metadata']['holdings_total_cad']
    total_portfolio_value = rbc_holdings_total + combined_cash_total
    
    # Create comprehensive metadata
    comprehensive_metadata = {
        'total_rbc_holdings': rbc_data['metadata']['total_holdings'],
        'total_rbc_cash_balances': rbc_data['metadata']['total_cash_balances'],
        'total_benefits_accounts': len(benefits_accounts),
        'rbc_cash_total_cad': rbc_cash_total,
        'benefits_total_cad': benefits_total,
        'combined_cash_total_cad': combined_cash_total,
        'rbc_holdings_total_cad': rbc_holdings_total,
        'total_portfolio_value_cad': total_portfolio_value,
        'created_at': datetime.now().isoformat(),
        'data_sources': {
            'rbc_holdings': 'consolidated_holdings_RBC_only_automated_enriched',
            'benefits_data': 'benefits_portal_automation'
        }
    }
    
    # Combine all cash balances
    all_cash_balances = rbc_data.get('cash_balances', []) + benefits_accounts
    
    # Create comprehensive data structure
    comprehensive_data = {
        'metadata': comprehensive_metadata,
        'holdings': rbc_data['holdings'],
        'cash_balances': all_cash_balances
    }
    
    # Save comprehensive file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'comprehensive_holdings_RBC_and_Benefits_{timestamp}.json'
    output_path = Path('data/output') / output_filename
    
    with open(output_path, 'w') as f:
        json.dump(comprehensive_data, f, indent=2)
    
    print(f"\n✅ Comprehensive holdings saved to: {output_filename}")
    print(f"📊 Summary:")
    print(f"   RBC Holdings: {rbc_data['metadata']['total_holdings']}")
    print(f"   RBC Cash Balances: {rbc_data['metadata']['total_cash_balances']}")
    print(f"   Benefits Accounts: {len(benefits_accounts)}")
    print(f"   RBC Cash Total: ${rbc_cash_total:,.2f} CAD")
    print(f"   Benefits Total: ${benefits_total:,.2f} CAD")
    print(f"   Combined Cash Total: ${combined_cash_total:,.2f} CAD")
    print(f"   RBC Holdings Total: ${rbc_holdings_total:,.2f} CAD")
    print(f"   Total Portfolio Value: ${total_portfolio_value:,.2f} CAD")
    
    print(f"\n💰 Benefits Accounts:")
    for acc in benefits_accounts:
        print(f"   {acc['Account_Name']}: ${acc['Amount']:,.2f} CAD")
    
    return output_path

if __name__ == "__main__":
    create_comprehensive_holdings()
