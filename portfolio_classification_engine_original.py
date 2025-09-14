#!/usr/bin/env python3
"""
Portfolio Classification + Consolidation Engine
Role: Deterministic portfolio data engine for comprehensive classification
Goal: Ingest combined data, normalize, apply classification methodology, 
      compute standardized analytics, and emit enriched holdings + rollups
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

class AssetType(Enum):
    CASH_EQUIVALENTS = "Cash & Equivalents"
    BOND_FIXED_INCOME = "Bond / Fixed Income"
    COMMON_EQUITY = "Common Equity"
    PREFERRED_SHARE = "Preferred Share"
    REIT_EQUITY = "REIT – Equity"
    ETF_EQUITY = "ETF – Equity"
    ETF_DIVIDEND_EQUITY = "ETF – Dividend Equity"
    ETF_REIT = "ETF – REIT"
    ETF_REGIONAL_EQUITY = "ETF – Regional Equity"
    ETF_THEMATIC_EQUITY = "ETF – Thematic Equity"
    ETF_BOND = "ETF – Bond"
    ETF_CASH_ULTRA_SHORT = "ETF – Cash / Ultra-Short"
    ACCOUNT_PLAN_PLACEHOLDER = "Account / Plan Placeholder"

class AssetStructure(Enum):
    COMMON_STOCK = "Common Stock"
    ADR_GDR = "ADR/GDR"
    TRUST_UNIT = "Trust Unit"
    LP_MLP_UNIT = "LP/MLP Unit"
    ETF_ETN = "ETF/ETN"
    NOTE_DEBENTURE_BOND = "Note/Debenture/Bond"
    MONEY_MARKET_FUND = "Money Market Fund"
    PLAN_PLACEHOLDER = "Plan Placeholder"
    OTHER = "Other"

class AccountType(Enum):
    TAXABLE = "Taxable"
    REGISTERED = "Registered"
    PENSION = "Pension"
    UNKNOWN = "Unknown"

class FXHedged(Enum):
    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"

class IncomeType(Enum):
    DIVIDEND = "Dividend"
    DISTRIBUTION = "Distribution"
    INTEREST = "Interest"
    NONE = "None"
    UNKNOWN = "Unknown"

class ProductNormalized(Enum):
    COMMON_SHARES = "Common Shares"
    ETFS_ETNS = "ETFs and ETNs"
    CASH = "Cash"
    FIXED_INCOME = "Fixed Income"
    TRUST_UNITS = "Trust Units"
    PENSION_PLAN = "Pension Plan"
    OTHER = "Other"

@dataclass
class EnrichmentRecord:
    value: str
    source_url: str
    fetched_at: str
    snippet: str
    confidence: float

@dataclass
class ClassificationResult:
    asset_type: AssetType
    asset_structure: AssetStructure
    issuer_region: str
    listing_country: str
    sector: str
    fx_hedged: FXHedged
    income_type: IncomeType
    confidence: float
    source_notes: str

class PortfolioClassificationEngine:
    """Deterministic portfolio classification engine"""
    
    def __init__(self):
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Classification mappings
        self.sector_mappings = {
            # Energy
            'ENB': 'Energy (Midstream)',
            'PPL': 'Energy (Midstream)', 
            'EPD': 'Energy (Midstream)',
            'ET': 'Energy (Midstream)',
            
            # Financials
            'BN': 'Financials (Alternative Asset Manager)',
            'KKR': 'Financials (Alternative Asset Manager)',
            
            # Utilities
            'NEE': 'Utilities',
            'BEPC': 'Utilities (Clean Energy)',
            
            # REITs
            'O': 'Real Estate',
            'REXR': 'Real Estate',
            'STAG': 'Real Estate',
            'NWH.UN': 'Real Estate',
            'PMZ.UN': 'Real Estate',
        }
        
        self.region_mappings = {
            # US Companies
            'AAPL': 'United States', 'MSFT': 'United States', 'GOOGL': 'United States',
            'AMZN': 'United States', 'TSLA': 'United States', 'META': 'United States',
            'NVDA': 'United States', 'NFLX': 'United States', 'ADBE': 'United States',
            'CRM': 'United States', 'ORCL': 'United States', 'INTC': 'United States',
            'AMD': 'United States', 'QCOM': 'United States', 'AVGO': 'United States',
            'TXN': 'United States', 'MU': 'United States', 'AMAT': 'United States',
            'LRCX': 'United States', 'KLAC': 'United States', 'MCHP': 'United States',
            'ADI': 'United States', 'MRVL': 'United States', 'SNPS': 'United States',
            'CDNS': 'United States', 'ANSS': 'United States', 'FTNT': 'United States',
            'CRWD': 'United States', 'OKTA': 'United States', 'ZS': 'United States',
            'PANW': 'United States', 'NET': 'United States', 'DDOG': 'United States',
            'SNOW': 'United States', 'PLTR': 'United States', 'MDB': 'United States',
            'ESTC': 'United States', 'SPLK': 'United States', 'WDAY': 'United States',
            'NOW': 'United States', 'TEAM': 'United States', 'ZM': 'United States',
            'DOCU': 'United States', 'ROKU': 'United States', 'SPOT': 'United States',
            'UBER': 'United States', 'LYFT': 'United States', 'ABNB': 'United States',
            'SQ': 'United States', 'PYPL': 'United States', 'V': 'United States',
            'MA': 'United States', 'AXP': 'United States', 'COF': 'United States',
            'JPM': 'United States', 'BAC': 'United States', 'WFC': 'United States',
            'C': 'United States', 'GS': 'United States', 'MS': 'United States',
            'BLK': 'United States', 'SCHW': 'United States', 'ICE': 'United States',
            'CME': 'United States', 'NDAQ': 'United States', 'SPGI': 'United States',
            'MCO': 'United States', 'FICO': 'United States', 'TRV': 'United States',
            'AON': 'United States', 'MMC': 'United States', 'MSCI': 'United States',
            'VRSK': 'United States', 'FTV': 'United States', 'IT': 'United States',
            'GPN': 'United States', 'FIS': 'United States', 'FISV': 'United States',
            'JKHY': 'United States', 'PAYX': 'United States', 'ADP': 'United States',
            'WU': 'United States', 'EFX': 'United States', 'FLT': 'United States',
            'V': 'United States', 'MA': 'United States', 'AXP': 'United States',
            'COF': 'United States', 'DFS': 'United States', 'SYF': 'United States',
            'ALL': 'United States', 'AIG': 'United States', 'CB': 'United States',
            'CINF': 'United States', 'HIG': 'United States', 'L': 'United States',
            'MMC': 'United States', 'PGR': 'United States', 'PRU': 'United States',
            'TRV': 'United States', 'UNM': 'United States', 'WRB': 'United States',
            'XL': 'United States', 'ZEN': 'United States', 'ZTS': 'United States',
            
            # Canadian Companies
            'SHOP': 'Canada', 'BN': 'Canada', 'ENB': 'Canada', 'CNR': 'Canada',
            'CP': 'Canada', 'TRP': 'Canada', 'PPL': 'Canada', 'SU': 'Canada',
            'CNQ': 'Canada', 'IMO': 'Canada', 'CVE': 'Canada', 'MEG': 'Canada',
            'TOU': 'Canada', 'ARX': 'Canada', 'KEY': 'Canada', 'WCP': 'Canada',
            'BTE': 'Canada', 'ERF': 'Canada', 'PSK': 'Canada', 'VET': 'Canada',
            'TVE': 'Canada', 'GXE': 'Canada', 'FRU': 'Canada', 'PXT': 'Canada',
            'PGF': 'Canada', 'POU': 'Canada', 'PIF': 'Canada', 'PPL': 'Canada',
            'PPL.PR.A': 'Canada', 'PPL.PR.B': 'Canada', 'PPL.PR.C': 'Canada',
            'PPL.PR.D': 'Canada', 'PPL.PR.E': 'Canada', 'PPL.PR.F': 'Canada',
            'PPL.PR.G': 'Canada', 'PPL.PR.H': 'Canada', 'PPL.PR.I': 'Canada',
            'PPL.PR.J': 'Canada', 'PPL.PR.K': 'Canada', 'PPL.PR.L': 'Canada',
            'PPL.PR.M': 'Canada', 'PPL.PR.N': 'Canada', 'PPL.PR.O': 'Canada',
            'PPL.PR.P': 'Canada', 'PPL.PR.Q': 'Canada', 'PPL.PR.R': 'Canada',
            'PPL.PR.S': 'Canada', 'PPL.PR.T': 'Canada', 'PPL.PR.U': 'Canada',
            'PPL.PR.V': 'Canada', 'PPL.PR.W': 'Canada', 'PPL.PR.X': 'Canada',
            'PPL.PR.Y': 'Canada', 'PPL.PR.Z': 'Canada',
            
            # International
            'TSM': 'Taiwan',
            'BABA': 'China', 'PDD': 'China', 'JD': 'China', 'BIDU': 'China',
            'NIO': 'China', 'XPEV': 'China', 'LI': 'China', 'BILI': 'China',
            'TME': 'China', 'VIPS': 'China', 'YMM': 'China', 'WB': 'China',
            'MC': 'France',
        }
        
        # ETF Classification mappings
        self.etf_classifications = {
            # Cash/Ultra-Short ETFs
            'CMR': {'type': AssetType.ETF_CASH_ULTRA_SHORT, 'region': 'Canada', 'sector': 'Cash Equivalent'},
            'MNY': {'type': AssetType.ETF_CASH_ULTRA_SHORT, 'region': 'Canada', 'sector': 'Cash Equivalent'},
            'ICSH': {'type': AssetType.ETF_CASH_ULTRA_SHORT, 'region': 'United States', 'sector': 'Cash Equivalent'},
            'HISU.U': {'type': AssetType.ETF_CASH_ULTRA_SHORT, 'region': 'United States', 'sector': 'Cash Equivalent'},
            
            # Dividend ETFs
            'CDZ': {'type': AssetType.ETF_DIVIDEND_EQUITY, 'region': 'Canada', 'sector': 'Multi-Sector Equity'},
            'XDV': {'type': AssetType.ETF_DIVIDEND_EQUITY, 'region': 'Canada', 'sector': 'Multi-Sector Equity'},
            
            # REIT ETFs
            'ZRE': {'type': AssetType.ETF_REIT, 'region': 'Canada', 'sector': 'Real Estate'},
            
            # Regional ETFs
            'XEH': {'type': AssetType.ETF_REGIONAL_EQUITY, 'region': 'Europe', 'sector': 'Multi-Sector Equity', 'fx_hedged': FXHedged.YES},
            'IEV': {'type': AssetType.ETF_REGIONAL_EQUITY, 'region': 'Europe', 'sector': 'Multi-Sector Equity'},
            
            # Thematic ETFs
            'SMH': {'type': AssetType.ETF_THEMATIC_EQUITY, 'region': 'United States', 'sector': 'Information Technology'},
            'TAN': {'type': AssetType.ETF_THEMATIC_EQUITY, 'region': 'United States', 'sector': 'Utilities (Clean Energy)'},
            
            # Bond ETFs
            'HYG': {'type': AssetType.ETF_BOND, 'region': 'United States', 'sector': 'Fixed Income (High Yield)'},
        }
    
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol: uppercase, trim, preserve dots"""
        if not symbol:
            return ""
        return str(symbol).strip().upper()
    
    def normalize_name(self, name: str, description: str = "") -> str:
        """Normalize name: trim spaces, fallback to description"""
        if not name and description:
            return str(description).strip()
        return str(name or "").strip()
    
    def normalize_percentage(self, pct_str: str) -> float:
        """Convert percentage string to decimal (e.g., '-1.58%' -> -0.0158)"""
        if not pct_str:
            return 0.0
        pct_str = str(pct_str).replace('%', '').replace(',', '').strip()
        try:
            return float(pct_str) / 100.0
        except (ValueError, TypeError):
            return 0.0
    
    def normalize_amount(self, amount: Union[str, float, int]) -> float:
        """Convert amount to decimal, handling commas and currency symbols"""
        if amount is None:
            return 0.0
        if isinstance(amount, (int, float)):
            return float(amount)
        
        amount_str = str(amount).replace(',', '').replace('$', '').replace('CAD', '').replace('USD', '').strip()
        try:
            return float(amount_str)
        except (ValueError, TypeError):
            return 0.0
    
    def normalize_product(self, product: str) -> ProductNormalized:
        """Map Product to Product_Normalized enum"""
        if not product:
            return ProductNormalized.OTHER
        
        product_lower = str(product).lower()
        if 'common share' in product_lower:
            return ProductNormalized.COMMON_SHARES
        elif 'etf' in product_lower or 'etn' in product_lower:
            return ProductNormalized.ETFS_ETNS
        elif 'cash' in product_lower:
            return ProductNormalized.CASH
        elif 'fixed income' in product_lower or 'bond' in product_lower:
            return ProductNormalized.FIXED_INCOME
        elif 'trust unit' in product_lower:
            return ProductNormalized.TRUST_UNITS
        elif 'pension' in product_lower:
            return ProductNormalized.PENSION_PLAN
        else:
            return ProductNormalized.OTHER
    
    def detect_account_type(self, account_id: str, symbol: str) -> AccountType:
        """Detect account type based on account ID and symbol"""
        if 'DC_PENSION' in symbol or 'PENSION' in symbol:
            return AccountType.PENSION
        elif 'RRSP' in symbol or 'RRSP' in account_id:
            return AccountType.REGISTERED
        else:
            return AccountType.TAXABLE
    
    def classify_asset_structure(self, symbol: str, product: str, name: str) -> AssetStructure:
        """Classify asset structure based on symbol, product, and name"""
        symbol_upper = str(symbol).upper()
        product_lower = str(product).lower()
        name_lower = str(name).lower()
        
        if 'etf' in product_lower or 'etn' in product_lower:
            return AssetStructure.ETF_ETN
        elif any(term in product_lower for term in ['note', 'debenture', 'bond', 'mtn']):
            return AssetStructure.NOTE_DEBENTURE_BOND
        elif '.UN' in symbol_upper or 'trust' in product_lower or 'trust' in name_lower:
            return AssetStructure.TRUST_UNIT
        elif any(term in name_lower for term in ['lp', 'mlp', 'partnership']):
            return AssetStructure.LP_MLP_UNIT
        elif any(term in name_lower for term in ['adr', 'sponsored adr']):
            return AssetStructure.ADR_GDR
        elif 'money market' in name_lower or 'mmf' in name_lower:
            return AssetStructure.MONEY_MARKET_FUND
        elif symbol_upper in ['DC_PENSION', 'RRSP', 'RRSP_BELL']:
            return AssetStructure.PLAN_PLACEHOLDER
        else:
            return AssetStructure.COMMON_STOCK
    
    def classify_asset_type(self, symbol: str, product: str, name: str, etf_type: str = "", etf_region: str = "") -> AssetType:
        """Classify asset type using comprehensive rules"""
        symbol_upper = str(symbol).upper()
        product_lower = str(product).lower()
        name_lower = str(name).lower()
        etf_type_lower = str(etf_type).lower()
        etf_region_lower = str(etf_region).lower()
        
        # Plan placeholders first
        if symbol_upper in ['DC_PENSION', 'RRSP', 'RRSP_BELL']:
            return AssetType.ACCOUNT_PLAN_PLACEHOLDER
        
        # Cash detection
        if product_lower == 'cash' or name_lower.startswith('cash -'):
            return AssetType.CASH_EQUIVALENTS
        
        # ETF classification (check specific ETFs first)
        if symbol_upper in self.etf_classifications:
            return self.etf_classifications[symbol_upper]['type']
        
        # General ETF classification
        if 'etf' in product_lower or 'etn' in product_lower:
            # Cash/Ultra-short ETFs
            if any(term in name_lower for term in ['money market', 'hisa', 'ultra short', 'cash']):
                return AssetType.ETF_CASH_ULTRA_SHORT
            # Bond ETFs
            elif 'bond' in etf_type_lower or 'fixed income' in etf_type_lower:
                return AssetType.ETF_BOND
            # REIT ETFs
            elif 'reit' in etf_type_lower or 'reit' in name_lower:
                return AssetType.ETF_REIT
            # Dividend ETFs
            elif any(term in name_lower for term in ['dividend', 'aristocrat', 'select dividend']):
                return AssetType.ETF_DIVIDEND_EQUITY
            # Thematic ETFs
            elif any(term in name_lower for term in ['semiconductor', 'clean energy', 'solar', 'wind']):
                return AssetType.ETF_THEMATIC_EQUITY
            # Regional ETFs
            elif any(term in etf_region_lower for term in ['europe', 'us', 'canada', 'eafe', 'em']):
                return AssetType.ETF_REGIONAL_EQUITY
            # Default ETF
            else:
                return AssetType.ETF_EQUITY
        
        # Bond/Note classification
        if any(term in product_lower for term in ['bond', 'note', 'debenture', 'mtn']):
            return AssetType.BOND_FIXED_INCOME
        
        # Trust/REIT classification
        if '.UN' in symbol_upper or 'trust' in product_lower:
            return AssetType.REIT_EQUITY
        
        # Individual REIT stocks
        if symbol_upper in ['O', 'REXR', 'STAG', 'NWH.UN', 'PMZ.UN']:
            return AssetType.REIT_EQUITY
        
        # Default to Common Equity
        return AssetType.COMMON_EQUITY
    
    def classify_issuer_region(self, symbol: str, name: str, etf_region: str = "", asset_type: AssetType = None) -> str:
        """Classify issuer region"""
        symbol_upper = str(symbol).upper()
        
        # Check specific mappings first
        if symbol_upper in self.region_mappings:
            return self.region_mappings[symbol_upper]
        
        # ETF region classification
        if asset_type and asset_type.value.startswith('ETF'):
            etf_region_lower = str(etf_region).lower()
            if 'canada' in etf_region_lower:
                return 'Canada'
            elif 'us' in etf_region_lower or 'united states' in etf_region_lower:
                return 'United States'
            elif 'europe' in etf_region_lower:
                return 'Europe'
            elif 'global' in etf_region_lower:
                return 'Global'
            elif 'asia' in etf_region_lower:
                return 'Asia'
            elif 'emerging' in etf_region_lower:
                return 'Emerging Markets'
        
        # Default to Unknown for now (will be enriched later)
        return 'Unknown'
    
    def classify_listing_country(self, symbol: str, name: str) -> str:
        """Classify listing country based on exchange"""
        symbol_upper = str(symbol).upper()
        
        # TSX listings (Canadian)
        if '.TO' in symbol_upper or any(suffix in symbol_upper for suffix in ['.B', '.UN', '.U']):
            return 'Canada'
        
        # US exchanges
        if any(suffix in symbol_upper for suffix in ['.N', '.A', '.B', '.C', '.D', '.E', '.F', '.G', '.H', '.I', '.J', '.K', '.L', '.M', '.N', '.O', '.P', '.Q', '.R', '.S', '.T', '.U', '.V', '.W', '.X', '.Y', '.Z']):
            return 'United States'
        
        # Default based on common patterns
        if symbol_upper in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']:
            return 'United States'
        elif symbol_upper in ['SHOP', 'BN', 'ENB', 'CNR', 'CP', 'TRP']:
            return 'Canada'
        
        return 'Unknown'
    
    def classify_sector(self, symbol: str, name: str, asset_type: AssetType, etf_type: str = "") -> str:
        """Classify sector using comprehensive rules"""
        symbol_upper = str(symbol).upper()
        name_lower = str(name).lower()
        etf_type_lower = str(etf_type).lower()
        
        # Check specific mappings first
        if symbol_upper in self.sector_mappings:
            return self.sector_mappings[symbol_upper]
        
        # ETF sector classification
        if asset_type.value.startswith('ETF'):
            if symbol_upper in self.etf_classifications:
                return self.etf_classifications[symbol_upper]['sector']
            
            # General ETF sector rules
            if 'semiconductor' in name_lower or 'chip' in name_lower:
                return 'Information Technology'
            elif any(term in name_lower for term in ['clean energy', 'solar', 'wind', 'renewable']):
                return 'Utilities (Clean Energy)'
            elif 'reit' in name_lower or 'real estate' in name_lower:
                return 'Real Estate'
            elif any(term in name_lower for term in ['bond', 'fixed income', 'treasury']):
                return 'Fixed Income (High Yield)'
            elif any(term in name_lower for term in ['dividend', 'aristocrat']):
                return 'Multi-Sector Equity'
            elif any(term in name_lower for term in ['money market', 'cash', 'hisa']):
                return 'Cash Equivalent'
            else:
                return 'Multi-Sector Equity'
        
        # Cash classification
        if asset_type == AssetType.CASH_EQUIVALENTS:
            return 'Cash Equivalent'
        
        # Bond classification
        if asset_type == AssetType.BOND_FIXED_INCOME:
            return 'Fixed Income (High Yield)'
        
        # REIT classification
        if asset_type == AssetType.REIT_EQUITY:
            return 'Real Estate'
        
        # Default to Unknown (will be enriched later)
        return 'Unknown'
    
    def classify_fx_hedged(self, symbol: str, name: str, asset_structure: AssetStructure) -> FXHedged:
        """Classify FX hedging"""
        name_lower = str(name).lower()
        
        # ADRs are not hedged
        if asset_structure == AssetStructure.ADR_GDR:
            return FXHedged.NO
        
        # Check for hedging indicators in ETF names
        if any(term in name_lower for term in ['hedged', 'cad-hedged', 'currency hedged']):
            return FXHedged.YES
        
        # Default to Unknown
        return FXHedged.UNKNOWN
    
    def classify_income_type(self, asset_type: AssetType, annual_dividend_per_share: float) -> IncomeType:
        """Classify income type"""
        if annual_dividend_per_share and annual_dividend_per_share > 0:
            if asset_type in [AssetType.REIT_EQUITY, AssetType.ETF_REIT]:
                return IncomeType.DISTRIBUTION
            elif asset_type == AssetType.BOND_FIXED_INCOME:
                return IncomeType.INTEREST
            else:
                return IncomeType.DIVIDEND
        else:
            return IncomeType.NONE
    
    def classify_holding(self, holding: Dict[str, Any]) -> ClassificationResult:
        """Main classification function for a single holding"""
        symbol = self.normalize_symbol(holding.get('Symbol', ''))
        name = self.normalize_name(holding.get('Name', ''), holding.get('Description', ''))
        product = str(holding.get('Product', ''))
        etf_type = str(holding.get('ETF_Type', ''))
        etf_region = str(holding.get('ETF_Region', ''))
        annual_dividend_per_share = self.normalize_amount(holding.get('Annual Dividend Amount $', 0))
        
        # Classify asset structure first
        asset_structure = self.classify_asset_structure(symbol, product, name)
        
        # Classify asset type
        asset_type = self.classify_asset_type(symbol, product, name, etf_type, etf_region)
        
        # Classify issuer region
        issuer_region = self.classify_issuer_region(symbol, name, etf_region, asset_type)
        
        # Classify listing country
        listing_country = self.classify_listing_country(symbol, name)
        
        # Classify sector
        sector = self.classify_sector(symbol, name, asset_type, etf_type)
        
        # Classify FX hedging
        fx_hedged = self.classify_fx_hedged(symbol, name, asset_structure)
        
        # Classify income type
        income_type = self.classify_income_type(asset_type, annual_dividend_per_share)
        
        # Calculate confidence
        confidence = 1.0
        if issuer_region == 'Unknown':
            confidence -= 0.2
        if sector == 'Unknown':
            confidence -= 0.2
        if fx_hedged == FXHedged.UNKNOWN:
            confidence -= 0.1
        
        # Generate source notes
        source_notes = f"Classified using deterministic rules. Asset type: {asset_type.value}"
        if confidence < 0.8:
            source_notes += f" (Confidence: {confidence:.1f})"
        
        return ClassificationResult(
            asset_type=asset_type,
            asset_structure=asset_structure,
            issuer_region=issuer_region,
            listing_country=listing_country,
            sector=sector,
            fx_hedged=fx_hedged,
            income_type=income_type,
            confidence=confidence,
            source_notes=source_notes
        )
    
    def process_holdings(self, input_file: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Process holdings and create enriched data"""
        print(f"🔄 Loading data from {input_file}...")
        
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Handle holdings_combined_*.json format (array of objects with type/data structure)
        if isinstance(data, list):
            # Extract components from array format
            financial_summaries = [item for item in data if item.get('type') == 'financial_summary']
            holdings = [item for item in data if item.get('type') == 'current_holdings']
            
            # Create metadata
            metadata = {
                'created_at': datetime.now().isoformat(),
                'total_holdings': len(holdings),
                'total_financial_summaries': len(financial_summaries),
                'rbc_holdings_count': len([h for h in holdings if h.get('data', {}).get('Source') != 'Benefits']),
                'benefits_holdings_count': len([h for h in holdings if h.get('data', {}).get('Source') == 'Benefits'])
            }
            
            # Extract data from the type/data structure
            financial_summaries = [item['data'] for item in financial_summaries]
            holdings = [item['data'] for item in holdings]
            
        else:
            # Handle step1 format (object with metadata/financial_summaries/holdings keys)
            metadata = data.get('metadata', {})
            financial_summaries = data.get('financial_summaries', [])
            holdings = data.get('holdings', [])
        
        print(f"   📊 Loaded {len(holdings)} holdings and {len(financial_summaries)} financial summaries")
        
        # Create FX lookup from financial summaries
        fx_lookup = {}
        account_totals = {}
        for summary in financial_summaries:
            account_data = summary.get('data', {})
            account_id = account_data.get('Account #', '')
            fx_lookup[account_id] = self.normalize_amount(account_data.get('Exchange Rate to CAD', 1.0))
            account_totals[account_id] = self.normalize_amount(account_data.get('Total (CAD)', 0.0))
        
        # Process each holding
        enriched_holdings = []
        total_portfolio_value = 0.0
        
        for holding in holdings:
            # Get account info
            account_id = str(holding.get('Account #', ''))
            fx_to_cad = fx_lookup.get(account_id, 1.0)
            
            # Normalize basic fields
            symbol_normalized = self.normalize_symbol(holding.get('Symbol', ''))
            name_normalized = self.normalize_name(holding.get('Name', ''), holding.get('Description', ''))
            product_normalized = self.normalize_product(holding.get('Product', ''))
            account_type = self.detect_account_type(account_id, symbol_normalized)
            
            # Classify the holding
            classification = self.classify_holding(holding)
            
            # Calculate financial metrics
            price = self.normalize_amount(holding.get('Last Price', 0))
            quantity = self.normalize_amount(holding.get('Quantity', 0))
            market_value_local = self.normalize_amount(holding.get('Total Market Value', 0))
            book_value_local = self.normalize_amount(holding.get('Total Book Cost', 0))
            
            # Use calculated market value if not provided
            if market_value_local == 0 and price > 0 and quantity > 0:
                market_value_local = price * quantity
            
            # Convert to CAD
            market_value_cad = market_value_local * fx_to_cad
            book_value_cad = book_value_local * fx_to_cad
            unrealized_pnl_cad = market_value_cad - book_value_cad
            
            # Calculate weights (will be updated after all holdings are processed)
            weight_in_account = 0.0
            weight_total_portfolio = 0.0
            
            # Calculate income metrics
            annual_dividend_per_share = self.normalize_amount(holding.get('Annual Dividend Amount $', 0))
            indicated_annual_income = annual_dividend_per_share * quantity * fx_to_cad if annual_dividend_per_share > 0 and quantity > 0 else None
            indicated_yield_on_market = (indicated_annual_income / market_value_cad) if indicated_annual_income and market_value_cad > 0 else None
            yield_on_cost = (indicated_annual_income / book_value_cad) if indicated_annual_income and book_value_cad > 0 else None
            
            # Cap yields to 0-50%
            if indicated_yield_on_market and (indicated_yield_on_market < 0 or indicated_yield_on_market > 0.5):
                indicated_yield_on_market = None
            if yield_on_cost and (yield_on_cost < 0 or yield_on_cost > 0.5):
                yield_on_cost = None
            
            # Determine if include in exposure
            include_in_exposure = classification.asset_type != AssetType.ACCOUNT_PLAN_PLACEHOLDER
            
            # Create enriched holding
            enriched_holding = {
                # Original fields (preserved)
                **holding,
                
                # Identity & Normalization
                'Symbol_Normalized': symbol_normalized,
                'Name_Normalized': name_normalized,
                'Product_Normalized': product_normalized.value,
                'Account_Id': account_id,
                'Account_Type': account_type.value,
                
                # Classification
                'Asset_Type': classification.asset_type.value,
                'Asset_Structure': classification.asset_structure.value,
                'Issuer_Region': classification.issuer_region,
                'Listing_Country': classification.listing_country,
                'Sector': classification.sector,
                'Sector_in_Region': f"{classification.sector} — {classification.issuer_region}",
                'FX_Hedged': classification.fx_hedged.value,
                'Income_Type': classification.income_type.value,
                'Include_in_Exposure': include_in_exposure,
                
                # Pricing, P&L, and Currency
                'Price': price,
                'Quantity': quantity,
                'Market_Value': market_value_local,
                'Book_Value': book_value_local,
                'Unrealized_PnL': market_value_local - book_value_local,
                'Day_Change_Value': self.normalize_amount(holding.get('Change $', 0)),
                'Day_Change_Pct': self.normalize_percentage(holding.get('Change %', 0)),
                'Currency_Local': str(holding.get('Currency', '')),
                'FX_To_CAD': fx_to_cad,
                'Market_Value_CAD': market_value_cad,
                'Book_Value_CAD': book_value_cad,
                'Unrealized_PnL_CAD': unrealized_pnl_cad,
                'Weight_in_Account': weight_in_account,
                'Weight_Total_Portfolio': weight_total_portfolio,
                
                # Income & Yield
                'Indicated_Annual_Income': indicated_annual_income,
                'Indicated_Yield_on_Market': indicated_yield_on_market,
                'Yield_on_Cost': yield_on_cost,
                
                # Security-Specific
                'ETF_Region_Input': str(holding.get('ETF_Region', '')),
                'ETF_Type_Input': str(holding.get('ETF_Type', '')),
                'ETF_Region_Final': classification.issuer_region if classification.asset_type.value.startswith('ETF') else None,
                'ETF_Type_Final': classification.asset_type.value if classification.asset_type.value.startswith('ETF') else None,
                
                # Governance, Sourcing, QA
                'Source_Primary': 'RBC Holdings Feed',
                'Source_Notes': classification.source_notes,
                'Last_Verified_Date': datetime.now().strftime('%Y-%m-%d'),
                'Confidence': classification.confidence,
                
                # Quality Flags
                'Is_Duplicate_Cash_Line': False,  # Will be set later
                'Needs_Manual_Review': classification.confidence < 0.9 or classification.issuer_region == 'Unknown' or classification.sector == 'Unknown'
            }
            
            enriched_holdings.append(enriched_holding)
            
            if include_in_exposure:
                total_portfolio_value += market_value_cad
        
        # Calculate weights now that we have total portfolio value
        for holding in enriched_holdings:
            if holding['Include_in_Exposure']:
                account_total = account_totals.get(holding['Account_Id'], 0)
                if account_total > 0:
                    holding['Weight_in_Account'] = holding['Market_Value_CAD'] / account_total
                if total_portfolio_value > 0:
                    holding['Weight_Total_Portfolio'] = holding['Market_Value_CAD'] / total_portfolio_value
        
        # Create rollups
        rollups = self.create_rollups(enriched_holdings, financial_summaries, total_portfolio_value)
        
        return enriched_holdings, rollups
    
    def create_rollups(self, holdings: List[Dict[str, Any]], financial_summaries: List[Dict[str, Any]], total_portfolio_value: float) -> Dict[str, Any]:
        """Create rollup summaries"""
        print("🔄 Creating rollups...")
        
        # By Account
        by_account = []
        for summary in financial_summaries:
            account_data = summary.get('data', {})
            account_id = account_data.get('Account #', '')
            
            # Get holdings for this account
            account_holdings = [h for h in holdings if h['Account_Id'] == account_id]
            account_total_cad = sum(h['Market_Value_CAD'] for h in account_holdings if h['Include_in_Exposure'])
            
            # Calculate weights by asset type
            asset_weights = {}
            for holding in account_holdings:
                if holding['Include_in_Exposure']:
                    asset_type = holding['Asset_Type']
                    if asset_type not in asset_weights:
                        asset_weights[asset_type] = 0
                    asset_weights[asset_type] += holding['Weight_in_Account']
            
            by_account.append({
                'Account_Id': account_id,
                'Currency_Base': account_data.get('Currency', ''),
                'FX_To_CAD': self.normalize_amount(account_data.get('Exchange Rate to CAD', 1.0)),
                'Cash_CAD': self.normalize_amount(account_data.get('Cash (CAD)', 0)),
                'Investments_CAD': self.normalize_amount(account_data.get('Investments (CAD)', 0)),
                'Total_CAD': self.normalize_amount(account_data.get('Total (CAD)', 0)),
                'Holdings_Sum_CAD': account_total_cad,
                'Delta_vs_Summary_CAD': self.normalize_amount(account_data.get('Total (CAD)', 0)) - account_total_cad,
                'weights': asset_weights
            })
        
        # By Asset Type
        by_asset_type = {}
        for holding in holdings:
            if holding['Include_in_Exposure']:
                asset_type = holding['Asset_Type']
                if asset_type not in by_asset_type:
                    by_asset_type[asset_type] = {'Total_CAD': 0, 'Count': 0}
                by_asset_type[asset_type]['Total_CAD'] += holding['Market_Value_CAD']
                by_asset_type[asset_type]['Count'] += 1
        
        by_asset_type_list = [{'Asset_Type': k, **v, 'Percentage': v['Total_CAD'] / total_portfolio_value * 100} 
                             for k, v in by_asset_type.items()]
        
        # By Sector
        by_sector = {}
        for holding in holdings:
            if holding['Include_in_Exposure']:
                sector = holding['Sector']
                if sector not in by_sector:
                    by_sector[sector] = {'Total_CAD': 0, 'Count': 0}
                by_sector[sector]['Total_CAD'] += holding['Market_Value_CAD']
                by_sector[sector]['Count'] += 1
        
        by_sector_list = [{'Sector': k, **v, 'Percentage': v['Total_CAD'] / total_portfolio_value * 100} 
                         for k, v in by_sector.items()]
        
        # By Region
        by_region = {}
        for holding in holdings:
            if holding['Include_in_Exposure']:
                region = holding['Issuer_Region']
                if region not in by_region:
                    by_region[region] = {'Total_CAD': 0, 'Count': 0}
                by_region[region]['Total_CAD'] += holding['Market_Value_CAD']
                by_region[region]['Count'] += 1
        
        by_region_list = [{'Issuer_Region': k, **v, 'Percentage': v['Total_CAD'] / total_portfolio_value * 100} 
                         for k, v in by_region.items()]
        
        # Exceptions
        exceptions = []
        for holding in holdings:
            if holding['Needs_Manual_Review']:
                reasons = []
                if holding['Issuer_Region'] == 'Unknown':
                    reasons.append('Issuer_Region Unknown')
                if holding['Sector'] == 'Unknown':
                    reasons.append('Sector Unknown')
                if holding['Confidence'] < 0.9:
                    reasons.append(f'Low Confidence ({holding["Confidence"]:.1f})')
                
                exceptions.append({
                    'Account_Id': holding['Account_Id'],
                    'Symbol': holding['Symbol'],
                    'Reason': '; '.join(reasons),
                    'Confidence': holding['Confidence']
                })
        
        return {
            'generated_at': datetime.now().isoformat(),
            'pipeline_version': 'v1.0',
            'by_account': by_account,
            'by_asset_type': by_asset_type_list,
            'by_sector': by_sector_list,
            'by_region': by_region_list,
            'exceptions': exceptions
        }
    
    def save_results(self, holdings: List[Dict[str, Any]], rollups: Dict[str, Any], input_file: str):
        """Save enriched holdings and rollups to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save holdings detailed
        holdings_file = self.output_dir / f"holdings_detailed_{timestamp}.json"
        with open(holdings_file, 'w') as f:
            json.dump(holdings, f, indent=2, default=str)
        
        # Save rollups
        rollups_file = self.output_dir / f"rollups_{timestamp}.json"
        with open(rollups_file, 'w') as f:
            json.dump(rollups, f, indent=2, default=str)
        
        print(f"✅ Saved enriched holdings to {holdings_file}")
        print(f"✅ Saved rollups to {rollups_file}")
        
        return holdings_file, rollups_file

def main():
    """Main execution function"""
    engine = PortfolioClassificationEngine()
    
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
        # Process holdings
        holdings, rollups = engine.process_holdings(input_file)
        
        # Save results
        holdings_file, rollups_file = engine.save_results(holdings, rollups, input_file)
        
        print(f"\n📊 Processing Summary:")
        print(f"   Total Holdings: {len(holdings)}")
        print(f"   Total Portfolio Value: ${sum(h['Market_Value_CAD'] for h in holdings if h['Include_in_Exposure']):,.2f}")
        print(f"   Exceptions: {len(rollups['exceptions'])}")
        
        # Show asset type breakdown
        print(f"\n📈 Asset Type Breakdown:")
        for asset_type in rollups['by_asset_type']:
            print(f"   {asset_type['Asset_Type']}: ${asset_type['Total_CAD']:,.2f} ({asset_type['Percentage']:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error processing holdings: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
