#!/usr/bin/env python3
"""
Create proper holdings detailed file with correct data structure:
1. Combine RBC holdings + benefits into unified file
2. Generate unique holding IDs
3. Handle cash balances properly (no symbols)
4. Apply classification only to holdings with symbols
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid

def load_rbc_holdings_files():
    """Load all RBC holdings CSV files from input directory"""
    downloads_dir = Path('data/input/downloaded_files')
    csv_files = list(downloads_dir.glob('*.csv'))
    
    all_holdings = []
    
    for csv_file in csv_files:
        print(f"Loading {csv_file.name}...")
        try:
            df = pd.read_csv(csv_file)
            
            # Extract account number from filename
            account_id = csv_file.stem.split(' ')[1]  # "Holdings 49813791 September 3, 2025.csv"
            
            # Add account information
            df['Account_Number'] = account_id
            df['Source_File'] = csv_file.name
            
            all_holdings.append(df)
            
        except Exception as e:
            print(f"Error loading {csv_file}: {e}")
    
    if all_holdings:
        combined_df = pd.concat(all_holdings, ignore_index=True)
        print(f"Loaded {len(combined_df)} holdings from {len(csv_files)} files")
        return combined_df
    else:
        print("No RBC holdings files found")
        return pd.DataFrame()

def load_benefits_data():
    """Load benefits data from the latest benefits file and create synthetic holdings"""
    output_dir = Path('data/output')
    benefits_files = list(output_dir.glob('benefits_data_*.json'))
    
    if not benefits_files:
        print("No benefits data files found")
        return pd.DataFrame()
    
    latest_file = max(benefits_files, key=lambda f: f.stat().st_mtime)
    print(f"Loading benefits data from {latest_file.name}...")
    
    with open(latest_file, 'r') as f:
        benefits_data = json.load(f)
    
    # Create synthetic holdings for benefits data
    benefits_list = []
    
    # DC Pension Plan
    if 'dc_pension_plan' in benefits_data:
        dc_value = float(benefits_data['dc_pension_plan'].replace('$', '').replace(',', ''))
        benefits_list.append({
            'Symbol': 'DC-PENSION',
            'Description': 'BELL DEFINED CONTRIBUTION PENSION PLAN',
            'Product': 'Pension Plan',
            'Quantity': 1,
            'Last Price': dc_value,
            'Currency': 'CAD',
            'Total Market Value': dc_value,
            'Total Book Cost': dc_value,
            'Unrealized Gain/Loss $': 0,
            'Unrealized Gain/Loss %': 0,
            'Account_Number': 'BENEFITS01',
            'Source_File': 'benefits_data'
        })
    
    # RRSP
    if 'rrsp' in benefits_data:
        rrsp_value = float(benefits_data['rrsp'].replace('$', '').replace(',', ''))
        benefits_list.append({
            'Symbol': 'RRSP-BELL',
            'Description': 'BELL REGISTERED RETIREMENT SAVINGS PLAN',
            'Product': 'RRSP',
            'Quantity': 1,
            'Last Price': rrsp_value,
            'Currency': 'CAD',
            'Total Market Value': rrsp_value,
            'Total Book Cost': rrsp_value,
            'Unrealized Gain/Loss $': 0,
            'Unrealized Gain/Loss %': 0,
            'Account_Number': 'BENEFITS02',
            'Source_File': 'benefits_data'
        })
    
    if benefits_list:
        benefits_df = pd.DataFrame(benefits_list)
        print(f"Created {len(benefits_df)} synthetic benefits holdings")
        return benefits_df
    else:
        print("No benefits holdings created")
        return pd.DataFrame()

def extract_cash_balances(df):
    """Extract cash balances from holdings data"""
    cash_holdings = []
    
    # Look for cash-related entries
    cash_mask = (
        df['Product'].str.contains('CASH', case=False, na=False) |
        df['Symbol'].str.contains('CASH', case=False, na=False) |
        df['Description'].str.contains('CASH', case=False, na=False)
    )
    
    cash_df = df[cash_mask].copy()
    
    for _, row in cash_df.iterrows():
        # Determine if this is CAD or USD cash
        currency = row.get('Currency', 'CAD')
        if currency == 'USD':
            asset_type = 'Cash USD'
        else:
            asset_type = 'Cash CAD'
        
        # Create cash holding entry
        cash_holding = {
            'Holding_ID': str(uuid.uuid4()),
            'Symbol': None,  # Cash has no symbol
            'Name': f"{currency} Cash Balance",
            'Account_Number': row['Account_Number'],
            'Asset_Type': asset_type,
            'Sector': 'Cash & Equivalents',
            'Issuer_Region': 'Cash',
            'Listing_Country': 'Cash',
            'Industry': None,
            'Currency': currency,
            'Quantity': None,
            'Last_Price': 1.0,  # Cash is always $1
            'Market_Value': row['Total Market Value'],
            'Market_Value_CAD': row['Total Market Value'],  # Assuming already in CAD
            'Book_Value': row['Total Book Cost'],
            'Book_Value_CAD': row['Total Book Cost'],
            'Unrealized_Gain_Loss': row['Unrealized Gain/Loss $'],
            'Unrealized_Gain_Loss_Pct': row['Unrealized Gain/Loss %'],
            'Classification_Source': 'Cash_Balance',
            'LLM_Reasoning': f'Cash balance extracted from {currency} cash position',
            'Source_File': row['Source_File']
        }
        
        cash_holdings.append(cash_holding)
    
    return cash_holdings

def create_symbol_holdings(df):
    """Create holdings entries for items with symbols"""
    symbol_holdings = []
    
    # Filter out cash entries and entries without symbols
    symbol_mask = (
        df['Symbol'].notna() & 
        (df['Symbol'] != '') &
        (~df['Symbol'].str.contains('CASH', case=False, na=False))
    )
    
    symbol_df = df[symbol_mask].copy()
    
    for _, row in symbol_df.iterrows():
        # Determine asset type based on product type
        product = row.get('Product', '').upper()
        if 'ETF' in product or 'FUND' in product:
            if 'CASH' in product or 'MONEY MARKET' in product:
                asset_type = 'ETF – Cash / Ultra-Short'
            elif 'REIT' in product:
                asset_type = 'ETF – Real Estate'
            elif 'BOND' in product or 'FIXED' in product:
                asset_type = 'ETF – Fixed Income'
            else:
                asset_type = 'ETF – Equity'
        elif 'STOCK' in product or 'SHARE' in product:
            asset_type = 'Common Equity'
        elif 'BOND' in product or 'NOTE' in product:
            asset_type = 'Fixed Income'
        else:
            asset_type = 'Common Equity'  # Default
        
        # Create symbol holding entry
        symbol_holding = {
            'Holding_ID': str(uuid.uuid4()),
            'Symbol': row['Symbol'],
            'Name': row.get('Description', row['Symbol']),
            'Account_Number': row['Account_Number'],
            'Asset_Type': asset_type,
            'Sector': 'Unknown',  # Will be filled by classification
            'Issuer_Region': 'Unknown',  # Will be filled by classification
            'Listing_Country': 'Unknown',  # Will be filled by classification
            'Industry': 'Unknown',  # Will be filled by classification
            'Currency': row.get('Currency', 'CAD'),
            'Quantity': row.get('Quantity', 0),
            'Last_Price': row.get('Last Price', 0),
            'Market_Value': row['Total Market Value'],
            'Market_Value_CAD': row['Total Market Value'],  # Assuming already in CAD
            'Book_Value': row['Total Book Cost'],
            'Book_Value_CAD': row['Total Book Cost'],
            'Unrealized_Gain_Loss': row['Unrealized Gain/Loss $'],
            'Unrealized_Gain_Loss_Pct': row['Unrealized Gain/Loss %'],
            'Classification_Source': 'Pending_Classification',
            'LLM_Reasoning': 'Symbol-based holding pending classification',
            'Source_File': row['Source_File']
        }
        
        symbol_holdings.append(symbol_holding)
    
    return symbol_holdings

def apply_basic_classifications(holdings_list):
    """Apply basic classifications to holdings with symbols"""
    from src.external_data_enricher import enrich_holdings_with_yahoo
    
    # Only classify holdings with symbols
    symbol_holdings = [h for h in holdings_list if h['Symbol'] is not None]
    cash_holdings = [h for h in holdings_list if h['Symbol'] is None]
    
    print(f"Applying classifications to {len(symbol_holdings)} holdings with symbols...")
    
    # Convert to DataFrame for Yahoo enrichment
    symbol_df = pd.DataFrame(symbol_holdings)
    
    # Apply Yahoo Finance enrichment
    enriched_df = enrich_holdings_with_yahoo(symbol_df)
    
    # Convert back to list format
    enriched_holdings = enriched_df.to_dict('records')
    
    # Combine with cash holdings
    all_holdings = enriched_holdings + cash_holdings
    
    return all_holdings

def fix_industry_classifications(holdings_list):
    """Fix specific industry classifications based on business rules"""
    
    for holding in holdings_list:
        symbol = holding.get('Symbol', '')
        sector = holding.get('Sector', '')
        industry = holding.get('Industry', '')
        
        # Fix Energy Midstream → Pipeline
        if sector == 'Energy (Midstream)':
            holding['Industry'] = 'Pipeline'
            holding['Classification_Source'] = 'Manual_Correction'
            holding['LLM_Reasoning'] = 'Energy midstream companies are classified as Pipeline industry'
        
        # Fix ETF Regional Equity → No Industry
        elif 'ETF' in holding.get('Asset_Type', '') and 'Regional' in sector:
            holding['Industry'] = None
            holding['Classification_Source'] = 'Manual_Correction'
            holding['LLM_Reasoning'] = 'ETF Regional Equity holdings do not have an industry classification'
        
        # Fix ARC → Energy (if misclassified)
        elif symbol == 'ARC' and sector != 'Energy':
            holding['Sector'] = 'Energy'
            holding['Industry'] = 'Oil & Gas Exploration'
            holding['Classification_Source'] = 'Manual_Correction'
            holding['LLM_Reasoning'] = 'ARC Resources is an energy company, not financials'
    
    return holdings_list

def save_holdings_detailed(holdings_list):
    """Save the properly structured holdings detailed file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/output/holdings_detailed_proper_{timestamp}.json'
    
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
    
    print(f"Saved {len(holdings_list)} holdings to {filename}")
    return filename

