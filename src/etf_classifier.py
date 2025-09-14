"""
ETF/ETN Classification System
Classifies ETFs and ETNs by region and type for better portfolio analysis
"""

import re
from typing import Dict, Tuple

class ETFClassifier:
    """Classifies ETFs and ETNs by region and type based on symbol and description."""
    
    def __init__(self):
        # Region classification patterns
        self.region_patterns = {
            'Canada': [
                r'CANADIAN', r'TSX', r'CDN', r'CANADA', r'BMO', r'ISHARES.*CANADIAN',
                r'PURPOSE.*CANADIAN', r'NATIONAL.*BANK'
            ],
            'US': [
                r'US\b', r'U\.S\.', r'UNITED STATES', r'AMERICAN', r'SCHWAB', r'VANECK',
                r'INVESCO.*US', r'SPDR', r'VANGUARD.*US', r'ISHARES.*US'
            ],
            'Europe': [
                r'EUROPE', r'EURO', r'EUROPEAN', r'EMU', r'ISHARES.*EUROPE',
                r'MSCI.*EUROPE', r'STOXX'
            ],
            'Global': [
                r'GLOBAL', r'WORLD', r'INTERNATIONAL', r'EMERGING', r'DEVELOPING',
                r'ALL.*COUNTRY', r'ACWI', r'MSCI.*WORLD'
            ],
            'Emerging Markets': [
                r'EMERGING', r'DEVELOPING', r'FRONTIER', r'BRIC', r'ASIA.*EX.*JAPAN'
            ]
        }
        
        # ETF/ETN type classification patterns
        self.type_patterns = {
            'Bond/Fixed Income': [
                r'BOND', r'CORPORATE', r'MONEY MARKET', r'TREASURY', r'GOVERNMENT',
                r'CREDIT', r'DURATION', r'YIELD', r'INVESTMENT GRADE', r'HIGH YIELD',
                r'SHORT.*TERM', r'LONG.*TERM', r'INTERMEDIATE'
            ],
            'Dividend Equity': [
                r'DIVIDEND', r'INCOME', r'ARISTOCRAT', r'SELECT.*DIVIDEND'
            ],
            'Broad Market Index': [
                r'INDEX', r'S&P', r'DOW', r'NASDAQ', r'RUSSELL', r'MSCI.*INDEX',
                r'TOTAL.*MARKET', r'MARKET.*CAP'
            ],
            'Utilities': [
                r'UTILITIES', r'UTILITY', r'ELECTRIC', r'POWER', r'ENERGY.*UTILITY'
            ],
            'Semiconductors': [
                r'SEMICONDUCTOR', r'CHIP', r'MICROCHIP', r'PROCESSOR'
            ],
            'Technology': [
                r'TECHNOLOGY', r'TECH', r'SOFTWARE', r'INTERNET', r'CYBERSECURITY',
                r'ARTIFICIAL.*INTELLIGENCE', r'AI', r'BLOCKCHAIN', r'DIGITAL'
            ],
            'Healthcare': [
                r'HEALTHCARE', r'HEALTH', r'BIOTECH', r'PHARMACEUTICAL', r'MEDICAL'
            ],
            'Energy': [
                r'ENERGY', r'OIL', r'GAS', r'CRUDE', r'NATURAL.*GAS', r'PETROLEUM'
            ],
            'Financial': [
                r'FINANCIAL', r'BANK', r'INSURANCE', r'FINANCE', r'CREDIT'
            ],
            'Consumer': [
                r'CONSUMER', r'RETAIL', r'DISCRETIONARY', r'STAPLES'
            ],
            'Industrial': [
                r'INDUSTRIAL', r'MANUFACTURING', r'AEROSPACE', r'DEFENSE'
            ],
            'Materials': [
                r'MATERIALS', r'MINING', r'METALS', r'CHEMICALS'
            ],
            'Communication': [
                r'COMMUNICATION', r'TELECOM', r'MEDIA', r'ENTERTAINMENT'
            ],
            'Real Estate': [
                r'REAL.*ESTATE', r'REIT', r'REALTY', r'PROPERTY'
            ],
            'Clean Energy': [
                r'CLEAN.*ENERGY', r'RENEWABLE', r'SOLAR', r'WIND', r'GREEN.*ENERGY'
            ],
            'Commodity': [
                r'GOLD', r'SILVER', r'OIL', r'ENERGY', r'COMMODITY', r'PRECIOUS.*METAL',
                r'CRUDE', r'NATURAL.*GAS', r'AGRICULTURE'
            ],
            'Currency': [
                r'CURRENCY', r'FOREX', r'HEDGED', r'UNHEDGED', r'DOLLAR'
            ]
        }
        
        # Special symbol-based classifications
        self.symbol_classifications = {
            # Canadian ETFs
            'CDZ': ('Canada', 'Dividend Equity'),
            'XDV': ('Canada', 'Dividend Equity'),
            'ZRE': ('Canada', 'REIT'),
            'XEH': ('Europe', 'Broad Market Index'),
            
            # US ETFs
            'SCHD': ('US', 'Dividend Equity'),
            'SMH': ('US', 'Semiconductors'),
            'TAN': ('US', 'Clean Energy'),
            'HYG': ('US', 'Bond/Fixed Income'),
            'ICSH': ('US', 'Bond/Fixed Income'),
            'HISU.U': ('US', 'Bond/Fixed Income'),
            
            # European ETFs
            'IEV': ('Europe', 'Broad Market Index'),
            
            # Global/Other
            'CMR': ('Global', 'Bond/Fixed Income'),
            'MNY': ('Global', 'Bond/Fixed Income'),
        }
    
    def classify_etf(self, symbol: str, description: str) -> Tuple[str, str]:
        """
        Classify an ETF/ETN by region and type.
        
        Args:
            symbol: ETF/ETN symbol
            description: ETF/ETN description
            
        Returns:
            Tuple of (region, type)
        """
        # First check symbol-based classifications
        if symbol in self.symbol_classifications:
            return self.symbol_classifications[symbol]
        
        # Convert to uppercase for pattern matching
        desc_upper = description.upper()
        
        # Classify region
        region = self._classify_region(desc_upper)
        
        # Classify type
        etf_type = self._classify_type(desc_upper)
        
        return region, etf_type
    
    def _classify_region(self, description: str) -> str:
        """Classify the geographic region of the ETF."""
        for region, patterns in self.region_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    return region
        return 'Unknown'
    
    def _classify_type(self, description: str) -> str:
        """Classify the type/category of the ETF."""
        for etf_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    return etf_type
        return 'Other'
    
    def get_classification_summary(self, holdings_df) -> Dict:
        """Get a summary of ETF/ETN classifications."""
        etf_holdings = holdings_df[holdings_df['Asset Type'].str.contains('ETF|ETN', case=False, na=False)]
        
        summary = {
            'total_etfs': len(etf_holdings),
            'by_region': {},
            'by_type': {},
            'classifications': []
        }
        
        for _, row in etf_holdings.iterrows():
            symbol = row['Symbol']
            description = row['Description']
            region, etf_type = self.classify_etf(symbol, description)
            
            # Count by region
            if region not in summary['by_region']:
                summary['by_region'][region] = 0
            summary['by_region'][region] += 1
            
            # Count by type
            if etf_type not in summary['by_type']:
                summary['by_type'][etf_type] = 0
            summary['by_type'][etf_type] += 1
            
            # Store individual classification
            summary['classifications'].append({
                'symbol': symbol,
                'description': description,
                'region': region,
                'type': etf_type
            })
        
        return summary

