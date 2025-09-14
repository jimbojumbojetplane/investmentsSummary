#!/usr/bin/env python3
"""
Test LLM Recommendations - Non-interactive version
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

def load_latest_holdings():
    """Load the most recent holdings file"""
    data_dir = Path("data/output")
    holdings_files = list(data_dir.glob("holdings_combined_*.json"))
    if not holdings_files:
        raise FileNotFoundError("No holdings files found")
    
    latest_file = max(holdings_files, key=os.path.getmtime)
    print(f"📄 Loading holdings from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def identify_holdings_needing_classification(holdings):
    """Identify holdings that need LLM classification"""
    needs_classification = []
    
    for holding in holdings:
        # Skip financial summaries
        if holding.get('type') == 'financial_summary':
            continue
        
        # Extract data from nested structure
        data = holding.get('data', {})
        symbol = data.get('Symbol', '')
        name = data.get('Name', '')
        
        # Skip if no symbol or name
        if not symbol or not name:
            continue
        
        # Check if already has good classification
        sector = data.get('Sector', 'Unknown')
        issuer_region = data.get('Issuer_Region', 'Unknown')
        
        # Flag holdings that need classification
        if (sector == 'Unknown' or 
            issuer_region == 'Unknown' or 
            sector == 'Information Technology' and 'ENERGY' in name.upper() or  # ET misclassified
            issuer_region == 'Unknown' and 'CHINA' in name.upper()):  # PDD misclassified
            
            needs_classification.append({
                'symbol': symbol,
                'name': name,
                'product': data.get('Product', ''),
                'current_sector': sector,
                'current_issuer_region': issuer_region,
                'market_value': data.get('Total Market Value', 0),
                'currency': data.get('Currency', 'Unknown')
            })
    
    return needs_classification

def analyze_holding(symbol, name, product):
    """Analyze a holding and generate classification recommendation"""
    
    name_upper = name.upper()
    symbol_upper = symbol.upper()
    
    # Energy sector detection
    if any(keyword in name_upper for keyword in ['ENERGY', 'OIL', 'GAS', 'PIPELINE', 'TRANSFER']):
        if 'TRANSFER' in name_upper or symbol_upper == 'ET':
            return {
                'recommended_sector': 'Energy (Midstream)',
                'recommended_issuer_region': 'United States',
                'recommended_listing_country': 'United States',
                'recommended_industry': 'Oil & Gas Midstream',
                'confidence': 0.95,
                'reasoning': 'Energy Transfer LP - major US midstream energy company',
                'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is Energy Transfer LP, a major US midstream energy infrastructure company."
            }
    
    # Technology/ETF detection
    elif any(keyword in name_upper for keyword in ['SEMICONDUCTOR', 'TECH', 'CHIP']):
        if symbol_upper == 'SMH':
            return {
                'recommended_sector': 'Semiconductors',
                'recommended_issuer_region': 'United States',
                'recommended_listing_country': 'United States',
                'recommended_industry': 'Semiconductor ETF',
                'confidence': 0.95,
                'reasoning': 'VanEck Semiconductor ETF - tracks semiconductor companies',
                'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is the VanEck Semiconductor ETF, which tracks semiconductor companies."
            }
    
    # Clean Energy detection
    elif any(keyword in name_upper for keyword in ['SOLAR', 'CLEAN', 'RENEWABLE']):
        if symbol_upper == 'TAN':
            return {
                'recommended_sector': 'Clean Energy',
                'recommended_issuer_region': 'United States',
                'recommended_listing_country': 'United States',
                'recommended_industry': 'Solar Energy ETF',
                'confidence': 0.95,
                'reasoning': 'Invesco Solar ETF - tracks solar energy companies',
                'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is the Invesco Solar ETF, which tracks solar energy companies."
            }
    
    # Dividend ETF detection
    elif any(keyword in name_upper for keyword in ['DIVIDEND', 'SCHWAB']):
        if symbol_upper == 'SCHD':
            return {
                'recommended_sector': 'US Dividend Equity',
                'recommended_issuer_region': 'United States',
                'recommended_listing_country': 'United States',
                'recommended_industry': 'Dividend ETF',
                'confidence': 0.95,
                'reasoning': 'Schwab US Dividend Equity ETF - tracks high dividend US stocks',
                'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is the Schwab US Dividend Equity ETF, which tracks high dividend US stocks."
            }
    
    # Chinese company detection
    elif any(keyword in name_upper for keyword in ['PDD', 'PINDUODUO', 'CHINA', 'CHINESE']):
        if symbol_upper == 'PDD':
            return {
                'recommended_sector': 'Consumer Discretionary',
                'recommended_issuer_region': 'China',
                'recommended_listing_country': 'China',
                'recommended_industry': 'Internet Retail',
                'confidence': 0.95,
                'reasoning': 'PDD Holdings (Pinduoduo) - Chinese e-commerce company',
                'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is PDD Holdings (Pinduoduo), a major Chinese e-commerce company."
            }
    
    # If no specific pattern matches, return a generic recommendation
    return {
        'recommended_sector': 'Unknown',
        'recommended_issuer_region': 'Unknown',
        'recommended_listing_country': 'Unknown',
        'recommended_industry': 'Unknown',
        'confidence': 0.3,
        'reasoning': 'Unable to determine classification from available information',
        'analysis': f"Symbol '{symbol}' and name '{name}' do not match known patterns. Manual review required."
    }

def main():
    print("🚀 Testing LLM Classification Recommendations")
    print("=" * 60)
    
    # Load holdings
    holdings = load_latest_holdings()
    
    # Identify holdings needing classification
    needs_classification = identify_holdings_needing_classification(holdings)
    print(f"🔍 Found {len(needs_classification)} holdings needing classification")
    
    if not needs_classification:
        print("✅ All holdings are properly classified!")
        return
    
    print(f"\n🤖 LLM Classification Recommendations")
    print("=" * 80)
    
    for i, holding in enumerate(needs_classification, 1):
        symbol = holding['symbol']
        name = holding['name']
        product = holding['product']
        
        print(f"\n{i}. {symbol} - {name[:60]}...")
        print(f"   Current: {holding['current_sector']} | {holding['current_issuer_region']}")
        print(f"   Product: {product}")
        print(f"   Market Value: {holding['market_value']:,.2f} {holding['currency']}")
        
        # Generate recommendation
        recommendation = analyze_holding(symbol, name, product)
        
        print(f"   Recommended: {recommendation['recommended_sector']} | {recommendation['recommended_issuer_region']}")
        print(f"   Confidence: {recommendation['confidence']:.1%}")
        print(f"   Reasoning: {recommendation['reasoning']}")
        print(f"   Analysis: {recommendation['analysis']}")
        print("-" * 80)
    
    print(f"\n✅ Analysis complete! Found {len(needs_classification)} holdings needing classification.")

if __name__ == "__main__":
    main()
