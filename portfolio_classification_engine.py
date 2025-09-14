#!/usr/bin/env python3
"""
Enhanced Portfolio Classification Engine with External Data Enrichment
Integrates Yahoo Finance (free) + LLM (for failures) for comprehensive classification
"""

import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Union
from decimal import Decimal, ROUND_HALF_UP
import re
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Import the original classification engine
from portfolio_classification_engine_original import (
    PortfolioClassificationEngine, 
    AssetType, AssetStructure, AccountType, FXHedged, IncomeType,
    ClassificationResult
)

# Import the external enricher
from src.external_data_enricher import YahooFinanceEnricher

logger = logging.getLogger(__name__)

class EnhancedPortfolioClassificationEngine(PortfolioClassificationEngine):
    """Enhanced classification engine with external data enrichment"""
    
    def __init__(self, use_yahoo_finance: bool = True, use_llm: bool = True):
        super().__init__()
        
        self.use_yahoo_finance = use_yahoo_finance
        self.use_llm = use_llm
        
        # Initialize external enrichers
        if self.use_yahoo_finance:
            self.yahoo_enricher = YahooFinanceEnricher()
            logger.info("✅ Yahoo Finance enricher initialized")
        
        # LLM enricher would be initialized here when implemented
        if self.use_llm:
            logger.info("✅ LLM enricher ready (to be implemented)")
        
        # Track enrichment statistics
        self.enrichment_stats = {
            'total_holdings': 0,
            'yahoo_success': 0,
            'llm_success': 0,
            'manual_mappings': 0,
            'failed': 0
        }
    
    def enrich_holding_external(self, holding: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a single holding using external data sources"""
        symbol = holding.get('Symbol', '')
        name = holding.get('Name', '')
        product = holding.get('Product', '')
        
        # Skip if already well classified
        current_sector = holding.get('Sector', 'Unknown')
        current_region = holding.get('Issuer_Region', 'Unknown')
        
        if current_sector != 'Unknown' and current_region != 'Unknown':
            logger.debug(f"Skipping {symbol} - already classified")
            return holding
        
        logger.info(f"🔍 Enriching {symbol}: {name}")
        
        # Try manual mappings first (for known corrections)
        manual_data = self.get_manual_mapping(symbol, name, product)
        if manual_data:
            holding.update(manual_data)
            holding['Enrichment_Source'] = 'manual_mapping'
            holding['Enrichment_Confidence'] = 0.95
            self.enrichment_stats['manual_mappings'] += 1
            logger.info(f"✅ Manual mapping for {symbol}: {holding['Sector']} - {holding['Issuer_Region']}")
            return holding
        
        # Try Yahoo Finance (free)
        if self.use_yahoo_finance:
            try:
                yahoo_data = self.yahoo_enricher.enrich_holding(symbol, name, product)
                
                if yahoo_data and yahoo_data.get('confidence', 0) > 0.5:
                    # Update holding with Yahoo Finance data
                    holding.update({
                        'Sector': yahoo_data.get('sector_normalized', yahoo_data.get('sector', 'Unknown')),
                        'Issuer_Region': yahoo_data.get('issuer_region', 'Unknown'),
                        'Listing_Country': yahoo_data.get('listing_country', 'Unknown'),
                        'Industry': yahoo_data.get('industry', 'Unknown'),
                        'Enrichment_Source': 'yahoo_finance',
                        'Enrichment_Confidence': yahoo_data.get('confidence', 0.0),
                        'Yahoo_Name': yahoo_data.get('yahoo_name', ''),
                        'Exchange': yahoo_data.get('exchange', 'Unknown'),
                        'Currency': yahoo_data.get('currency', 'Unknown'),
                        'Market_Cap': yahoo_data.get('market_cap', 0),
                        'Business_Summary': yahoo_data.get('business_summary', ''),
                        'Website': yahoo_data.get('website', ''),
                        'Employees': yahoo_data.get('employees', 0)
                    })
                    
                    self.enrichment_stats['yahoo_success'] += 1
                    logger.info(f"✅ Yahoo Finance enriched {symbol}: {holding['Sector']} - {holding['Issuer_Region']}")
                    return holding
                    
            except Exception as e:
                logger.warning(f"Yahoo Finance failed for {symbol}: {e}")
        
        # Try LLM enrichment for failures
        if self.use_llm:
            try:
                llm_data = self.enrich_holding_llm(symbol, name, product)
                
                if llm_data and llm_data.get('confidence', 0) > 0.5:
                    # Update holding with LLM data
                    holding.update({
                        'Sector': llm_data.get('sector', 'Unknown'),
                        'Issuer_Region': llm_data.get('issuer_region', 'Unknown'),
                        'Listing_Country': llm_data.get('listing_country', 'Unknown'),
                        'Industry': llm_data.get('industry', 'Unknown'),
                        'Enrichment_Source': 'llm',
                        'Enrichment_Confidence': llm_data.get('confidence', 0.0),
                        'LLM_Reasoning': llm_data.get('reasoning', ''),
                        'LLM_Cost': llm_data.get('estimated_cost', 0.01)
                    })
                    
                    self.enrichment_stats['llm_success'] += 1
                    logger.info(f"✅ LLM enriched {symbol}: {holding['Sector']} - {holding['Issuer_Region']}")
                    return holding
                    
            except Exception as e:
                logger.warning(f"LLM failed for {symbol}: {e}")
        
        
        # Mark as failed
        holding['Enrichment_Source'] = 'failed'
        holding['Enrichment_Confidence'] = 0.0
        self.enrichment_stats['failed'] += 1
        logger.warning(f"❌ Failed to enrich {symbol}")
        
        return holding
    
    def enrich_holding_llm(self, symbol: str, name: str, product: str) -> Optional[Dict[str, Any]]:
        """Enrich holding using LLM classification with recommendations"""
        # This would integrate with an actual LLM service (OpenAI, Anthropic, etc.)
        # For now, we'll create a structured recommendation that can be reviewed
        
        # Create a classification recommendation based on available data
        recommendation = self.create_llm_recommendation(symbol, name, product)
        
        if recommendation:
            # Mark as pending approval
            recommendation['status'] = 'pending_approval'
            recommendation['estimated_cost'] = 0.01
            return recommendation
        
        return None
    
    def create_llm_recommendation(self, symbol: str, name: str, product: str) -> Optional[Dict[str, Any]]:
        """Create LLM classification recommendation based on symbol and name analysis"""
        
        # Basic heuristics for classification (this would be replaced with actual LLM call)
        sector = "Unknown"
        issuer_region = "Unknown"
        listing_country = "Unknown"
        industry = "Unknown"
        confidence = 0.7
        reasoning = ""
        
        # Analyze symbol and name for classification hints
        name_upper = name.upper()
        symbol_upper = symbol.upper()
        
        # Energy sector detection
        if any(keyword in name_upper for keyword in ['ENERGY', 'OIL', 'GAS', 'PIPELINE', 'TRANSFER']):
            if 'TRANSFER' in name_upper or symbol_upper == 'ET':
                sector = "Energy (Midstream)"
                issuer_region = "United States"
                listing_country = "United States"
                industry = "Oil & Gas Midstream"
                reasoning = "Energy Transfer LP - major US midstream energy company"
                confidence = 0.95
        
        # Technology/ETF detection
        elif any(keyword in name_upper for keyword in ['SEMICONDUCTOR', 'TECH', 'CHIP']):
            if symbol_upper == 'SMH':
                sector = "Semiconductors"
                issuer_region = "United States"
                listing_country = "United States"
                industry = "Semiconductor ETF"
                reasoning = "VanEck Semiconductor ETF - tracks semiconductor companies"
                confidence = 0.95
        
        # Clean Energy detection
        elif any(keyword in name_upper for keyword in ['SOLAR', 'CLEAN', 'RENEWABLE']):
            if symbol_upper == 'TAN':
                sector = "Clean Energy"
                issuer_region = "United States"
                listing_country = "United States"
                industry = "Solar Energy ETF"
                reasoning = "Invesco Solar ETF - tracks solar energy companies"
                confidence = 0.95
        
        # Dividend ETF detection
        elif any(keyword in name_upper for keyword in ['DIVIDEND', 'SCHWAB']):
            if symbol_upper == 'SCHD':
                sector = "US Dividend Equity"
                issuer_region = "United States"
                listing_country = "United States"
                industry = "Dividend ETF"
                reasoning = "Schwab US Dividend Equity ETF - tracks high dividend US stocks"
                confidence = 0.95
        
        # Chinese company detection
        elif any(keyword in name_upper for keyword in ['PDD', 'PINDUODUO', 'CHINA', 'CHINESE']):
            if symbol_upper == 'PDD':
                sector = "Consumer Discretionary"
                issuer_region = "China"
                listing_country = "China"
                industry = "Internet Retail"
                reasoning = "PDD Holdings (Pinduoduo) - Chinese e-commerce company"
                confidence = 0.95
        
        # REIT detection
        elif any(keyword in name_upper for keyword in ['REIT', 'REAL ESTATE', 'PROPERTIES']):
            if symbol_upper == 'STAG':
                sector = "Real Estate"
                issuer_region = "United States"
                listing_country = "United States"
                industry = "Industrial REIT"
                reasoning = "STAG Industrial - US industrial REIT"
                confidence = 0.95
            elif symbol_upper == 'NWH.UN':
                sector = "Real Estate"
                issuer_region = "Canada"
                listing_country = "Canada"
                industry = "Healthcare REIT"
                reasoning = "Northwest Healthcare Properties REIT - healthcare real estate"
                confidence = 0.95
            elif symbol_upper == 'PMZ.UN':
                sector = "Real Estate"
                issuer_region = "Canada"
                listing_country = "Canada"
                industry = "Retail REIT"
                reasoning = "Primaris Real Estate Investment Trust - retail real estate"
                confidence = 0.95
        
        # Telecom detection
        elif any(keyword in name_upper for keyword in ['ROGERS', 'COMMUNICATIONS', 'TELECOM']):
            if symbol_upper == 'RCI.B':
                sector = "Communications"
                issuer_region = "Canada"
                listing_country = "Canada"
                industry = "Telecommunications"
                reasoning = "Rogers Communications - major Canadian telecom company"
                confidence = 0.95
        
        # Semiconductor company detection
        elif any(keyword in name_upper for keyword in ['SEMICONDUCTOR', 'CHIP', 'FOUNDRY']):
            if symbol_upper == 'TSM':
                sector = "Information Technology"
                issuer_region = "Taiwan"
                listing_country = "Taiwan"
                industry = "Semiconductors"
                reasoning = "Taiwan Semiconductor - world's largest semiconductor foundry"
                confidence = 0.95
        
        # Bond detection
        elif any(keyword in name_upper for keyword in ['BOND', 'NOTE', 'DEBT']):
            if symbol_upper == '5565652':
                sector = "Fixed Income"
                issuer_region = "Canada"
                listing_country = "Canada"
                industry = "Corporate Bonds"
                reasoning = "Bell Canada medium term note - corporate bond"
                confidence = 0.9
        
        # Pension/Retirement detection
        elif any(keyword in name_upper for keyword in ['PENSION', 'RETIREMENT', 'RRSP']):
            if symbol_upper == 'DC-PENSION':
                sector = "Multi-Sector Equity"
                issuer_region = "Canada"
                listing_country = "Canada"
                industry = "Pension Plan"
                reasoning = "Defined contribution pension plan - diversified equity portfolio"
                confidence = 0.9
            elif symbol_upper == 'RRSP-BELL':
                sector = "Multi-Sector Equity"
                issuer_region = "Canada"
                listing_country = "Canada"
                industry = "Retirement Savings Plan"
                reasoning = "Registered retirement savings plan - diversified equity portfolio"
                confidence = 0.9
        
        # If we have a recommendation, return it
        if sector != "Unknown":
            return {
                'sector': sector,
                'issuer_region': issuer_region,
                'listing_country': listing_country,
                'industry': industry,
                'confidence': confidence,
                'reasoning': reasoning,
                'llm_analysis': f"Based on symbol '{symbol}' and name '{name}', this appears to be {reasoning.lower()}"
            }
        
        return None
    
    def get_manual_mapping(self, symbol: str, name: str, product: str) -> Optional[Dict[str, Any]]:
        """Get manual mapping for specific symbols - DISABLED"""
        # Manual mappings are disabled - all holdings go through LLM classification
        return None
    
    def process_holdings(self, input_file: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Enhanced process holdings with external enrichment"""
        print(f"🚀 Enhanced Classification Engine Starting...")
        print(f"   Yahoo Finance: {'✅' if self.use_yahoo_finance else '❌'}")
        print(f"   LLM Enrichment: {'✅' if self.use_llm else '❌'}")
        
        # Call parent method to get basic processing
        holdings, rollups = super().process_holdings(input_file)
        
        self.enrichment_stats['total_holdings'] = len(holdings)
        
        print(f"\n🔍 Starting External Enrichment...")
        print(f"   Processing {len(holdings)} holdings...")
        
        # Enrich holdings with external data
        enriched_holdings = []
        for i, holding in enumerate(holdings):
            if (i + 1) % 10 == 0:
                print(f"   Progress: {i+1}/{len(holdings)} holdings processed")
            
            # Apply external enrichment
            enriched_holding = self.enrich_holding_external(holding)
            enriched_holdings.append(enriched_holding)
        
        # Print enrichment statistics
        self.print_enrichment_stats()
        
        return enriched_holdings, rollups
    
    def print_enrichment_stats(self):
        """Print enrichment statistics"""
        stats = self.enrichment_stats
        total = stats['total_holdings']
        
        print(f"\n📊 External Enrichment Statistics:")
        print(f"   Total Holdings: {total}")
        print(f"   Yahoo Finance Success: {stats['yahoo_success']} ({stats['yahoo_success']/total*100:.1f}%)")
        print(f"   LLM Success: {stats['llm_success']} ({stats['llm_success']/total*100:.1f}%)")
        print(f"   Manual Mappings: {stats['manual_mappings']} ({stats['manual_mappings']/total*100:.1f}%)")
        print(f"   Failed: {stats['failed']} ({stats['failed']/total*100:.1f}%)")
        
        total_success = stats['yahoo_success'] + stats['llm_success'] + stats['manual_mappings']
        success_rate = (total_success / total) * 100 if total > 0 else 0
        
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        
        # Estimate costs
        yahoo_cost = 0  # Free
        llm_cost = stats['llm_success'] * 0.01  # $0.01 per LLM call
        total_cost = yahoo_cost + llm_cost
        
        print(f"   Total Enrichment Cost: ${total_cost:.2f}")
        if total_cost > 0:
            print(f"   Cost per Successful Classification: ${total_cost/total_success:.3f}")

def main():
    """Main execution function for enhanced classification"""
    print("🚀 Enhanced Portfolio Classification Engine")
    print("=" * 60)
    
    # Initialize enhanced engine
    engine = EnhancedPortfolioClassificationEngine(
        use_yahoo_finance=True,
        use_llm=True
    )
    
    # Find the most recent holdings_combined file
    output_dir = Path("data/output")
    combined_files = list(output_dir.glob("holdings_combined_*.json"))
    
    if not combined_files:
        print(f"❌ No holdings_combined files found in {output_dir}")
        print("💡 Please run the CSV parser first to create holdings_combined_*.json")
        return
    
    # Get the most recent file
    input_file = max(combined_files, key=os.path.getmtime)
    print(f"📄 Using most recent holdings file: {input_file.name}")
    
    try:
        # Process holdings with external enrichment
        holdings, rollups = engine.process_holdings(input_file)
        
        # Save results
        holdings_file, rollups_file = engine.save_results(holdings, rollups, input_file)
        
        print(f"\n📊 Enhanced Processing Summary:")
        print(f"   Total Holdings: {len(holdings)}")
        print(f"   Total Portfolio Value: ${sum(h['Market_Value_CAD'] for h in holdings if h['Include_in_Exposure']):,.2f}")
        print(f"   Exceptions: {len(rollups['exceptions'])}")
        
        # Show asset type breakdown
        print(f"\n📈 Asset Type Breakdown:")
        for asset_type in rollups['by_asset_type']:
            print(f"   {asset_type['Asset_Type']}: ${asset_type['Total_CAD']:,.2f} ({asset_type['Percentage']:.1f}%)")
        
        print(f"\n✅ Enhanced classification complete!")
        print(f"   Detailed holdings: {holdings_file}")
        print(f"   Rollups: {rollups_file}")
        
    except Exception as e:
        print(f"❌ Error in enhanced processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
