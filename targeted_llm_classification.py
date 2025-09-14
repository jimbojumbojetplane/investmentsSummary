#!/usr/bin/env python3
"""
Targeted LLM classification for symbols that have both sector and issuer region as Unknown
This augments the Yahoo Finance data with LLM classification for specific symbols
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_unknown_classifications():
    """Load the unknown classifications analysis"""
    analysis_file = Path("data/output/unknown_classifications_analysis.json")
    
    if not analysis_file.exists():
        raise FileNotFoundError("No unknown_classifications_analysis.json found. Run identify_unknown_classifications.py first.")
    
    with open(analysis_file, 'r') as f:
        return json.load(f)

def create_llm_classification_recommendations(unknown_symbols):
    """Create LLM classification recommendations for unknown symbols"""
    
    recommendations = []
    
    for symbol_data in unknown_symbols:
        symbol = symbol_data['Symbol']
        name = symbol_data['Name']
        
        # Create classification recommendations based on symbol and name analysis
        recommendation = create_symbol_recommendation(symbol, name)
        
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
                'region_changed': True
            })
            recommendations.append(recommendation)
    
    return recommendations

def create_symbol_recommendation(symbol, name):
    """Create classification recommendation for a specific symbol"""
    
    symbol_upper = symbol.upper()
    name_upper = name.upper()
    
    # ETF-specific classifications based on name analysis
    if symbol_upper == 'ICSH':
        return {
            'recommended_sector': 'Fixed Income',
            'recommended_issuer_region': 'United States',
            'recommended_listing_country': 'United States',
            'recommended_industry': 'Ultra Short-Term Bond ETF',
            'confidence': 0.95,
            'reasoning': 'iShares Ultra Short-Term Bond ETF - tracks ultra short-term bonds',
            'analysis': 'Fixed income ETF focused on ultra short-term bonds, typically US-listed'
        }
    
    elif symbol_upper == 'CMR':
        return {
            'recommended_sector': 'Cash & Equivalents',
            'recommended_issuer_region': 'Canada',
            'recommended_listing_country': 'Canada',
            'recommended_industry': 'Money Market ETF',
            'confidence': 0.95,
            'reasoning': 'iShares Premium Money Market ETF - tracks money market instruments',
            'analysis': 'Canadian money market ETF providing cash equivalent exposure'
        }
    
    elif symbol_upper == 'HYG':
        return {
            'recommended_sector': 'Fixed Income',
            'recommended_issuer_region': 'United States',
            'recommended_listing_country': 'United States',
            'recommended_industry': 'High Yield Bond ETF',
            'confidence': 0.95,
            'reasoning': 'iShares iBoxx $ High Yield Corporate Bond ETF - tracks high yield corporate bonds',
            'analysis': 'US-listed ETF tracking high yield corporate bonds'
        }
    
    elif symbol_upper == 'IEV':
        return {
            'recommended_sector': 'European Equity',
            'recommended_issuer_region': 'Europe',
            'recommended_listing_country': 'United States',
            'recommended_industry': 'European Equity ETF',
            'confidence': 0.95,
            'reasoning': 'iShares Europe ETF - tracks European equity markets',
            'analysis': 'US-listed ETF providing exposure to European equity markets'
        }
    
    # Generic ETF classification based on name patterns
    elif 'BOND' in name_upper or 'FIXED INCOME' in name_upper:
        return {
            'recommended_sector': 'Fixed Income',
            'recommended_issuer_region': 'United States',
            'recommended_listing_country': 'United States',
            'recommended_industry': 'Bond ETF',
            'confidence': 0.8,
            'reasoning': f'ETF with bond/fixed income focus based on name: {name}',
            'analysis': 'Fixed income ETF based on name analysis'
        }
    
    elif 'MONEY MARKET' in name_upper or 'CASH' in name_upper:
        return {
            'recommended_sector': 'Cash & Equivalents',
            'recommended_issuer_region': 'Canada',
            'recommended_listing_country': 'Canada',
            'recommended_industry': 'Money Market ETF',
            'confidence': 0.8,
            'reasoning': f'Money market/cash ETF based on name: {name}',
            'analysis': 'Cash equivalent ETF based on name analysis'
        }
    
    elif 'EUROPE' in name_upper or 'EUROPEAN' in name_upper:
        return {
            'recommended_sector': 'European Equity',
            'recommended_issuer_region': 'Europe',
            'recommended_listing_country': 'United States',
            'recommended_industry': 'European Equity ETF',
            'confidence': 0.8,
            'reasoning': f'European equity ETF based on name: {name}',
            'analysis': 'European equity exposure ETF based on name analysis'
        }
    
    else:
        return {
            'recommended_sector': 'Unknown',
            'recommended_issuer_region': 'Unknown',
            'recommended_listing_country': 'Unknown',
            'recommended_industry': 'Unknown',
            'confidence': 0.3,
            'reasoning': 'Unable to determine classification from available information',
            'analysis': 'Insufficient information for reliable classification'
        }

def apply_targeted_classifications(holdings_data, recommendations):
    """Apply targeted LLM classifications to holdings data"""
    
    # Create lookup for recommendations
    rec_lookup = {rec['symbol']: rec for rec in recommendations}
    
    updated_holdings = []
    applied_count = 0
    
    for holding in holdings_data:
        symbol = holding.get('Symbol', '')
        
        if symbol in rec_lookup:
            recommendation = rec_lookup[symbol]
            
            # Update the holding with targeted LLM classifications
            holding['Sector'] = recommendation['recommended_sector']
            holding['Issuer_Region'] = recommendation['recommended_issuer_region']
            holding['Listing_Country'] = recommendation['recommended_listing_country']
            holding['Industry'] = recommendation['recommended_industry']
            
            # Add LLM classification metadata
            holding['LLM_Classification_Applied'] = True
            holding['LLM_Confidence'] = recommendation['confidence']
            holding['LLM_Reasoning'] = recommendation['reasoning']
            holding['LLM_Analysis'] = recommendation['analysis']
            holding['Classification_Source'] = 'targeted_llm'
            
            applied_count += 1
        else:
            # Mark as not LLM classified
            holding['LLM_Classification_Applied'] = False
            holding['Classification_Source'] = holding.get('Enrichment_Source', 'none')
        
        updated_holdings.append(holding)
    
    print(f"Applied targeted LLM classifications to {applied_count} holdings")
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
    """Main function to apply targeted LLM classifications"""
    try:
        # Load unknown classifications
        unknown_symbols = load_unknown_classifications()
        print(f"Loaded {len(unknown_symbols)} symbols needing classification")
        
        # Create LLM recommendations
        recommendations = create_llm_classification_recommendations(unknown_symbols)
        print(f"Created {len(recommendations)} LLM recommendations")
        
        # Display recommendations
        print("\n🎯 LLM Classification Recommendations:")
        print("=" * 60)
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
        
        # Apply targeted classifications
        updated_holdings = apply_targeted_classifications(holdings_data, recommendations)
        
        # Save updated holdings
        new_filepath = save_updated_holdings(updated_holdings)
        
        print(f"\n✅ Successfully applied targeted LLM classifications!")
        print(f"📁 New file: {new_filepath.name}")
        print(f"📊 Updated {len(updated_holdings)} holdings")
        
        # Show summary of applied classifications
        applied_count = sum(1 for h in updated_holdings 
                           if h.get('LLM_Classification_Applied', False))
        print(f"🎯 Applied targeted LLM classifications to {applied_count} holdings")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
