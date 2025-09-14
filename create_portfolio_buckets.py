#!/usr/bin/env python3
"""
Create portfolio buckets based on decision tree logic:
1. Broad Market Equity (RRSP, Broad Market ETFs)
2. Sector Equity (ETFs/Stocks by sector - Utilities, Healthcare, etc.)
3. Regional Equity (US, Canadian, European, other regional ETFs)
4. Cash Alternatives (Short-term ETFs, Cash savings ETFs)
5. Fixed Income (Bond ETFs, individual bonds)
6. Cash (Actual cash balances)
7. Benefits Accounts (DC Pension, RRSP)
"""

import json
from collections import defaultdict
from pathlib import Path

def classify_holding(holding):
    """Classify a single holding into appropriate bucket"""
    
    symbol = holding.get('Symbol', '')
    name = holding.get('Name', '')
    product = holding.get('Product', '')
    sector = holding.get('Sector', '')
    industry = holding.get('Industry', '')
    
    # Convert to lowercase for easier matching
    name_lower = name.lower()
    product_lower = product.lower()
    sector_lower = sector.lower()
    industry_lower = industry.lower()
    
    # Decision Tree Logic
    
    # 1. CASH - Actual cash balances (but not MNY which is cash management fund)
    if symbol == 'CASH' or (name_lower == 'cash' and symbol != 'MNY'):
        return 'Cash'
    
    # 2. FIXED INCOME - Bond ETFs and individual bonds
    if any(keyword in name_lower for keyword in ['bond', 'treasury', 'corporate bond', 'government bond', 'note', 'debenture']):
        return 'Fixed Income'
    if any(keyword in industry_lower for keyword in ['bond', 'fixed income']):
        return 'Fixed Income'
    if sector_lower == 'fixed income':
        return 'Fixed Income'
    if 'bond' in product_lower or 'note' in product_lower:
        return 'Fixed Income'
    
    # 3. CASH ALTERNATIVES - Short-term ETFs, Money Market ETFs, Cash savings
    if symbol in ['MNY', 'HISU.U'] or any(keyword in name_lower for keyword in ['money market', 'cash management', 'short term', 'ultra short', 'high interest savings']):
        return 'Cash Alternatives'
    if any(keyword in industry_lower for keyword in ['money market', 'cash management', 'short term']):
        return 'Cash Alternatives'
    if sector_lower in ['money market', 'cash']:
        return 'Cash Alternatives'
    
    # 4. REAL ESTATE - REITs and Real Estate ETFs (excluded from equity)
    if any(keyword in name_lower for keyword in ['reit', 'real estate', 'property']):
        return 'Real Estate'
    if sector_lower == 'real estate':
        return 'Real Estate'
    
    # 5. BROAD MARKET EQUITY - Broad market ETFs and RRSP
    broad_market_keywords = [
        's&p', 'sp500', 'sp 500', 'total market', 'broad market', 'composite',
        'tsx', 'canadian index', 'us index', 'europe index', 'global',
        'all country', 'world', 'msci world', 'msci eafe', 'european',
        'developed markets', 'emerging markets'
    ]
    
    # Check for broad market ETFs
    if any(keyword in name_lower for keyword in broad_market_keywords):
        # Further classify by region for broad market
        if any(keyword in name_lower for keyword in ['canadian', 'canada', 'tsx']):
            return 'Broad Market Equity - Canada'
        elif any(keyword in name_lower for keyword in ['us', 'united states', 'sp500', 's&p']):
            return 'Broad Market Equity - US'
        elif any(keyword in name_lower for keyword in ['europe', 'european']):
            return 'Broad Market Equity - Europe'
        elif any(keyword in name_lower for keyword in ['global', 'world', 'international']):
            return 'Broad Market Equity - Global'
        else:
            return 'Broad Market Equity - Other'
    
    # 6. SECTOR EQUITY - ETFs and stocks by sector (excluding broad market)
    sector_equity_keywords = [
        'technology', 'healthcare', 'financial', 'energy', 'utilities',
        'consumer', 'communication', 'industrials', 'materials', 'semiconductor',
        'biotech', 'pharmaceutical', 'bank', 'oil', 'gas', 'renewable',
        'solar', 'wind', 'tech', 'fintech'
    ]
    
    if any(keyword in name_lower for keyword in sector_equity_keywords):
        # Classify by sector
        if any(keyword in name_lower for keyword in ['technology', 'tech', 'semiconductor', 'software']):
            return 'Sector Equity - Technology'
        elif any(keyword in name_lower for keyword in ['healthcare', 'health', 'pharmaceutical', 'biotech', 'medical']):
            return 'Sector Equity - Healthcare'
        elif any(keyword in name_lower for keyword in ['financial', 'bank', 'fintech']):
            return 'Sector Equity - Financial Services'
        elif any(keyword in name_lower for keyword in ['energy', 'oil', 'gas', 'renewable', 'solar', 'wind']):
            return 'Sector Equity - Energy'
        elif any(keyword in name_lower for keyword in ['consumer', 'retail', 'cyclical']):
            return 'Sector Equity - Consumer'
        elif any(keyword in name_lower for keyword in ['communication', 'telecom', 'media']):
            return 'Sector Equity - Communication Services'
        elif any(keyword in name_lower for keyword in ['utilities', 'utility']):
            return 'Sector Equity - Utilities'
        elif any(keyword in name_lower for keyword in ['industrial', 'materials']):
            return 'Sector Equity - Industrials'
        else:
            return 'Sector Equity - Other'
    
    # 7. DIVIDEND FOCUSED - Dividend ETFs and stocks (but not if it's broad market)
    if symbol == 'CDZ' or any(keyword in name_lower for keyword in ['dividend', 'income', 'aristocrat', 'yield']):
        return 'Dividend Focused Equity'
    
    # 8. REGIONAL EQUITY - Regional ETFs (not broad market)
    if any(keyword in name_lower for keyword in ['europe', 'european', 'asia', 'asian', 'china', 'japan']):
        return 'Regional Equity'
    
    # 9. BENEFITS ACCOUNTS - Special handling (split by account type)
    if 'BENEFITS' in holding.get('Account_Number', ''):
        account_name = holding.get('Account_Name', '').lower()
        if 'dc pension' in account_name or 'dc' in account_name:
            return 'DC Pension Plan'
        elif 'rsp' in account_name or 'rrsp' in account_name:
            return 'RRSP Account'
        else:
            return 'Benefits Accounts'
    
    # 10. DEFAULT - If we can't classify, put in appropriate bucket based on sector
    if sector_lower == 'equity':
        return 'Sector Equity - Other'
    elif sector_lower in ['technology', 'healthcare', 'financial services', 'energy', 'consumer cyclical', 'communication services', 'utilities', 'industrials']:
        return f'Sector Equity - {sector.title()}'
    else:
        return 'Unclassified'

