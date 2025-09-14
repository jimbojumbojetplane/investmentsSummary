#!/usr/bin/env python3
"""
Refined Portfolio Dashboard with Decision Tree Bucketing
Implements the refined bucketing logic from create_portfolio_buckets.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
from collections import defaultdict

def classify_holding(holding):
    """Classify a single holding into appropriate bucket using decision tree logic"""
    
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

def load_comprehensive_data():
    """Load the comprehensive holdings data"""
    output_dir = Path('data/output')
    comprehensive_files = list(output_dir.glob('comprehensive_holdings_with_etf_dividends_*.json'))
    
    if not comprehensive_files:
        st.error("No comprehensive holdings files found!")
        return None
    
    # Load the most recent file
    latest_file = max(comprehensive_files, key=lambda f: f.stat().st_mtime)
    st.info(f"Loading data from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data

def create_asset_class_overview(data):
    """Create asset class overview using refined bucketing"""
    st.header("📊 Asset Classes Overview")
    
    # Classify all holdings
    buckets = defaultdict(lambda: {'holdings': [], 'total_value': 0, 'count': 0})
    
    # Process RBC holdings
    for holding in data['holdings']:
        bucket = classify_holding(holding)
        value = holding.get('Market_Value_CAD', 0)
        
        buckets[bucket]['holdings'].append(holding)
        buckets[bucket]['total_value'] += value
        buckets[bucket]['count'] += 1
    
    # Process cash balances
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
        else:
            # RBC cash
            bucket = 'Cash'
        
        value = cash.get('Amount_CAD', 0)
        buckets[bucket]['holdings'].append(cash)
        buckets[bucket]['total_value'] += value
        buckets[bucket]['count'] += 1
    
    # Calculate total portfolio value
    total_portfolio_value = sum(bucket['total_value'] for bucket in buckets.values())
    
    # Create asset class data for visualization
    asset_classes = []
    sorted_buckets = sorted(buckets.items(), key=lambda x: x[1]['total_value'], reverse=True)
    
    for bucket_name, bucket_data in sorted_buckets:
        if bucket_data['total_value'] > 0:
            percentage = (bucket_data['total_value'] / total_portfolio_value * 100)
            asset_classes.append({
                'Asset_Class': bucket_name,
                'Value': bucket_data['total_value'],
                'Count': bucket_data['count'],
                'Percentage': percentage
            })
    
    # Create bar chart
    df = pd.DataFrame(asset_classes)
    
    fig = px.bar(
        df,
        x='Asset_Class',
        y='Value',
        title="Portfolio by Asset Class",
        color='Value',
        color_continuous_scale='Viridis',
        text='Percentage'
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display summary table
    st.subheader("Asset Class Summary")
    summary_df = df[['Asset_Class', 'Count', 'Value', 'Percentage']].copy()
    summary_df.columns = ['Asset Class', 'Holdings', 'Value (CAD)', 'Percentage']
    summary_df['Value (CAD)'] = summary_df['Value (CAD)'].apply(lambda x: f"${x:,.0f}")
    summary_df['Percentage'] = summary_df['Percentage'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(summary_df, use_container_width=True)
    
    return buckets

def create_portfolio_treemap(data, buckets):
    """Create portfolio treemap using refined bucketing"""
    st.header("🌳 Portfolio Tree Map")
    
    # Prepare data for treemap
    tree_data = []
    
    for bucket_name, bucket_data in buckets.items():
        if bucket_data['total_value'] > 0:
            # Add bucket level
            tree_data.append({
                'Bucket': bucket_name,
                'Holding': bucket_name,
                'Value': bucket_data['total_value'],
                'Level': 'Bucket',
                'Symbol': '',
                'Name': bucket_name,
                'Account_Number': '',
                'Dividend_Status': 'N/A'
            })
            
            # Add individual holdings within bucket
            for holding in bucket_data['holdings']:
                symbol = holding.get('Symbol', 'N/A')
                name = holding.get('Name', holding.get('Account_Name', ''))
                value = holding.get('Market_Value_CAD', holding.get('Amount_CAD', 0))
                account = holding.get('Account_Number', '')
                dividend_status = 'Paying' if holding.get('Indicated_Annual_Income', 0) > 0 else 'Non-Paying'
                
                tree_data.append({
                    'Bucket': bucket_name,
                    'Holding': f"{symbol} - {name[:30]}",
                    'Value': value,
                    'Level': 'Holding',
                    'Symbol': symbol,
                    'Name': name,
                    'Account_Number': account,
                    'Dividend_Status': dividend_status
                })
    
    # Create treemap
    tree_df = pd.DataFrame(tree_data)
    
    fig = px.treemap(
        tree_df,
        path=['Bucket', 'Holding'],
        values='Value',
        title="Portfolio Tree Map - Refined Buckets",
        color='Value',
        color_continuous_scale='Viridis',
        custom_data=['Name', 'Account_Number', 'Dividend_Status']
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<br>Name: %{customdata[0]}<br>Account: %{customdata[1]}<br>Dividend: %{customdata[2]}<extra></extra>'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_dividend_summary(data):
    """Create dividend summary section"""
    st.header("💰 Dividend Summary")
    
    # Filter holdings with dividend data
    dividend_holdings = []
    for holding in data['holdings']:
        if holding.get('Indicated_Annual_Income', 0) > 0:
            dividend_holdings.append(holding)
    
    if not dividend_holdings:
        st.warning("No dividend data found!")
        return
    
    # Calculate totals
    total_annual_dividends = sum(h.get('Indicated_Annual_Income', 0) for h in dividend_holdings)
    total_quarterly_dividends = sum(h.get('Quarterly_Dividend', 0) for h in dividend_holdings)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Annual Dividends",
            f"${total_annual_dividends:,.0f}"
        )
    
    with col2:
        st.metric(
            "Total Quarterly Dividends",
            f"${total_quarterly_dividends:,.0f}"
        )
    
    with col3:
        if dividend_holdings:
            max_dividend = max(dividend_holdings, key=lambda x: x.get('Indicated_Annual_Income', 0))
            st.metric(
                "Largest Dividend Payer",
                f"{max_dividend.get('Symbol', 'N/A')} - ${max_dividend.get('Indicated_Annual_Income', 0):,.0f}"
            )
    
    with col4:
        if dividend_holdings:
            min_dividend = min(dividend_holdings, key=lambda x: x.get('Indicated_Annual_Income', 0))
            st.metric(
                "Smallest Dividend Payer",
                f"{min_dividend.get('Symbol', 'N/A')} - ${min_dividend.get('Indicated_Annual_Income', 0):,.0f}"
            )
    
    # Create dividend chart
    dividend_df = pd.DataFrame(dividend_holdings)
    
    if not dividend_df.empty:
        # Top dividend payers chart
        fig = px.bar(
            dividend_df.nlargest(15, 'Indicated_Annual_Income'),
            x='Symbol',
            y='Indicated_Annual_Income',
            title="Top 15 Dividend Payers (Annual)",
            color='Indicated_Yield_on_Market',
            color_continuous_scale='Greens',
            text='Indicated_Yield_on_Market'
        )
        
        fig.update_traces(
            texttemplate='%{text:.1%}',
            textposition='outside'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Dividend details table
        st.subheader("Dividend Details")
        dividend_details = dividend_df[['Symbol', 'Name', 'Account_Number', 'Sector', 'Quantity', 'Indicated_Annual_Income', 'Quarterly_Dividend', 'Indicated_Yield_on_Market', 'Market_Value_CAD']].copy()
        dividend_details.columns = ['Symbol', 'Name', 'Account', 'Sector', 'Quantity', 'Annual Dividend', 'Quarterly Dividend', 'Yield', 'Market Value']
        
        # Format columns
        dividend_details['Annual Dividend'] = dividend_details['Annual Dividend'].apply(lambda x: f"${x:,.0f}")
        dividend_details['Quarterly Dividend'] = dividend_details['Quarterly Dividend'].apply(lambda x: f"${x:,.0f}")
        dividend_details['Yield'] = dividend_details['Yield'].apply(lambda x: f"{x:.1%}")
        dividend_details['Market Value'] = dividend_details['Market Value'].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(dividend_details, use_container_width=True)

def create_detailed_holdings_table(data, buckets):
    """Create detailed holdings table"""
    st.header("📋 Detailed Holdings Table")
    
    # Prepare holdings data
    holdings_data = []
    
    for bucket_name, bucket_data in buckets.items():
        for holding in bucket_data['holdings']:
            holdings_data.append({
                'Symbol': holding.get('Symbol', ''),
                'Name': holding.get('Name', holding.get('Account_Name', '')),
                'Account_Number': holding.get('Account_Number', ''),
                'Bucket': bucket_name,
                'Sector': holding.get('Sector', ''),
                'Industry': holding.get('Industry', ''),
                'Region': holding.get('Issuer_Region', ''),
                'Currency': holding.get('Currency', ''),
                'Quantity': holding.get('Quantity', 0),
                'Last_Price': holding.get('Last_Price', 0),
                'Market_Value_CAD': holding.get('Market_Value_CAD', holding.get('Amount_CAD', 0)),
                'Annual_Dividend': holding.get('Indicated_Annual_Income', 0),
                'Dividend_Yield': holding.get('Indicated_Yield_on_Market', 0)
            })
    
    df = pd.DataFrame(holdings_data)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        buckets_list = ['All'] + sorted(df['Bucket'].unique().tolist())
        selected_bucket = st.selectbox("Bucket", buckets_list)
    
    with col2:
        sectors = ['All'] + sorted(df['Sector'].unique().tolist())
        selected_sector = st.selectbox("Sector", sectors)
    
    with col3:
        industries = ['All'] + sorted(df['Industry'].unique().tolist())
        selected_industry = st.selectbox("Industry", industries)
    
    with col4:
        currencies = ['All'] + sorted(df['Currency'].unique().tolist())
        selected_currency = st.selectbox("Currency", currencies)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_bucket != 'All':
        filtered_df = filtered_df[filtered_df['Bucket'] == selected_bucket]
    
    if selected_sector != 'All':
        filtered_df = filtered_df[filtered_df['Sector'] == selected_sector]
    
    if selected_industry != 'All':
        filtered_df = filtered_df[filtered_df['Industry'] == selected_industry]
    
    if selected_currency != 'All':
        filtered_df = filtered_df[filtered_df['Currency'] == selected_currency]
    
    # Display table
    st.write(f"Showing {len(filtered_df)} holdings")
    
    # Format numeric columns
    display_df = filtered_df.copy()
    display_df['Last_Price'] = display_df['Last_Price'].apply(lambda x: f"${x:.2f}" if x > 0 else "")
    display_df['Market_Value_CAD'] = display_df['Market_Value_CAD'].apply(lambda x: f"${x:,.0f}")
    display_df['Annual_Dividend'] = display_df['Annual_Dividend'].apply(lambda x: f"${x:,.0f}" if x > 0 else "")
    display_df['Dividend_Yield'] = display_df['Dividend_Yield'].apply(lambda x: f"{x:.1%}" if x > 0 else "")
    
    st.dataframe(display_df, use_container_width=True)

def main():
    st.set_page_config(
        page_title="Refined Portfolio Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Refined Portfolio Dashboard")
    st.markdown("Portfolio analysis with decision tree bucketing logic")
    
    # Load data
    data = load_comprehensive_data()
    if data is None:
        return
    
    # Create sections
    buckets = create_asset_class_overview(data)
    create_portfolio_treemap(data, buckets)
    create_dividend_summary(data)
    create_detailed_holdings_table(data, buckets)

if __name__ == "__main__":
    main()
