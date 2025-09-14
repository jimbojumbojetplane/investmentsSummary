#!/usr/bin/env python3
"""
Apply comprehensive LLM classifications to the holdings detailed file
This updates the holdings_detailed_*.json with improved classifications
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

def load_latest_comprehensive_classifications():
    """Load the most recent comprehensive classifications file"""
    output_dir = Path("data/output")
    classification_files = list(output_dir.glob("comprehensive_classifications_*.json"))
    
    if not classification_files:
        raise FileNotFoundError("No comprehensive_classifications_*.json files found")
    
    latest_file = max(classification_files, key=lambda f: f.stat().st_mtime)
    print(f"Loading latest comprehensive classifications: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def apply_classifications_to_holdings(holdings_data, classifications_data):
    """Apply comprehensive classifications to holdings data"""
    
    # Create a lookup dictionary for classifications by symbol
    classification_lookup = {}
    for classification in classifications_data:
        symbol = classification['symbol']
        classification_lookup[symbol] = classification
    
    print(f"Created classification lookup for {len(classification_lookup)} symbols")
    
    # Apply classifications to holdings
    updated_holdings = []
    applied_count = 0
    
    for holding in holdings_data:
        # Extract symbol directly from the holding (flat structure)
        symbol = holding.get('Symbol', '')
        
        if symbol in classification_lookup:
            classification = classification_lookup[symbol]
            
            # Update the holding with comprehensive classifications (flat structure)
            holding['Sector'] = classification['recommended_sector']
            holding['Issuer_Region'] = classification['recommended_issuer_region']
            holding['Listing_Country'] = classification['recommended_listing_country']
            holding['Industry'] = classification['recommended_industry']
            
            # Add classification metadata
            holding['Classification_Confidence'] = classification['confidence']
            holding['Classification_Reasoning'] = classification['reasoning']
            holding['Classification_Source'] = 'comprehensive_llm'
            holding['Classification_Applied'] = True
            
            applied_count += 1
        else:
            # Mark as not classified
            holding['Classification_Applied'] = False
            holding['Classification_Source'] = 'none'
        
        updated_holdings.append(holding)
    
    print(f"Applied classifications to {applied_count} holdings")
    return updated_holdings

def save_updated_holdings(holdings_data, original_file):
    """Save the updated holdings data with a new timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"holdings_detailed_{timestamp}.json"
    new_filepath = original_file.parent / new_filename
    
    with open(new_filepath, 'w') as f:
        json.dump(holdings_data, f, indent=2)
    
    print(f"Saved updated holdings to: {new_filename}")
    return new_filepath

def main():
    """Main function to apply comprehensive classifications to holdings detailed file"""
    try:
        # Load the latest files
        holdings_data, holdings_file = load_latest_holdings_detailed()
        classifications_data = load_latest_comprehensive_classifications()
        
        print(f"Loaded {len(holdings_data)} holdings")
        print(f"Loaded {len(classifications_data)} classifications")
        
        # Apply classifications
        updated_holdings = apply_classifications_to_holdings(holdings_data, classifications_data)
        
        # Save updated holdings
        new_filepath = save_updated_holdings(updated_holdings, holdings_file)
        
        print(f"\n✅ Successfully updated holdings detailed file!")
        print(f"📁 New file: {new_filepath.name}")
        print(f"📊 Updated {len(updated_holdings)} holdings with comprehensive classifications")
        
        # Show summary of applied classifications
        applied_count = sum(1 for h in updated_holdings 
                           if h.get('data', {}).get('Classification_Applied', False))
        print(f"🎯 Applied classifications to {applied_count} holdings")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
