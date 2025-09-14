#!/usr/bin/env python3
"""
List all symbols with their current sector classifications
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

def list_all_symbols_with_sectors(holdings_data):
    """List all symbols with their sector classifications"""
    
    all_symbols = []
    
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
        
        all_symbols.append({
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
    
    return all_symbols

def main():
    """Main function to list all symbols with sectors"""
    try:
        # Load the latest holdings detailed file
        holdings_data, holdings_file = load_latest_holdings_detailed()
        
        print(f"Loaded {len(holdings_data)} holdings")
        
        # List all symbols with sectors
        all_symbols = list_all_symbols_with_sectors(holdings_data)
        
        # Create DataFrame for better display
        df = pd.DataFrame(all_symbols)
        
        # Sort by market value (descending)
        df = df.sort_values('Market_Value', ascending=False)
        
        print(f"\n📊 All {len(all_symbols)} Symbols with Sector Classifications:")
        print("=" * 100)
        
        # Display all symbols
        for i, row in df.iterrows():
            print(f"Symbol: {row['Symbol']}")
            print(f"Name: {row['Name']}")
            print(f"Sector: {row['Sector']}")
            print(f"Issuer Region: {row['Issuer_Region']}")
            print(f"Industry: {row['Industry']}")
            print(f"Market Value: ${row['Market_Value']:,.2f} {row['Currency']}")
            print(f"Classification Source: {row['Classification_Source']}")
            print(f"LLM Applied: {row['LLM_Applied']}")
            print("-" * 50)
        
        # Summary statistics
        total_value = df['Market_Value'].sum()
        print(f"\n📈 Summary Statistics:")
        print(f"Total symbols: {len(all_symbols)}")
        print(f"Total market value: ${total_value:,.2f}")
        
        # Count by sector
        print(f"\n🏷️ Symbols by Sector:")
        sector_counts = df['Sector'].value_counts()
        for sector, count in sector_counts.items():
            sector_value = df[df['Sector'] == sector]['Market_Value'].sum()
            print(f"  {sector}: {count} symbols (${sector_value:,.2f})")
        
        # Count by classification source
        print(f"\n🔍 Symbols by Classification Source:")
        source_counts = df['Classification_Source'].value_counts()
        for source, count in source_counts.items():
            source_value = df[df['Classification_Source'] == source]['Market_Value'].sum()
            print(f"  {source}: {count} symbols (${source_value:,.2f})")
        
        # Count by issuer region
        print(f"\n🌍 Symbols by Issuer Region:")
        region_counts = df['Issuer_Region'].value_counts()
        for region, count in region_counts.items():
            region_value = df[df['Issuer_Region'] == region]['Market_Value'].sum()
            print(f"  {region}: {count} symbols (${region_value:,.2f})")
        
        # Check for any unknown sectors
        unknown_sectors = df[df['Sector'] == 'Unknown']
        if len(unknown_sectors) > 0:
            print(f"\n⚠️ Symbols with Unknown Sector: {len(unknown_sectors)}")
            for _, row in unknown_sectors.iterrows():
                print(f"  {row['Symbol']}: {row['Name']}")
        else:
            print(f"\n✅ All symbols have known sectors!")
        
        # Save to file for reference
        output_file = "data/output/all_symbols_with_sectors.json"
        with open(output_file, 'w') as f:
            json.dump(all_symbols, f, indent=2)
        print(f"\n💾 Saved complete list to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
