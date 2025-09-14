#!/usr/bin/env python3
"""
External Data Enricher using Yahoo Finance (FREE)
Enriches holdings with sector, region, and other classification data
"""

import yfinance as yf
import re
import time
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class YahooFinanceEnricher:
    """Enriches holdings data using free Yahoo Finance API"""
    
    def __init__(self, cache_file: str = "data/output/yfinance_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
        
        # Country to region mapping
        self.country_to_region = {
            'United States': 'United States',
            'Canada': 'Canada',
            'United Kingdom': 'Europe',
            'Germany': 'Europe',
            'France': 'Europe',
            'Netherlands': 'Europe',
            'Switzerland': 'Europe',
            'Italy': 'Europe',
            'Spain': 'Europe',
            'Japan': 'Asia',
            'China': 'Asia',
            'Hong Kong': 'Asia',
            'South Korea': 'Asia',
            'Taiwan': 'Asia',
            'India': 'Asia',
            'Australia': 'Asia',
            'Brazil': 'South America',
            'Mexico': 'North America',
            'Argentina': 'South America',
            'Chile': 'South America'
        }
        
        # Sector normalization mapping
        self.sector_mapping = {
            'Healthcare': 'Healthcare',
            'Technology': 'Information Technology',
            'Financial Services': 'Financials',
            'Communication Services': 'Communications',
            'Consumer Cyclical': 'Consumer Discretionary',
            'Consumer Defensive': 'Consumer Staples',
            'Energy': 'Energy',
            'Industrials': 'Industrials',
            'Materials': 'Materials',
            'Real Estate': 'Real Estate',
            'Utilities': 'Utilities',
            'Basic Materials': 'Materials',
            'Consumer Goods': 'Consumer Staples'
        }
        
        # ETF name patterns for classification
        self.etf_patterns = {
            'canada': ['canadian', 'canada', 'tsx', 'toronto'],
            'us': ['us', 'united states', 's&p', 'sp500', 'nasdaq', 'dow'],
            'europe': ['europe', 'european', 'euro', 'ftse', 'stoxx'],
            'asia': ['asia', 'asian', 'china', 'japan', 'emerging'],
            'global': ['global', 'world', 'international', 'developed'],
            'dividend': ['dividend', 'income', 'yield'],
            'bond': ['bond', 'fixed income', 'treasury', 'corporate'],
            'reit': ['reit', 'real estate', 'property'],
            'technology': ['tech', 'technology', 'innovation', 'digital'],
            'healthcare': ['health', 'healthcare', 'biotech', 'pharma'],
            'energy': ['energy', 'oil', 'gas', 'renewable'],
            'financial': ['financial', 'bank', 'finance']
        }
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cached enrichment data"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save enrichment data to cache"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _normalize_canadian_symbol(self, symbol: str) -> str:
        """Convert Canadian symbols to Yahoo Finance format"""
        if symbol.endswith('.B') or symbol.endswith('.A'):
            return symbol.replace('.B', '.TO').replace('.A', '.TO')
        elif not symbol.endswith('.TO') and not symbol.endswith('.V'):
            # Check if it's a Canadian symbol by context
            if any(indicator in symbol for indicator in ['RCI', 'CNQ', 'CVE', 'ENB', 'PPL', 'T']):
                return symbol + '.TO'
        return symbol
    
    def _parse_etf_name(self, name: str, symbol: str) -> Dict[str, str]:
        """Parse ETF name to extract region and sector information"""
        name_lower = name.lower()
        symbol_lower = symbol.lower()
        
        result = {
            'sector': 'Unknown',
            'issuer_region': 'Unknown',
            'confidence': 0.6  # Medium confidence for name parsing
        }
        
        # Determine region
        for region, patterns in self.etf_patterns.items():
            if region in ['canada', 'us', 'europe', 'asia', 'global']:
                if any(pattern in name_lower for pattern in patterns):
                    result['issuer_region'] = region.title()
                    break
        
        # Determine sector/type
        for sector, patterns in self.etf_patterns.items():
            if sector in ['dividend', 'bond', 'reit', 'technology', 'healthcare', 'energy', 'financial']:
                if any(pattern in name_lower for pattern in patterns):
                    result['sector'] = sector.title()
                    break
        
        # Special handling for dividend ETFs
        if 'dividend' in name_lower:
            result['sector'] = 'Multi-Sector Equity'
        
        return result
    
    def enrich_holding(self, symbol: str, name: str, product_type: str) -> Dict[str, Any]:
        """Enrich a single holding with external data"""
        
        # Check cache first
        cache_key = f"{symbol}_{name}"
        if cache_key in self.cache:
            logger.info(f"Using cached data for {symbol}")
            return self.cache[cache_key]
        
        logger.info(f"Enriching {symbol}: {name}")
        
        enrichment_data = {
            'symbol': symbol,
            'name': name,
            'product_type': product_type,
            'sector': 'Unknown',
            'issuer_region': 'Unknown',
            'listing_country': 'Unknown',
            'industry': 'Unknown',
            'confidence': 0.0,
            'source': 'none',
            'error': None
        }
        
        try:
            # Try Yahoo Finance first
            yahoo_data = self._enrich_with_yahoo_finance(symbol, name)
            if yahoo_data and yahoo_data['confidence'] > 0.5:
                enrichment_data.update(yahoo_data)
                enrichment_data['source'] = 'yahoo_finance'
            else:
                # Fall back to name parsing for ETFs
                if 'ETF' in product_type or 'ETN' in product_type:
                    name_data = self._parse_etf_name(name, symbol)
                    if name_data['confidence'] > 0.5:
                        enrichment_data.update(name_data)
                        enrichment_data['source'] = 'name_parsing'
        
        except Exception as e:
            logger.error(f"Error enriching {symbol}: {e}")
            enrichment_data['error'] = str(e)
        
        # Cache the result
        self.cache[cache_key] = enrichment_data
        self._save_cache()
        
        # Add small delay to be respectful to Yahoo Finance
        time.sleep(0.1)
        
        return enrichment_data
    
    def _enrich_with_yahoo_finance(self, symbol: str, name: str) -> Optional[Dict[str, Any]]:
        """Enrich using Yahoo Finance API"""
        try:
            # Normalize Canadian symbols
            yahoo_symbol = self._normalize_canadian_symbol(symbol)
            
            # Get ticker data
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            
            # Check if we got valid data
            if not info or info.get('longName') is None:
                logger.warning(f"No data from Yahoo Finance for {symbol} (tried {yahoo_symbol})")
                return None
            
            # Extract classification data
            result = {
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'listing_country': info.get('country', 'Unknown'),
                'issuer_region': self.country_to_region.get(info.get('country', ''), 'Unknown'),
                'confidence': 0.8,
                'yahoo_name': info.get('longName', ''),
                'exchange': info.get('exchange', 'Unknown'),
                'currency': info.get('currency', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'business_summary': info.get('longBusinessSummary', ''),
                'website': info.get('website', ''),
                'employees': info.get('fullTimeEmployees', 0)
            }
            
            # Normalize sector
            result['sector_normalized'] = self.sector_mapping.get(
                result['sector'], 
                result['sector']
            )
            
            logger.info(f"Yahoo Finance enrichment successful for {symbol}: {result['sector']} - {result['issuer_region']}")
            return result
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            return None
    
    def enrich_holdings_batch(self, holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich a batch of holdings"""
        logger.info(f"Starting batch enrichment of {len(holdings)} holdings")
        
        enriched_holdings = []
        stats = {
            'total': len(holdings),
            'yahoo_finance': 0,
            'name_parsing': 0,
            'failed': 0,
            'cached': 0
        }
        
        for i, holding in enumerate(holdings):
            symbol = holding.get('Symbol', '')
            name = holding.get('Name', '')
            product = holding.get('Product', '')
            
            logger.info(f"Processing {i+1}/{len(holdings)}: {symbol}")
            
            # Check if already enriched (skip if both sector and region are known)
            if holding.get('Sector') and holding.get('Sector') != 'Unknown' and holding.get('Issuer_Region') and holding.get('Issuer_Region') != 'Unknown':
                logger.info(f"Skipping {symbol} - already classified")
                enriched_holdings.append(holding)
                continue
            
            # Enrich the holding
            enrichment = self.enrich_holding(symbol, name, product)
            
            # Update the holding with enrichment data
            enriched_holding = holding.copy()
            enriched_holding.update({
                'Sector': enrichment.get('sector_normalized', enrichment.get('sector', 'Unknown')),
                'Issuer_Region': enrichment.get('issuer_region', 'Unknown'),
                'Listing_Country': enrichment.get('listing_country', 'Unknown'),
                'Industry': enrichment.get('industry', 'Unknown'),
                'Enrichment_Confidence': enrichment.get('confidence', 0.0),
                'Enrichment_Source': enrichment.get('source', 'none')
            })
            
            enriched_holdings.append(enriched_holding)
            
            # Update stats
            source = enrichment.get('source', 'none')
            if source == 'yahoo_finance':
                stats['yahoo_finance'] += 1
            elif source == 'name_parsing':
                stats['name_parsing'] += 1
            elif source == 'none':
                stats['failed'] += 1
            
            # Progress update
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i+1}/{len(holdings)} holdings processed")
        
        # Save final cache
        self._save_cache()
        
        # Log final stats
        logger.info("Batch enrichment completed!")
        logger.info(f"Total holdings: {stats['total']}")
        logger.info(f"Yahoo Finance enriched: {stats['yahoo_finance']}")
        logger.info(f"Name parsing enriched: {stats['name_parsing']}")
        logger.info(f"Failed to enrich: {stats['failed']}")
        logger.info(f"Success rate: {((stats['yahoo_finance'] + stats['name_parsing']) / stats['total'] * 100):.1f}%")
        
        return enriched_holdings

def main():
    """Test the enricher with sample holdings"""
    enricher = YahooFinanceEnricher()
    
    # Test with sample holdings
    test_holdings = [
        {'Symbol': 'RCI.B', 'Name': 'ROGERS COMMUNICATIONS INC CL B NON-VTG', 'Product': 'Common Shares'},
        {'Symbol': 'PFE', 'Name': 'PFIZER INC', 'Product': 'Common Shares'},
        {'Symbol': 'MRK', 'Name': 'MERCK & CO INC', 'Product': 'Common Shares'},
        {'Symbol': 'XDV', 'Name': 'ISHARES CANADIAN SELECT DIVIDEND INDEX ETF', 'Product': 'ETFs and ETNs'},
        {'Symbol': 'AAPL', 'Name': 'APPLE INC', 'Product': 'Common Shares'},
        {'Symbol': 'ZRE', 'Name': 'BMO EQUAL WEIGHT REITS INDEX ETF', 'Product': 'ETFs and ETNs'}
    ]
    
    print("🧪 Testing Yahoo Finance Enricher")
    print("=" * 50)
    
    enriched = enricher.enrich_holdings_batch(test_holdings)
    
    for holding in enriched:
        print(f"\n📊 {holding['Symbol']}: {holding['Name']}")
        print(f"   Sector: {holding.get('Sector', 'Unknown')}")
        print(f"   Region: {holding.get('Issuer_Region', 'Unknown')}")
        print(f"   Source: {holding.get('Enrichment_Source', 'none')}")
        print(f"   Confidence: {holding.get('Enrichment_Confidence', 0.0)}")

if __name__ == "__main__":
    main()
