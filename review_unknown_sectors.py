#!/usr/bin/env python3
"""
Review all symbols with sector "Unknown" to see what still needs classification
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

def review_unknown_sectors(holdings_data):
    """Review all symbols with sector as Unknown"""
    
    unknown_sectors = []
    
    for holding in holdings_data:
        symbol = holding.get('Symbol', '')
        name = holding.get('Name', '')
        sector = holding.get('Sector', '')
        issuer_region = holding.get('Issuer_Region', '')
        industry = holding.get('Industry', '')
        market_value = holding.get('Total Market Value', 0)
        currency = holding.get('Currency', 'CAD')
        enrichment_source = holding.get('Enrichment_Source', 'none')
        llm_applied = holding.get('LLM_Classification_Applied', False)
        classification_source = holding.get('Classification_Source', 'none')
        
        # Check if sector is Unknown
        if sector == 'Unknown':
            unknown_sectors.append({
                'Symbol': symbol,
                'Name': name,
                'Sector': sector,
                'Issuer_Region': issuer_region,
                'Industry': industry,
                'Market_Value': market_value,
                'Currency': currency,
                'Enrichment_Source': enrichment_source,
                'LLM_Applied': llm_applied,
                'Classification_Source': classification_source
            })
    
    return unknown_sectors

def main():
    """Main function to review unknown sectors"""
    try:
        # Load the latest holdings detailed file
        holdings_data, holdings_file = load_latest_holdings_detailed()
        
        print(f"Loaded {len(holdings_data)} holdings")
        
        # Review unknown sectors
        unknown_sectors = review_unknown_sectors(holdings_data)
        
        print(f"\n🔍 Found {len(unknown_sectors)} symbols with Sector as 'Unknown':")
        print("=" * 80)
        
        if unknown_sectors:
            # Create DataFrame for better display
            df = pd.DataFrame(unknown_sectors)
            
            # Sort by market value (descending)
            df = df.sort_values('Market_Value', ascending=False)
            
            # Display the results
            for i, row in df.iterrows():
                print(f"Symbol: {row['Symbol']}")
                print(f"Name: {row['Name']}")
                print(f"Market Value: ${row['Market_Value']:,.2f} {row['Currency']}")
                print(f"Sector: {row['Sector']}")
                print(f"Issuer Region: {row['Issuer_Region']}")
                print(f"Industry: {row['Industry']}")
                print(f"Enrichment Source: {row['Enrichment_Source']}")
                print(f"LLM Applied: {row['LLM_Applied']}")
                print(f"Classification Source: {row['Classification_Source']}")
                print("-" * 40)
            
            # Summary statistics
            total_value = df['Market_Value'].sum()
            print(f"\n📊 Summary:")
            print(f"Total symbols with unknown sector: {len(unknown_sectors)}")
            print(f"Total market value: ${total_value:,.2f}")
            if len(unknown_sectors) > 0:
                print(f"Average market value: ${total_value/len(unknown_sectors):,.2f}")
            
            # Show by enrichment source
            print(f"\n📈 By Enrichment Source:")
            source_counts = df['Enrichment_Source'].value_counts()
            for source, count in source_counts.items():
                source_value = df[df['Enrichment_Source'] == source]['Market_Value'].sum()
                print(f"  {source}: {count} symbols (${source_value:,.2f})")
            
            # Show by classification source
            print(f"\n🏷️ By Classification Source:")
            class_counts = df['Classification_Source'].value_counts()
            for source, count in class_counts.items():
                source_value = df[df['Classification_Source'] == source]['Market_Value'].sum()
                print(f"  {source}: {count} symbols (${source_value:,.2f})")
            
            # Show by issuer region
            print(f"\n🌍 By Issuer Region:")
            region_counts = df['Issuer_Region'].value_counts()
            for region, count in region_counts.items():
                region_value = df[df['Issuer_Region'] == region]['Market_Value'].sum()
                print(f"  {region}: {count} symbols (${region_value:,.2f})")
            
            # Save to file for further analysis
            output_file = "data/output/unknown_sectors_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(unknown_sectors, f, indent=2)
            print(f"\n💾 Saved detailed analysis to: {output_file}")
            
        else:
            print("✅ All symbols have known sectors!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
