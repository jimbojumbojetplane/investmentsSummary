#!/usr/bin/env python3
"""
Classify the remaining 3 symbols with Unknown sectors using targeted LLM classification
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_unknown_sectors_analysis():
    """Load the unknown sectors analysis"""
    analysis_file = Path("data/output/unknown_sectors_analysis.json")
    
    if not analysis_file.exists():
        raise FileNotFoundError("No unknown_sectors_analysis.json found. Run review_unknown_sectors.py first.")
    
    with open(analysis_file, 'r') as f:
        return json.load(f)

def create_remaining_symbol_recommendations(unknown_symbols):
    """Create LLM classification recommendations for remaining unknown symbols"""
    
    recommendations = []
    
    for symbol_data in unknown_symbols:
        symbol = symbol_data['Symbol']
        name = symbol_data['Name']
        issuer_region = symbol_data['Issuer_Region']
        
        # Create classification recommendations based on symbol and name analysis
        recommendation = create_remaining_symbol_recommendation(symbol, name, issuer_region)
        
        if recommendation:
            recommendation.update({
                'symbol': symbol,
                'name': name,
                'market_value': symbol_data['Market_Value'],
                'currency': symbol_data['Currency'],
                'current_sector': symbol_data['Sector'],
                'current_issuer_region': symbol_data['Issuer_Region'],
                'current_industry': symbol_data['Industry'],
                'has_change': True,
                'sector_changed': True,
                'region_changed': False  # Keep existing region
            })
            recommendations.append(recommendation)
    
    return recommendations

def create_remaining_symbol_recommendation(symbol, name, issuer_region):
    """Create classification recommendation for remaining unknown symbols"""
    
    symbol_upper = symbol.upper()
    name_upper = name.upper()
    
    # HISU.U - US High Interest Savings Account Fund
    if symbol_upper == 'HISU.U':
        return {
            'recommended_sector': 'Cash & Equivalents',
            'recommended_issuer_region': 'United States',
            'recommended_listing_country': 'Canada',
            'recommended_industry': 'High Interest Savings ETF',
            'confidence': 0.95,
            'reasoning': 'US High Interest Savings Account Fund - tracks high interest savings accounts',
            'analysis': 'Canadian-listed ETF providing exposure to US high interest savings accounts'
        }
    
    # XEH - iShares MSCI Europe IMI Index ETF CAD-Hedged
    elif symbol_upper == 'XEH':
        return {
            'recommended_sector': 'European Equity',
            'recommended_issuer_region': 'Europe',
            'recommended_listing_country': 'Canada',
            'recommended_industry': 'European Equity ETF (CAD Hedged)',
            'confidence': 0.95,
            'reasoning': 'iShares MSCI Europe IMI Index ETF - tracks European equity markets with CAD hedging',
            'analysis': 'Canadian-listed ETF providing CAD-hedged exposure to European equity markets'
        }
    
    # PDD - PDD Holdings (Pinduoduo)
    elif symbol_upper == 'PDD':
        return {
            'recommended_sector': 'Consumer Discretionary',
            'recommended_issuer_region': 'China',
            'recommended_listing_country': 'China',
            'recommended_industry': 'Internet Retail',
            'confidence': 0.95,
            'reasoning': 'PDD Holdings (Pinduoduo) - Chinese e-commerce company',
            'analysis': 'Chinese e-commerce company operating online retail platforms'
        }
    
    else:
        return {
            'recommended_sector': 'Unknown',
            'recommended_issuer_region': issuer_region,
            'recommended_listing_country': 'Unknown',
            'recommended_industry': 'Unknown',
            'confidence': 0.3,
            'reasoning': 'Unable to determine classification from available information',
            'analysis': 'Insufficient information for reliable classification'
        }

def apply_remaining_classifications(holdings_data, recommendations):
    """Apply remaining LLM classifications to holdings data"""
    
    # Create lookup for recommendations
    rec_lookup = {rec['symbol']: rec for rec in recommendations}
    
    updated_holdings = []
    applied_count = 0
    
    for holding in holdings_data:
        symbol = holding.get('Symbol', '')
        
        if symbol in rec_lookup:
            recommendation = rec_lookup[symbol]
            
            # Update the holding with remaining LLM classifications
            holding['Sector'] = recommendation['recommended_sector']
            holding['Issuer_Region'] = recommendation['recommended_issuer_region']
            holding['Listing_Country'] = recommendation['recommended_listing_country']
            holding['Industry'] = recommendation['recommended_industry']
            
            # Add LLM classification metadata
            holding['LLM_Classification_Applied'] = True
            holding['LLM_Confidence'] = recommendation['confidence']
            holding['LLM_Reasoning'] = recommendation['reasoning']
            holding['LLM_Analysis'] = recommendation['analysis']
            holding['Classification_Source'] = 'remaining_llm'
            
            applied_count += 1
        else:
            # Keep existing classification source
            if 'Classification_Source' not in holding:
                holding['Classification_Source'] = holding.get('Enrichment_Source', 'none')
        
        updated_holdings.append(holding)
    
    print(f"Applied remaining LLM classifications to {applied_count} holdings")
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
    """Main function to classify remaining unknown sectors"""
    try:
        # Load unknown sectors analysis
        unknown_symbols = load_unknown_sectors_analysis()
        print(f"Loaded {len(unknown_symbols)} symbols with unknown sectors")
        
        # Create LLM recommendations
        recommendations = create_remaining_symbol_recommendations(unknown_symbols)
        print(f"Created {len(recommendations)} LLM recommendations")
        
        # Display recommendations
        print("\n🎯 LLM Classification Recommendations for Remaining Unknown Sectors:")
        print("=" * 70)
        for rec in recommendations:
            print(f"Symbol: {rec['symbol']}")
            print(f"Name: {rec['name']}")
            print(f"Recommended Sector: {rec['recommended_sector']}")
            print(f"Recommended Region: {rec['recommended_issuer_region']}")
            print(f"Recommended Industry: {rec['recommended_industry']}")
            print(f"Confidence: {rec['confidence']}")
            print(f"Reasoning: {rec['reasoning']}")
            print("-" * 40)
        
        # Load current holdings data
        output_dir = Path("data/output")
        holdings_files = list(output_dir.glob("holdings_detailed_*.json"))
        latest_file = max(holdings_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            holdings_data = json.load(f)
        
        # Apply remaining classifications
        updated_holdings = apply_remaining_classifications(holdings_data, recommendations)
        
        # Save updated holdings
        new_filepath = save_updated_holdings(updated_holdings)
        
        print(f"\n✅ Successfully applied remaining LLM classifications!")
        print(f"📁 New file: {new_filepath.name}")
        print(f"📊 Updated {len(updated_holdings)} holdings")
        
        # Show summary of applied classifications
        applied_count = sum(1 for h in updated_holdings 
                           if h.get('LLM_Classification_Applied', False))
        print(f"🎯 Applied LLM classifications to {applied_count} holdings total")
        
        # Verify no more unknown sectors
        unknown_count = sum(1 for h in updated_holdings 
                           if h.get('Sector', '') == 'Unknown')
        print(f"🔍 Remaining symbols with Unknown sector: {unknown_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
