#!/usr/bin/env python3
"""
Analyze the 67 added fields and recommend which to keep based on financial management best practices
"""

import json
from pathlib import Path

def main():
    print("=== FIELD RECOMMENDATION ANALYSIS ===")
    
    # Load enriched file to get field examples
    enriched_file = Path('data/output/holdings_detailed_final_20250912_154120.json')
    with open(enriched_file, 'r') as f:
        enriched_data = json.load(f)
    
    # Get a sample holding with all fields
    sample_holding = next(h for h in enriched_data if h.get('Symbol') and h.get('Symbol') != 'None')
    
    print(f"Sample holding: {sample_holding.get('Symbol')} - {sample_holding.get('Name', 'Unknown')}")
    
    # Original RBC fields (keep all)
    original_fields = {
        'Holding_ID', 'Account_Number', 'Product', 'Symbol', 'Name', 'Quantity', 
        'Last_Price', 'Currency', 'Book_Value', 'Book_Value_CAD', 'Market_Value', 
        'Market_Value_CAD', 'Unrealized_Gain_Loss', 'Unrealized_Gain_Loss_Pct', 
        'Annual_Dividend', 'Source_File'
    }
    
    # All fields in enriched data
    all_fields = set(sample_holding.keys())
    added_fields = all_fields - original_fields
    
    print(f"\n=== FIELD RECOMMENDATIONS ===")
    
    # ESSENTIAL FIELDS (Keep - Core Financial Management)
    essential_fields = {
        # Asset Classification
        'Asset_Type',           # Equity, Fixed Income, REIT, etc.
        'Sector',               # Technology, Healthcare, Financials, etc.
        'Industry',             # Software, Banks, Pharmaceuticals, etc.
        'Issuer_Region',        # North America, Europe, Asia, etc.
        'Listing_Country',      # US, Canada, UK, etc.
        
        # Risk & Return Metrics
        'Weight_Total_Portfolio',  # Portfolio allocation percentage
        'Indicated_Yield_on_Market',  # Current dividend yield
        'Yield_on_Cost',        # Dividend yield based on cost basis
        
        # Performance Metrics
        'Day_Change_Pct',       # Daily price change percentage
        'Day_Change_Value',     # Daily price change in dollars
        
        # Income Analysis
        'Income_Type',          # Dividend, Interest, etc.
        'Indicated_Annual_Income',  # Expected annual income
        
        # Data Quality
        'Classification_Source',  # yahoo_finance, llm, manual
        'Enrichment_Confidence',  # Quality score of classification
        'Last_Verified_Date'    # When data was last updated
    }
    
    # VALUABLE FIELDS (Keep - Enhanced Analysis)
    valuable_fields = {
        # Market Data
        'Exchange',             # NYSE, NASDAQ, TSX, etc.
        'Market_Cap',           # Company market capitalization
        'Employees',            # Company size indicator
        
        # ETF Specific
        'ETF_Type_Final',       # Bond, Equity, REIT, etc.
        'ETF_Region_Final',     # Geographic focus
        
        # Business Intelligence
        'Business_Summary',     # Company description
        'Website',              # Company website
        
        # Currency & FX
        'Currency_Local',       # Local trading currency
        'FX_To_CAD',           # Exchange rate to CAD
        
        # Portfolio Management
        'Weight_in_Account',    # Allocation within account
        'Include_in_Exposure'   # Whether to include in risk calculations
    }
    
    # CONDITIONAL FIELDS (Keep if relevant to use case)
    conditional_fields = {
        # Dividend Analysis
        'Dividend Ex Date',     # Next ex-dividend date
        
        # Account Management
        'Account_Type',         # Taxable, RRSP, TFSA, etc.
        'RSP Eligibility',      # RRSP eligibility
        'DRIP Eligibility',     # Dividend reinvestment eligibility
        
        # Trading Information
        'Average Cost',         # Average purchase price
        'Load Type',            # Commission structure
        
        # Risk Management
        'FX_Hedged',           # Currency hedging status
    }
    
    # LOW VALUE FIELDS (Consider removing - Limited financial value)
    low_value_fields = {
        # Redundant Data
        'Account #',            # Duplicate of Account_Number
        'Account_Id',           # Duplicate of Account_Number
        'Last Price',           # Duplicate of Last_Price
        'Price',                # Duplicate of Last_Price
        'Name_Normalized',      # Duplicate of Name
        'Product_Normalized',   # Duplicate of Product
        'Symbol_Normalized',    # Duplicate of Symbol
        'Total Book Cost',      # Duplicate of Book_Value_CAD
        'Total Market Value',   # Duplicate of Market_Value_CAD
        'Unrealized Gain/Loss $', # Duplicate of Unrealized_Gain_Loss
        'Unrealized Gain/Loss %', # Duplicate of Unrealized_Gain_Loss_Pct
        'Unrealized_PnL',       # Duplicate of Unrealized_Gain_Loss
        'Unrealized_PnL_CAD',   # Duplicate of Unrealized_Gain_Loss
        'Change $',             # Duplicate of Day_Change_Value
        'Change %',             # Duplicate of Day_Change_Pct
        'Annual Dividend Amount $', # Duplicate of Annual_Dividend
        
        # Administrative Fields
        'Source_Notes',         # Internal processing notes
        'Source_Primary',       # Internal source tracking
        'Yahoo_Name',           # Duplicate of Name
        'Asset_Structure',      # Redundant with Asset_Type
        
        # Low-Use Fields
        'Automatic Investment Plan', # Rarely used
        'Coupon Rate',          # Only for bonds
        'Maturity Date',        # Only for bonds
        'Expiration Date',      # Only for options
        'Open Interest',        # Only for options
        'Load Type',            # Commission info (rarely used)
        'ETF_Region_Input',     # Processing field
        'ETF_Type_Input',       # Processing field
        
        # Internal Processing
        'Is_Duplicate_Cash_Line', # Internal flag
        'LLM_Classification_Applied', # Processing flag
        'Needs_Manual_Review',  # Processing flag
        'Confidence',           # Duplicate of Enrichment_Confidence
        'LLM_Reasoning'         # Only for LLM-enriched holdings
    }
    
    # Analyze each field
    print(f"\n=== RECOMMENDED TO KEEP ({len(essential_fields) + len(valuable_fields)} fields) ===")
    
    print(f"\nESSENTIAL FIELDS ({len(essential_fields)}):")
    for field in sorted(essential_fields):
        if field in added_fields:
            value = sample_holding.get(field, 'N/A')
            print(f"  ✅ {field}: {value}")
        else:
            print(f"  ❌ {field}: Not found")
    
    print(f"\nVALUABLE FIELDS ({len(valuable_fields)}):")
    for field in sorted(valuable_fields):
        if field in added_fields:
            value = sample_holding.get(field, 'N/A')
            print(f"  ✅ {field}: {value}")
        else:
            print(f"  ❌ {field}: Not found")
    
    print(f"\n=== CONDITIONAL FIELDS ({len(conditional_fields)}) ===")
    for field in sorted(conditional_fields):
        if field in added_fields:
            value = sample_holding.get(field, 'N/A')
            print(f"  ⚠️  {field}: {value}")
    
    print(f"\n=== RECOMMENDED TO REMOVE ({len(low_value_fields)}) ===")
    for field in sorted(low_value_fields):
        if field in added_fields:
            print(f"  ❌ {field}: Redundant or low value")
    
    # Summary
    keep_fields = essential_fields | valuable_fields
    conditional_keep = conditional_fields
    remove_fields = low_value_fields
    
    print(f"\n=== SUMMARY ===")
    print(f"Original RBC fields: {len(original_fields)} (Keep all)")
    print(f"Essential fields to keep: {len(essential_fields & added_fields)}")
    print(f"Valuable fields to keep: {len(valuable_fields & added_fields)}")
    print(f"Conditional fields: {len(conditional_fields & added_fields)}")
    print(f"Fields to remove: {len(low_value_fields & added_fields)}")
    
    total_recommended = len(original_fields) + len(keep_fields & added_fields)
    print(f"\nTotal recommended fields: {total_recommended}")
    print(f"Current total fields: {len(all_fields)}")
    print(f"Reduction: {len(all_fields) - total_recommended} fields")
    
    print(f"\n=== FINANCIAL MANAGEMENT BEST PRACTICES ===")
    print(f"✅ Asset classification (Sector, Industry, Region)")
    print(f"✅ Risk metrics (Portfolio weights, yields)")
    print(f"✅ Performance tracking (Daily changes)")
    print(f"✅ Income analysis (Dividend yields, income type)")
    print(f"✅ Data quality tracking (Source, confidence, verification)")
    print(f"✅ Market intelligence (Market cap, exchange, business info)")

if __name__ == "__main__":
    main()
