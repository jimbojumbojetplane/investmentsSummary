#!/usr/bin/env python3
"""
Canadian ETF Enrichment using multiple free data sources
Alternative to Yahoo Finance for Canadian ETFs
"""

import requests
import json
import time
import pandas as pd
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CanadianETFEnricher:
    """Enrich Canadian ETF data using multiple free sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Comprehensive ETF mapping with accurate sector/industry classifications
        self.etf_mappings = {
            # iShares Canadian ETFs
            'XIC': {'name': 'iShares Core S&P/TSX Capped Composite Index ETF', 'sector': 'Equity', 'industry': 'Broad Market ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'XIU': {'name': 'iShares S&P/TSX 60 Index ETF', 'sector': 'Equity', 'industry': 'Large Cap ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'XDV': {'name': 'iShares Canadian Select Dividend Index ETF', 'sector': 'Equity', 'industry': 'Dividend ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'XSP': {'name': 'iShares Core S&P 500 Index ETF (CAD-Hedged)', 'sector': 'Equity', 'industry': 'Large Cap ETF', 'region': 'United States', 'listing_country': 'Canada', 'currency': 'CAD'},
            'XEF': {'name': 'iShares Core MSCI EAFE IMI Index ETF (CAD-Hedged)', 'sector': 'Equity', 'industry': 'International ETF', 'region': 'International', 'listing_country': 'Canada', 'currency': 'CAD'},
            'XEC': {'name': 'iShares Core MSCI Emerging Markets IMI Index ETF (CAD-Hedged)', 'sector': 'Equity', 'industry': 'Emerging Markets ETF', 'region': 'International', 'listing_country': 'Canada', 'currency': 'CAD'},
            'XBB': {'name': 'iShares Core Canadian Universe Bond Index ETF', 'sector': 'Fixed Income', 'industry': 'Government Bond ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'XSB': {'name': 'iShares Core Canadian Short Term Bond Index ETF', 'sector': 'Fixed Income', 'industry': 'Short Term Bond ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'XHY': {'name': 'iShares U.S. High Yield Bond Index ETF (CAD-Hedged)', 'sector': 'Fixed Income', 'industry': 'High Yield Bond ETF', 'region': 'United States', 'listing_country': 'Canada', 'currency': 'CAD'},
            'XRE': {'name': 'iShares S&P/TSX Capped REIT Index ETF', 'sector': 'Real Estate', 'industry': 'REIT ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            
            # Vanguard Canadian ETFs
            'VCN': {'name': 'Vanguard FTSE Canada All Cap Index ETF', 'sector': 'Equity', 'industry': 'Broad Market ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'VUN': {'name': 'Vanguard U.S. Total Market Index ETF', 'sector': 'Equity', 'industry': 'Broad Market ETF', 'region': 'United States', 'listing_country': 'Canada', 'currency': 'CAD'},
            'VIU': {'name': 'Vanguard FTSE Developed All Cap ex North America Index ETF', 'sector': 'Equity', 'industry': 'International ETF', 'region': 'International', 'listing_country': 'Canada', 'currency': 'CAD'},
            'VEE': {'name': 'Vanguard FTSE Emerging Markets All Cap Index ETF', 'sector': 'Equity', 'industry': 'Emerging Markets ETF', 'region': 'International', 'listing_country': 'Canada', 'currency': 'CAD'},
            'VAB': {'name': 'Vanguard Canadian Aggregate Bond Index ETF', 'sector': 'Fixed Income', 'industry': 'Government Bond ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'VSB': {'name': 'Vanguard Canadian Short-Term Bond Index ETF', 'sector': 'Fixed Income', 'industry': 'Short Term Bond ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            
            # BMO ETFs
            'ZCN': {'name': 'BMO S&P/TSX Capped Composite Index ETF', 'sector': 'Equity', 'industry': 'Broad Market ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'ZSP': {'name': 'BMO S&P 500 Index ETF', 'sector': 'Equity', 'industry': 'Large Cap ETF', 'region': 'United States', 'listing_country': 'Canada', 'currency': 'CAD'},
            'ZEA': {'name': 'BMO MSCI EAFE Hedged to CAD Index ETF', 'sector': 'Equity', 'industry': 'International ETF', 'region': 'International', 'listing_country': 'Canada', 'currency': 'CAD'},
            'ZEM': {'name': 'BMO MSCI Emerging Markets Index ETF', 'sector': 'Equity', 'industry': 'Emerging Markets ETF', 'region': 'International', 'listing_country': 'Canada', 'currency': 'CAD'},
            'ZRE': {'name': 'BMO Equal Weight REITs Index ETF', 'sector': 'Real Estate', 'industry': 'REIT ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            
            # Horizons ETFs
            'HXQ': {'name': 'Horizons NASDAQ-100 Index ETF', 'sector': 'Equity', 'industry': 'Technology ETF', 'region': 'United States', 'listing_country': 'Canada', 'currency': 'CAD'},
            'HXU': {'name': 'Horizons S&P/TSX 60 Bull Plus ETF', 'sector': 'Equity', 'industry': 'Leveraged ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'HXD': {'name': 'Horizons S&P/TSX 60 Bear Plus ETF', 'sector': 'Equity', 'industry': 'Inverse ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'MNY': {'name': 'Horizons Active CDN Money Market ETF', 'sector': 'Money Market', 'industry': 'Money Market ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'HISU.U': {'name': 'Horizons US Dollar High Interest Savings ETF', 'sector': 'Money Market', 'industry': 'Money Market ETF', 'region': 'United States', 'listing_country': 'Canada', 'currency': 'USD'},
            
            # US ETFs (your specific list)
            'XEH': {'name': 'iShares MSCI Europe IMI Index ETF', 'sector': 'Equity', 'industry': 'European ETF', 'region': 'Europe', 'listing_country': 'Canada', 'currency': 'CAD'},
            'SCHD': {'name': 'Schwab U.S. Dividend Equity ETF', 'sector': 'Equity', 'industry': 'Dividend ETF', 'region': 'United States', 'listing_country': 'United States', 'currency': 'USD'},
            'CDZ': {'name': 'iShares S&P/TSX Canadian Dividend Aristocrats Index ETF', 'sector': 'Equity', 'industry': 'Dividend ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'CMR': {'name': 'iShares Premium Money Market ETF', 'sector': 'Money Market', 'industry': 'Money Market ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'HYG': {'name': 'iShares iBoxx $ High Yield Corporate Bond ETF', 'sector': 'Fixed Income', 'industry': 'High Yield Bond ETF', 'region': 'United States', 'listing_country': 'United States', 'currency': 'USD'},
            'ICSH': {'name': 'iShares Ultra Short-Term Bond ETF', 'sector': 'Fixed Income', 'industry': 'Short Term Bond ETF', 'region': 'United States', 'listing_country': 'United States', 'currency': 'USD'},
            'IEV': {'name': 'iShares Europe ETF', 'sector': 'Equity', 'industry': 'European ETF', 'region': 'Europe', 'listing_country': 'United States', 'currency': 'USD'},
            'SMH': {'name': 'VanEck Semiconductor ETF', 'sector': 'Technology', 'industry': 'Semiconductor ETF', 'region': 'United States', 'listing_country': 'United States', 'currency': 'USD'},
            'TAN': {'name': 'Invesco Solar ETF', 'sector': 'Energy', 'industry': 'Solar Energy ETF', 'region': 'United States', 'listing_country': 'United States', 'currency': 'USD'},
            
            # Other Canadian ETFs
            'CASH': {'name': 'Purpose High Interest Savings ETF', 'sector': 'Money Market', 'industry': 'Money Market ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
        }
    
    def get_alpha_vantage_data(self, symbol: str, api_key: str = None) -> Dict:
        """Get data from Alpha Vantage (free tier)"""
        if not api_key:
            # Use demo key for testing
            api_key = "demo"
        
        try:
            # Try overview endpoint
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'Symbol' in data:
                    return {
                        'source': 'alpha_vantage',
                        'sector': data.get('Sector', 'Unknown'),
                        'industry': data.get('Industry', 'Unknown'),
                        'country': data.get('Country', 'Unknown'),
                        'exchange': data.get('Exchange', 'Unknown'),
                        'market_cap': data.get('MarketCapitalization', 0),
                        'description': data.get('Description', ''),
                        'website': data.get('Website', ''),
                        'employees': data.get('FullTimeEmployees', 0)
                    }
        except Exception as e:
            logger.warning(f"Alpha Vantage error for {symbol}: {e}")
        
        return {}
    
    def get_morningstar_canada_data(self, symbol: str) -> Dict:
        """Scrape basic data from Morningstar Canada (free tier)"""
        try:
            # Morningstar Canada ETF page structure
            url = f"https://www.morningstar.ca/ca/etfs/snapshot/snapshot.aspx?id={symbol}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Basic parsing - would need more sophisticated parsing for full data
                content = response.text
                
                # Extract basic info using simple text parsing
                data = {'source': 'morningstar_canada'}
                
                # Look for sector information in the page
                if 'Sector' in content:
                    data['has_morningstar_data'] = True
                else:
                    data['has_morningstar_data'] = False
                
                return data
        except Exception as e:
            logger.warning(f"Morningstar Canada error for {symbol}: {e}")
        
        return {}
    
    def get_etf_mapping_data(self, symbol: str) -> Dict:
        """Get data from our Canadian ETF mapping"""
        if symbol in self.etf_mappings:
            mapping = self.etf_mappings[symbol]
            return {
                'source': 'etf_mapping',
                'product_name': mapping['name'],
                'sector': mapping['sector'],
                'region': mapping['region'],
                'industry': f"{mapping['sector']} ETF",
                'listing_country': 'Canada',
                'currency': 'CAD',
                'confidence': 0.9
            }
        return {}
    
    def enrich_symbol(self, symbol: str, api_key: str = None) -> Dict:
        """Enrich a single Canadian ETF symbol"""
        logger.info(f"Enriching Canadian ETF: {symbol}")
        
        # Combine data from multiple sources
        enriched_data = {
            'symbol': symbol,
            'enrichment_sources': [],
            'classification_source': 'multiple_sources'
        }
        
        # 1. Try our ETF mapping first (most reliable for Canadian ETFs)
        mapping_data = self.get_etf_mapping_data(symbol)
        if mapping_data:
            enriched_data.update(mapping_data)
            enriched_data['enrichment_sources'].append('etf_mapping')
        
        # 2. Try Alpha Vantage for additional data
        av_data = self.get_alpha_vantage_data(symbol, api_key)
        if av_data:
            # Only use AV data if it doesn't conflict with our mapping
            if not enriched_data.get('sector') or enriched_data['sector'] == 'Unknown':
                enriched_data['sector'] = av_data.get('sector', 'Unknown')
            if not enriched_data.get('industry') or enriched_data['industry'] == 'Unknown':
                enriched_data['industry'] = av_data.get('industry', 'Unknown')
            
            enriched_data['enrichment_sources'].append('alpha_vantage')
        
        # 3. Try Morningstar Canada
        ms_data = self.get_morningstar_canada_data(symbol)
        if ms_data:
            enriched_data['enrichment_sources'].append('morningstar_canada')
        
        # Set confidence based on number of sources
        source_count = len(enriched_data['enrichment_sources'])
        enriched_data['enrichment_confidence'] = min(0.5 + (source_count * 0.2), 0.95)
        
        # Add timestamp
        enriched_data['last_verified_date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        return enriched_data
    
    def enrich_holdings(self, holdings_data: List[Dict], api_key: str = None) -> List[Dict]:
        """Enrich a list of holdings with Canadian ETF data"""
        enriched_holdings = []
        
        for holding in holdings_data:
            symbol = holding.get('Symbol', '')
            
            if not symbol:
                enriched_holdings.append(holding)
                continue
            
            # Get enrichment data
            enrichment = self.enrich_symbol(symbol, api_key)
            
            # Merge with existing holding data
            enriched_holding = holding.copy()
            
            # Update fields with enriched data
            for key, value in enrichment.items():
                if key not in ['symbol'] and value:
                    enriched_holding[key] = value
            
            # Ensure key fields are set
            if not enriched_holding.get('Asset_Type'):
                enriched_holding['Asset_Type'] = 'ETF'
            
            enriched_holdings.append(enriched_holding)
            
            # Rate limiting
            time.sleep(0.1)
        
        return enriched_holdings

def main():
    """Test the Canadian ETF enricher"""
    enricher = CanadianETFEnricher()
    
    # Test with the specific ETFs mentioned by the user
    test_symbols = ['XEH', 'SCHD', 'CDZ', 'CMR', 'HYG', 'MNY', 'ZRE', 'HISU.U', 'ICSH', 'IEV', 'SMH', 'TAN']
    
    for symbol in test_symbols:
        print(f"\n=== Enriching {symbol} ===")
        result = enricher.enrich_symbol(symbol)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
