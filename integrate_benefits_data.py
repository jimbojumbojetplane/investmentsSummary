#!/usr/bin/env python3
"""
Integrate benefits data with holdings to create complete portfolio
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

def main():
    print("=== INTEGRATING BENEFITS DATA WITH HOLDINGS ===")
    
    # Load the final corrected holdings file
    output_dir = Path('data/output')
    final_files = list(output_dir.glob('holdings_detailed_restructured_final_*.json'))
    if not final_files:
        print("No final corrected holdings file found!")
        return
    
    latest_file = max(final_files, key=lambda f: f.stat().st_mtime)
    print(f'Loading holdings: {latest_file.name}')
    
    with open(latest_file, 'r') as f:
        holdings_data = json.load(f)
    
    holdings = holdings_data['holdings']
    
    # Load benefits data
    benefits_file = output_dir / 'benefits_data_20250912_114921.json'
    if not benefits_file.exists():
        print("No benefits data file found!")
        return
    
    print(f'Loading benefits: {benefits_file.name}')
    with open(benefits_file, 'r') as f:
        benefits_data = json.load(f)
    
    # Extract benefits values (remove $ and commas)
    dc_pension = float(benefits_data['dc_pension_plan'].replace('$', '').replace(',', ''))
    rrsp_benefits = float(benefits_data['rrsp'].replace('$', '').replace(',', ''))
    total_benefits = dc_pension + rrsp_benefits
    
    print(f'\nBenefits data:')
    print(f'  DC Pension Plan: ${dc_pension:,.2f}')
    print(f'  RRSP: ${rrsp_benefits:,.2f}')
    print(f'  Total Benefits: ${total_benefits:,.2f}')
    
    # Calculate current holdings total
    current_total = sum(h.get('Market_Value_CAD', 0) for h in holdings)
    print(f'\nCurrent holdings total: ${current_total:,.2f}')
    
    # Create benefits holdings
    benefits_holdings = []
    
    # DC Pension Plan holding
    dc_holding = {
        'Holding_ID': str(uuid.uuid4()),
        'Symbol': None,
        'Name': 'DC Pension Plan',
        'Account_Number': 'BENEFITS',
        'Asset_Type': 'Pension Plan',
        'Sector': 'Retirement Savings',
        'Issuer_Region': 'Canada',
        'Listing_Country': None,
        'Industry': None,
        'Currency': 'CAD',
        'Quantity': dc_pension,
        'Last_Price': 1.0,
        'Market_Value': dc_pension,
        'Market_Value_CAD': dc_pension,
        'Book_Value': dc_pension,
        'Book_Value_CAD': dc_pension,
        'Unrealized_Gain_Loss': 0.0,
        'Unrealized_Gain_Loss_Pct': 0.0,
        'Classification_Source': 'Benefits_Portal',
        'LLM_Reasoning': None,
        'Source_File': 'Benefits Data',
        'Include_in_Exposure': True
    }
    benefits_holdings.append(dc_holding)
    
    # RRSP Benefits holding
    rrsp_holding = {
        'Holding_ID': str(uuid.uuid4()),
        'Symbol': None,
        'Name': 'RRSP Benefits',
        'Account_Number': 'BENEFITS',
        'Asset_Type': 'RRSP',
        'Sector': 'Retirement Savings',
        'Issuer_Region': 'Canada',
        'Listing_Country': None,
        'Industry': None,
        'Currency': 'CAD',
        'Quantity': rrsp_benefits,
        'Last_Price': 1.0,
        'Market_Value': rrsp_benefits,
        'Market_Value_CAD': rrsp_benefits,
        'Book_Value': rrsp_benefits,
        'Book_Value_CAD': rrsp_benefits,
        'Unrealized_Gain_Loss': 0.0,
        'Unrealized_Gain_Loss_Pct': 0.0,
        'Classification_Source': 'Benefits_Portal',
        'LLM_Reasoning': None,
        'Source_File': 'Benefits Data',
        'Include_in_Exposure': True
    }
    benefits_holdings.append(rrsp_holding)
    
    # Combine all holdings
    complete_holdings = holdings + benefits_holdings
    
    # Calculate new total
    new_total = sum(h.get('Market_Value_CAD', 0) for h in complete_holdings)
    
    print(f'\n=== INTEGRATION COMPLETE ===')
    print(f'Original holdings: {len(holdings)} (${current_total:,.2f})')
    print(f'Benefits holdings: {len(benefits_holdings)} (${total_benefits:,.2f})')
    print(f'Complete holdings: {len(complete_holdings)} (${new_total:,.2f})')
    
    # Create complete metadata
    complete_metadata = {
        'creation_date': datetime.now().isoformat(),
        'total_holdings': len(complete_holdings),
        'rbc_holdings': len(holdings),
        'benefits_holdings': len(benefits_holdings),
        'total_value_cad': new_total,
        'rbc_value_cad': current_total,
        'benefits_value_cad': total_benefits,
        'source_files': ['RBC Holdings CSV Files', 'Benefits Portal Data'],
        'notes': 'Complete portfolio including RBC holdings and benefits data'
    }
    
    # Create complete data structure
    complete_data = {
        'metadata': complete_metadata,
        'holdings': complete_holdings
    }
    
    # Save complete file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    complete_filename = f"holdings_detailed_restructured_complete_{timestamp}.json"
    complete_filepath = output_dir / complete_filename
    
    with open(complete_filepath, 'w') as f:
        json.dump(complete_data, f, indent=2)
    
    print(f'\n=== COMPLETE PORTFOLIO FILE CREATED ===')
    print(f'File: {complete_filename}')
    print(f'Total holdings: {len(complete_holdings)}')
    print(f'Total value: ${new_total:,.2f}')
    
    # Verify against expected total
    expected_total = 3700000
    difference = abs(new_total - expected_total)
    if difference < 1000:  # Within $1000
        print(f'✅ Portfolio total matches expected $3.7M (within ${difference:,.2f})')
    else:
        print(f'❌ Portfolio total: ${new_total:,.2f}, Expected: ${expected_total:,.2f}, Difference: ${difference:,.2f}')
    
    return complete_filepath

if __name__ == "__main__":
    main()
