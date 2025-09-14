"""
Comprehensive Ticker Classification Database
Based on industry-standard sources: GICS, ICB, S&P, MSCI, and major financial data providers
"""

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class TickerClassificationDatabase:
    """Comprehensive database of ticker classifications using industry standards."""
    
    def __init__(self):
        self.classifications = self._load_classifications()
    
    def _load_classifications(self) -> Dict[str, Dict]:
        """Load comprehensive ticker classifications."""
        return {
            # === REITs (Real Estate Investment Trusts) ===
            "REITS": {
                "STAG": {"name": "STAG Industrial Inc", "sector": "Industrial REIT", "region": "US", "gics_sector": "Real Estate", "gics_industry": "Industrial REITs"},
                "REXR": {"name": "Rexford Industrial Realty Inc", "sector": "Industrial REIT", "region": "US", "gics_sector": "Real Estate", "gics_industry": "Industrial REITs"},
                "O": {"name": "Realty Income Corp", "sector": "Retail REIT", "region": "US", "gics_sector": "Real Estate", "gics_industry": "Retail REITs"},
                "ZRE": {"name": "BMO Equal Weight REITs Index ETF", "sector": "REIT ETF", "region": "Canada", "gics_sector": "Real Estate", "gics_industry": "Real Estate Management & Development"},
                "VRE": {"name": "Vanguard FTSE Canadian Capped REIT Index ETF", "sector": "REIT ETF", "region": "Canada", "gics_sector": "Real Estate", "gics_industry": "Real Estate Management & Development"},
                "XRE": {"name": "iShares S&P/TSX Capped REIT Index ETF", "sector": "REIT ETF", "region": "Canada", "gics_sector": "Real Estate", "gics_industry": "Real Estate Management & Development"},
                "VNQ": {"name": "Vanguard Real Estate ETF", "sector": "REIT ETF", "region": "US", "gics_sector": "Real Estate", "gics_industry": "Real Estate Management & Development"},
                "IYR": {"name": "iShares U.S. Real Estate ETF", "sector": "REIT ETF", "region": "US", "gics_sector": "Real Estate", "gics_industry": "Real Estate Management & Development"}
            },
            
            # === Technology Sector ===
            "TECHNOLOGY": {
                "AAPL": {"name": "Apple Inc", "sector": "Technology Hardware", "region": "US", "gics_sector": "Information Technology", "gics_industry": "Technology Hardware, Storage & Peripherals"},
                "GOOGL": {"name": "Alphabet Inc Class A", "sector": "Internet Services", "region": "US", "gics_sector": "Communication Services", "gics_industry": "Interactive Media & Services"},
                "MSFT": {"name": "Microsoft Corp", "sector": "Software", "region": "US", "gics_sector": "Information Technology", "gics_industry": "Systems Software"},
                "AMZN": {"name": "Amazon.com Inc", "sector": "E-commerce", "region": "US", "gics_sector": "Consumer Discretionary", "gics_industry": "Internet & Direct Marketing Retail"},
                "ADBE": {"name": "Adobe Inc", "sector": "Software", "region": "US", "gics_sector": "Information Technology", "gics_industry": "Application Software"},
                "CRM": {"name": "Salesforce Inc", "sector": "Software", "region": "US", "gics_sector": "Information Technology", "gics_industry": "Application Software"},
                "SHOP": {"name": "Shopify Inc", "sector": "E-commerce Software", "region": "Canada", "gics_sector": "Information Technology", "gics_industry": "Application Software"},
                "NFLX": {"name": "Netflix Inc", "sector": "Streaming Services", "region": "US", "gics_sector": "Communication Services", "gics_industry": "Entertainment"},
                "TSLA": {"name": "Tesla Inc", "sector": "Electric Vehicles", "region": "US", "gics_sector": "Consumer Discretionary", "gics_industry": "Automobile Manufacturers"},
                "NVDA": {"name": "NVIDIA Corp", "sector": "Semiconductors", "region": "US", "gics_sector": "Information Technology", "gics_industry": "Semiconductors & Semiconductor Equipment"},
                "SMH": {"name": "VanEck Semiconductor ETF", "sector": "Semiconductor ETF", "region": "US", "gics_sector": "Information Technology", "gics_industry": "Semiconductors & Semiconductor Equipment"},
                "TAN": {"name": "Invesco Solar ETF", "sector": "Clean Energy ETF", "region": "US", "gics_sector": "Utilities", "gics_industry": "Independent Power and Renewable Electricity Producers"}
            },
            
            # === Healthcare Sector ===
            "HEALTHCARE": {
                "PFE": {"name": "Pfizer Inc", "sector": "Pharmaceuticals", "region": "US", "gics_sector": "Health Care", "gics_industry": "Pharmaceuticals"},
                "MRK": {"name": "Merck & Co Inc", "sector": "Pharmaceuticals", "region": "US", "gics_sector": "Health Care", "gics_industry": "Pharmaceuticals"},
                "JNJ": {"name": "Johnson & Johnson", "sector": "Healthcare Conglomerate", "region": "US", "gics_sector": "Health Care", "gics_industry": "Health Care Equipment & Supplies"},
                "UNH": {"name": "UnitedHealth Group Inc", "sector": "Health Insurance", "region": "US", "gics_sector": "Health Care", "gics_industry": "Managed Health Care"},
                "ABBV": {"name": "AbbVie Inc", "sector": "Pharmaceuticals", "region": "US", "gics_sector": "Health Care", "gics_industry": "Pharmaceuticals"},
                "XLV": {"name": "Health Care Select Sector SPDR Fund", "sector": "Healthcare ETF", "region": "US", "gics_sector": "Health Care", "gics_industry": "Health Care Equipment & Supplies"}
            },
            
            # === Communications Sector ===
            "COMMUNICATIONS": {
                "T": {"name": "AT&T Inc", "sector": "Telecommunications", "region": "US", "gics_sector": "Communication Services", "gics_industry": "Integrated Telecommunication Services"},
                "VZ": {"name": "Verizon Communications Inc", "sector": "Telecommunications", "region": "US", "gics_sector": "Communication Services", "gics_industry": "Integrated Telecommunication Services"},
                "CMCSA": {"name": "Comcast Corp", "sector": "Media & Communications", "region": "US", "gics_sector": "Communication Services", "gics_industry": "Cable & Satellite"},
                "DIS": {"name": "Walt Disney Co", "sector": "Entertainment", "region": "US", "gics_sector": "Communication Services", "gics_industry": "Entertainment"},
                "XLC": {"name": "Communication Services Select Sector SPDR Fund", "sector": "Communications ETF", "region": "US", "gics_sector": "Communication Services", "gics_industry": "Integrated Telecommunication Services"}
            },
            
            # === Consumer Discretionary ===
            "CONSUMER_DISCRETIONARY": {
                "NKE": {"name": "Nike Inc", "sector": "Apparel & Footwear", "region": "US", "gics_sector": "Consumer Discretionary", "gics_industry": "Apparel, Accessories & Luxury Goods"},
                "HD": {"name": "Home Depot Inc", "sector": "Home Improvement Retail", "region": "US", "gics_sector": "Consumer Discretionary", "gics_industry": "Home Improvement Retail"},
                "MCD": {"name": "McDonald's Corp", "sector": "Restaurants", "region": "US", "gics_sector": "Consumer Discretionary", "gics_industry": "Restaurants"},
                "XLY": {"name": "Consumer Discretionary Select Sector SPDR Fund", "sector": "Consumer Discretionary ETF", "region": "US", "gics_sector": "Consumer Discretionary", "gics_industry": "Automobile Manufacturers"}
            },
            
            # === Consumer Staples ===
            "CONSUMER_STAPLES": {
                "PG": {"name": "Procter & Gamble Co", "sector": "Consumer Products", "region": "US", "gics_sector": "Consumer Staples", "gics_industry": "Household Products"},
                "KO": {"name": "Coca-Cola Co", "sector": "Beverages", "region": "US", "gics_sector": "Consumer Staples", "gics_industry": "Soft Drinks & Non-alcoholic Beverages"},
                "WMT": {"name": "Walmart Inc", "sector": "Retail", "region": "US", "gics_sector": "Consumer Staples", "gics_industry": "Hypermarkets & Super Centers"},
                "XLP": {"name": "Consumer Staples Select Sector SPDR Fund", "sector": "Consumer Staples ETF", "region": "US", "gics_sector": "Consumer Staples", "gics_industry": "Food & Staples Retailing"}
            },
            
            # === Industrial Sector ===
            "INDUSTRIAL": {
                "UPS": {"name": "United Parcel Service Inc", "sector": "Transportation", "region": "US", "gics_sector": "Industrials", "gics_industry": "Air Freight & Logistics"},
                "BA": {"name": "Boeing Co", "sector": "Aerospace", "region": "US", "gics_sector": "Industrials", "gics_industry": "Aerospace & Defense"},
                "CAT": {"name": "Caterpillar Inc", "sector": "Heavy Machinery", "region": "US", "gics_sector": "Industrials", "gics_industry": "Construction & Mining Machinery"},
                "GE": {"name": "General Electric Co", "sector": "Industrial Conglomerate", "region": "US", "gics_sector": "Industrials", "gics_industry": "Industrial Conglomerates"},
                "XLI": {"name": "Industrial Select Sector SPDR Fund", "sector": "Industrial ETF", "region": "US", "gics_sector": "Industrials", "gics_industry": "Industrial Conglomerates"}
            },
            
            # === Utilities Sector ===
            "UTILITIES": {
                "NEE": {"name": "NextEra Energy Inc", "sector": "Electric Utilities", "region": "US", "gics_sector": "Utilities", "gics_industry": "Electric Utilities"},
                "DUK": {"name": "Duke Energy Corp", "sector": "Electric Utilities", "region": "US", "gics_sector": "Utilities", "gics_industry": "Electric Utilities"},
                "SO": {"name": "Southern Co", "sector": "Electric Utilities", "region": "US", "gics_sector": "Utilities", "gics_industry": "Electric Utilities"},
                "XLU": {"name": "Utilities Select Sector SPDR Fund", "sector": "Utilities ETF", "region": "US", "gics_sector": "Utilities", "gics_industry": "Electric Utilities"}
            },
            
            # === Energy Sector ===
            "ENERGY": {
                "ARX": {"name": "ARC Resources Ltd", "sector": "Oil & Gas Exploration", "region": "Canada", "gics_sector": "Energy", "gics_industry": "Oil & Gas Exploration & Production"},
                "CNQ": {"name": "Canadian Natural Resources Ltd", "sector": "Oil & Gas Exploration", "region": "Canada", "gics_sector": "Energy", "gics_industry": "Oil & Gas Exploration & Production"},
                "CVE": {"name": "Cenovus Energy Inc", "sector": "Oil & Gas Exploration", "region": "Canada", "gics_sector": "Energy", "gics_industry": "Oil & Gas Exploration & Production"},
                "ENB": {"name": "Enbridge Inc", "sector": "Energy Infrastructure", "region": "Canada", "gics_sector": "Energy", "gics_industry": "Oil & Gas Storage & Transportation"},
                "PPL": {"name": "Pembina Pipeline Corp", "sector": "Energy Infrastructure", "region": "Canada", "gics_sector": "Energy", "gics_industry": "Oil & Gas Storage & Transportation"},
                "XLE": {"name": "Energy Select Sector SPDR Fund", "sector": "Energy ETF", "region": "US", "gics_sector": "Energy", "gics_industry": "Oil & Gas Exploration & Production"},
                "XEG": {"name": "iShares S&P/TSX Capped Energy Index ETF", "sector": "Energy ETF", "region": "Canada", "gics_sector": "Energy", "gics_industry": "Oil & Gas Exploration & Production"}
            },
            
            # === Financial Sector ===
            "FINANCIAL": {
                "JPM": {"name": "JPMorgan Chase & Co", "sector": "Banking", "region": "US", "gics_sector": "Financials", "gics_industry": "Diversified Banks"},
                "BAC": {"name": "Bank of America Corp", "sector": "Banking", "region": "US", "gics_sector": "Financials", "gics_industry": "Diversified Banks"},
                "WFC": {"name": "Wells Fargo & Co", "sector": "Banking", "region": "US", "gics_sector": "Financials", "gics_industry": "Diversified Banks"},
                "GS": {"name": "Goldman Sachs Group Inc", "sector": "Investment Banking", "region": "US", "gics_sector": "Financials", "gics_industry": "Investment Banking & Brokerage"},
                "XLF": {"name": "Financial Select Sector SPDR Fund", "sector": "Financial ETF", "region": "US", "gics_sector": "Financials", "gics_industry": "Diversified Banks"}
            },
            
            # === Materials Sector ===
            "MATERIALS": {
                "FCX": {"name": "Freeport-McMoRan Inc", "sector": "Mining", "region": "US", "gics_sector": "Materials", "gics_industry": "Copper"},
                "NEM": {"name": "Newmont Corp", "sector": "Mining", "region": "US", "gics_sector": "Materials", "gics_industry": "Gold"},
                "XLB": {"name": "Materials Select Sector SPDR Fund", "sector": "Materials ETF", "region": "US", "gics_sector": "Materials", "gics_industry": "Diversified Chemicals"}
            },
            
            # === Fixed Income ===
            "FIXED_INCOME": {
                "TLT": {"name": "iShares 20+ Year Treasury Bond ETF", "sector": "Government Bonds", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "IEF": {"name": "iShares 7-10 Year Treasury Bond ETF", "sector": "Government Bonds", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "SHY": {"name": "iShares 1-3 Year Treasury Bond ETF", "sector": "Government Bonds", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "LQD": {"name": "iShares iBoxx $ Investment Grade Corporate Bond ETF", "sector": "Corporate Bonds", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "HYG": {"name": "iShares iBoxx $ High Yield Corporate Bond ETF", "sector": "High Yield Bonds", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "BNDX": {"name": "Vanguard Total International Bond ETF", "sector": "International Bonds", "region": "Global", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "MNY": {"name": "Purpose High Interest Savings ETF", "sector": "Money Market", "region": "Canada", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "HISU.U": {"name": "Horizons USD Cash Maximizer ETF", "sector": "Money Market", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "ICSH": {"name": "iShares Ultra Short-Term Bond ETF", "sector": "Short-Term Bonds", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"}
            },
            
            # === Canadian ETFs ===
            "CANADIAN_ETFS": {
                "CDZ": {"name": "iShares S&P/TSX Canadian Dividend Aristocrats Index ETF", "sector": "Dividend ETF", "region": "Canada", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "XDV": {"name": "iShares Core MSCI Canadian Quality Dividend Index ETF", "sector": "Dividend ETF", "region": "Canada", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "XIC": {"name": "iShares Core S&P/TSX Capped Composite Index ETF", "sector": "Broad Market ETF", "region": "Canada", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "VCN": {"name": "Vanguard FTSE Canada All Cap Index ETF", "sector": "Broad Market ETF", "region": "Canada", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "ZCN": {"name": "BMO S&P/TSX Capped Composite Index ETF", "sector": "Broad Market ETF", "region": "Canada", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"}
            },
            
            # === US ETFs ===
            "US_ETFS": {
                "SCHD": {"name": "Schwab US Dividend Equity ETF", "sector": "Dividend ETF", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "VTI": {"name": "Vanguard Total Stock Market ETF", "sector": "Broad Market ETF", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "SPY": {"name": "SPDR S&P 500 ETF Trust", "sector": "Large Cap ETF", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "IVV": {"name": "iShares Core S&P 500 ETF", "sector": "Large Cap ETF", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "VOO": {"name": "Vanguard S&P 500 ETF", "sector": "Large Cap ETF", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "QQQ": {"name": "Invesco QQQ Trust", "sector": "Technology ETF", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"}
            },
            
            # === International ETFs ===
            "INTERNATIONAL_ETFS": {
                "IEV": {"name": "iShares Europe ETF", "sector": "European ETF", "region": "Europe", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "XEH": {"name": "iShares Core MSCI EAFE IMI Index ETF", "sector": "International ETF", "region": "Global", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "VEA": {"name": "Vanguard FTSE Developed Markets ETF", "sector": "Developed Markets ETF", "region": "Global", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "VWO": {"name": "Vanguard FTSE Emerging Markets ETF", "sector": "Emerging Markets ETF", "region": "Global", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "ACWI": {"name": "iShares MSCI ACWI ETF", "sector": "Global ETF", "region": "Global", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"}
            },
            
            # === Chinese/International Stocks ===
            "CHINESE_STOCKS": {
                "BABA": {"name": "Alibaba Group Holding Ltd", "sector": "E-commerce", "region": "China", "gics_sector": "Consumer Discretionary", "gics_industry": "Internet & Direct Marketing Retail"},
                "PDD": {"name": "PDD Holdings Inc", "sector": "E-commerce", "region": "China", "gics_sector": "Consumer Discretionary", "gics_industry": "Internet & Direct Marketing Retail"},
                "TSM": {"name": "Taiwan Semiconductor Manufacturing Co Ltd", "sector": "Semiconductors", "region": "Taiwan", "gics_sector": "Information Technology", "gics_industry": "Semiconductors & Semiconductor Equipment"}
            },
            
            # === Canadian Stocks ===
            "CANADIAN_STOCKS": {
                "BN": {"name": "Brookfield Corp", "sector": "Asset Management", "region": "Canada", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "LULU": {"name": "Lululemon Athletica Inc", "sector": "Apparel", "region": "Canada", "gics_sector": "Consumer Discretionary", "gics_industry": "Apparel, Accessories & Luxury Goods"},
                "MC": {"name": "Magna International Inc", "sector": "Auto Parts", "region": "Canada", "gics_sector": "Consumer Discretionary", "gics_industry": "Auto Parts & Equipment"},
                "ELV": {"name": "Elevance Health Inc", "sector": "Health Insurance", "region": "US", "gics_sector": "Health Care", "gics_industry": "Managed Health Care"},
                "KKR": {"name": "KKR & Co Inc", "sector": "Private Equity", "region": "US", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"},
                "RCI.B": {"name": "Rogers Communications Inc", "sector": "Telecommunications", "region": "Canada", "gics_sector": "Communication Services", "gics_industry": "Integrated Telecommunication Services"},
                "BEPC": {"name": "Brookfield Renewable Partners LP", "sector": "Renewable Energy", "region": "Canada", "gics_sector": "Utilities", "gics_industry": "Independent Power and Renewable Electricity Producers"},
                "EPD": {"name": "Enterprise Products Partners LP", "sector": "Energy Infrastructure", "region": "US", "gics_sector": "Energy", "gics_industry": "Oil & Gas Storage & Transportation"},
                "ET": {"name": "Energy Transfer LP", "sector": "Energy Infrastructure", "region": "US", "gics_sector": "Energy", "gics_industry": "Oil & Gas Storage & Transportation"}
            },
            
            # === Cash and Money Market ===
            "CASH": {
                "CASH": {"name": "Cash", "sector": "Cash", "region": "N/A", "gics_sector": "Financials", "gics_industry": "Asset Management & Custody Banks"}
            }
        }
    
    def get_classification(self, symbol: str) -> Optional[Dict]:
        """Get classification for a ticker symbol."""
        symbol = symbol.upper()
        
        # Search through all categories
        for category, tickers in self.classifications.items():
            if symbol in tickers:
                return tickers[symbol]
        
        return None
    
    def get_all_tickers(self) -> List[str]:
        """Get all ticker symbols in the database."""
        all_tickers = []
        for category, tickers in self.classifications.items():
            all_tickers.extend(tickers.keys())
        return sorted(all_tickers)
    
    def get_tickers_by_sector(self, sector: str) -> List[str]:
        """Get all tickers in a specific sector."""
        tickers = []
        for category, ticker_data in self.classifications.items():
            for symbol, data in ticker_data.items():
                if data.get("sector", "").lower() == sector.lower():
                    tickers.append(symbol)
        return sorted(tickers)
    
    def get_tickers_by_region(self, region: str) -> List[str]:
        """Get all tickers in a specific region."""
        tickers = []
        for category, ticker_data in self.classifications.items():
            for symbol, data in ticker_data.items():
                if data.get("region", "").lower() == region.lower():
                    tickers.append(symbol)
        return sorted(tickers)
    
    def get_gics_classification(self, symbol: str) -> Optional[Tuple[str, str]]:
        """Get GICS sector and industry for a ticker."""
        classification = self.get_classification(symbol)
        if classification:
            return classification.get("gics_sector"), classification.get("gics_industry")
        return None
    
    def export_to_json(self, filepath: str):
        """Export the classification database to JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.classifications, f, indent=2)
    
    def get_statistics(self) -> Dict:
        """Get statistics about the classification database."""
        total_tickers = len(self.get_all_tickers())
        sectors = set()
        regions = set()
        gics_sectors = set()
        
        for category, ticker_data in self.classifications.items():
            for symbol, data in ticker_data.items():
                sectors.add(data.get("sector", ""))
                regions.add(data.get("region", ""))
                gics_sectors.add(data.get("gics_sector", ""))
        
        return {
            "total_tickers": total_tickers,
            "total_categories": len(self.classifications),
            "unique_sectors": len(sectors),
            "unique_regions": len(regions),
            "unique_gics_sectors": len(gics_sectors),
            "sectors": sorted(list(sectors)),
            "regions": sorted(list(regions)),
            "gics_sectors": sorted(list(gics_sectors))
        }

# Example usage and testing
if __name__ == "__main__":
    db = TickerClassificationDatabase()
    
    print("=== TICKER CLASSIFICATION DATABASE ===")
    print()
    
    # Test some classifications
    test_symbols = ["AAPL", "STAG", "ARX", "BABA", "CDZ", "HYG"]
    
    for symbol in test_symbols:
        classification = db.get_classification(symbol)
        if classification:
            print(f"{symbol:6} | {classification['name']:40} | {classification['sector']:20} | {classification['region']:8} | {classification['gics_sector']}")
        else:
            print(f"{symbol:6} | NOT FOUND")
    
    print()
    
    # Get statistics
    stats = db.get_statistics()
    print("=== DATABASE STATISTICS ===")
    print(f"Total Tickers: {stats['total_tickers']}")
    print(f"Categories: {stats['total_categories']}")
    print(f"Unique Sectors: {stats['unique_sectors']}")
    print(f"Unique Regions: {stats['unique_regions']}")
    print(f"GICS Sectors: {stats['unique_gics_sectors']}")
    print()
    print("GICS Sectors:", ", ".join(stats['gics_sectors']))