def create_portfolio_buckets():
    """Create portfolio buckets using decision tree logic"""
    
    # Load comprehensive data
    with open('data/output/comprehensive_holdings_with_etf_dividends_20250913_150846.json', 'r') as f:
        data = json.load(f)
    
    print("🏗️ CREATING PORTFOLIO BUCKETS")
    print("=" * 60)
    
    # Initialize buckets
    buckets = defaultdict(lambda: {'holdings': [], 'total_value': 0, 'count': 0})
    
    # Process RBC holdings
    print("📊 Classifying RBC Holdings:")
    for holding in data['holdings']:
        bucket = classify_holding(holding)
        value = holding.get('Market_Value_CAD', 0)
        
        buckets[bucket]['holdings'].append(holding)
        buckets[bucket]['total_value'] += value
        buckets[bucket]['count'] += 1
        
        print(f"   {holding.get('Symbol', 'N/A'):6s} {holding.get('Name', '')[:50]:50s} → {bucket}")
    
    # Process cash balances
    print("\n💰 Classifying Cash Balances:")
    cash_balances = data.get('cash_balances', [])
    for cash in cash_balances:
        if cash.get('Account_Type') == 'Benefits':
            # Split benefits accounts
            account_name = cash.get('Account_Name', 'Unknown').lower()
            if 'dc pension' in account_name or 'dc' in account_name:
                bucket = 'DC Pension Plan'
            elif 'rsp' in account_name or 'rrsp' in account_name:
                bucket = 'RRSP Account'
            else:
                bucket = 'Benefits Accounts'
            print(f"   {cash.get('Account_Name', 'Unknown'):30s} → {bucket}")
        else:
            # RBC cash
            bucket = 'Cash'
            print(f"   {cash.get('Currency', 'Unknown'):6s} Cash → {bucket}")
        
        value = cash.get('Amount_CAD', 0)
        buckets[bucket]['holdings'].append(cash)
        buckets[bucket]['total_value'] += value
        buckets[bucket]['count'] += 1
    
    # Display bucket summary
    print("\n📈 PORTFOLIO BUCKET SUMMARY:")
    print("=" * 60)
    
    total_portfolio_value = sum(bucket['total_value'] for bucket in buckets.values())
    
    sorted_buckets = sorted(buckets.items(), key=lambda x: x[1]['total_value'], reverse=True)
    
    for bucket_name, bucket_data in sorted_buckets:
        value = bucket_data['total_value']
        count = bucket_data['count']
        percentage = (value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
        
        print(f"{bucket_name:30s} {count:3d} holdings ${value:10,.0f} ({percentage:5.1f}%)")
    
    print(f"\n{'TOTAL PORTFOLIO':30s} ${total_portfolio_value:10,.0f} (100.0%)")
    
    # Detailed breakdown for each bucket
    print("\n🔍 DETAILED BUCKET BREAKDOWN:")
    print("=" * 60)
    
    for bucket_name, bucket_data in sorted_buckets:
        if bucket_data['count'] > 0:
            print(f"\n📦 {bucket_name.upper()}:")
            print(f"   Total Value: ${bucket_data['total_value']:,.0f}")
            print(f"   Holdings: {bucket_data['count']}")
            
            # Show top holdings in this bucket
            sorted_holdings = sorted(bucket_data['holdings'], key=lambda x: x.get('Market_Value_CAD', x.get('Amount_CAD', 0)), reverse=True)
            for holding in sorted_holdings[:5]:  # Show top 5
                symbol = holding.get('Symbol', 'N/A')
                name = holding.get('Name', holding.get('Account_Name', ''))
                value = holding.get('Market_Value_CAD', holding.get('Amount_CAD', 0))
                print(f"     {symbol:6s} {name[:40]:40s} ${value:8,.0f}")
            
            if len(sorted_holdings) > 5:
                print(f"     ... and {len(sorted_holdings) - 5} more holdings")
    
    # Create consolidated sector equity bucket
    consolidated_buckets = {}
    sector_equity_total = 0
    sector_equity_count = 0
    sector_equity_holdings = []
    
    for bucket_name, bucket_data in buckets.items():
        if bucket_name.startswith('Sector Equity -'):
            sector_equity_total += bucket_data['total_value']
            sector_equity_count += bucket_data['count']
            sector_equity_holdings.extend(bucket_data['holdings'])
        else:
            consolidated_buckets[bucket_name] = bucket_data
    
    # Add consolidated sector equity bucket
    if sector_equity_total > 0:
        consolidated_buckets['Sector Equity'] = {
            'holdings': sector_equity_holdings,
            'total_value': sector_equity_total,
            'count': sector_equity_count,
            'sub_buckets': {name: data for name, data in buckets.items() if name.startswith('Sector Equity -')}
        }
    
    return consolidated_buckets

if __name__ == "__main__":
    create_portfolio_buckets()
