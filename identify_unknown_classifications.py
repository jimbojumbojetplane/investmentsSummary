#!/usr/bin/env python3
"""
Identify symbols that have both sector and issuer region as "Unknown"
These are candidates for LLM classification augmentation
"""

import json
import pandas as pd
from pathlib import Path

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

def identify_unknown_classifications(holdings_data):
    """Identify symbols with both sector and issuer region as Unknown"""
    
    unknown_classifications = []
    
    for holding in holdings_data:
        symbol = holding.get('Symbol', '')
        name = holding.get('Name', '')
        sector = holding.get('Sector', '')
        issuer_region = holding.get('Issuer_Region', '')
        market_value = holding.get('Total Market Value', 0)
        enrichment_source = holding.get('Enrichment_Source', 'none')
        industry = holding.get('Industry', '')
        
        # Check if both sector and issuer region are Unknown
        if sector == 'Unknown' and issuer_region == 'Unknown':
            unknown_classifications.append({
                'Symbol': symbol,
                'Name': name,
                'Sector': sector,
                'Issuer_Region': issuer_region,
                'Industry': industry,
                'Market_Value': market_value,
                'Enrichment_Source': enrichment_source,
                'Currency': holding.get('Currency', 'CAD')
            })
    
    return unknown_classifications

def main():
    """Main function to identify unknown classifications"""
    try:
        # Load the latest holdings detailed file
        holdings_data, holdings_file = load_latest_holdings_detailed()
        
        print(f"Loaded {len(holdings_data)} holdings")
        
        # Identify unknown classifications
        unknown_classifications = identify_unknown_classifications(holdings_data)
        
        print(f"\n🔍 Found {len(unknown_classifications)} symbols with both Sector and Issuer_Region as 'Unknown':")
        print("=" * 80)
        
        if unknown_classifications:
            # Create DataFrame for better display
            df = pd.DataFrame(unknown_classifications)
            
            # Sort by market value (descending)
            df = df.sort_values('Market_Value', ascending=False)
            
            # Display the results
            for i, row in df.iterrows():
                print(f"Symbol: {row['Symbol']}")
                print(f"Name: {row['Name']}")
                print(f"Market Value: ${row['Market_Value']:,.2f} {row['Currency']}")
                print(f"Industry: {row['Industry']}")
                print(f"Enrichment Source: {row['Enrichment_Source']}")
                print("-" * 40)
            
            # Summary statistics
            total_value = df['Market_Value'].sum()
            print(f"\n📊 Summary:")
            print(f"Total symbols needing classification: {len(unknown_classifications)}")
            print(f"Total market value: ${total_value:,.2f}")
            print(f"Average market value: ${total_value/len(unknown_classifications):,.2f}")
            
            # Show by enrichment source
            print(f"\n📈 By Enrichment Source:")
            source_counts = df['Enrichment_Source'].value_counts()
            for source, count in source_counts.items():
                source_value = df[df['Enrichment_Source'] == source]['Market_Value'].sum()
                print(f"  {source}: {count} symbols (${source_value:,.2f})")
            
            # Save to file for further analysis
            output_file = "data/output/unknown_classifications_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(unknown_classifications, f, indent=2)
            print(f"\n💾 Saved detailed analysis to: {output_file}")
            
        else:
            print("✅ All symbols have at least one classification (Sector or Issuer_Region)!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
