#!/usr/bin/env python3
"""
Fix the cash balance extraction to properly capture all cash balances from CSV files
and create a corrected restructured holdings file
"""

import pandas as pd
import json
from pathlib import Path
import uuid
from datetime import datetime

def extract_cash_balances_from_csv(file_path):
    """Extract actual cash balances (not cash ETFs) from a single CSV file"""
    print(f"\n=== Analyzing {file_path.name} ===")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find account number and name
    account_info = None
    for line in lines:
        if line.startswith('Account:'):
            account_info = line.strip().replace('Account: ', '')
            break
    
    print(f"Account: {account_info}")
    
    # Find currency and cash information
    cash_balances = []
    in_currency_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for currency section header
        if line.startswith('Currency,Cash,Investments'):
            in_currency_section = True
            continue
            
        # Parse currency lines
        if in_currency_section and line and not line.startswith('Currency'):
            if ',' in line:
                parts = line.split(',')
                if len(parts) >= 3:
                    currency = parts[0].strip('"')
                    cash_str = parts[1].strip('"')
                    investments_str = parts[2].strip('"')
                    total_str = parts[3].strip('"') if len(parts) > 3 else None
                    
                    try:
                        cash_value = float(cash_str) if cash_str and cash_str != 'N/A' else 0
                        investments_value = float(investments_str) if investments_str and investments_str != 'N/A' else 0
                        total_value = float(total_str) if total_str and total_str != 'N/A' else cash_value + investments_value
                        
                        if cash_value > 0:
                            # Extract account number from account_info
                            account_number = account_info.split(' - ')[0] if ' - ' in account_info else account_info
                            account_name = account_info.split(' - ')[1] if ' - ' in account_info else account_info
                            
                            cash_balances.append({
                                'account_number': account_number,
                                'account_name': account_name,
                                'currency': currency,
                                'cash_value': cash_value,
                                'investments_value': investments_value,
                                'total_value': total_value,
                                'line_number': i + 1
                            })
                            print(f"  {currency} Cash: ${cash_value:,.2f}")
                            
                    except ValueError:
                        continue
            else:
                # End of currency section
                break
    
    return cash_balances

def create_cash_balance_holdings(cash_balances):
    """Convert cash balances to holdings format"""
    cash_holdings = []
    
    for cb in cash_balances:
        # Generate unique holding ID
        holding_id = str(uuid.uuid4())
        
        # Convert USD to CAD if needed
        if cb['currency'] == 'USD':
            market_value_cad = cb['cash_value'] * 1.38535
            asset_type = 'Cash USD'
        else:
            market_value_cad = cb['cash_value']
            asset_type = 'Cash CAD'
        
        cash_holding = {
            'Holding_ID': holding_id,
            'Symbol': None,  # No symbol for cash balances
            'Name': 'Cash Balance',
            'Account_Number': cb['account_number'],
            'Asset_Type': asset_type,
            'Sector': 'Cash & Equivalents',
            'Issuer_Region': 'Cash',
            'Listing_Country': None,
            'Industry': None,
            'Currency': cb['currency'],
            'Quantity': cb['cash_value'],  # Cash amount as quantity
            'Last_Price': 1.0,  # Cash is always $1
            'Market_Value': cb['cash_value'],
            'Market_Value_CAD': market_value_cad,
            'Book_Value': cb['cash_value'],
            'Book_Value_CAD': market_value_cad,
            'Unrealized_Gain_Loss': 0.0,
            'Unrealized_Gain_Loss_Pct': 0.0,
            'Classification_Source': 'RBC_CSV_Cash_Balance',
            'LLM_Reasoning': None,
            'Source_File': 'Original CSV Files',
            'Include_in_Exposure': True
        }
        
        cash_holdings.append(cash_holding)
    
    return cash_holdings

