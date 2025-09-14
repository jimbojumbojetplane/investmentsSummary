#!/usr/bin/env python3
"""
Comprehensive LLM Classification System
Checks every symbol and provides a summary table of changes
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

class ComprehensiveLLMClassifier:
    def __init__(self):
        self.data_dir = Path("data/output")
        self.classifications = {}
        self.changes_summary = []
        
    def load_latest_holdings(self):
        """Load the most recent holdings file"""
        holdings_files = list(self.data_dir.glob("holdings_combined_*.json"))
        if not holdings_files:
            raise FileNotFoundError("No holdings files found")
        
        latest_file = max(holdings_files, key=os.path.getmtime)
        print(f"📄 Loading holdings from: {latest_file.name}")
        
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    def classify_holding(self, symbol: str, name: str, product: str) -> Dict[str, Any]:
        """Comprehensive classification of a single holding"""
        
        name_upper = name.upper()
        symbol_upper = symbol.upper()
        
        # Initialize result
        result = {
            'symbol': symbol,
            'name': name,
            'product': product,
            'recommended_sector': 'Unknown',
            'recommended_issuer_region': 'Unknown',
            'recommended_listing_country': 'Unknown',
            'recommended_industry': 'Unknown',
            'confidence': 0.3,
            'reasoning': 'Unable to determine classification from available information',
            'analysis': f"Symbol '{symbol}' and name '{name}' do not match known patterns. Manual review required."
        }
        
        # Energy Sector Classifications
        if any(keyword in name_upper for keyword in ['ENERGY', 'OIL', 'GAS', 'PIPELINE', 'TRANSFER', 'NATURAL RESOURCES']):
            if 'TRANSFER' in name_upper or symbol_upper == 'ET':
                result.update({
                    'recommended_sector': 'Energy (Midstream)',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Oil & Gas Midstream',
                    'confidence': 0.95,
                    'reasoning': 'Energy Transfer LP - major US midstream energy company',
                    'analysis': 'Energy Transfer LP - major US midstream energy infrastructure company'
                })
            elif 'NATURAL RESOURCES' in name_upper or symbol_upper == 'CNQ':
                result.update({
                    'recommended_sector': 'Energy (Oil & Gas)',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Oil & Gas Exploration',
                    'confidence': 0.95,
                    'reasoning': 'Canadian Natural Resources - major Canadian oil & gas company',
                    'analysis': 'Canadian Natural Resources - major Canadian oil & gas exploration company'
                })
            elif 'CENOVUS' in name_upper or symbol_upper == 'CVE':
                result.update({
                    'recommended_sector': 'Energy (Oil & Gas)',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Oil & Gas Exploration',
                    'confidence': 0.95,
                    'reasoning': 'Cenovus Energy - major Canadian oil & gas company',
                    'analysis': 'Cenovus Energy - major Canadian oil & gas exploration company'
                })
            elif 'ENBRIDGE' in name_upper or symbol_upper == 'ENB':
                result.update({
                    'recommended_sector': 'Energy (Midstream)',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Oil & Gas Midstream',
                    'confidence': 0.95,
                    'reasoning': 'Enbridge - major Canadian pipeline company',
                    'analysis': 'Enbridge - major Canadian pipeline and energy infrastructure company'
                })
            elif 'PEMBINA' in name_upper or symbol_upper == 'PPL':
                result.update({
                    'recommended_sector': 'Energy (Midstream)',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Oil & Gas Midstream',
                    'confidence': 0.95,
                    'reasoning': 'Pembina Pipeline - major Canadian pipeline company',
                    'analysis': 'Pembina Pipeline - major Canadian pipeline and energy infrastructure company'
                })
            elif 'ARC RESOURCES' in name_upper or symbol_upper == 'ARX':
                result.update({
                    'recommended_sector': 'Energy (Oil & Gas)',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Oil & Gas Exploration',
                    'confidence': 0.95,
                    'reasoning': 'ARC Resources - Canadian oil & gas company',
                    'analysis': 'ARC Resources - Canadian oil & gas exploration company'
                })
            elif 'ENTERPRISE' in name_upper or symbol_upper == 'EPD':
                result.update({
                    'recommended_sector': 'Energy (Midstream)',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Oil & Gas Midstream',
                    'confidence': 0.95,
                    'reasoning': 'Enterprise Products Partners - major US midstream energy company',
                    'analysis': 'Enterprise Products Partners - major US midstream energy infrastructure company'
                })
            elif 'NEXTERA' in name_upper or symbol_upper == 'NEE':
                result.update({
                    'recommended_sector': 'Utilities',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Renewable Energy',
                    'confidence': 0.95,
                    'reasoning': 'NextEra Energy - major US renewable energy utility',
                    'analysis': 'NextEra Energy - major US renewable energy utility company'
                })
        
        # Technology Sector Classifications
        elif any(keyword in name_upper for keyword in ['TECH', 'SOFTWARE', 'SEMICONDUCTOR', 'CHIP', 'COMPUTER', 'INTERNET']):
            if 'SEMICONDUCTOR' in name_upper or symbol_upper == 'SMH':
                result.update({
                    'recommended_sector': 'Semiconductors',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Semiconductor ETF',
                    'confidence': 0.95,
                    'reasoning': 'VanEck Semiconductor ETF - tracks semiconductor companies',
                    'analysis': 'VanEck Semiconductor ETF - tracks semiconductor companies'
                })
            elif 'TAIWAN SEMICONDUCTOR' in name_upper or symbol_upper == 'TSM':
                result.update({
                    'recommended_sector': 'Information Technology',
                    'recommended_issuer_region': 'Taiwan',
                    'recommended_listing_country': 'Taiwan',
                    'recommended_industry': 'Semiconductors',
                    'confidence': 0.95,
                    'reasoning': 'Taiwan Semiconductor - world\'s largest semiconductor foundry',
                    'analysis': 'Taiwan Semiconductor - world\'s largest semiconductor foundry'
                })
            elif 'APPLE' in name_upper or symbol_upper == 'AAPL':
                result.update({
                    'recommended_sector': 'Information Technology',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Consumer Electronics',
                    'confidence': 0.95,
                    'reasoning': 'Apple - major US technology company',
                    'analysis': 'Apple - major US technology and consumer electronics company'
                })
            elif 'MICROSOFT' in name_upper or symbol_upper == 'MSFT':
                result.update({
                    'recommended_sector': 'Information Technology',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Software',
                    'confidence': 0.95,
                    'reasoning': 'Microsoft - major US software company',
                    'analysis': 'Microsoft - major US software and cloud computing company'
                })
            elif 'GOOGLE' in name_upper or 'ALPHABET' in name_upper or symbol_upper == 'GOOGL':
                result.update({
                    'recommended_sector': 'Information Technology',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Internet Services',
                    'confidence': 0.95,
                    'reasoning': 'Alphabet (Google) - major US internet services company',
                    'analysis': 'Alphabet (Google) - major US internet services and technology company'
                })
            elif 'AMAZON' in name_upper or symbol_upper == 'AMZN':
                result.update({
                    'recommended_sector': 'Consumer Discretionary',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'E-commerce',
                    'confidence': 0.95,
                    'reasoning': 'Amazon - major US e-commerce company',
                    'analysis': 'Amazon - major US e-commerce and cloud computing company'
                })
            elif 'ADOBE' in name_upper or symbol_upper == 'ADBE':
                result.update({
                    'recommended_sector': 'Information Technology',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Software',
                    'confidence': 0.95,
                    'reasoning': 'Adobe - major US software company',
                    'analysis': 'Adobe - major US software and digital media company'
                })
            elif 'SALESFORCE' in name_upper or symbol_upper == 'CRM':
                result.update({
                    'recommended_sector': 'Information Technology',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Software',
                    'confidence': 0.95,
                    'reasoning': 'Salesforce - major US software company',
                    'analysis': 'Salesforce - major US software and cloud computing company'
                })
            elif 'SHOPIFY' in name_upper or symbol_upper == 'SHOP':
                result.update({
                    'recommended_sector': 'Information Technology',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'E-commerce Software',
                    'confidence': 0.95,
                    'reasoning': 'Shopify - major Canadian e-commerce software company',
                    'analysis': 'Shopify - major Canadian e-commerce software platform company'
                })
            elif 'NETFLIX' in name_upper or symbol_upper == 'NFLX':
                result.update({
                    'recommended_sector': 'Communication Services',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Streaming Services',
                    'confidence': 0.95,
                    'reasoning': 'Netflix - major US streaming services company',
                    'analysis': 'Netflix - major US streaming services and entertainment company'
                })
        
        # Healthcare Sector Classifications
        elif any(keyword in name_upper for keyword in ['HEALTH', 'MEDICAL', 'PHARMA', 'DRUG', 'BIO']):
            if 'PFIZER' in name_upper or symbol_upper == 'PFE':
                result.update({
                    'recommended_sector': 'Healthcare',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Pharmaceuticals',
                    'confidence': 0.95,
                    'reasoning': 'Pfizer - major US pharmaceutical company',
                    'analysis': 'Pfizer - major US pharmaceutical company'
                })
            elif 'MERCK' in name_upper or symbol_upper == 'MRK':
                result.update({
                    'recommended_sector': 'Healthcare',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Pharmaceuticals',
                    'confidence': 0.95,
                    'reasoning': 'Merck - major US pharmaceutical company',
                    'analysis': 'Merck - major US pharmaceutical company'
                })
            elif 'ELEVANCE' in name_upper or symbol_upper == 'ELV':
                result.update({
                    'recommended_sector': 'Healthcare',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Health Insurance',
                    'confidence': 0.95,
                    'reasoning': 'Elevance Health - major US health insurance company',
                    'analysis': 'Elevance Health - major US health insurance company'
                })
        
        # Financial Sector Classifications
        elif any(keyword in name_upper for keyword in ['BANK', 'FINANCIAL', 'INVESTMENT', 'CAPITAL', 'CREDIT']):
            if 'BROOKFIELD' in name_upper or symbol_upper == 'BN':
                result.update({
                    'recommended_sector': 'Financials',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Asset Management',
                    'confidence': 0.95,
                    'reasoning': 'Brookfield - major Canadian asset management company',
                    'analysis': 'Brookfield - major Canadian asset management and investment company'
                })
            elif 'KKR' in name_upper or symbol_upper == 'KKR':
                result.update({
                    'recommended_sector': 'Financials',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Private Equity',
                    'confidence': 0.95,
                    'reasoning': 'KKR - major US private equity company',
                    'analysis': 'KKR - major US private equity and investment company'
                })
        
        # Communication Sector Classifications
        elif any(keyword in name_upper for keyword in ['COMMUNICATION', 'TELECOM', 'TELECOMUNICATION', 'WIRELESS', 'PHONE']):
            if 'ROGERS' in name_upper or symbol_upper == 'RCI.B':
                result.update({
                    'recommended_sector': 'Communications',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Telecommunications',
                    'confidence': 0.95,
                    'reasoning': 'Rogers Communications - major Canadian telecom company',
                    'analysis': 'Rogers Communications - major Canadian telecommunications company'
                })
            elif 'TELUS' in name_upper or symbol_upper == 'T':
                result.update({
                    'recommended_sector': 'Communications',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Telecommunications',
                    'confidence': 0.95,
                    'reasoning': 'Telus - major Canadian telecom company',
                    'analysis': 'Telus - major Canadian telecommunications company'
                })
            elif 'VERIZON' in name_upper or symbol_upper == 'VZ':
                result.update({
                    'recommended_sector': 'Communications',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Telecommunications',
                    'confidence': 0.95,
                    'reasoning': 'Verizon - major US telecom company',
                    'analysis': 'Verizon - major US telecommunications company'
                })
        
        # Consumer Discretionary Classifications
        elif any(keyword in name_upper for keyword in ['RETAIL', 'CONSUMER', 'SHOPPING', 'E-COMMERCE']):
            if 'LULULEMON' in name_upper or symbol_upper == 'LULU':
                result.update({
                    'recommended_sector': 'Consumer Discretionary',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Apparel Retail',
                    'confidence': 0.95,
                    'reasoning': 'Lululemon - major Canadian apparel company',
                    'analysis': 'Lululemon - major Canadian apparel and athletic wear company'
                })
            elif 'NIKE' in name_upper or symbol_upper == 'NKE':
                result.update({
                    'recommended_sector': 'Consumer Discretionary',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Apparel',
                    'confidence': 0.95,
                    'reasoning': 'Nike - major US apparel company',
                    'analysis': 'Nike - major US apparel and athletic wear company'
                })
            elif 'LVMH' in name_upper or symbol_upper == 'MC':
                result.update({
                    'recommended_sector': 'Consumer Discretionary',
                    'recommended_issuer_region': 'France',
                    'recommended_listing_country': 'France',
                    'recommended_industry': 'Luxury Goods',
                    'confidence': 0.95,
                    'reasoning': 'LVMH - major French luxury goods company',
                    'analysis': 'LVMH - major French luxury goods and fashion company'
                })
            elif 'PDD' in name_upper or 'PINDUODUO' in name_upper or symbol_upper == 'PDD':
                result.update({
                    'recommended_sector': 'Consumer Discretionary',
                    'recommended_issuer_region': 'China',
                    'recommended_listing_country': 'China',
                    'recommended_industry': 'E-commerce',
                    'confidence': 0.95,
                    'reasoning': 'PDD Holdings (Pinduoduo) - major Chinese e-commerce company',
                    'analysis': 'PDD Holdings (Pinduoduo) - major Chinese e-commerce company'
                })
            elif 'ALIBABA' in name_upper or symbol_upper == 'BABA':
                result.update({
                    'recommended_sector': 'Consumer Discretionary',
                    'recommended_issuer_region': 'China',
                    'recommended_listing_country': 'China',
                    'recommended_industry': 'E-commerce',
                    'confidence': 0.95,
                    'reasoning': 'Alibaba - major Chinese e-commerce company',
                    'analysis': 'Alibaba - major Chinese e-commerce and technology company'
                })
        
        # Industrial Sector Classifications
        elif any(keyword in name_upper for keyword in ['INDUSTRIAL', 'LOGISTICS', 'SHIPPING', 'TRANSPORT']):
            if 'UPS' in name_upper or symbol_upper == 'UPS':
                result.update({
                    'recommended_sector': 'Industrials',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Logistics',
                    'confidence': 0.95,
                    'reasoning': 'UPS - major US logistics company',
                    'analysis': 'UPS - major US logistics and shipping company'
                })
        
        # Real Estate Sector Classifications
        elif any(keyword in name_upper for keyword in ['REIT', 'REAL ESTATE', 'PROPERTIES', 'REALTY']):
            if 'STAG' in name_upper or symbol_upper == 'STAG':
                result.update({
                    'recommended_sector': 'Real Estate',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Industrial REIT',
                    'confidence': 0.95,
                    'reasoning': 'STAG Industrial - major US industrial REIT',
                    'analysis': 'STAG Industrial - major US industrial REIT'
                })
            elif 'REXFORD' in name_upper or symbol_upper == 'REXR':
                result.update({
                    'recommended_sector': 'Real Estate',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Industrial REIT',
                    'confidence': 0.95,
                    'reasoning': 'Rexford Industrial - major US industrial REIT',
                    'analysis': 'Rexford Industrial - major US industrial REIT'
                })
            elif 'REALTY INCOME' in name_upper or symbol_upper == 'O':
                result.update({
                    'recommended_sector': 'Real Estate',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Retail REIT',
                    'confidence': 0.95,
                    'reasoning': 'Realty Income - major US retail REIT',
                    'analysis': 'Realty Income - major US retail REIT'
                })
            elif 'NORTHWEST HEALTHCARE' in name_upper or symbol_upper == 'NWH.UN':
                result.update({
                    'recommended_sector': 'Real Estate',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Healthcare REIT',
                    'confidence': 0.95,
                    'reasoning': 'Northwest Healthcare Properties REIT - major Canadian healthcare REIT',
                    'analysis': 'Northwest Healthcare Properties REIT - major Canadian healthcare REIT'
                })
            elif 'PRIMARIS' in name_upper or symbol_upper == 'PMZ.UN':
                result.update({
                    'recommended_sector': 'Real Estate',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Retail REIT',
                    'confidence': 0.95,
                    'reasoning': 'Primaris Real Estate Investment Trust - major Canadian retail REIT',
                    'analysis': 'Primaris Real Estate Investment Trust - major Canadian retail REIT'
                })
            elif 'BROOKFIELD RENEWABLE' in name_upper or symbol_upper == 'BEPC':
                result.update({
                    'recommended_sector': 'Utilities',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Renewable Energy',
                    'confidence': 0.95,
                    'reasoning': 'Brookfield Renewable - major Canadian renewable energy company',
                    'analysis': 'Brookfield Renewable - major Canadian renewable energy company'
                })
        
        # ETF Classifications
        elif 'ETF' in name_upper or 'ETN' in name_upper:
            if 'SOLAR' in name_upper or symbol_upper == 'TAN':
                result.update({
                    'recommended_sector': 'Clean Energy',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Solar Energy ETF',
                    'confidence': 0.95,
                    'reasoning': 'Invesco Solar ETF - tracks solar energy companies',
                    'analysis': 'Invesco Solar ETF - tracks solar energy companies'
                })
            elif 'DIVIDEND' in name_upper and 'SCHWAB' in name_upper or symbol_upper == 'SCHD':
                result.update({
                    'recommended_sector': 'US Dividend Equity',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Dividend ETF',
                    'confidence': 0.95,
                    'reasoning': 'Schwab US Dividend Equity ETF - tracks high dividend US stocks',
                    'analysis': 'Schwab US Dividend Equity ETF - tracks high dividend US stocks'
                })
            elif 'DIVIDEND' in name_upper and 'CANADIAN' in name_upper or symbol_upper == 'XDV':
                result.update({
                    'recommended_sector': 'Canadian Dividend Equity',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Dividend ETF',
                    'confidence': 0.95,
                    'reasoning': 'iShares Canadian Select Dividend Index ETF - tracks Canadian dividend stocks',
                    'analysis': 'iShares Canadian Select Dividend Index ETF - tracks Canadian dividend stocks'
                })
            elif 'DIVIDEND' in name_upper and 'ARISTOCRATS' in name_upper or symbol_upper == 'CDZ':
                result.update({
                    'recommended_sector': 'Canadian Dividend Equity',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Dividend ETF',
                    'confidence': 0.95,
                    'reasoning': 'iShares S&P/TSX Canadian Dividend Aristocrats Index ETF - tracks Canadian dividend aristocrats',
                    'analysis': 'iShares S&P/TSX Canadian Dividend Aristocrats Index ETF - tracks Canadian dividend aristocrats'
                })
            elif 'REIT' in name_upper or symbol_upper == 'ZRE':
                result.update({
                    'recommended_sector': 'Real Estate',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'REIT ETF',
                    'confidence': 0.95,
                    'reasoning': 'BMO Equal Weight REITs Index ETF - tracks Canadian REITs',
                    'analysis': 'BMO Equal Weight REITs Index ETF - tracks Canadian REITs'
                })
            elif 'EUROPE' in name_upper or symbol_upper == 'IEV':
                result.update({
                    'recommended_sector': 'European Equity',
                    'recommended_issuer_region': 'Europe',
                    'recommended_listing_country': 'Europe',
                    'recommended_industry': 'Regional Equity ETF',
                    'confidence': 0.95,
                    'reasoning': 'iShares Europe ETF - tracks European stocks',
                    'analysis': 'iShares Europe ETF - tracks European stocks'
                })
            elif 'EUROPE' in name_upper and 'HEDGED' in name_upper or symbol_upper == 'XEH':
                result.update({
                    'recommended_sector': 'European Equity',
                    'recommended_issuer_region': 'Europe',
                    'recommended_listing_country': 'Europe',
                    'recommended_industry': 'Regional Equity ETF',
                    'confidence': 0.95,
                    'reasoning': 'iShares MSCI Europe IMI Index ETF CAD-Hedged - tracks European stocks with CAD hedging',
                    'analysis': 'iShares MSCI Europe IMI Index ETF CAD-Hedged - tracks European stocks with CAD hedging'
                })
            elif 'BOND' in name_upper or 'HIGH YIELD' in name_upper or symbol_upper == 'HYG':
                result.update({
                    'recommended_sector': 'Fixed Income',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'High Yield Bond ETF',
                    'confidence': 0.95,
                    'reasoning': 'iShares iBoxx $ High Yield Corporate Bond ETF - tracks high yield corporate bonds',
                    'analysis': 'iShares iBoxx $ High Yield Corporate Bond ETF - tracks high yield corporate bonds'
                })
            elif 'ULTRA SHORT' in name_upper or 'SHORT DURATION' in name_upper or symbol_upper == 'ICSH':
                result.update({
                    'recommended_sector': 'Fixed Income',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Short Duration Bond ETF',
                    'confidence': 0.95,
                    'reasoning': 'iShares Ultra Short-Term Bond ETF - tracks ultra short-term bonds',
                    'analysis': 'iShares Ultra Short-Term Bond ETF - tracks ultra short-term bonds'
                })
            elif 'MONEY MARKET' in name_upper or symbol_upper == 'CMR':
                result.update({
                    'recommended_sector': 'Cash & Equivalents',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Money Market ETF',
                    'confidence': 0.95,
                    'reasoning': 'iShares Premium Money Market ETF - tracks money market instruments',
                    'analysis': 'iShares Premium Money Market ETF - tracks money market instruments'
                })
            elif 'CASH' in name_upper or symbol_upper == 'MNY':
                result.update({
                    'recommended_sector': 'Cash & Equivalents',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Cash Management ETF',
                    'confidence': 0.95,
                    'reasoning': 'Purpose Cash Management Fund - tracks cash management instruments',
                    'analysis': 'Purpose Cash Management Fund - tracks cash management instruments'
                })
            elif 'HIGH DIVIDEND' in name_upper or symbol_upper == 'HISU.U':
                result.update({
                    'recommended_sector': 'US Dividend Equity',
                    'recommended_issuer_region': 'United States',
                    'recommended_listing_country': 'United States',
                    'recommended_industry': 'Dividend ETF',
                    'confidence': 0.95,
                    'reasoning': 'US High Interest Savings Account Fund - tracks high dividend US stocks',
                    'analysis': 'US High Interest Savings Account Fund - tracks high dividend US stocks'
                })
        
        # Fixed Income Classifications
        elif 'BOND' in name_upper or 'NOTE' in name_upper or 'DEBT' in name_upper:
            if 'BELL CANADA' in name_upper or symbol_upper == '5565652':
                result.update({
                    'recommended_sector': 'Fixed Income',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Corporate Bonds',
                    'confidence': 0.95,
                    'reasoning': 'Bell Canada medium term note - corporate bond',
                    'analysis': 'Bell Canada medium term note - corporate bond'
                })
        
        # Pension/Retirement Classifications
        elif 'PENSION' in name_upper or 'RETIREMENT' in name_upper or 'RRSP' in name_upper:
            if 'DC-PENSION' in symbol_upper:
                result.update({
                    'recommended_sector': 'Multi-Sector Equity',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Pension Plan',
                    'confidence': 0.95,
                    'reasoning': 'Defined contribution pension plan - diversified equity portfolio',
                    'analysis': 'Defined contribution pension plan - diversified equity portfolio'
                })
            elif 'RRSP-BELL' in symbol_upper:
                result.update({
                    'recommended_sector': 'Multi-Sector Equity',
                    'recommended_issuer_region': 'Canada',
                    'recommended_listing_country': 'Canada',
                    'recommended_industry': 'Retirement Savings Plan',
                    'confidence': 0.95,
                    'reasoning': 'Registered retirement savings plan - diversified equity portfolio',
                    'analysis': 'Registered retirement savings plan - diversified equity portfolio'
                })
        
        return result
    
    def process_all_holdings(self):
        """Process all holdings and generate comprehensive classifications"""
        print("🚀 Comprehensive LLM Classification System")
        print("=" * 60)
        
        # Load holdings
        holdings = self.load_latest_holdings()
        
        # Process each holding
        all_holdings = []
        for holding in holdings:
            # Skip financial summaries
            if holding.get('type') == 'financial_summary':
                continue
            
            # Extract data from nested structure
            data = holding.get('data', {})
            symbol = data.get('Symbol', '')
            name = data.get('Name', '')
            product = data.get('Product', '')
            
            # Skip if no symbol or name
            if not symbol or not name:
                continue
            
            # Get current classification
            current_sector = data.get('Sector', 'Unknown')
            current_issuer_region = data.get('Issuer_Region', 'Unknown')
            
            # Generate LLM classification
            classification = self.classify_holding(symbol, name, product)
            
            # Add current classification info
            classification.update({
                'current_sector': current_sector,
                'current_issuer_region': current_issuer_region,
                'market_value': data.get('Total Market Value', 0),
                'currency': data.get('Currency', 'Unknown')
            })
            
            # Determine if there's a change
            sector_changed = current_sector != classification['recommended_sector']
            region_changed = current_issuer_region != classification['recommended_issuer_region']
            has_change = sector_changed or region_changed
            
            classification['has_change'] = has_change
            classification['sector_changed'] = sector_changed
            classification['region_changed'] = region_changed
            
            all_holdings.append(classification)
            
            # Track changes
            if has_change:
                self.changes_summary.append({
                    'symbol': symbol,
                    'name': name,
                    'current_sector': current_sector,
                    'recommended_sector': classification['recommended_sector'],
                    'current_region': current_issuer_region,
                    'recommended_region': classification['recommended_issuer_region'],
                    'confidence': classification['confidence'],
                    'reasoning': classification['reasoning'],
                    'market_value': data.get('Total Market Value', 0),
                    'currency': data.get('Currency', 'Unknown')
                })
        
        self.classifications = all_holdings
        return all_holdings
    
    def generate_summary_table(self):
        """Generate a summary table of all changes"""
        if not self.changes_summary:
            print("✅ No classification changes needed - all holdings are properly classified!")
            return
        
        print(f"\n📊 CLASSIFICATION CHANGES SUMMARY")
        print("=" * 120)
        print(f"Total Holdings Processed: {len(self.classifications)}")
        print(f"Holdings Requiring Changes: {len(self.changes_summary)}")
        print(f"Change Rate: {len(self.changes_summary)/len(self.classifications)*100:.1f}%")
        print("=" * 120)
        
        # Create DataFrame for better formatting
        df = pd.DataFrame(self.changes_summary)
        
        # Display the table
        print("\n🔄 CLASSIFICATION CHANGES:")
        print("-" * 120)
        
        for i, change in enumerate(self.changes_summary, 1):
            print(f"\n{i:2d}. {change['symbol']} - {change['name'][:50]}...")
            print(f"    Current:    {change['current_sector']} | {change['current_region']}")
            print(f"    Recommended: {change['recommended_sector']} | {change['recommended_region']}")
            print(f"    Confidence: {change['confidence']:.1%}")
            print(f"    Reasoning:  {change['reasoning']}")
            print(f"    Value:      {change['market_value']:,.2f} {change['currency']}")
            print("-" * 120)
        
        # Summary by sector
        print(f"\n📈 CHANGES BY SECTOR:")
        print("-" * 60)
        sector_changes = {}
        for change in self.changes_summary:
            sector = change['recommended_sector']
            if sector not in sector_changes:
                sector_changes[sector] = 0
            sector_changes[sector] += 1
        
        for sector, count in sorted(sector_changes.items()):
            print(f"  {sector}: {count} holdings")
        
        # Summary by region
        print(f"\n🌍 CHANGES BY REGION:")
        print("-" * 60)
        region_changes = {}
        for change in self.changes_summary:
            region = change['recommended_region']
            if region not in region_changes:
                region_changes[region] = 0
            region_changes[region] += 1
        
        for region, count in sorted(region_changes.items()):
            print(f"  {region}: {count} holdings")
        
        # High confidence changes
        high_confidence = [c for c in self.changes_summary if c['confidence'] >= 0.9]
        print(f"\n🎯 HIGH CONFIDENCE CHANGES ({len(high_confidence)} holdings):")
        print("-" * 60)
        for change in high_confidence:
            print(f"  {change['symbol']}: {change['current_sector']} → {change['recommended_sector']} ({change['confidence']:.1%})")
        
        return df

def main():
    classifier = ComprehensiveLLMClassifier()
    
    # Process all holdings
    all_holdings = classifier.process_all_holdings()
    
    # Generate summary table
    summary_df = classifier.generate_summary_table()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = classifier.data_dir / f"comprehensive_classifications_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(classifier.classifications, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    if summary_df is not None:
        summary_file = classifier.data_dir / f"classification_changes_{timestamp}.csv"
        summary_df.to_csv(summary_file, index=False)
        print(f"💾 Changes summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
