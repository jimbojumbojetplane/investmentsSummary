#!/usr/bin/env python3
"""
Consolidate the 5 most recent RBC holdings CSV files into a single file
Creates consolidated_holdings_RBC_only.json with proper structure
"""

import json
import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime
import re

def parse_rbc_csv(file_path):
    """Parse a single RBC CSV file and extract holdings and cash balances"""
    print(f"Parsing: {file_path.name}")
    
    holdings = []
    cash_balances = []
    account_info = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract account number from filename or content
    account_match = re.search(r'(\d+)', file_path.name)
    account_number = account_match.group(1) if account_match else "Unknown"
    
    # Find the holdings section
    holdings_start = None
    for i, line in enumerate(lines):
        if 'Product,Symbol,Name,Quantity' in line:
            holdings_start = i + 1
            break
    
    if holdings_start is None:
        print(f"  Warning: No holdings section found in {file_path.name}")
        return holdings, cash_balances, account_info
    
    # Parse holdings
    for i in range(holdings_start, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith('"'):
            continue
            
        # Split by comma but handle quoted fields
        parts = []
        current_part = ""
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                parts.append(current_part.strip())
                current_part = ""
                continue
            current_part += char
        
        if current_part:
            parts.append(current_part.strip())
        
        # Skip if not enough parts or if it's a header
        if len(parts) < 14 or parts[1] == 'Product':
            continue
        
        try:
            # Extract holding data
            product = parts[1].strip('"')
            symbol = parts[2].strip('"')
            name = parts[3].strip('"')
            quantity = float(parts[4].strip('"')) if parts[4].strip('"') else 0
            last_price = float(parts[5].strip('"')) if parts[5].strip('"') else 0
            currency = parts[6].strip('"')
            total_book_cost = float(parts[9].strip('"')) if parts[9].strip('"') else 0
            total_market_value = float(parts[10].strip('"')) if parts[10].strip('"') else 0
            unrealized_gain_loss = float(parts[11].strip('"')) if parts[11].strip('"') else 0
            unrealized_gain_loss_pct = float(parts[12].strip('"').replace('%', '')) if parts[12].strip('"') else 0
            annual_dividend = float(parts[14].strip('"')) if parts[14].strip('"') else 0
            
            # Convert USD to CAD if needed
            if currency == 'USD':
                market_value_cad = total_market_value * 1.38535
                book_value_cad = total_book_cost * 1.38535
            else:
                market_value_cad = total_market_value
                book_value_cad = total_book_cost
            
            holding = {
                'Holding_ID': str(uuid.uuid4()),
                'Account_Number': account_number,
                'Product': product,
                'Symbol': symbol,
                'Name': name,
                'Quantity': quantity,
                'Last_Price': last_price,
                'Currency': currency,
                'Book_Value': total_book_cost,
                'Book_Value_CAD': book_value_cad,
                'Market_Value': total_market_value,
                'Market_Value_CAD': market_value_cad,
                'Unrealized_Gain_Loss': unrealized_gain_loss,
                'Unrealized_Gain_Loss_Pct': unrealized_gain_loss_pct,
                'Annual_Dividend': annual_dividend,
                'Source_File': file_path.name
            }
            
            holdings.append(holding)
            
        except (ValueError, IndexError) as e:
            print(f"  Warning: Error parsing line {i+1}: {e}")
            continue
    
    # Extract cash balances from financial summary
    for i, line in enumerate(lines):
        if 'Currency,Cash,Investments' in line:
            # Look for both CAD and USD cash lines
            for j in range(i + 1, min(i + 5, len(lines))):  # Check next 4 lines
                cash_line = lines[j].strip()
                if cash_line and ('CAD,' in cash_line or 'USD,' in cash_line):
                    parts = cash_line.split(',')
                    if len(parts) >= 5:  # Handle both formats
                        try:
                            currency = parts[0].strip('"')
                            cash_amount = float(parts[1].strip('"')) if parts[1].strip('"') else 0
                            investments = float(parts[2].strip('"')) if parts[2].strip('"') else 0
                            
                            # Handle different column layouts
                            if len(parts) >= 7:  # Currency,Cash,Investments,Short,Total,Margin,Exchange Rate
                                total = float(parts[4].strip('"')) if parts[4].strip('"') else 0
                                exchange_rate = float(parts[6].strip('"')) if len(parts) > 6 and parts[6].strip('"') else 1.0
                            else:  # Currency,Cash,Investments,Total,Exchange Rate
                                total = float(parts[3].strip('"')) if parts[3].strip('"') else 0
                                exchange_rate = float(parts[4].strip('"')) if len(parts) > 4 and parts[4].strip('"') else 1.0
                            
                            if cash_amount > 0:
                                cash_balance = {
                                    'Cash_ID': str(uuid.uuid4()),
                                    'Account_Number': account_number,
                                    'Currency': currency,
                                    'Amount': cash_amount,
                                    'Amount_CAD': cash_amount * exchange_rate,
                                    'Exchange_Rate': exchange_rate,
                                    'Source_File': file_path.name
                                }
                                cash_balances.append(cash_balance)
                                print(f"    Found {currency} cash: ${cash_amount:,.2f} (CAD: ${cash_amount * exchange_rate:,.2f})")
                                
                        except (ValueError, IndexError) as e:
                            print(f"  Warning: Error parsing cash data: {e}")
            break
    
    # Extract account summary
    for i, line in enumerate(lines):
        if 'Trailing 12 Mo Return' in line:
            if i + 1 < len(lines):
                summary_line = lines[i + 1].strip()
                if summary_line:
                    parts = summary_line.split(',')
                    if len(parts) >= 8:
                        try:
                            account_info = {
                                'Account_Number': account_number,
                                'Trailing_12_Mo_Return': parts[1].strip('"').replace('%', '') if len(parts) > 1 else '',
                                'Unrealized_Gain_Loss_CAD': float(parts[2].strip('"')) if len(parts) > 2 and parts[2].strip('"') else 0,
                                'Unrealized_Gain_Loss_Pct': parts[3].strip('"').replace('%', '') if len(parts) > 3 else '',
                                'Combined_Book_Cost_CAD': float(parts[4].strip('"')) if len(parts) > 4 and parts[4].strip('"') else 0,
                                'Combined_Total_CAD': float(parts[6].strip('"')) if len(parts) > 6 and parts[6].strip('"') else 0,
                                'Source_File': file_path.name
                            }
                        except (ValueError, IndexError) as e:
                            print(f"  Warning: Error parsing account summary: {e}")
            break
    
    print(f"  Extracted: {len(holdings)} holdings, {len(cash_balances)} cash balances")
    return holdings, cash_balances, account_info

def main():
    print("=== CONSOLIDATING RBC HOLDINGS ===")
    
    # Find the 5 most recent RBC CSV files
    input_dir = Path('data/input/downloaded_files')
    csv_files = list(input_dir.glob('Holdings *.csv'))
    
    # Sort by modification time and take the 5 most recent
    csv_files = sorted(csv_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]
    
    print(f"Found {len(csv_files)} RBC CSV files:")
    for file in csv_files:
        print(f"  - {file.name}")
    
    # Parse all files
    all_holdings = []
    all_cash_balances = []
    all_account_summaries = []
    
    for csv_file in csv_files:
        holdings, cash_balances, account_info = parse_rbc_csv(csv_file)
        all_holdings.extend(holdings)
        all_cash_balances.extend(cash_balances)
        if account_info:
            all_account_summaries.append(account_info)
    
    # Calculate totals
    holdings_total = sum(h.get('Market_Value_CAD', 0) for h in all_holdings)
    cash_total = sum(c.get('Amount_CAD', 0) for c in all_cash_balances)
    total_value = holdings_total + cash_total
    
    print(f'\n=== CONSOLIDATION COMPLETE ===')
    print(f'Total holdings: {len(all_holdings)}')
    print(f'Total cash balances: {len(all_cash_balances)}')
    print(f'Holdings total: ${holdings_total:,.2f}')
    print(f'Cash total: ${cash_total:,.2f}')
    print(f'Combined total: ${total_value:,.2f}')
    
    # Create consolidated structure
    consolidated_data = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'source': 'RBC CSV Consolidation',
            'total_holdings': len(all_holdings),
            'total_cash_balances': len(all_cash_balances),
            'total_accounts': len(all_account_summaries),
            'holdings_total_cad': holdings_total,
            'cash_total_cad': cash_total,
            'combined_total_cad': total_value
        },
        'account_summaries': all_account_summaries,
        'holdings': all_holdings,
        'cash_balances': all_cash_balances
    }
    
    # Save consolidated file
    output_dir = Path('data/output')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"consolidated_holdings_RBC_only_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(consolidated_data, f, indent=2)
    
    print(f'\n=== CONSOLIDATED FILE CREATED ===')
    print(f'File: {output_file.name}')
    print(f'Size: {output_file.stat().st_size:,} bytes')
    
    # Show breakdown by account
    print(f'\n=== BREAKDOWN BY ACCOUNT ===')
    account_breakdown = {}
    for holding in all_holdings:
        account = holding['Account_Number']
        if account not in account_breakdown:
            account_breakdown[account] = {'holdings': 0, 'total': 0}
        account_breakdown[account]['holdings'] += 1
        account_breakdown[account]['total'] += holding['Market_Value_CAD']
    
    for account, data in account_breakdown.items():
        print(f'  Account {account}: {data["holdings"]} holdings, ${data["total"]:,.2f}')
    
    return output_file

if __name__ == "__main__":
    main()
