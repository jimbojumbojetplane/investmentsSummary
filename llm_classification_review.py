#!/usr/bin/env python3
"""
LLM Classification Review Tool

This script generates LLM classification recommendations for holdings that need
classification and allows the user to review and approve them.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

class LLMClassificationReviewer:
    def __init__(self):
        self.data_dir = Path("data/output")
        self.recommendations_file = self.data_dir / "llm_recommendations.json"
        self.approved_file = self.data_dir / "approved_classifications.json"
        
    def load_latest_holdings(self) -> List[Dict[str, Any]]:
        """Load the most recent holdings file"""
        holdings_files = list(self.data_dir.glob("holdings_combined_*.json"))
        if not holdings_files:
            raise FileNotFoundError("No holdings files found")
        
        latest_file = max(holdings_files, key=os.path.getmtime)
        print(f"📄 Loading holdings from: {latest_file.name}")
        
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    def identify_holdings_needing_classification(self, holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
    
    def generate_llm_recommendations(self, holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate LLM classification recommendations"""
        recommendations = []
        
        for holding in holdings:
            symbol = holding['symbol']
            name = holding['name']
            product = holding['product']
            
            # Generate recommendation based on analysis
            recommendation = self.analyze_holding(symbol, name, product)
            
            if recommendation:
                recommendation.update({
                    'symbol': symbol,
                    'name': name,
                    'product': product,
                    'current_sector': holding['current_sector'],
                    'current_issuer_region': holding['current_issuer_region'],
                    'market_value': holding['market_value'],
                    'currency': holding['currency'],
                    'recommendation_id': f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'status': 'pending_review',
                    'created_at': datetime.now().isoformat()
                })
                recommendations.append(recommendation)
        
        return recommendations
    
    def analyze_holding(self, symbol: str, name: str, product: str) -> Optional[Dict[str, Any]]:
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
        
        # REIT detection
        elif any(keyword in name_upper for keyword in ['REIT', 'REAL ESTATE', 'PROPERTIES']):
            if symbol_upper == 'STAG':
                return {
                    'recommended_sector': 'Real Estate',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Industrial REIT',
                    'confidence': 0.95,
                    'reasoning': 'STAG Industrial - US industrial REIT',
                    'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is STAG Industrial, a US industrial REIT."
                }
            elif symbol_upper == 'NWH.UN':
                return {
                    'recommended_sector': 'Real Estate',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Healthcare REIT',
                    'confidence': 0.95,
                    'reasoning': 'Northwest Healthcare Properties REIT - healthcare real estate',
                    'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is Northwest Healthcare Properties REIT, a Canadian healthcare REIT."
                }
            elif symbol_upper == 'PMZ.UN':
                return {
                    'recommended_sector': 'Real Estate',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Retail REIT',
                    'confidence': 0.95,
                    'reasoning': 'Primaris Real Estate Investment Trust - retail real estate',
                    'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is Primaris Real Estate Investment Trust, a Canadian retail REIT."
                }
        
        # Telecom detection
        elif any(keyword in name_upper for keyword in ['ROGERS', 'COMMUNICATIONS', 'TELECOM']):
            if symbol_upper == 'RCI.B':
                return {
                    'recommended_sector': 'Communications',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Telecommunications',
                    'confidence': 0.95,
                    'reasoning': 'Rogers Communications - major Canadian telecom company',
                    'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is Rogers Communications, a major Canadian telecommunications company."
                }
        
        # Semiconductor company detection
        elif any(keyword in name_upper for keyword in ['SEMICONDUCTOR', 'CHIP', 'FOUNDRY']):
            if symbol_upper == 'TSM':
                return {
                    'recommended_sector': 'Information Technology',
                    'recommended_issuer_region': 'Taiwan',
                    'recommended_listing_country': 'Taiwan',
                    'recommended_industry': 'Semiconductors',
                    'confidence': 0.95,
                    'reasoning': 'Taiwan Semiconductor - world\'s largest semiconductor foundry',
                    'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is Taiwan Semiconductor, the world's largest semiconductor foundry."
                }
        
        # Bond detection
        elif any(keyword in name_upper for keyword in ['BOND', 'NOTE', 'DEBT']):
            if symbol_upper == '5565652':
                return {
                    'recommended_sector': 'Fixed Income',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Corporate Bonds',
                    'confidence': 0.9,
                    'reasoning': 'Bell Canada medium term note - corporate bond',
                    'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is a Bell Canada medium term note, which is a corporate bond."
                }
        
        # Pension/Retirement detection
        elif any(keyword in name_upper for keyword in ['PENSION', 'RETIREMENT', 'RRSP']):
            if symbol_upper == 'DC-PENSION':
                return {
                    'recommended_sector': 'Multi-Sector Equity',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Pension Plan',
                    'confidence': 0.9,
                    'reasoning': 'Defined contribution pension plan - diversified equity portfolio',
                    'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is a defined contribution pension plan with a diversified equity portfolio."
                }
            elif symbol_upper == 'RRSP-BELL':
                return {
                    'recommended_sector': 'Multi-Sector Equity',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Retirement Savings Plan',
                    'confidence': 0.9,
                    'reasoning': 'Registered retirement savings plan - diversified equity portfolio',
                    'analysis': f"Symbol '{symbol}' and name '{name}' indicate this is a registered retirement savings plan with a diversified equity portfolio."
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
    
    def save_recommendations(self, recommendations: List[Dict[str, Any]]):
        """Save recommendations to file"""
        with open(self.recommendations_file, 'w') as f:
            json.dump(recommendations, f, indent=2)
        print(f"💾 Saved {len(recommendations)} recommendations to {self.recommendations_file}")
    
    def display_recommendations(self, recommendations: List[Dict[str, Any]]):
        """Display recommendations for review"""
        print(f"\n🤖 LLM Classification Recommendations")
        print("=" * 80)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['symbol']} - {rec['name'][:60]}...")
            print(f"   Current: {rec['current_sector']} | {rec['current_issuer_region']}")
            print(f"   Recommended: {rec['recommended_sector']} | {rec['recommended_issuer_region']}")
            print(f"   Confidence: {rec['confidence']:.1%}")
            print(f"   Reasoning: {rec['reasoning']}")
            print(f"   Analysis: {rec['analysis']}")
            print(f"   Market Value: {rec['market_value']:,.2f} {rec['currency']}")
            print("-" * 80)
    
    def interactive_review(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Interactive review of recommendations"""
        approved = []
        
        print(f"\n📋 Interactive Review Mode")
        print("Commands: 'y' = approve, 'n' = reject, 's' = skip, 'q' = quit")
        print("=" * 80)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n[{i}/{len(recommendations)}] {rec['symbol']} - {rec['name'][:60]}...")
            print(f"Current: {rec['current_sector']} | {rec['current_issuer_region']}")
            print(f"Recommended: {rec['recommended_sector']} | {rec['recommended_issuer_region']}")
            print(f"Confidence: {rec['confidence']:.1%}")
            print(f"Reasoning: {rec['reasoning']}")
            print(f"Analysis: {rec['analysis']}")
            print(f"Market Value: {rec['market_value']:,.2f} {rec['currency']}")
            
            while True:
                response = input("\nApprove this recommendation? (y/n/s/q): ").lower().strip()
                
                if response == 'q':
                    print("Exiting review...")
                    return approved
                elif response == 'y':
                    rec['status'] = 'approved'
                    rec['approved_at'] = datetime.now().isoformat()
                    approved.append(rec)
                    print("✅ Approved")
                    break
                elif response == 'n':
                    rec['status'] = 'rejected'
                    rec['rejected_at'] = datetime.now().isoformat()
                    print("❌ Rejected")
                    break
                elif response == 's':
                    rec['status'] = 'skipped'
                    rec['skipped_at'] = datetime.now().isoformat()
                    print("⏭️ Skipped")
                    break
                else:
                    print("Please enter 'y', 'n', 's', or 'q'")
        
        return approved
    
    def save_approved_classifications(self, approved: List[Dict[str, Any]]):
        """Save approved classifications"""
        with open(self.approved_file, 'w') as f:
            json.dump(approved, f, indent=2)
        print(f"💾 Saved {len(approved)} approved classifications to {self.approved_file}")
    
    def run_review_process(self):
        """Run the complete review process"""
        print("🚀 LLM Classification Review Process")
        print("=" * 50)
        
        # Load holdings
        holdings = self.load_latest_holdings()
        
        # Identify holdings needing classification
        needs_classification = self.identify_holdings_needing_classification(holdings)
        print(f"🔍 Found {len(needs_classification)} holdings needing classification")
        
        if not needs_classification:
            print("✅ All holdings are properly classified!")
            return
        
        # Generate recommendations
        print("🤖 Generating LLM recommendations...")
        recommendations = self.generate_llm_recommendations(needs_classification)
        
        # Save recommendations
        self.save_recommendations(recommendations)
        
        # Display recommendations
        self.display_recommendations(recommendations)
        
        # Interactive review
        approved = self.interactive_review(recommendations)
        
        # Save approved classifications
        if approved:
            self.save_approved_classifications(approved)
            print(f"\n✅ Review complete! {len(approved)} classifications approved.")
        else:
            print("\n⏭️ No classifications were approved.")

def main():
    reviewer = LLMClassificationReviewer()
    reviewer.run_review_process()

if __name__ == "__main__":
    main()
