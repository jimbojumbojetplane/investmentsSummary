"""
Comprehensive Asset Classification System
Based on GICS (Global Industry Classification Standard) and ICB (Industry Classification Benchmark)
"""

import pandas as pd
import re
from typing import Dict, Tuple, List, Optional
from .ticker_classification_database import TickerClassificationDatabase

class AssetClassifier:
    """Comprehensive asset classification system for financial instruments."""
    
    def __init__(self):
        self.ticker_db = TickerClassificationDatabase()
        self.setup_classification_rules()
    
    def setup_classification_rules(self):
        """Setup comprehensive classification rules based on industry standards."""
        
        # REITs - Real Estate Investment Trusts
        self.reits = {
            'STAG': 'STAG Industrial Inc',
            'REXR': 'Rexford Industrial Realty Inc', 
            'O': 'Realty Income Corp',
            'ZRE': 'BMO Equal Weight REITs Index ETF',
            'VRE': 'Vanguard FTSE Canadian Capped REIT Index ETF',
            'XRE': 'iShares S&P/TSX Capped REIT Index ETF'
        }
        
        # Technology Sector
        self.technology = {
            'AAPL': 'Apple Inc',
            'GOOGL': 'Alphabet Inc Class A',
            'MSFT': 'Microsoft Corp',
            'AMZN': 'Amazon.com Inc',
            'ADBE': 'Adobe Inc',
            'CRM': 'Salesforce Inc',
            'SHOP': 'Shopify Inc',
            'NFLX': 'Netflix Inc',
            'SMH': 'VanEck Semiconductor ETF',
            'TAN': 'Invesco Solar ETF',
            'QQQ': 'Invesco QQQ Trust',
            'XLK': 'Technology Select Sector SPDR Fund'
        }
        
        # Healthcare Sector
        self.healthcare = {
            'PFE': 'Pfizer Inc',
            'MRK': 'Merck & Co Inc',
            'JNJ': 'Johnson & Johnson',
            'UNH': 'UnitedHealth Group Inc',
            'ABBV': 'AbbVie Inc',
            'XLV': 'Health Care Select Sector SPDR Fund'
        }
        
        # Communications Sector
        self.communications = {
            'T': 'AT&T Inc',
            'VZ': 'Verizon Communications Inc',
            'CMCSA': 'Comcast Corp',
            'DIS': 'Walt Disney Co',
            'XLC': 'Communication Services Select Sector SPDR Fund'
        }
        
        # Consumer Discretionary
        self.consumer_discretionary = {
            'NKE': 'Nike Inc',
            'TSLA': 'Tesla Inc',
            'HD': 'Home Depot Inc',
            'MCD': 'McDonald\'s Corp',
            'XLY': 'Consumer Discretionary Select Sector SPDR Fund'
        }
        
        # Consumer Staples
        self.consumer_staples = {
            'PG': 'Procter & Gamble Co',
            'KO': 'Coca-Cola Co',
            'WMT': 'Walmart Inc',
            'XLP': 'Consumer Staples Select Sector SPDR Fund'
        }
        
        # Industrial Sector
        self.industrial = {
            'UPS': 'United Parcel Service Inc',
            'BA': 'Boeing Co',
            'CAT': 'Caterpillar Inc',
            'GE': 'General Electric Co',
            'XLI': 'Industrial Select Sector SPDR Fund'
        }
        
        # Utilities Sector
        self.utilities = {
            'NEE': 'NextEra Energy Inc',
            'DUK': 'Duke Energy Corp',
            'SO': 'Southern Co',
            'XLU': 'Utilities Select Sector SPDR Fund'
        }
        
        # Energy Sector
        self.energy = {
            'ARX': 'ARC Resources Ltd',
            'CNQ': 'Canadian Natural Resources Ltd',
            'CVE': 'Cenovus Energy Inc',
            'ENB': 'Enbridge Inc',
            'PPL': 'Pembina Pipeline Corp',
            'XLE': 'Energy Select Sector SPDR Fund',
            'XEG': 'iShares S&P/TSX Capped Energy Index ETF'
        }
        
        # Financial Sector
        self.financial = {
            'JPM': 'JPMorgan Chase & Co',
            'BAC': 'Bank of America Corp',
            'WFC': 'Wells Fargo & Co',
            'GS': 'Goldman Sachs Group Inc',
            'XLF': 'Financial Select Sector SPDR Fund'
        }
        
        # Materials Sector
        self.materials = {
            'FCX': 'Freeport-McMoRan Inc',
            'NEM': 'Newmont Corp',
            'XLB': 'Materials Select Sector SPDR Fund'
        }
        
        # Fixed Income - Government Bonds
        self.government_bonds = {
            'TLT': 'iShares 20+ Year Treasury Bond ETF',
            'IEF': 'iShares 7-10 Year Treasury Bond ETF',
            'SHY': 'iShares 1-3 Year Treasury Bond ETF',
            'VGIT': 'Vanguard Intermediate-Term Treasury ETF'
        }
        
        # Fixed Income - Corporate Bonds
        self.corporate_bonds = {
            'LQD': 'iShares iBoxx $ Investment Grade Corporate Bond ETF',
            'HYG': 'iShares iBoxx $ High Yield Corporate Bond ETF',
            'VCIT': 'Vanguard Intermediate-Term Corporate Bond ETF',
            'VCSH': 'Vanguard Short-Term Corporate Bond ETF'
        }
        
        # Fixed Income - International Bonds
        self.international_bonds = {
            'BNDX': 'Vanguard Total International Bond ETF',
            'BWX': 'SPDR Bloomberg International Treasury Bond ETF',
            'IGOV': 'iShares International Treasury Bond ETF'
        }
        
        # Canadian ETFs
        self.canadian_etfs = {
            'CDZ': 'iShares S&P/TSX Canadian Dividend Aristocrats Index ETF',
            'XDV': 'iShares Core MSCI Canadian Quality Dividend Index ETF',
            'XIC': 'iShares Core S&P/TSX Capped Composite Index ETF',
            'VCN': 'Vanguard FTSE Canada All Cap Index ETF',
            'ZCN': 'BMO S&P/TSX Capped Composite Index ETF'
        }
        
        # International/Global ETFs
        self.international_etfs = {
            'IEV': 'iShares Europe ETF',
            'XEH': 'iShares Core MSCI EAFE IMI Index ETF',
            'VEA': 'Vanguard FTSE Developed Markets ETF',
            'VWO': 'Vanguard FTSE Emerging Markets ETF',
            'ACWI': 'iShares MSCI ACWI ETF'
        }
        
        # US ETFs
        self.us_etfs = {
            'SCHD': 'Schwab US Dividend Equity ETF',
            'VTI': 'Vanguard Total Stock Market ETF',
            'SPY': 'SPDR S&P 500 ETF Trust',
            'IVV': 'iShares Core S&P 500 ETF',
            'VOO': 'Vanguard S&P 500 ETF'
        }
        
        # Cash and Money Market
        self.cash_instruments = {
            'CASH': 'Cash',
            'MNY': 'Purpose High Interest Savings ETF',
            'HISU.U': 'Horizons USD Cash Maximizer ETF',
            'ICSH': 'iShares Ultra Short-Term Bond ETF'
        }
        
        # Chinese/International Stocks
        self.chinese_stocks = {
            'BABA': 'Alibaba Group Holding Ltd',
            'PDD': 'PDD Holdings Inc',
            'TSM': 'Taiwan Semiconductor Manufacturing Co Ltd'
        }
        
        # Canadian Stocks
        self.canadian_stocks = {
            'BN': 'Brookfield Corp',
            'LULU': 'Lululemon Athletica Inc',
            'MC': 'Magna International Inc',
            'ELV': 'Elevance Health Inc',
            'KKR': 'KKR & Co Inc'
        }
    
    def classify_holding(self, symbol: str, name: str = "", asset_class: str = "", 
                        sub_category: str = "", region: str = "", etf_type: str = "", 
                        value: float = 0) -> Tuple[str, str, str, str]:
        """
        Classify a holding into comprehensive categories using industry-standard database.
        
        Returns:
            Tuple of (Asset_Class, Sector, Region, Description)
        """
        symbol = str(symbol).upper() if symbol else ""
        name = str(name) if name else ""
        
        # First, try to get classification from comprehensive database
        db_classification = self.ticker_db.get_classification(symbol)
        if db_classification:
            # Map database classification to our system
            asset_class = self._map_gics_to_asset_class(db_classification.get("gics_sector", ""))
            sector = db_classification.get("sector", "")
            region = db_classification.get("region", "")
            description = db_classification.get("name", name if name else symbol)
            
            return asset_class, sector, region, description
        
        # Fallback to legacy classification if not found in database
        return self._legacy_classify_holding(symbol, name, asset_class, sub_category, region, etf_type, value)
    
    def _map_gics_to_asset_class(self, gics_sector: str) -> str:
        """Map GICS sector to our asset class system."""
        gics_mapping = {
            "Real Estate": "Real Estate",
            "Financials": "Fixed Income",  # Most financial ETFs are fixed income
            "Information Technology": "Equity",
            "Communication Services": "Equity",
            "Consumer Discretionary": "Equity",
            "Consumer Staples": "Equity",
            "Industrials": "Equity",
            "Utilities": "Equity",
            "Energy": "Equity",
            "Materials": "Equity",
            "Health Care": "Equity"
        }
        return gics_mapping.get(gics_sector, "Equity")
    
    def _legacy_classify_holding(self, symbol: str, name: str = "", asset_class: str = "", 
                                sub_category: str = "", region: str = "", etf_type: str = "", 
                                value: float = 0) -> Tuple[str, str, str, str]:
        """
        Legacy classification method (fallback).
        
        Returns:
            Tuple of (Asset_Class, Sector, Region, Description)
        """
        # Get description from name or symbol
        description = name if name else symbol
        
        # 1. CASH CLASSIFICATION
        if symbol in self.cash_instruments or asset_class == 'Cash':
            return 'Cash', 'Cash', 'N/A', description
        
        # 2. REIT CLASSIFICATION
        if symbol in self.reits or 'REIT' in name.upper() or 'REALTY' in name.upper():
            region = self._determine_region(symbol, name)
            return 'Real Estate', 'REIT', region, description
        
        # 3. FIXED INCOME CLASSIFICATION
        if symbol in self.government_bonds or 'TREASURY' in name.upper() or 'GOVERNMENT' in name.upper():
            return 'Fixed Income', 'Government Bonds', 'US', description
        elif symbol in self.corporate_bonds or 'CORPORATE' in name.upper() or 'HIGH YIELD' in name.upper():
            return 'Fixed Income', 'Corporate Bonds', 'US', description
        elif symbol in self.international_bonds or 'INTERNATIONAL' in name.upper():
            return 'Fixed Income', 'International Bonds', 'Global', description
        elif 'BOND' in name.upper() or 'FIXED INCOME' in name.upper():
            return 'Fixed Income', 'Bonds', 'Global', description
        
        # 4. EQUITY CLASSIFICATION BY SECTOR
        if symbol in self.technology or 'TECH' in name.upper() or 'SOFTWARE' in name.upper():
            region = self._determine_region(symbol, name)
            return 'Equity', 'Technology', region, description
        elif symbol in self.healthcare or 'HEALTH' in name.upper() or 'PHARMA' in name.upper():
            region = self._determine_region(symbol, name)
            return 'Equity', 'Healthcare', region, description
        elif symbol in self.communications or 'COMMUNICATION' in name.upper() or 'TELECOM' in name.upper():
            region = self._determine_region(symbol, name)
            return 'Equity', 'Communications', region, description
        elif symbol in self.consumer_discretionary or 'CONSUMER' in name.upper() and 'STAPLE' not in name.upper():
            region = self._determine_region(symbol, name)
            return 'Equity', 'Consumer Discretionary', region, description
        elif symbol in self.consumer_staples or 'STAPLE' in name.upper():
            region = self._determine_region(symbol, name)
            return 'Equity', 'Consumer Staples', region, description
        elif symbol in self.industrial or 'INDUSTRIAL' in name.upper():
            region = self._determine_region(symbol, name)
            return 'Equity', 'Industrial', region, description
        elif symbol in self.utilities or 'UTILITY' in name.upper() or 'ENERGY' in name.upper() and 'OIL' not in name.upper():
            region = self._determine_region(symbol, name)
            return 'Equity', 'Utilities', region, description
        elif symbol in self.energy or 'ENERGY' in name.upper() or 'OIL' in name.upper() or 'GAS' in name.upper():
            region = self._determine_region(symbol, name)
            return 'Equity', 'Energy', region, description
        elif symbol in self.financial or 'BANK' in name.upper() or 'FINANCIAL' in name.upper():
            region = self._determine_region(symbol, name)
            return 'Equity', 'Financial', region, description
        elif symbol in self.materials or 'MATERIAL' in name.upper() or 'MINING' in name.upper():
            region = self._determine_region(symbol, name)
            return 'Equity', 'Materials', region, description
        
        # 5. ETF CLASSIFICATION
        if symbol in self.canadian_etfs or 'CANADIAN' in name.upper():
            return 'Equity', 'Canadian ETF', 'Canada', description
        elif symbol in self.us_etfs or 'US' in name.upper() or 'S&P' in name.upper():
            return 'Equity', 'US ETF', 'US', description
        elif symbol in self.international_etfs or 'INTERNATIONAL' in name.upper() or 'GLOBAL' in name.upper():
            return 'Equity', 'International ETF', 'Global', description
        
        # 6. GEOGRAPHIC CLASSIFICATION FOR INDIVIDUAL STOCKS
        if symbol in self.chinese_stocks:
            return 'Equity', 'Technology', 'China', description
        elif symbol in self.canadian_stocks:
            return 'Equity', 'Diversified', 'Canada', description
        
        # 7. DEFAULT CLASSIFICATION
        region = self._determine_region(symbol, name)
        return 'Equity', 'Diversified', region, description
    
    def _determine_region(self, symbol: str, name: str) -> str:
        """Determine the geographic region of a holding."""
        name_upper = name.upper()
        
        # Canadian indicators
        if any(indicator in name_upper for indicator in ['LTD', 'CORP', 'INC']) and 'CANADIAN' in name_upper:
            return 'Canada'
        elif any(indicator in name_upper for indicator in ['LTD', 'CORP', 'INC']) and not any(geo in name_upper for geo in ['US', 'AMERICAN', 'CHINA', 'CHINESE']):
            return 'Canada'  # Default for Canadian companies
        
        # US indicators
        if any(indicator in name_upper for indicator in ['INC', 'CORP', 'CO']) and any(geo in name_upper for geo in ['US', 'AMERICAN']):
            return 'US'
        elif any(indicator in name_upper for indicator in ['INC', 'CORP', 'CO']) and not any(geo in name_upper for geo in ['CANADIAN', 'CHINA', 'CHINESE']):
            return 'US'  # Default for US companies
        
        # Chinese indicators
        if any(geo in name_upper for geo in ['CHINA', 'CHINESE', 'ALIBABA', 'PDD']):
            return 'China'
        
        # European indicators
        if any(geo in name_upper for geo in ['EUROPE', 'EUROPEAN', 'GERMAN', 'FRENCH', 'BRITISH']):
            return 'Europe'
        
        # Default
        return 'Global'
    
    def get_sector_breakdown(self, holdings_df: pd.DataFrame) -> pd.DataFrame:
        """Get detailed sector breakdown of holdings."""
        classified_data = []
        
        for _, row in holdings_df.iterrows():
            symbol = row.get('Symbol', '')
            name = row.get('Name', row.get('Description', ''))
            asset_class = row.get('High_Level_Asset_Class', '')
            sub_category = row.get('Sub_Category', '')
            region = row.get('ETF_Region', '')
            etf_type = row.get('ETF_Type', '')
            value = row.get('Total_Market_Value', row.get('Market Value', 0))
            
            asset_class_new, sector, region_new, description = self.classify_holding(
                symbol, name, asset_class, sub_category, region, etf_type, value
            )
            
            classified_data.append({
                'Symbol': symbol,
                'Name': name,
                'Description': description,
                'Asset_Class': asset_class_new,
                'Sector': sector,
                'Region': region_new,
                'Market_Value': value,
                'Account': row.get('Account', ''),
                'Source': row.get('Source', '')
            })
        
        return pd.DataFrame(classified_data)
    
    def get_classification_summary(self, holdings_df: pd.DataFrame) -> Dict:
        """Get comprehensive classification summary."""
        classified_df = self.get_sector_breakdown(holdings_df)
        
        # Asset class summary
        asset_class_summary = classified_df.groupby('Asset_Class')['Market_Value'].sum().to_dict()
        
        # Sector summary
        sector_summary = classified_df.groupby(['Asset_Class', 'Sector'])['Market_Value'].sum().to_dict()
        
        # Regional summary
        regional_summary = classified_df.groupby(['Asset_Class', 'Region'])['Market_Value'].sum().to_dict()
        
        return {
            'asset_classes': asset_class_summary,
            'sectors': sector_summary,
            'regions': regional_summary,
            'classified_data': classified_df
        }