def main():
    """Main function to fix cash balance extraction"""
    print("=== FIXING CASH BALANCE EXTRACTION ===")
    
    # Directory containing CSV files
    csv_dir = Path("data/input/downloaded_files")
    
    # Find all September 10, 2025 CSV files
    csv_files = list(csv_dir.glob("*September 10, 2025.csv"))
    csv_files.sort()
    
    print(f"Found {len(csv_files)} CSV files from September 10, 2025")
    
    # Extract cash balances from all files
    all_cash_balances = []
    for csv_file in csv_files:
        cash_balances = extract_cash_balances_from_csv(csv_file)
        all_cash_balances.extend(cash_balances)
    
    print(f"\n=== SUMMARY OF CASH BALANCES FOUND ===")
    print(f"Total cash balance entries: {len(all_cash_balances)}")
    
    # Calculate totals
    cad_total = sum(cb['cash_value'] for cb in all_cash_balances if cb['currency'] == 'CAD')
    usd_total = sum(cb['cash_value'] for cb in all_cash_balances if cb['currency'] == 'USD')
    
    print(f"CAD Cash: ${cad_total:,.2f}")
    print(f"USD Cash: ${usd_total:,.2f}")
    print(f"Total CAD Equivalent: ${cad_total + usd_total * 1.38535:,.2f}")
    
    # Create cash holdings in the proper format
    cash_holdings = create_cash_balance_holdings(all_cash_balances)
    
    print(f"\n=== CREATING CORRECTED RESTRUCTURED FILE ===")
    
    # Load the existing restructured file
    output_dir = Path("data/output")
    restructured_files = list(output_dir.glob("holdings_detailed_restructured_*.json"))
    if restructured_files:
        latest_file = max(restructured_files, key=lambda f: f.stat().st_mtime)
        print(f"Loading existing file: {latest_file.name}")
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'holdings' in data:
            existing_holdings = data['holdings']
            
            # Remove existing cash balance holdings (those without symbols)
            symbol_holdings = [h for h in existing_holdings if h.get('Symbol') is not None and h.get('Symbol') != '']
            
            print(f"Existing symbol holdings: {len(symbol_holdings)}")
            print(f"Existing cash holdings (removing): {len(existing_holdings) - len(symbol_holdings)}")
            print(f"New cash holdings (adding): {len(cash_holdings)}")
            
            # Combine symbol holdings with new cash holdings
            corrected_holdings = symbol_holdings + cash_holdings
            
            # Create corrected metadata
            corrected_metadata = {
                'creation_date': datetime.now().isoformat(),
                'total_holdings': len(corrected_holdings),
                'symbol_holdings': len(symbol_holdings),
                'cash_holdings': len(cash_holdings),
                'total_value_cad': sum(h.get('Market_Value_CAD', 0) for h in corrected_holdings),
                'cash_balance_cad': sum(h.get('Market_Value_CAD', 0) for h in cash_holdings),
                'source_files': [f.name for f in csv_files],
                'notes': 'Corrected with proper cash balance extraction from original CSV files'
            }
            
            # Create corrected data structure
            corrected_data = {
                'metadata': corrected_metadata,
                'holdings': corrected_holdings
            }
            
            # Save corrected file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            corrected_filename = f"holdings_detailed_restructured_corrected_{timestamp}.json"
            corrected_filepath = output_dir / corrected_filename
            
            with open(corrected_filepath, 'w') as f:
                json.dump(corrected_data, f, indent=2)
            
            print(f"\n=== CORRECTED FILE CREATED ===")
            print(f"File: {corrected_filename}")
            print(f"Total holdings: {len(corrected_holdings)}")
            print(f"Symbol holdings: {len(symbol_holdings)}")
            print(f"Cash holdings: {len(cash_holdings)}")
            print(f"Total value: ${corrected_metadata['total_value_cad']:,.2f}")
            print(f"Cash balance value: ${corrected_metadata['cash_balance_cad']:,.2f}")
            
            # Verify cash balances
            print(f"\n=== VERIFICATION ===")
            print(f"Expected cash balance: ${cad_total + usd_total * 1.38535:,.2f}")
            print(f"Actual cash balance: ${corrected_metadata['cash_balance_cad']:,.2f}")
            
            if abs((cad_total + usd_total * 1.38535) - corrected_metadata['cash_balance_cad']) < 0.01:
                print("✅ Cash balances match perfectly!")
            else:
                print("❌ Cash balances don't match!")
            
            # Show breakdown by account
            print(f"\n=== CASH BALANCE BREAKDOWN BY ACCOUNT ===")
            for cb in all_cash_balances:
                print(f"{cb['account_name']} ({cb['account_number']}): {cb['currency']} ${cb['cash_value']:,.2f}")
            
            return corrected_filepath
    
    return None

if __name__ == "__main__":
    main()
