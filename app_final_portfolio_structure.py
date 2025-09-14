#!/usr/bin/env python3
"""
Final Portfolio Dashboard - Exact Structure as Specified
Follows the precise structure requested - never change unless asked
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
    
    # Check if this is a cash balance object (different structure)
    if 'Cash_ID' in holding:
        return 'Cash'
    
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
    # Also check for cash balances with null symbol and "Cash Balance" name
    if symbol is None and 'cash balance' in name_lower:
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
    elif any(keyword in name_lower for keyword in ['technology', 'tech', 'semiconductor', 'software']):
        return 'Sector Equity - Technology'
    elif any(keyword in name_lower for keyword in ['energy', 'oil', 'gas', 'renewable']):
        return 'Sector Equity - Energy'
    elif any(keyword in name_lower for keyword in ['financial', 'bank', 'fintech']):
        return 'Sector Equity - Financial Services'
    elif any(keyword in name_lower for keyword in ['healthcare', 'health', 'pharmaceutical', 'biotech']):
        return 'Sector Equity - Healthcare'
    elif any(keyword in name_lower for keyword in ['consumer', 'retail']):
        return 'Sector Equity - Consumer'
    elif any(keyword in name_lower for keyword in ['communication', 'telecom', 'media']):
        return 'Sector Equity - Communication Services'
    else:
        return 'Sector Equity - Other'

def load_comprehensive_data():
    """Load the comprehensive holdings data"""
    
    # Check if we're running on Streamlit Cloud (look for cloud data file first)
    cloud_data_file = Path('data/consolidated_holdings_RBC_enriched_benefits_dividends_latest.json')
    if cloud_data_file.exists():
        st.info(f"Loading cloud data from: {cloud_data_file.name}")
        with open(cloud_data_file, 'r') as f:
            data = json.load(f)
        return data
    
    # Otherwise, load from local development directory
    output_dir = Path('data/output')
    
    # First try to load the corrected CAD dividends file
    corrected_files = list(output_dir.glob('comprehensive_holdings_dividends_cad_corrected_*.json'))
    if corrected_files:
        latest_file = max(corrected_files, key=lambda f: f.stat().st_mtime)
        st.info(f"Loading local data from: {latest_file.name} (CAD dividends corrected)")
    else:
        # Fallback to original files
        comprehensive_files = list(output_dir.glob('comprehensive_holdings_with_etf_dividends_*.json'))
        if not comprehensive_files:
            st.error("No comprehensive holdings files found!")
            return None
        latest_file = max(comprehensive_files, key=lambda f: f.stat().st_mtime)
        st.info(f"Loading local data from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data

def create_section_1_total_portfolio(data):
    """Section 1: Total Portfolio - All Accounts (DC Pension, RRSP, RBC Accounts)"""
    st.header("💰 Total Portfolio - All Accounts")
    
    # Calculate total portfolio value and USD breakdown
    total_value = 0
    account_summary = []
    
    # Process RBC holdings with USD tracking
    rbc_accounts = defaultdict(lambda: {
        'value': 0, 
        'count': 0, 
        'usd_value': 0, 
        'usd_original': 0,
        'usd_count': 0
    })
    
    for holding in data['holdings']:
        account = holding.get('Account_Number', 'Unknown')
        currency = holding.get('Currency', 'CAD')
        value = holding.get('Market_Value_CAD', 0)
        usd_original = holding.get('Market_Value', 0) if currency == 'USD' else 0
        
        rbc_accounts[account]['value'] += value
        rbc_accounts[account]['count'] += 1
        total_value += value
        
        if currency == 'USD':
            rbc_accounts[account]['usd_value'] += value
            rbc_accounts[account]['usd_original'] += usd_original
            rbc_accounts[account]['usd_count'] += 1
    
    # Add RBC cash balances (always CAD)
    cash_balances = data.get('cash_balances', [])
    for cash in cash_balances:
        if cash.get('Account_Type') != 'Benefits':  # RBC cash only
            account = cash.get('Account_Number', 'Unknown')
            value = cash.get('Amount_CAD', 0)
            rbc_accounts[account]['value'] += value
            rbc_accounts[account]['count'] += 1
            total_value += value
    
    # Add benefits accounts (always CAD)
    for cash in cash_balances:
        if cash.get('Account_Type') == 'Benefits':
            account_name = cash.get('Account_Name', 'Unknown')
            value = cash.get('Amount_CAD', 0)
            total_value += value
            account_summary.append({
                'Account': account_name,
                'Type': 'Benefits',
                'Value': value,
                'Count': 1,
                'USD_Value': 0,
                'USD_Original': 0,
                'USD_Count': 0
            })
    
    # Add RBC accounts with USD data
    for account, info in rbc_accounts.items():
        account_summary.append({
            'Account': f"RBC Account {account}",
            'Type': 'RBC',
            'Value': info['value'],
            'Count': info['count'],
            'USD_Value': info['usd_value'],
            'USD_Original': info['usd_original'],
            'USD_Count': info['usd_count']
        })
    
    # Display total portfolio value in large text at top left
    st.markdown(f"<h1 style='text-align: left; font-size: 3em; margin-bottom: 0.5em;'>${total_value:,.0f}</h1>", unsafe_allow_html=True)
    
    # Create simple account summary table
    df = pd.DataFrame(account_summary)
    df = df.sort_values('Value', ascending=False)
    
    # Calculate CAD and USD totals for each account
    df['CAD_Value'] = df['Value'] - df['USD_Value']
    df['USD_Percent'] = (df['USD_Value'] / df['Value'] * 100).round(1)
    
    # Format the display table
    display_df = pd.DataFrame({
        'Account': df['Account'],
        'Value_CAD': df['Value'].apply(lambda x: f"${x:,.0f}"),
        'CAD_Value': df['CAD_Value'].apply(lambda x: f"${x:,.0f}"),
        'USD_Value': df['USD_Value'].apply(lambda x: f"${x:,.0f}"),
        'USD_Percent': df['USD_Percent'].apply(lambda x: f"{x:.1f}%")
    })
    
    # Rename columns for display
    display_df.columns = ['Account', 'Total Value (CAD)', 'CAD Holdings', 'USD Holdings', '% USD']
    
    st.markdown("### Account Summary")
    
    # Add CSS for larger table fonts and taller rows
    st.markdown("""
    <style>
    .account-summary .stDataFrame > div {
        font-size: 16px !important;
    }
    .account-summary .stDataFrame table {
        font-size: 16px !important;
    }
    .account-summary .stDataFrame th {
        font-size: 18px !important;
        padding: 15px !important;
    }
    .account-summary .stDataFrame td {
        font-size: 16px !important;
        padding: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    return total_value

def apply_correct_grouping(data):
    """Apply the correct grouping logic to create 6 clean buckets"""
    
    # Initialize 6 buckets
    buckets = {
        'DC Pension': {'value': 0, 'count': 0, 'holdings': []},
        'RRSP': {'value': 0, 'count': 0, 'holdings': []},
        'Equity': {'value': 0, 'count': 0, 'holdings': []},
        'Fixed Income': {'value': 0, 'count': 0, 'holdings': []},
        'Cash & Cash Equivalents': {'value': 0, 'count': 0, 'holdings': []},
        'Real Estate': {'value': 0, 'count': 0, 'holdings': []}
    }
    
    # Process cash balances first (for DC Pension and RRSP)
    cash_balances = data.get('cash_balances', [])
    
    for cash in cash_balances:
        account_name = cash.get('Account_Name', 'Unknown')
        account_type = cash.get('Account_Type', 'Unknown')
        value = cash.get('Amount_CAD', 0)
        
        if account_type == 'Benefits':
            if 'DC Pension' in account_name or 'DC' in account_name:
                buckets['DC Pension']['value'] += value
                buckets['DC Pension']['count'] += 1
                buckets['DC Pension']['holdings'].append(cash)
            elif 'RSP' in account_name or 'RRSP' in account_name:
                buckets['RRSP']['value'] += value
                buckets['RRSP']['count'] += 1
                buckets['RRSP']['holdings'].append(cash)
        else:
            # RBC cash - goes to Cash & Cash Equivalents
            buckets['Cash & Cash Equivalents']['value'] += value
            buckets['Cash & Cash Equivalents']['count'] += 1
            buckets['Cash & Cash Equivalents']['holdings'].append(cash)
    
    # Process holdings with correct filtering logic
    holdings = data['holdings']
    
    for holding in holdings:
        symbol = holding.get('Symbol', '')
        name = holding.get('Name', '')
        value = holding.get('Market_Value_CAD', 0)
        
        # Convert to lowercase for easier matching
        name_lower = name.lower()
        
        # RULE 1: Real Estate - REITs and real estate ETFs (check first)
        if any(keyword in name_lower for keyword in ['reit', 'real estate', 'property']) or symbol in ['ZRE', 'O', 'REXR', 'STAG', 'NWH.UN', 'PMZ.UN']:
            buckets['Real Estate']['value'] += value
            buckets['Real Estate']['count'] += 1
            buckets['Real Estate']['holdings'].append(holding)
            continue
        
        # RULE 2: Fixed Income - Bonds and bond ETFs
        if any(keyword in name_lower for keyword in ['bond', 'treasury', 'corporate bond', 'government bond', 'note', 'debenture']) or symbol in ['HYG', 'ICSH', '5565652']:
            buckets['Fixed Income']['value'] += value
            buckets['Fixed Income']['count'] += 1
            buckets['Fixed Income']['holdings'].append(holding)
            continue
        
        # RULE 3: Cash Equivalents - Money market and cash equivalent ETFs
        if any(keyword in name_lower for keyword in ['money market', 'cash management', 'short term', 'ultra short', 'high interest savings']) or symbol in ['CMR', 'MNY', 'HISU.U']:
            buckets['Cash & Cash Equivalents']['value'] += value
            buckets['Cash & Cash Equivalents']['count'] += 1
            buckets['Cash & Cash Equivalents']['holdings'].append(holding)
            continue
        
        # RULE 4: Everything else goes to Equity
        buckets['Equity']['value'] += value
        buckets['Equity']['count'] += 1
        buckets['Equity']['holdings'].append(holding)
    
    return buckets

def create_section_2_asset_class_overview(data):
    """Section 2: Asset Class Overview - 6 Highest Level Buckets"""
    st.header("📊 Asset Class Overview")
    
    # Apply correct grouping logic
    buckets = apply_correct_grouping(data)
    
    # Calculate total and percentages
    total_value = sum(bucket['value'] for bucket in buckets.values())
    
    # Create visualization with USD breakdown
    asset_data = []
    for bucket_name, bucket_info in buckets.items():
        if bucket_info['value'] > 0:
            percentage = (bucket_info['value'] / total_value * 100)
            
            # Calculate USD amount for this bucket
            usd_value = 0
            for holding in bucket_info['holdings']:
                if holding.get('Currency') == 'USD':
                    usd_value += holding.get('Market_Value_CAD', 0)
            
            asset_data.append({
                'Asset_Class': bucket_name,
                'Value': bucket_info['value'],
                'USD_Value': usd_value,
                'CAD_Value': bucket_info['value'] - usd_value,
                'Count': bucket_info['count'],
                'Percentage': percentage
            })
    
    df = pd.DataFrame(asset_data)
    
    # Create symmetrical layout - exactly half screen each
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Summary View")
        
        fig = px.pie(
            df,
            values='Value',
            names='Asset_Class'
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont=dict(size=14)
        )
        
        fig.update_layout(
            height=600,  # Taller for better visibility
            font=dict(size=16),  # Larger text
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,  # More space between pie chart and legend
                xanchor="center",
                x=0.5,
                font=dict(size=14)
            ),
            showlegend=True
            # Removed title from pie chart
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Asset Class Mix and USD")
        
        # Create enhanced table with CAD/USD breakdown
        table_data = []
        total_value = 0
        total_cad = 0
        total_usd = 0
        
        for _, row in df.iterrows():
            table_data.append({
                'Asset Class': row['Asset_Class'],
                'Total (CAD)': f"${row['Value']:,.0f}",
                'CAD': f"${row['CAD_Value']:,.0f}",
                'USD': f"${row['USD_Value']:,.0f}",
                '% USD': f"{(row['USD_Value']/row['Value']*100):.1f}%" if row['Value'] > 0 else "0.0%"
            })
            total_value += row['Value']
            total_cad += row['CAD_Value']
            total_usd += row['USD_Value']
        
        # Add total row
        table_data.append({
            'Asset Class': '**TOTAL**',
            'Total (CAD)': f"${total_value:,.0f}",
            'CAD': f"${total_cad:,.0f}",
            'USD': f"${total_usd:,.0f}",
            '% USD': f"{(total_usd/total_value*100):.1f}%" if total_value > 0 else "0.0%"
        })
        
        table_df = pd.DataFrame(table_data)
        
        # Add CSS for larger table fonts and taller rows
        st.markdown("""
        <style>
        .stDataFrame > div {
            font-size: 16px !important;
        }
        .stDataFrame table {
            font-size: 16px !important;
        }
        .stDataFrame th {
            font-size: 18px !important;
            padding: 15px !important;
        }
        .stDataFrame td {
            font-size: 16px !important;
            padding: 15px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Style the table for better height and readability with larger fonts
        st.dataframe(
            table_df, 
            use_container_width=True, 
            hide_index=True,
            height=600  # Match pie chart height
        )
    
    return buckets

def create_section_3_detailed_groupings(data, buckets):
    """Section 3: Detailed Groupings - Simple Working Treemap"""
    st.header("🌳 Detailed Holdings by Asset Class")
    
    # Create simple treemap structure
    tree_data = []
    
    # Process each bucket
    for bucket_name, bucket_info in buckets.items():
        if bucket_info['value'] > 0:
            holdings = bucket_info['holdings']
            
            # For DC Pension and RRSP - force 3 levels
            if bucket_name in ['DC Pension', 'RRSP']:
                for holding in holdings:
                    symbol = holding.get('Symbol', 'N/A')
                    name = holding.get('Name', holding.get('Account_Name', ''))
                    value = holding.get('Market_Value_CAD', holding.get('Amount_CAD', 0))
                    
                    # Level 3: Just symbol, or blank if N/A
                    holding_label = symbol if symbol != 'N/A' else ''
                    
                    # Use the actual account name as level 2
                    account_name = holding.get('Account_Name', 'Managed Account')
                    
                    tree_data.append({
                        'Group': bucket_name,
                        'SubGroup': account_name,  # Level 2: actual account name
                        'Holding': holding_label,  # Level 3 just symbol or blank
                        'Value': value,
                        'Symbol': holding_label,
                        'Gain_Loss': f"{holding.get('Unrealized_Gain_Loss_Pct', 0):.1f}%",
                        'Holding_Data': holding  # Store full holding data
                    })
            
            # For Cash & Cash Equivalents - break down by type
            elif bucket_name == 'Cash & Cash Equivalents':
                cash_groups = defaultdict(list)
                
                for holding in holdings:
                    bucket_type = classify_holding(holding)
                    value = holding.get('Market_Value_CAD', holding.get('Amount_CAD', 0))
                    symbol = holding.get('Symbol', 'N/A')
                    name = holding.get('Name', holding.get('Account_Name', ''))
                    
                    cash_groups[bucket_type].append({
                        'symbol': symbol,
                        'name': name,
                        'value': value
                    })
                
                # Add cash groups with shortened labels
                for group_name, group_holdings in cash_groups.items():
                    # Shorten the group names for better display
                    short_group_name = group_name.replace('Cash Alternatives', 'Cash Alternatives')
                    
                    for holding_info in group_holdings:
                        # Level 3: Just symbol, or blank if N/A
                        holding_label = holding_info['symbol'] if holding_info['symbol'] != 'N/A' else ''
                        
                        # Find the original holding data for cash items
                        original_cash_holding = None
                        for holding in holdings:
                            if holding.get('Symbol') == holding_info['symbol']:
                                original_cash_holding = holding
                                break
                        
                        tree_data.append({
                            'Group': 'Cash & Cash Equivalents',
                            'SubGroup': short_group_name,
                            'Holding': holding_label,  # Level 3 just symbol or blank
                            'Value': holding_info['value'],
                            'Symbol': holding_label,
                            'Gain_Loss': f"{original_cash_holding.get('Unrealized_Gain_Loss_Pct', 0):.1f}%" if original_cash_holding else "0.0%",
                            'Holding_Data': original_cash_holding  # Store full holding data
                        })
            
            # For Equity - break down by sectors
            elif bucket_name == 'Equity':
                equity_groups = defaultdict(list)
                
                for holding in holdings:
                    bucket_type = classify_holding(holding)
                    value = holding.get('Market_Value_CAD', 0)
                    symbol = holding.get('Symbol', 'N/A')
                    name = holding.get('Name', '')
                    
                    equity_groups[bucket_type].append({
                        'symbol': symbol,
                        'name': name,
                        'value': value
                    })
                
                # Add equity groups with shortened labels
                for group_name, group_holdings in equity_groups.items():
                    # Shorten the group names for better display
                    short_group_name = group_name.replace('Sector Equity - ', '').replace('Broad Market Equity - ', '').replace('Dividend Focused Equity', 'Dividend Focused')
                    
                    for holding_info in group_holdings:
                        # Level 3: Just symbol, or blank if N/A
                        holding_label = holding_info['symbol'] if holding_info['symbol'] != 'N/A' else ''
                        
                        # Find the original holding data for this symbol
                        original_holding = None
                        for holding in holdings:
                            if holding.get('Symbol') == holding_info['symbol']:
                                original_holding = holding
                                break
                        
                        tree_data.append({
                            'Group': 'Equity',
                            'SubGroup': short_group_name,
                            'Holding': holding_label,  # Level 3 just symbol or blank
                            'Value': holding_info['value'],
                            'Symbol': holding_label,
                            'Gain_Loss': f"{original_holding.get('Unrealized_Gain_Loss_Pct', 0):.1f}%" if original_holding else "0.0%",
                            'Holding_Data': original_holding  # Store full holding data
                        })
            
            # For other buckets (Fixed Income, Real Estate) - force 3 levels
            else:
                for holding in holdings:
                    symbol = holding.get('Symbol', 'N/A')
                    name = holding.get('Name', '')
                    value = holding.get('Market_Value_CAD', 0)
                    
                    # Level 3: Just symbol, or blank if N/A
                    holding_label = symbol if symbol != 'N/A' else ''
                    
                    # Use shortened level 2 labels based on bucket type
                    if bucket_name == 'Fixed Income':
                        sub_group = 'Bonds'
                    elif bucket_name == 'Real Estate':
                        sub_group = 'REITs'
                    else:
                        sub_group = 'Holdings'
                    
                    tree_data.append({
                        'Group': bucket_name,
                        'SubGroup': sub_group,  # Level 2: descriptive category
                        'Holding': holding_label,  # Level 3 just symbol or blank
                        'Value': value,
                        'Symbol': holding_label,
                        'Gain_Loss': f"{holding.get('Unrealized_Gain_Loss_Pct', 0):.1f}%",
                        'Holding_Data': holding  # Store full holding data
                    })
    
    # Create treemap
    if tree_data:
        tree_df = pd.DataFrame(tree_data)
        
        fig = px.treemap(
            tree_df,
            path=['Group', 'SubGroup', 'Holding'],
            values='Value',
            color='Value',
            color_continuous_scale='Viridis'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<br>Symbol: %{customdata[0]}<br>Gain/Loss: %{customdata[1]}<br><i>Click to navigate to detailed table</i><extra></extra>',
            customdata=tree_df[['Symbol', 'Gain_Loss']].values
        )
        
        # Add click handling for navigation
        selected_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        
        # Handle treemap clicks for navigation
        if selected_data and 'selection' in selected_data:
            selected_points = selected_data['selection']['points']
            if selected_points:
                # Get the clicked path to filter the detailed table
                clicked_path = selected_points[0]['path']
                clicked_value = selected_points[0].get('value', 0)
                clicked_label = selected_points[0].get('label', '')
                
                # Check if this is a level 3 holding (individual stock)
                if len(clicked_path) == 3:  # Group > SubGroup > Holding
                    clicked_symbol = clicked_path[2]
                    if clicked_symbol and clicked_symbol != '':
                        # Find the holding data from the treemap data
                        holding_data = None
                        for _, row in tree_df.iterrows():
                            if row['Holding'] == clicked_symbol:
                                holding_data = row['Holding_Data']
                                break
                        
                        if holding_data:
                            # Store holding data for detailed view
                            st.session_state.selected_holding = {
                                'symbol': holding_data.get('Symbol', ''),
                                'name': holding_data.get('Name', ''),
                                'value': holding_data.get('Market_Value_CAD', 0),
                                'shares': holding_data.get('Quantity', 0),
                                'dividend': holding_data.get('Indicated_Annual_Income', 0),
                                'yield': holding_data.get('Indicated_Yield_on_Market', 0),
                                'gain': holding_data.get('Unrealized_Gain_Loss_Pct', 0),
                                'account': holding_data.get('Account_Number', ''),
                                'sector': holding_data.get('Sector', ''),
                                'industry': holding_data.get('Industry', ''),
                                'currency': holding_data.get('Currency', ''),
                                'last_price': holding_data.get('Last_Price', 0)
                            }
                            st.success(f"Loading details for {clicked_symbol}")
                            st.rerun()
                
                elif len(clicked_path) >= 2:  # At least Group and SubGroup
                    clicked_group = clicked_path[0]
                    clicked_subgroup = clicked_path[1] if len(clicked_path) > 1 else None
                    
                    # Store in session state for filtering
                    st.session_state.treemap_filter = {
                        'group': clicked_group,
                        'subgroup': clicked_subgroup
                    }
                    
                    st.success(f"Navigating to: {clicked_group}" + (f" > {clicked_subgroup}" if clicked_subgroup else ""))
                    st.rerun()
    

def create_holding_detail_view():
    """Display detailed holding information"""
    if 'selected_holding' not in st.session_state:
        return False
    
    holding = st.session_state.selected_holding
    
    # Back button
    if st.button("← Back to Dashboard", key="back_button"):
        del st.session_state.selected_holding
        st.rerun()
    
    st.header(f"📊 {holding['symbol']} - {holding['name']}")
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Main holding information
        st.markdown("### Holding Details")
        
        # Key metrics in a grid - showing all requested data elements
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric(
                "Symbol",
                f"{holding['symbol']}",
                help="Stock ticker symbol"
            )
            st.metric(
                "Name",
                f"{holding['name'][:30]}{'...' if len(holding['name']) > 30 else ''}",
                help="Company name"
            )
            st.metric(
                "Market Value (CAD)",
                f"${holding['value']:,.0f}",
                help="Current market value in Canadian dollars"
            )
        
        with metric_col2:
            st.metric(
                "Number of Shares",
                f"{holding['shares']:,.0f}",
                help="Total number of shares held"
            )
            st.metric(
                "Annual Dividend (CAD)",
                f"${holding['dividend']:,.0f}",
                help="Annual dividend income in Canadian dollars"
            )
            st.metric(
                "Dividend Yield",
                f"{holding['yield']:.1%}",
                help="Annual dividend yield percentage"
            )
        
        with metric_col3:
            st.metric(
                "Unrealized Gain/Loss",
                f"{holding['gain']:.1f}%",
                help="Percentage gain or loss on position"
            )
            st.metric(
                "Last Price",
                f"${holding['last_price']:.2f}",
                help=f"Last trading price in {holding['currency']}"
            )
            st.metric(
                "Account",
                f"{holding['account']}",
                help="Account number holding this position"
            )
        
        # Additional details
        st.markdown("### Additional Information")
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.info(f"**Account:** {holding['account']}")
            st.info(f"**Currency:** {holding['currency']}")
        
        with detail_col2:
            st.info(f"**Sector:** {holding['sector']}")
            st.info(f"**Industry:** {holding['industry']}")
    
    with col2:
        st.markdown("### Placeholder for Future Features")
        st.markdown(f"""
        **{holding['symbol']} - {holding['name']}**
        
        This section will be populated with detailed information including:
        - Historical price charts
        - News and analysis
        - Performance metrics
        - Trading recommendations
        - Risk assessment
        - Peer comparisons
        """)
        
        # Placeholder chart area
        st.markdown("**Price Chart Placeholder**")
        st.info("Interactive price chart will be displayed here")
        
        st.markdown("**News Feed Placeholder**")
        st.info("Latest news and updates will be shown here")
        
        st.markdown("**Analysis Placeholder**")
        st.info("Technical and fundamental analysis will be shown here")
    
    return True

def create_section_4_dividends(data):
    """Section 4: Dividends - Keep current dividend summary"""
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
    
    # Calculate USD dividend breakdown
    usd_dividend_holdings = [h for h in dividend_holdings if h.get('Original_Dividend_USD', 0) > 0]
    total_usd_dividends = sum(h.get('Original_Dividend_USD', 0) for h in usd_dividend_holdings)
    cad_dividend_holdings = [h for h in dividend_holdings if h.get('Original_Dividend_USD', 0) == 0]
    total_cad_dividends = sum(h.get('Indicated_Annual_Income', 0) for h in cad_dividend_holdings)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Annual Dividends (CAD)",
            f"${total_annual_dividends:,.0f}",
            help="Total annual dividend income in CAD"
        )
    
    with col2:
        st.metric(
            "USD Dividends (Original)", 
            f"${total_usd_dividends:,.0f}",
            help="Original USD dividend payments converted to CAD"
        )
    
    with col3:
        # Calculate conversion details
        conversion_amount = total_annual_dividends - total_usd_dividends  # CAD dividends from USD conversion
        usd_percentage = (total_usd_dividends / total_annual_dividends * 100) if total_annual_dividends > 0 else 0
        
        st.metric(
            "USD Dividends",
            f"${total_usd_dividends:,.0f}",
            help=f"Original USD dividend payments: ${total_usd_dividends:,.0f} USD converted to ${total_usd_dividends + conversion_amount:,.0f} CAD"
        )
        st.caption(f"${conversion_amount:,.0f} CAD from conversion")
    
    with col4:
        st.metric(
            "USD Percentage",
            f"{usd_percentage:.1f}%",
            help="Percentage of total dividends paid in USD (original currency)"
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
            textposition='outside',
            textfont=dict(size=12)
        )
        
        fig.update_layout(
            font=dict(size=14),
            title_font=dict(size=18)
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

def create_section_5_detailed_holdings_table(data, buckets):
    """Section 5: Detailed Holdings Table with filters"""
    st.header("📋 Detailed Holdings Table")
    
    # Prepare holdings data with bucket information
    holdings_data = []
    
    for bucket_name, bucket_data in buckets.items():
        for holding in bucket_data['holdings']:
            # Determine subcategory for equity holdings
            subcategory = 'N/A'
            if bucket_name == 'Equity':
                bucket = classify_holding(holding)
                if bucket.startswith('Sector Equity -'):
                    subcategory = bucket.replace('Sector Equity - ', '')
                elif bucket.startswith('Broad Market Equity'):
                    subcategory = bucket.replace('Broad Market Equity - ', 'Broad Market ')
                elif bucket == 'Dividend Focused Equity':
                    subcategory = 'Dividend Focused'
                elif bucket == 'Regional Equity':
                    subcategory = 'Regional'
                else:
                    subcategory = 'Other Equity'
            elif bucket_name == 'Cash & Cash Equivalents':
                bucket = classify_holding(holding)
                if bucket == 'Cash':
                    subcategory = 'Cash'
                elif bucket == 'Cash Alternatives':
                    subcategory = 'Cash Alternatives'
                else:
                    subcategory = 'Other'
            else:
                subcategory = bucket_name
            
            holdings_data.append({
                'Symbol': holding.get('Symbol', ''),
                'Name': holding.get('Name', holding.get('Account_Name', '')),
                'Account_Number': holding.get('Account_Number', ''),
                'Group': bucket_name,
                'SubGroup': subcategory,
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
    col1, col2, col3 = st.columns(3)
    
    with col1:
        groups = ['All'] + sorted(df['Group'].unique().tolist())
        selected_group = st.selectbox("Group", groups)
    
    with col2:
        subgroups = ['All'] + sorted(df['SubGroup'].unique().tolist())
        selected_subgroup = st.selectbox("SubGroup", subgroups)
    
    with col3:
        regions = ['All'] + sorted(df['Region'].unique().tolist())
        selected_region = st.selectbox("Region", regions)
    
    # Apply filters
    filtered_df = df.copy()
    
    # Check for treemap navigation filter
    if 'treemap_filter' in st.session_state:
        treemap_filter = st.session_state.treemap_filter
        if treemap_filter['group']:
            filtered_df = filtered_df[filtered_df['Group'] == treemap_filter['group']]
        if treemap_filter['subgroup']:
            filtered_df = filtered_df[filtered_df['SubGroup'] == treemap_filter['subgroup']]
        
        # Clear the filter after applying
        del st.session_state.treemap_filter
        st.info("🎯 Filtered by treemap selection")
    else:
        # Apply manual filters
        if selected_group != 'All':
            filtered_df = filtered_df[filtered_df['Group'] == selected_group]
        
        if selected_subgroup != 'All':
            filtered_df = filtered_df[filtered_df['SubGroup'] == selected_subgroup]
        
        if selected_region != 'All':
            filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    
    # Display table
    st.write(f"Showing {len(filtered_df)} holdings")
    
    # Format numeric columns
    display_df = filtered_df.copy()
    display_df['Last_Price'] = display_df['Last_Price'].apply(lambda x: f"${x:.2f}" if x > 0 else "")
    display_df['Market_Value_CAD'] = display_df['Market_Value_CAD'].apply(lambda x: f"${x:,.0f}")
    display_df['Annual_Dividend'] = display_df['Annual_Dividend'].apply(lambda x: f"${x:,.0f}" if x > 0 else "")
    display_df['Dividend_Yield'] = display_df['Dividend_Yield'].apply(lambda x: f"{x:.1%}" if x > 0 else "")
    
    # Add CSS for larger table fonts and taller rows
    st.markdown("""
    <style>
    .detailed-holdings .stDataFrame > div {
        font-size: 16px !important;
    }
    .detailed-holdings .stDataFrame table {
        font-size: 16px !important;
    }
    .detailed-holdings .stDataFrame th {
        font-size: 18px !important;
        padding: 15px !important;
    }
    .detailed-holdings .stDataFrame td {
        font-size: 16px !important;
        padding: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(display_df, use_container_width=True)

def main():
    st.set_page_config(
        page_title="Final Portfolio Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Check if we should show holding detail view
    if create_holding_detail_view():
        return  # Exit early if showing holding detail
    
    st.title("📊 Final Portfolio Dashboard")
    st.markdown("Exact structure as specified - never change unless asked")
    
    # Load data
    data = load_comprehensive_data()
    if data is None:
        return
    
    # Create sections in exact order specified
    total_value = create_section_1_total_portfolio(data)
    buckets = create_section_2_asset_class_overview(data)
    create_section_3_detailed_groupings(data, buckets)
    create_section_4_dividends(data)
    create_section_5_detailed_holdings_table(data, buckets)

if __name__ == "__main__":
    main()