def main():
    """Main function to create proper holdings detailed file"""
    print("=== Creating Proper Holdings Detailed File ===")
    
    # Load source data
    print("\n1. Loading RBC Holdings Files...")
    rbc_df = load_rbc_holdings_files()
    
    print("\n2. Loading Benefits Data...")
    benefits_df = load_benefits_data()
    
    # Combine source data
    if not rbc_df.empty and not benefits_df.empty:
        combined_df = pd.concat([rbc_df, benefits_df], ignore_index=True)
    elif not rbc_df.empty:
        combined_df = rbc_df
    elif not benefits_df.empty:
        combined_df = benefits_df
    else:
        print("No source data found!")
        return
    
    print(f"\nCombined source data: {len(combined_df)} records")
    
    # Extract holdings
    print("\n3. Extracting Cash Balances...")
    cash_holdings = extract_cash_balances(combined_df)
    print(f"Found {len(cash_holdings)} cash holdings")
    
    print("\n4. Creating Symbol Holdings...")
    symbol_holdings = create_symbol_holdings(combined_df)
    print(f"Found {len(symbol_holdings)} symbol holdings")
    
    # Combine all holdings
    all_holdings = cash_holdings + symbol_holdings
    print(f"\nTotal holdings: {len(all_holdings)}")
    
    # Apply classifications
    print("\n5. Applying Classifications...")
    classified_holdings = apply_basic_classifications(all_holdings)
    
    # Fix industry classifications
    print("\n6. Fixing Industry Classifications...")
    final_holdings = fix_industry_classifications(classified_holdings)
    
    # Save results
    print("\n7. Saving Results...")
    filename = save_holdings_detailed(final_holdings)
    
    print(f"\n✅ Complete! Created proper holdings detailed file: {filename}")
    
    # Summary
    symbol_count = len([h for h in final_holdings if h['Symbol'] is not None])
    cash_count = len([h for h in final_holdings if h['Symbol'] is None])
    total_value = sum(h['Market_Value_CAD'] for h in final_holdings)
    
    print(f"\nSummary:")
    print(f"- Symbol Holdings: {symbol_count}")
    print(f"- Cash Holdings: {cash_count}")
    print(f"- Total Value (CAD): ${total_value:,.2f}")

if __name__ == "__main__":
    main()
