#!/usr/bin/env python3
"""
Automated ETF Enrichment System
- Uses curated database for known ETFs
- Automatically searches for missing data using multiple strategies
- Scales to handle new ETFs without manual intervention
"""

import requests
import json
import time
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import re
from urllib.parse import quote
import yfinance as yf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedETFEnricher:
    """Automated ETF enrichment with fallback search strategies"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Curated ETF database (starting point)
        self.etf_database = self._load_curated_database()
        
        # Search strategies in order of preference
        self.search_strategies = [
            self._search_etfdb,
            self._search_yfinance_detailed,
            self._search_alpha_vantage,
            self._search_name_parsing,
            self._search_morningstar,
        ]
    
    def _load_curated_database(self) -> Dict:
        """Load the curated ETF database"""
        return {
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
            
            # US ETFs
            'XEH': {'name': 'iShares MSCI Europe IMI Index ETF', 'sector': 'Equity', 'industry': 'European ETF', 'region': 'Europe', 'listing_country': 'Canada', 'currency': 'CAD'},
            'SCHD': {'name': 'Schwab U.S. Dividend Equity ETF', 'sector': 'Equity', 'industry': 'Dividend ETF', 'region': 'United States', 'listing_country': 'United States', 'currency': 'USD'},
            'CDZ': {'name': 'iShares S&P/TSX Canadian Dividend Aristocrats Index ETF', 'sector': 'Equity', 'industry': 'Dividend ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'CMR': {'name': 'iShares Premium Money Market ETF', 'sector': 'Money Market', 'industry': 'Money Market ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'HYG': {'name': 'iShares iBoxx $ High Yield Corporate Bond ETF', 'sector': 'Fixed Income', 'industry': 'High Yield Bond ETF', 'region': 'United States', 'listing_country': 'United States', 'currency': 'USD'},
            'ICSH': {'name': 'iShares Ultra Short-Term Bond ETF', 'sector': 'Fixed Income', 'industry': 'Short Term Bond ETF', 'region': 'United States', 'listing_country': 'United States', 'currency': 'USD'},
            'IEV': {'name': 'iShares Europe ETF', 'sector': 'Equity', 'industry': 'European ETF', 'region': 'Europe', 'listing_country': 'United States', 'currency': 'USD'},
            'SMH': {'name': 'VanEck Semiconductor ETF', 'sector': 'Technology', 'industry': 'Semiconductor ETF', 'region': 'United States', 'listing_country': 'United States', 'currency': 'USD'},
            'TAN': {'name': 'Invesco Solar ETF', 'sector': 'Energy', 'industry': 'Solar Energy ETF', 'region': 'United States', 'listing_country': 'United States', 'currency': 'USD'},
            'MNY': {'name': 'Horizons Active CDN Money Market ETF', 'sector': 'Money Market', 'industry': 'Money Market ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'ZRE': {'name': 'BMO Equal Weight REITs Index ETF', 'sector': 'Real Estate', 'industry': 'REIT ETF', 'region': 'Canada', 'listing_country': 'Canada', 'currency': 'CAD'},
            'HISU.U': {'name': 'Horizons US Dollar High Interest Savings ETF', 'sector': 'Money Market', 'industry': 'Money Market ETF', 'region': 'United States', 'listing_country': 'Canada', 'currency': 'USD'},
        }
    
    def _search_etfdb(self, symbol: str, etf_name: str = "") -> Dict:
        """Search ETF Database (etfdb.com) for ETF information"""
        try:
            # ETF Database search
            search_url = f"https://etfdb.com/etf/{symbol}/"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Extract information using regex patterns
                data = {'source': 'etfdb', 'symbol': symbol}
                
                # Extract sector information
                sector_match = re.search(r'"sector":\s*"([^"]+)"', content)
                if sector_match:
                    data['sector'] = sector_match.group(1)
                
                # Extract asset class
                asset_match = re.search(r'"asset_class":\s*"([^"]+)"', content)
                if asset_match:
                    data['asset_type'] = asset_match.group(1)
                
                # Extract expense ratio
                expense_match = re.search(r'"expense_ratio":\s*"([^"]+)"', content)
                if expense_match:
                    data['expense_ratio'] = expense_match.group(1)
                
                # Extract issuer
                issuer_match = re.search(r'"issuer":\s*"([^"]+)"', content)
                if issuer_match:
                    data['issuer'] = issuer_match.group(1)
                
                return data
        except Exception as e:
            logger.warning(f"ETFDB search failed for {symbol}: {e}")
        
        return {}
    
    def _search_yfinance_detailed(self, symbol: str, etf_name: str = "") -> Dict:
        """Enhanced Yahoo Finance search with better data extraction"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return {}
            
            data = {'source': 'yfinance_detailed', 'symbol': symbol}
            
            # Extract sector
            if 'sector' in info and info['sector']:
                data['sector'] = info['sector']
            
            # Extract industry
            if 'industry' in info and info['industry']:
                data['industry'] = info['industry']
            
            # Extract country
            if 'country' in info and info['country']:
                data['listing_country'] = info['country']
            
            # Extract currency
            if 'currency' in info and info['currency']:
                data['currency'] = info['currency']
            
            # Extract exchange
            if 'exchange' in info and info['exchange']:
                data['exchange'] = info['exchange']
            
            # Extract market cap
            if 'marketCap' in info and info['marketCap']:
                data['market_cap'] = info['marketCap']
            
            # Extract business summary
            if 'longBusinessSummary' in info and info['longBusinessSummary']:
                data['business_summary'] = info['longBusinessSummary']
            
            # Extract website
            if 'website' in info and info['website']:
                data['website'] = info['website']
            
            return data
        except Exception as e:
            logger.warning(f"Yahoo Finance detailed search failed for {symbol}: {e}")
        
        return {}
    
    def _search_alpha_vantage(self, symbol: str, etf_name: str = "") -> Dict:
        """Search Alpha Vantage for ETF information"""
        try:
            # Try with demo key first
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey=demo"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'Symbol' in data and data['Symbol']:
                    return {
                        'source': 'alpha_vantage',
                        'symbol': symbol,
                        'sector': data.get('Sector', ''),
                        'industry': data.get('Industry', ''),
                        'country': data.get('Country', ''),
                        'exchange': data.get('Exchange', ''),
                        'market_cap': data.get('MarketCapitalization', ''),
                        'description': data.get('Description', ''),
                        'website': data.get('Website', ''),
                        'employees': data.get('FullTimeEmployees', '')
                    }
        except Exception as e:
            logger.warning(f"Alpha Vantage search failed for {symbol}: {e}")
        
        return {}
    
    def _search_name_parsing(self, symbol: str, etf_name: str = "") -> Dict:
        """Parse ETF name to extract sector/industry information"""
        if not etf_name:
            return {}
        
        etf_name_lower = etf_name.lower()
        data = {'source': 'name_parsing', 'symbol': symbol}
        
        # Sector detection from name
        if any(word in etf_name_lower for word in ['bond', 'treasury', 'corporate', 'government']):
            data['sector'] = 'Fixed Income'
        elif any(word in etf_name_lower for word in ['reit', 'real estate']):
            data['sector'] = 'Real Estate'
        elif any(word in etf_name_lower for word in ['money market', 'cash']):
            data['sector'] = 'Money Market'
        elif any(word in etf_name_lower for word in ['commodity', 'gold', 'silver', 'oil']):
            data['sector'] = 'Commodities'
        else:
            data['sector'] = 'Equity'
        
        # Industry detection from name
        if 'dividend' in etf_name_lower:
            data['industry'] = 'Dividend ETF'
        elif 'semiconductor' in etf_name_lower:
            data['industry'] = 'Semiconductor ETF'
            data['sector'] = 'Technology'
        elif 'solar' in etf_name_lower:
            data['industry'] = 'Solar Energy ETF'
            data['sector'] = 'Energy'
        elif 'europe' in etf_name_lower or 'euro' in etf_name_lower:
            data['industry'] = 'European ETF'
            data['region'] = 'Europe'
        elif 'emerging' in etf_name_lower:
            data['industry'] = 'Emerging Markets ETF'
            data['region'] = 'International'
        elif 'nasdaq' in etf_name_lower:
            data['industry'] = 'Technology ETF'
            data['sector'] = 'Technology'
        elif 's&p' in etf_name_lower or 'sp' in etf_name_lower:
            data['industry'] = 'Large Cap ETF'
        elif 'small' in etf_name_lower or 'micro' in etf_name_lower:
            data['industry'] = 'Small Cap ETF'
        elif 'high yield' in etf_name_lower or 'junk' in etf_name_lower:
            data['industry'] = 'High Yield Bond ETF'
            data['sector'] = 'Fixed Income'
        elif 'short' in etf_name_lower and 'bond' in etf_name_lower:
            data['industry'] = 'Short Term Bond ETF'
            data['sector'] = 'Fixed Income'
        elif 'reit' in etf_name_lower:
            data['industry'] = 'REIT ETF'
            data['sector'] = 'Real Estate'
        elif 'money market' in etf_name_lower:
            data['industry'] = 'Money Market ETF'
            data['sector'] = 'Money Market'
        
        # Region detection
        if not data.get('region'):
            if any(word in etf_name_lower for word in ['canada', 'canadian', 'tsx']):
                data['region'] = 'Canada'
            elif any(word in etf_name_lower for word in ['us', 'usa', 'united states', 's&p 500', 'nasdaq']):
                data['region'] = 'United States'
            elif any(word in etf_name_lower for word in ['europe', 'euro', 'eafe']):
                data['region'] = 'Europe'
            elif any(word in etf_name_lower for word in ['emerging', 'asia', 'china', 'japan']):
                data['region'] = 'International'
        
        # Currency detection
        if 'cad' in etf_name_lower or 'canadian' in etf_name_lower:
            data['currency'] = 'CAD'
        elif 'usd' in etf_name_lower or 'dollar' in etf_name_lower:
            data['currency'] = 'USD'
        
        return data
    
    def _search_morningstar(self, symbol: str, etf_name: str = "") -> Dict:
        """Search Morningstar for ETF information"""
        try:
            # Morningstar search URL
            search_url = f"https://www.morningstar.com/etfs/xnas/{symbol}/quote"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                data = {'source': 'morningstar', 'symbol': symbol}
                
                # Look for sector information in the page
                if 'sector' in content.lower():
                    data['has_morningstar_data'] = True
                else:
                    data['has_morningstar_data'] = False
                
                return data
        except Exception as e:
            logger.warning(f"Morningstar search failed for {symbol}: {e}")
        
        return {}
    
    def _is_data_complete(self, data: Dict) -> bool:
        """Check if ETF data is complete enough"""
        required_fields = ['sector', 'industry', 'listing_country']
        return all(data.get(field) and data[field] != 'Unknown' for field in required_fields)
    
    def _merge_data(self, base_data: Dict, new_data: Dict) -> Dict:
        """Merge new data into base data, preferring non-empty values"""
        merged = base_data.copy()
        
        for key, value in new_data.items():
            if key in ['source', 'symbol']:
                continue
            
            # Only update if new value is not empty and base value is empty or 'Unknown'
            if value and value != 'Unknown' and (not merged.get(key) or merged.get(key) == 'Unknown'):
                merged[key] = value
        
        # Update sources list
        if 'enrichment_sources' not in merged:
            merged['enrichment_sources'] = []
        
        if new_data.get('source') and new_data['source'] not in merged['enrichment_sources']:
            merged['enrichment_sources'].append(new_data['source'])
        
        return merged
    
    def enrich_symbol(self, symbol: str, etf_name: str = "", force_search: bool = False) -> Dict:
        """Enrich a single ETF symbol with automated search fallbacks"""
        logger.info(f"Enriching ETF: {symbol} - {etf_name}")
        
        # Start with curated database if available
        if symbol in self.etf_database and not force_search:
            base_data = self.etf_database[symbol].copy()
            base_data['symbol'] = symbol
            base_data['enrichment_sources'] = ['curated_database']
            base_data['enrichment_confidence'] = 0.9
        else:
            base_data = {
                'symbol': symbol,
                'product_name': etf_name,
                'enrichment_sources': [],
                'enrichment_confidence': 0.0
            }
        
        # Check if data is complete
        if self._is_data_complete(base_data) and not force_search:
            logger.info(f"Data complete for {symbol}, using curated database")
            return base_data
        
        # Try each search strategy
        logger.info(f"Data incomplete for {symbol}, searching...")
        
        for strategy in self.search_strategies:
            try:
                search_result = strategy(symbol, etf_name)
                if search_result:
                    base_data = self._merge_data(base_data, search_result)
                    logger.info(f"Found data via {search_result['source']} for {symbol}")
                    
                    # If data is now complete, stop searching
                    if self._is_data_complete(base_data):
                        break
            except Exception as e:
                logger.warning(f"Search strategy {strategy.__name__} failed for {symbol}: {e}")
                continue
        
        # Calculate final confidence
        source_count = len(base_data.get('enrichment_sources', []))
        base_data['enrichment_confidence'] = min(0.5 + (source_count * 0.15), 0.95)
        base_data['last_verified_date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        return base_data
    
    def enrich_holdings(self, holdings_data: List[Dict], force_search: bool = False) -> List[Dict]:
        """Enrich a list of holdings with automated search"""
        enriched_holdings = []
        
        for holding in holdings_data:
            symbol = holding.get('Symbol', '')
            etf_name = holding.get('Name', '')
            
            if not symbol:
                enriched_holdings.append(holding)
                continue
            
            # Get enrichment data
            enrichment = self.enrich_symbol(symbol, etf_name, force_search)
            
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
            time.sleep(0.2)
        
        return enriched_holdings

def main():
    """Test the automated ETF enricher"""
    enricher = AutomatedETFEnricher()
    
    # Test with known ETFs
    test_symbols = [
        ('XEH', 'iShares MSCI Europe IMI Index ETF'),
        ('SCHD', 'Schwab U.S. Dividend Equity ETF'),
        ('SMH', 'VanEck Semiconductor ETF'),
        ('TAN', 'Invesco Solar ETF'),
        ('UNKNOWN', 'Some Unknown ETF'),  # Test with unknown ETF
    ]
    
    for symbol, name in test_symbols:
        print(f"\n=== Enriching {symbol} ===")
        result = enricher.enrich_symbol(symbol, name, force_search=True)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
