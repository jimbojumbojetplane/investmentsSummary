#!/usr/bin/env python3
"""
Fix the original holdings_detailed file by adding the missing cash balances
to get the correct $3.7M total
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

def main():
    print("=== FIXING ORIGINAL HOLDINGS FILE ===")
    
    # Load the most recent original holdings file
    output_dir = Path('data/output')
    holdings_files = [f for f in output_dir.glob('holdings_detailed_*.json') 
                     if 'restructured' not in f.name and 'corrected' not in f.name and 'complete' not in f.name and 'final' not in f.name]
    
    if not holdings_files:
        print("No original holdings files found!")
        return
    
    latest_file = max(holdings_files, key=lambda f: f.stat().st_mtime)
    print(f'Loading: {latest_file.name}')
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    # Calculate current total
    current_total = sum(h.get('Market_Value_CAD', 0) for h in data)
    print(f'Current total: ${current_total:,.2f}')
    
    # Expected cash balances from our CSV analysis
    expected_cash_balances = [
        {'account': '26674346', 'currency': 'CAD', 'amount': 2606.82},
        {'account': '49813791', 'currency': 'CAD', 'amount': 105657.24},
        {'account': '49813791', 'currency': 'USD', 'amount': 3736.75},
        {'account': '68000157', 'currency': 'CAD', 'amount': 0.77},
        {'account': '68000157', 'currency': 'USD', 'amount': 621.60},
        {'account': '69539728', 'currency': 'CAD', 'amount': 32439.03},
        {'account': '69539728', 'currency': 'USD', 'amount': 98722.65},
        {'account': '69549834', 'currency': 'CAD', 'amount': 169.03}
    ]
    
    # Create cash balance holdings
    cash_holdings = []
    total_cash_added = 0
    
    for cb in expected_cash_balances:
        # Convert USD to CAD if needed
        if cb['currency'] == 'USD':
            market_value_cad = cb['amount'] * 1.38535
            asset_type = 'Cash USD'
        else:
            market_value_cad = cb['amount']
            asset_type = 'Cash CAD'
        
        cash_holding = {
            'Holding_ID': str(uuid.uuid4()),
            'Symbol': None,
            'Name': 'Cash Balance',
            'Account': cb['account'],
            'Asset_Type': asset_type,
            'Sector': 'Cash & Equivalents',
            'Issuer_Region': 'Cash',
            'Listing_Country': None,
            'Industry': None,
            'Currency': cb['currency'],
            'Quantity': cb['amount'],
            'Last_Price': 1.0,
            'Market_Value': cb['amount'],
            'Market_Value_CAD': market_value_cad,
            'Book_Value': cb['amount'],
            'Book_Value_CAD': market_value_cad,
            'Unrealized_Gain_Loss': 0.0,
            'Unrealized_Gain_Loss_Pct': 0.0,
            'Classification_Source': 'RBC_CSV_Cash_Balance',
            'LLM_Reasoning': None,
            'Source_File': 'Original CSV Files',
            'Include_in_Exposure': True
        }
        
        cash_holdings.append(cash_holding)
        total_cash_added += market_value_cad
    
    print(f'Cash balances to add: ${total_cash_added:,.2f}')
    
    # Add cash holdings to the data
    corrected_data = data + cash_holdings
    
    # Calculate new total
    new_total = sum(h.get('Market_Value_CAD', 0) for h in corrected_data)
    
    print(f'\n=== CORRECTION COMPLETE ===')
    print(f'Original holdings: {len(data)} (${current_total:,.2f})')
    print(f'Cash holdings added: {len(cash_holdings)} (${total_cash_added:,.2f})')
    print(f'Corrected holdings: {len(corrected_data)} (${new_total:,.2f})')
    
    # Save corrected file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    corrected_filename = f"holdings_detailed_corrected_{timestamp}.json"
    corrected_filepath = output_dir / corrected_filename
    
    with open(corrected_filepath, 'w') as f:
        json.dump(corrected_data, f, indent=2)
    
    print(f'\n=== CORRECTED FILE CREATED ===')
    print(f'File: {corrected_filename}')
    print(f'Total holdings: {len(corrected_data)}')
    print(f'Total value: ${new_total:,.2f}')
    
    # Verify against expected total
    expected_total = 3700000
    difference = abs(new_total - expected_total)
    if difference < 1000:  # Within $1000
        print(f'✅ Portfolio total matches expected $3.7M (within ${difference:,.2f})')
    else:
        print(f'❌ Portfolio total: ${new_total:,.2f}, Expected: ${expected_total:,.2f}, Difference: ${difference:,.2f}')
    
    return corrected_filepath

if __name__ == "__main__":
    main()
