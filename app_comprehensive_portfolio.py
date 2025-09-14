#!/usr/bin/env python3
"""
Comprehensive Portfolio Dashboard
Shows RBC holdings + Benefits accounts with multiple summary levels
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

def load_comprehensive_data():
    """Load the most recent comprehensive holdings file"""
    output_dir = Path('data/output')
    comp_files = list(output_dir.glob('comprehensive_holdings_RBC_and_Benefits_*.json'))
    
    if not comp_files:
        st.error("No comprehensive holdings files found!")
        return None
    
    latest_file = max(comp_files, key=lambda f: f.stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data, latest_file.name

def main():
    st.set_page_config(
        page_title="Comprehensive Portfolio Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Comprehensive Portfolio Dashboard")
    st.markdown("**RBC Holdings + Benefits Accounts Analysis**")
    
    # Load data
    data, filename = load_comprehensive_data()
    if not data:
        return
    
    st.sidebar.info(f"📁 Data Source: {filename}")
    
    metadata = data['metadata']
    
    # Portfolio Summary
    st.header("💰 Portfolio Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Portfolio Value",
            f"${metadata['total_portfolio_value_cad']:,.0f} CAD",
            delta=None
        )
    
    with col2:
        st.metric(
            "Holdings Value",
            f"${metadata['rbc_holdings_total_cad']:,.0f} CAD",
            delta=f"{(metadata['rbc_holdings_total_cad'] / metadata['total_portfolio_value_cad'] * 100):.1f}%"
        )
    
    with col3:
        st.metric(
            "Cash & Benefits",
            f"${metadata['combined_cash_total_cad']:,.0f} CAD",
            delta=f"{(metadata['combined_cash_total_cad'] / metadata['total_portfolio_value_cad'] * 100):.1f}%"
        )
    
    with col4:
        st.metric(
            "Total Holdings",
            f"{metadata['total_rbc_holdings']}",
            delta=f"{metadata['total_rbc_cash_balances'] + metadata['total_benefits_accounts']} accounts"
        )
    
    # Analysis Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏦 By Account Type", 
        "📊 By Sector", 
        "📈 By Asset Type", 
        "💱 By Currency",
        "📋 Detailed Holdings"
    ])
    
    with tab1:
        st.header("🏦 Analysis by Account Type")
        
        # RBC vs Benefits breakdown
        rbc_accounts = [acc for acc in data['cash_balances'] if acc.get('Account_Type') != 'Benefits']
        benefits_accounts = [acc for acc in data['cash_balances'] if acc.get('Account_Type') == 'Benefits']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏦 RBC Accounts")
            rbc_df = pd.DataFrame(rbc_accounts)
            if not rbc_df.empty:
                rbc_df = rbc_df[['Account_Number', 'Currency', 'Amount', 'Amount_CAD']]
                rbc_df['Amount'] = rbc_df['Amount'].apply(lambda x: f"${x:,.2f}")
                rbc_df['Amount_CAD'] = rbc_df['Amount_CAD'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(rbc_df, use_container_width=True)
                
                rbc_total = sum(acc['Amount_CAD'] for acc in rbc_accounts)
                st.metric("RBC Total", f"${rbc_total:,.2f} CAD")
        
        with col2:
            st.subheader("🏛️ Benefits Accounts")
            benefits_df = pd.DataFrame(benefits_accounts)
            if not benefits_df.empty:
                benefits_df = benefits_df[['Account_Name', 'Amount_CAD']]
                benefits_df['Amount_CAD'] = benefits_df['Amount_CAD'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(benefits_df, use_container_width=True)
                
                benefits_total = sum(acc['Amount_CAD'] for acc in benefits_accounts)
                st.metric("Benefits Total", f"${benefits_total:,.2f} CAD")
    
    with tab2:
        st.header("📊 Analysis by Sector")
        
        # Sector analysis
        sector_summary = defaultdict(lambda: {'count': 0, 'total_value': 0, 'holdings': []})
        
        for holding in data['holdings']:
            sector = holding.get('Sector', 'Unknown')
            value = holding.get('Market_Value_CAD', 0)
            
            sector_summary[sector]['count'] += 1
            sector_summary[sector]['total_value'] += value
            sector_summary[sector]['holdings'].append({
                'symbol': holding.get('Symbol', ''),
                'name': holding.get('Name', ''),
                'value': value
            })
        
        # Create sector DataFrame
        sector_data = []
        for sector, info in sector_summary.items():
            sector_data.append({
                'Sector': sector,
                'Holdings': info['count'],
                'Total Value (CAD)': f"${info['total_value']:,.2f}",
                'Percentage': f"{(info['total_value'] / metadata['rbc_holdings_total_cad'] * 100):.1f}%"
            })
        
        sector_df = pd.DataFrame(sector_data)
        sector_df = sector_df.sort_values('Total Value (CAD)', ascending=False)
        st.dataframe(sector_df, use_container_width=True)
        
        # Sector pie chart
        if sector_summary:
            import plotly.express as px
            
            fig = px.pie(
                values=[info['total_value'] for info in sector_summary.values()],
                names=list(sector_summary.keys()),
                title="Portfolio by Sector"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("📈 Analysis by Asset Type")
        
        # Asset type analysis
        asset_summary = defaultdict(lambda: {'count': 0, 'total_value': 0})
        
        for holding in data['holdings']:
            asset_type = holding.get('Asset_Type', 'Unknown')
            value = holding.get('Market_Value_CAD', 0)
            
            asset_summary[asset_type]['count'] += 1
            asset_summary[asset_type]['total_value'] += value
        
        # Create asset type DataFrame
        asset_data = []
        for asset_type, info in asset_summary.items():
            asset_data.append({
                'Asset Type': asset_type,
                'Holdings': info['count'],
                'Total Value (CAD)': f"${info['total_value']:,.2f}",
                'Percentage': f"{(info['total_value'] / metadata['rbc_holdings_total_cad'] * 100):.1f}%"
            })
        
        asset_df = pd.DataFrame(asset_data)
        asset_df = asset_df.sort_values('Total Value (CAD)', ascending=False)
        st.dataframe(asset_df, use_container_width=True)
    
    with tab4:
        st.header("💱 Analysis by Currency")
        
        # Currency analysis
        currency_summary = defaultdict(lambda: {'holdings': 0, 'cash': 0, 'total': 0})
        
        # Analyze holdings
        for holding in data['holdings']:
            currency = holding.get('Currency', 'Unknown')
            value = holding.get('Market_Value_CAD', 0)
            currency_summary[currency]['holdings'] += value
            currency_summary[currency]['total'] += value
        
        # Analyze cash balances
        for cash in data['cash_balances']:
            currency = cash.get('Currency', 'Unknown')
            value = cash.get('Amount_CAD', 0)
            currency_summary[currency]['cash'] += value
            currency_summary[currency]['total'] += value
        
        # Create currency DataFrame
        currency_data = []
        for currency, info in currency_summary.items():
            currency_data.append({
                'Currency': currency,
                'Holdings (CAD)': f"${info['holdings']:,.2f}",
                'Cash (CAD)': f"${info['cash']:,.2f}",
                'Total (CAD)': f"${info['total']:,.2f}",
                'Percentage': f"{(info['total'] / metadata['total_portfolio_value_cad'] * 100):.1f}%"
            })
        
        currency_df = pd.DataFrame(currency_data)
        currency_df = currency_df.sort_values('Total (CAD)', ascending=False)
        st.dataframe(currency_df, use_container_width=True)
    
    with tab5:
        st.header("📋 Detailed Holdings")
        
        # Create holdings DataFrame
        holdings_data = []
        for holding in data['holdings']:
            holdings_data.append({
                'Symbol': holding.get('Symbol', ''),
                'Name': holding.get('Name', ''),
                'Sector': holding.get('Sector', ''),
                'Industry': holding.get('Industry', ''),
                'Asset Type': holding.get('Asset_Type', ''),
                'Currency': holding.get('Currency', ''),
                'Market Value (CAD)': f"${holding.get('Market_Value_CAD', 0):,.2f}",
                'Account': holding.get('Account_Number', '')
            })
        
        holdings_df = pd.DataFrame(holdings_data)
        
        # Filters
        st.subheader("🔍 Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sectors = ['All'] + sorted(holdings_df['Sector'].unique().tolist())
            selected_sector = st.selectbox("Filter by Sector", sectors)
        
        with col2:
            asset_types = ['All'] + sorted(holdings_df['Asset Type'].unique().tolist())
            selected_asset_type = st.selectbox("Filter by Asset Type", asset_types)
        
        with col3:
            currencies = ['All'] + sorted(holdings_df['Currency'].unique().tolist())
            selected_currency = st.selectbox("Filter by Currency", currencies)
        
        # Apply filters
        filtered_df = holdings_df.copy()
        
        if selected_sector != 'All':
            filtered_df = filtered_df[filtered_df['Sector'] == selected_sector]
        
        if selected_asset_type != 'All':
            filtered_df = filtered_df[filtered_df['Asset Type'] == selected_asset_type]
        
        if selected_currency != 'All':
            filtered_df = filtered_df[filtered_df['Currency'] == selected_currency]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Summary of filtered data
        if not filtered_df.empty:
            total_filtered_value = sum(
                float(row['Market Value (CAD)'].replace('$', '').replace(',', ''))
                for row in filtered_df.to_dict('records')
            )
            st.metric(f"Total Value ({len(filtered_df)} holdings)", f"${total_filtered_value:,.2f} CAD")

if __name__ == "__main__":
    main()
