#!/usr/bin/env python3
"""
Create enriched RBC holdings with only recommended fields
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
import yfinance as yf
import pandas as pd

def get_recommended_fields():
    """Return the list of fields to keep based on recommendations"""
    
    # Original RBC fields (keep all)
    original_fields = {
        'Holding_ID', 'Account_Number', 'Product', 'Symbol', 'Name', 'Quantity', 
        'Last_Price', 'Currency', 'Book_Value', 'Book_Value_CAD', 'Market_Value', 
        'Market_Value_CAD', 'Unrealized_Gain_Loss', 'Unrealized_Gain_Loss_Pct', 
        'Annual_Dividend', 'Source_File'
    }
    
    # Essential fields to keep
    essential_fields = {
        'Asset_Type', 'Sector', 'Industry', 'Issuer_Region', 'Listing_Country',
        'Weight_Total_Portfolio', 'Indicated_Yield_on_Market', 'Yield_on_Cost',
        'Day_Change_Pct', 'Day_Change_Value', 'Income_Type', 'Indicated_Annual_Income',
        'Classification_Source', 'Enrichment_Confidence', 'Last_Verified_Date'
    }
    
    # Valuable fields to keep
    valuable_fields = {
        'Exchange', 'Market_Cap', 'Employees', 'Business_Summary', 'Website',
        'ETF_Type_Final', 'ETF_Region_Final'
    }
    
    # Conditional fields to keep
    conditional_fields = {
        'Account_Type', 'ETF_Region_Final', 'Currency_Local', 'FX_To_CAD',
        'Include_in_Exposure', 'Weight_in_Account', 'Dividend Ex Date'
    }
    
    return original_fields | essential_fields | valuable_fields | conditional_fields

def enrich_holding_with_yahoo(symbol, name, product):
    """Enrich a single holding using Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get basic classification
        sector = info.get('sector', 'Unknown')
        industry = info.get('industry', 'Unknown')
        country = info.get('country', 'Unknown')
        exchange = info.get('exchange', 'Unknown')
        market_cap = info.get('marketCap', 0)
        employees = info.get('fullTimeEmployees', 0)
        website = info.get('website', '')
        business_summary = info.get('longBusinessSummary', '')
        
        # Determine asset type based on product and sector
        if 'ETF' in product or 'ETN' in product:
            asset_type = 'ETF'
            if 'bond' in name.lower() or 'bond' in business_summary.lower():
                etf_type = 'Bond'
            elif 'reit' in name.lower() or 'real estate' in business_summary.lower():
                etf_type = 'REIT'
            else:
                etf_type = 'Equity'
        elif 'REIT' in product or 'Real Estate' in product:
            asset_type = 'REIT'
            etf_type = None
        elif 'Fixed Income' in product or 'Bond' in product:
            asset_type = 'Fixed Income'
            etf_type = None
        else:
            asset_type = 'Equity'
            etf_type = None
        
        # Determine region
        if country in ['United States', 'US']:
            region = 'United States'
        elif country in ['Canada', 'CA']:
            region = 'Canada'
        elif country in ['United Kingdom', 'UK', 'Great Britain']:
            region = 'United Kingdom'
        else:
            region = 'International'
        
        # Get dividend information
        dividend_rate = info.get('dividendRate', 0)
        dividend_yield = info.get('dividendYield', 0)
        ex_dividend_date = info.get('exDividendDate', None)
        
        # Format ex-dividend date
        if ex_dividend_date:
            try:
                ex_dividend_date = datetime.fromtimestamp(ex_dividend_date).strftime('%Y-%m-%d')
            except:
                ex_dividend_date = None
        
        return {
            'Asset_Type': asset_type,
            'Sector': sector,
            'Industry': industry,
            'Issuer_Region': region,
            'Listing_Country': country,
            'Exchange': exchange,
            'Market_Cap': market_cap,
            'Employees': employees,
            'Website': website,
            'Business_Summary': business_summary,
            'ETF_Type_Final': etf_type,
            'ETF_Region_Final': region if asset_type == 'ETF' else None,
            'Income_Type': 'Dividend' if dividend_rate > 0 else 'None',
            'Indicated_Annual_Income': dividend_rate,
            'Indicated_Yield_on_Market': dividend_yield,
            'Yield_on_Cost': None,  # Will be calculated later
            'Dividend Ex Date': ex_dividend_date,
            'Classification_Source': 'yahoo_finance',
            'Enrichment_Confidence': 0.9,
            'Last_Verified_Date': datetime.now().strftime('%Y-%m-%d')
        }
        
    except Exception as e:
        print(f"  Warning: Could not enrich {symbol}: {e}")
        return {
            'Asset_Type': 'Unknown',
            'Sector': 'Unknown',
            'Industry': 'Unknown',
            'Issuer_Region': 'Unknown',
            'Listing_Country': 'Unknown',
            'Exchange': 'Unknown',
            'Market_Cap': 0,
            'Employees': 0,
            'Website': '',
            'Business_Summary': '',
            'ETF_Type_Final': None,
            'ETF_Region_Final': None,
            'Income_Type': 'None',
            'Indicated_Annual_Income': 0,
            'Indicated_Yield_on_Market': 0,
            'Yield_on_Cost': None,
            'Dividend Ex Date': None,
            'Classification_Source': 'failed',
            'Enrichment_Confidence': 0.0,
            'Last_Verified_Date': datetime.now().strftime('%Y-%m-%d')
        }

