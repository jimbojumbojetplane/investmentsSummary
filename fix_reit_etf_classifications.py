#!/usr/bin/env python3
"""
Fix REIT ETF classifications - REIT ETFs should be classified as Real Estate sector
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_latest_holdings_detailed():
    """Load the most recent holdings detailed file"""
    output_dir = Path("data/output")
    holdings_files = list(output_dir.glob("holdings_detailed_*.json"))
    
    if not holdings_files:
        raise FileNotFoundError("No holdings_detailed_*.json files found")
    
    latest_file = max(holdings_files, key=lambda f: f.stat().st_mtime)
    print(f"Loading latest holdings detailed file: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        return json.load(f), latest_file

def identify_reit_etfs(holdings_data):
    """Identify REIT ETFs that need classification fixes"""
    
    reit_etfs = []
    
    for holding in holdings_data:
        symbol = holding.get('Symbol', '')
        name = holding.get('Name', '')
        sector = holding.get('Sector', '')
        asset_type = holding.get('Asset_Type', '')
        product = holding.get('Product', '')
        
        # Check if this is a REIT ETF
        is_reit_etf = (
            # Check name for REIT keywords
            ('REIT' in name.upper() or 'REAL ESTATE' in name.upper()) and
            # Check if it's an ETF
            ('ETF' in name.upper() or 'ETN' in name.upper() or 
             'ETF' in asset_type.upper() or 'ETN' in asset_type.upper() or
             'ETF' in product.upper() or 'ETN' in product.upper())
        )
        
        if is_reit_etf:
            reit_etfs.append({
                'Symbol': symbol,
                'Name': name,
                'Current_Sector': sector,
                'Asset_Type': asset_type,
                'Product': product,
                'Market_Value': holding.get('Total Market Value', 0),
                'Currency': holding.get('Currency', 'CAD'),
                'Issuer_Region': holding.get('Issuer_Region', ''),
                'Classification_Source': holding.get('Classification_Source', 'none')
            })
    
    return reit_etfs

def create_reit_etf_recommendations(reit_etfs):
    """Create proper Real Estate classifications for REIT ETFs"""
    
    recommendations = []
    
    for etf in reit_etfs:
        symbol = etf['Symbol']
        name = etf['Name']
        
        # Determine region based on symbol and name
        if symbol in ['ZRE', 'CDZ', 'XDV']:  # Canadian ETFs
            recommended_region = 'Canada'
            recommended_country = 'Canada'
        elif 'US' in name.upper() or 'UNITED STATES' in name.upper():
            recommended_region = 'United States'
            recommended_country = 'United States'
        elif 'EUROPE' in name.upper() or 'EUROPEAN' in name.upper():
            recommended_region = 'Europe'
            recommended_country = 'Europe'
        else:
            # Default to Canada for Canadian-listed ETFs
            recommended_region = 'Canada'
            recommended_country = 'Canada'
        
        recommendations.append({
            'symbol': symbol,
            'name': name,
            'recommended_sector': 'Real Estate',
            'recommended_issuer_region': recommended_region,
            'recommended_listing_country': recommended_country,
            'recommended_industry': 'REIT ETF',
            'confidence': 0.95,
            'reasoning': f'REIT ETF - {name} tracks real estate investment trusts',
            'analysis': 'ETF providing exposure to real estate investment trusts'
        })
    
    return recommendations

def apply_reit_etf_fixes(holdings_data, recommendations):
    """Apply REIT ETF classification fixes"""
    
    # Create lookup for recommendations
    rec_lookup = {rec['symbol']: rec for rec in recommendations}
    
    updated_holdings = []
    fixed_count = 0
    
    for holding in holdings_data:
        symbol = holding.get('Symbol', '')
        
        if symbol in rec_lookup:
            recommendation = rec_lookup[symbol]
            
            # Update the holding with proper Real Estate classification
            holding['Sector'] = recommendation['recommended_sector']
            holding['Issuer_Region'] = recommendation['recommended_issuer_region']
            holding['Listing_Country'] = recommendation['recommended_listing_country']
            holding['Industry'] = recommendation['recommended_industry']
            
            # Add REIT ETF fix metadata
            holding['REIT_ETF_Fix_Applied'] = True
            holding['REIT_ETF_Confidence'] = recommendation['confidence']
            holding['REIT_ETF_Reasoning'] = recommendation['reasoning']
            holding['REIT_ETF_Analysis'] = recommendation['analysis']
            holding['Classification_Source'] = 'reit_etf_fix'
            
            fixed_count += 1
        else:
            # Keep existing classification source
            if 'Classification_Source' not in holding:
                holding['Classification_Source'] = holding.get('Enrichment_Source', 'none')
        
        updated_holdings.append(holding)
    
    print(f"Applied REIT ETF fixes to {fixed_count} holdings")
    return updated_holdings

def save_updated_holdings(holdings_data):
    """Save the updated holdings data with a new timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"holdings_detailed_{timestamp}.json"
    new_filepath = Path("data/output") / new_filename
    
    with open(new_filepath, 'w') as f:
        json.dump(holdings_data, f, indent=2)
    
    print(f"Saved updated holdings to: {new_filename}")
    return new_filepath

def main():
    """Main function to fix REIT ETF classifications"""
    try:
        # Load the latest holdings detailed file
        holdings_data, holdings_file = load_latest_holdings_detailed()
        
        print(f"Loaded {len(holdings_data)} holdings")
        
        # Identify REIT ETFs
        reit_etfs = identify_reit_etfs(holdings_data)
        
        print(f"\n🏢 Found {len(reit_etfs)} REIT ETFs:")
        print("=" * 60)
        
        if reit_etfs:
            for etf in reit_etfs:
                print(f"Symbol: {etf['Symbol']}")
                print(f"Name: {etf['Name']}")
                print(f"Current Sector: {etf['Current_Sector']}")
                print(f"Asset Type: {etf['Asset_Type']}")
                print(f"Market Value: ${etf['Market_Value']:,.2f} {etf['Currency']}")
                print(f"Current Classification Source: {etf['Classification_Source']}")
                print("-" * 40)
            
            # Create recommendations
            recommendations = create_reit_etf_recommendations(reit_etfs)
            
            print(f"\n🎯 REIT ETF Classification Fixes:")
            print("=" * 50)
            for rec in recommendations:
                print(f"Symbol: {rec['symbol']}")
                print(f"Name: {rec['name']}")
                print(f"Fixed Sector: {rec['recommended_sector']}")
                print(f"Fixed Region: {rec['recommended_issuer_region']}")
                print(f"Fixed Industry: {rec['recommended_industry']}")
                print(f"Confidence: {rec['confidence']}")
                print(f"Reasoning: {rec['reasoning']}")
                print("-" * 30)
            
            # Apply fixes
            updated_holdings = apply_reit_etf_fixes(holdings_data, recommendations)
            
            # Save updated holdings
            new_filepath = save_updated_holdings(updated_holdings)
            
            print(f"\n✅ Successfully fixed REIT ETF classifications!")
            print(f"📁 New file: {new_filepath.name}")
            print(f"📊 Updated {len(updated_holdings)} holdings")
            
            # Show summary of applied fixes
            fixed_count = sum(1 for h in updated_holdings 
                             if h.get('REIT_ETF_Fix_Applied', False))
            print(f"🏢 Applied REIT ETF fixes to {fixed_count} holdings")
            
        else:
            print("✅ No REIT ETFs found that need fixing!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