def add_etf_classifications(df):
    """
    Add ETF/ETN classification columns to the DataFrame.
    
    Args:
        df: DataFrame with holdings data
        
    Returns:
        DataFrame with added 'ETF_Region' and 'ETF_Type' columns
    """
    classifier = ETFClassifier()
    
    # Initialize new columns
    df['ETF_Region'] = None
    df['ETF_Type'] = None
    
    # Classify ETFs and ETNs - check for both possible column names
    asset_type_col = None
    for col in ['Asset Type', 'Product']:
        if col in df.columns:
            asset_type_col = col
            break
    
    if asset_type_col is None:
        return df
    
    etf_mask = df[asset_type_col].str.contains('ETF|ETN', case=False, na=False)
    
    for idx, row in df[etf_mask].iterrows():
        symbol = row.get('Symbol', '')
        description = row.get('Description', row.get('Name', ''))
        region, etf_type = classifier.classify_etf(symbol, description)
        
        df.at[idx, 'ETF_Region'] = region
        df.at[idx, 'ETF_Type'] = etf_type
    
    return df

if __name__ == "__main__":
    # Test the classifier
    import sys
    sys.path.append('.')
    from src.core.data_manager import DataManager
    
    dm = DataManager()
    df = dm.load_data()
    
    if df is not None:
        classifier = ETFClassifier()
        summary = classifier.get_classification_summary(df)
        
        print("ETF/ETN Classification Summary:")
        print("=" * 50)
        print(f"Total ETFs/ETNs: {summary['total_etfs']}")
        print()
        
        print("By Region:")
        for region, count in summary['by_region'].items():
            print(f"  {region}: {count}")
        print()
        
        print("By Type:")
        for etf_type, count in summary['by_type'].items():
            print(f"  {etf_type}: {count}")
        print()
        
        print("Individual Classifications:")
        for item in summary['classifications']:
            print(f"  {item['symbol']:8} | {item['region']:12} | {item['type']:20} | {item['description'][:50]}...")
    else:
        print("Failed to load data")