def calculate_portfolio_metrics(holdings):
    """Calculate portfolio-level metrics for each holding"""
    total_value = sum(h.get('Market_Value_CAD', 0) for h in holdings)
    
    for holding in holdings:
        market_value = holding.get('Market_Value_CAD', 0)
        book_value = holding.get('Book_Value_CAD', 0)
        quantity = holding.get('Quantity', 0)
        
        # Calculate portfolio weight
        if total_value > 0:
            holding['Weight_Total_Portfolio'] = market_value / total_value
        else:
            holding['Weight_Total_Portfolio'] = 0
        
        # Calculate yield on cost
        if book_value > 0 and holding.get('Indicated_Annual_Income', 0) > 0:
            holding['Yield_on_Cost'] = holding['Indicated_Annual_Income'] / book_value
        else:
            holding['Yield_on_Cost'] = None
        
        # Calculate daily change (placeholder - would need real-time data)
        holding['Day_Change_Pct'] = 0.0
        holding['Day_Change_Value'] = 0.0
        
        # Set additional fields
        holding['Currency_Local'] = holding.get('Currency', 'CAD')
        holding['FX_To_CAD'] = 1.0 if holding.get('Currency') == 'CAD' else 1.38535
        holding['Include_in_Exposure'] = True
        holding['Weight_in_Account'] = 0.0  # Would need account-level calculation
        holding['Account_Type'] = 'Taxable'  # Default, could be enhanced

def main():
    print("=== CREATING ENRICHED RBC HOLDINGS ===")
    
    # Load consolidated RBC holdings
    output_dir = Path('data/output')
    consolidated_files = list(output_dir.glob('consolidated_holdings_RBC_only_*.json'))
    
    if not consolidated_files:
        print("No consolidated RBC holdings files found!")
        return
    
    latest_consolidated = max(consolidated_files, key=lambda f: f.stat().st_mtime)
    print(f"Loading: {latest_consolidated.name}")
    
    with open(latest_consolidated, 'r') as f:
        consolidated_data = json.load(f)
    
    holdings = consolidated_data.get('holdings', [])
    print(f"Processing {len(holdings)} holdings with symbols")
    
    # Get recommended fields
    recommended_fields = get_recommended_fields()
    
    # Enrich each holding
    enriched_holdings = []
    for i, holding in enumerate(holdings):
        symbol = holding.get('Symbol')
        name = holding.get('Name', '')
        product = holding.get('Product', '')
        
        print(f"Enriching {i+1}/{len(holdings)}: {symbol} - {name[:50]}")
        
        # Start with original holding data
        enriched_holding = holding.copy()
        
        # Add Yahoo Finance enrichment
        yahoo_data = enrich_holding_with_yahoo(symbol, name, product)
        enriched_holding.update(yahoo_data)
        
        enriched_holdings.append(enriched_holding)
    
    # Calculate portfolio metrics
    print("Calculating portfolio metrics...")
    calculate_portfolio_metrics(enriched_holdings)
    
    # Filter to only recommended fields
    print("Filtering to recommended fields...")
    filtered_holdings = []
    for holding in enriched_holdings:
        filtered_holding = {k: v for k, v in holding.items() if k in recommended_fields}
        filtered_holdings.append(filtered_holding)
    
    # Create enriched data structure
    enriched_data = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'source': 'RBC Holdings Enrichment',
            'total_holdings': len(filtered_holdings),
            'enrichment_fields': len(recommended_fields),
            'original_file': latest_consolidated.name
        },
        'holdings': filtered_holdings
    }
    
    # Save enriched file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"consolidated_holdings_RBC_only_enriched_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(enriched_data, f, indent=2)
    
    print(f"\n=== ENRICHED FILE CREATED ===")
    print(f"File: {output_file.name}")
    print(f"Holdings: {len(filtered_holdings)}")
    print(f"Fields per holding: {len(recommended_fields)}")
    print(f"Size: {output_file.stat().st_size:,} bytes")
    
    # Summary of enrichment
    yahoo_success = sum(1 for h in filtered_holdings if h.get('Classification_Source') == 'yahoo_finance')
    failed_enrichment = sum(1 for h in filtered_holdings if h.get('Classification_Source') == 'failed')
    
    print(f"\n=== ENRICHMENT SUMMARY ===")
    print(f"Yahoo Finance success: {yahoo_success}/{len(filtered_holdings)} ({yahoo_success/len(filtered_holdings)*100:.1f}%)")
    print(f"Failed enrichments: {failed_enrichment}")
    
    return output_file

if __name__ == "__main__":
    main()
