#!/usr/bin/env python3
"""
Final Portfolio Dashboard with 4 sections:
1. Asset Classes Overview
2. Tree Map by Type/Sector/Region  
3. Dividend Summary
4. Detailed Holdings Table
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from collections import defaultdict

def load_comprehensive_data():
    """Load the most recent comprehensive holdings with dividends"""
    output_dir = Path('data/output')
    
    # Try dividend file first, then fall back to regular comprehensive file
    dividend_files = list(output_dir.glob('comprehensive_holdings_with_dividends_*.json'))
    comp_files = list(output_dir.glob('comprehensive_holdings_RBC_and_Benefits_*.json'))
    
    if dividend_files:
        latest_file = max(dividend_files, key=lambda f: f.stat().st_mtime)
        st.sidebar.success(f"📊 Using dividend-enriched data: {latest_file.name}")
    elif comp_files:
        latest_file = max(comp_files, key=lambda f: f.stat().st_mtime)
        st.sidebar.warning(f"📊 Using basic data (no dividends): {latest_file.name}")
    else:
        st.error("No comprehensive holdings files found!")
        return None, None
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data, latest_file.name

def create_asset_class_overview(data):
    """Section 1: Asset Classes Overview"""
    st.header("🏗️ Asset Classes Overview")
    st.markdown("**Portfolio breakdown by major asset classes including RBC holdings and Benefits accounts**")
    
    metadata = data['metadata']
    
    # Portfolio Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Portfolio",
            f"${metadata['total_portfolio_value_cad']:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "RBC Holdings",
            f"${metadata['rbc_holdings_total_cad']:,.0f}",
            delta=f"{(metadata['rbc_holdings_total_cad'] / metadata['total_portfolio_value_cad'] * 100):.1f}%"
        )
    
    with col3:
        st.metric(
            "Benefits Accounts",
            f"${metadata['benefits_total_cad']:,.0f}",
            delta=f"{(metadata['benefits_total_cad'] / metadata['total_portfolio_value_cad'] * 100):.1f}%"
        )
    
    with col4:
        st.metric(
            "Cash & Equivalents",
            f"${metadata['rbc_cash_total_cad']:,.0f}",
            delta=f"{(metadata['rbc_cash_total_cad'] / metadata['total_portfolio_value_cad'] * 100):.1f}%"
        )
    
    # Asset Class Breakdown
    st.subheader("📊 Asset Class Breakdown")
    
    # Analyze RBC holdings by sector (since Asset_Type doesn't exist)
    sector_analysis = defaultdict(lambda: {'value': 0, 'count': 0, 'holdings': []})
    
    for holding in data['holdings']:
        sector = holding.get('Sector', 'Unknown')
        value = holding.get('Market_Value_CAD', 0)
        
        sector_analysis[sector]['value'] += value
        sector_analysis[sector]['count'] += 1
        sector_analysis[sector]['holdings'].append(holding)
    
    # Create asset class data for visualization
    asset_classes = []
    
    # Add RBC sectors as asset classes
    for sector, info in sector_analysis.items():
        if info['value'] > 0:
            asset_classes.append({
                'Asset_Class': f"RBC {sector}",
                'Value': info['value'],
                'Count': info['count'],
                'Type': 'RBC Holdings',
                'Percentage': (info['value'] / metadata['total_portfolio_value_cad'] * 100)
            })
    
    # Add RBC Cash
    if metadata['rbc_cash_total_cad'] > 0:
        asset_classes.append({
            'Asset_Class': 'RBC Cash & Equivalents',
            'Value': metadata['rbc_cash_total_cad'],
            'Count': metadata['total_rbc_cash_balances'],
            'Type': 'Cash',
            'Percentage': (metadata['rbc_cash_total_cad'] / metadata['total_portfolio_value_cad'] * 100)
        })
    
    # Add Benefits accounts
    benefits_accounts = [acc for acc in data['cash_balances'] if acc.get('Account_Type') == 'Benefits']
    for acc in benefits_accounts:
        asset_classes.append({
            'Asset_Class': acc['Account_Name'],
            'Value': acc['Amount_CAD'],
            'Count': 1,
            'Type': 'Benefits',
            'Percentage': (acc['Amount_CAD'] / metadata['total_portfolio_value_cad'] * 100)
        })
    
    # Create DataFrame for display
    asset_df = pd.DataFrame(asset_classes)
    asset_df = asset_df.sort_values('Value', ascending=False)
    
    # Display asset class breakdown
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create horizontal bar chart
        fig = px.bar(
            asset_df, 
            x='Value', 
            y='Asset_Class',
            orientation='h',
            title="Portfolio by Asset Class",
            color='Type',
            color_discrete_map={
                'RBC Holdings': '#1f77b4',
                'Cash': '#ff7f0e', 
                'Benefits': '#2ca02c'
            }
        )
        fig.update_layout(
            height=400,
            xaxis_title="Value (CAD)",
            yaxis_title="Asset Class"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Asset class summary table
        st.subheader("Asset Class Summary")
        summary_df = asset_df[['Asset_Class', 'Value', 'Percentage']].copy()
        summary_df['Value'] = summary_df['Value'].apply(lambda x: f"${x:,.0f}")
        summary_df['Percentage'] = summary_df['Percentage'].apply(lambda x: f"{x:.1f}%")
        summary_df.columns = ['Asset Class', 'Value', '%']
        st.dataframe(summary_df, use_container_width=True)

def create_tree_map(data):
    """Section 2: Tree Map by Type/Sector/Region"""
    st.header("🌳 Holdings by Type, Sector & Region")
    st.markdown("**Interactive tree map showing individual holdings grouped by asset type, sector, and region**")
    
    # Separate RBC holdings and benefits
    rbc_holdings = data['holdings']
    benefits_accounts = [acc for acc in data['cash_balances'] if acc.get('Account_Type') == 'Benefits']
    
    # Create data for tree map
    tree_data = []
    
    # Add RBC holdings
    for holding in rbc_holdings:
        tree_data.append({
            'Symbol': holding.get('Symbol', 'Unknown'),
            'Name': holding.get('Name', ''),
            'Sector': holding.get('Sector', 'Unknown'),
            'Industry': holding.get('Industry', 'Unknown'),
            'Region': holding.get('Issuer_Region', 'Unknown'),
            'Value': holding.get('Market_Value_CAD', 0),
            'Account_Type': 'RBC',
            'Account_Number': holding.get('Account_Number', ''),
            'Dividend_Status': 'Paying' if holding.get('Indicated_Annual_Income', 0) > 0 else 'Non-Paying'
        })
    
    # Add Benefits accounts as special entries
    for acc in benefits_accounts:
        tree_data.append({
            'Symbol': acc['Account_Name'].replace(' ', '_'),
            'Name': acc['Account_Name'],
            'Sector': 'Benefits',
            'Industry': 'Benefits',
            'Region': 'Canada',
            'Value': acc['Amount_CAD'],
            'Account_Type': 'Benefits',
            'Account_Number': acc['Account_Number'],
            'Dividend_Status': 'N/A'
        })
    
    tree_df = pd.DataFrame(tree_data)
    
    # Create tree map
    fig = px.treemap(
        tree_df,
        path=['Account_Type', 'Sector', 'Industry', 'Region', 'Symbol'],
        values='Value',
        title="Portfolio Tree Map - Individual Holdings",
        color='Value',
        color_continuous_scale='Viridis',
        custom_data=['Name', 'Account_Number', 'Dividend_Status']
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>' +
                     'Name: %{customdata[0]}<br>' +
                     'Account: %{customdata[1]}<br>' +
                     'Value: $%{value:,.0f}<br>' +
                     'Dividend: %{customdata[2]}<br>' +
                     '<extra></extra>'
    )
    
    fig.update_layout(
        height=700,
        title_font_size=16
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Holdings", len(tree_df))
    
    with col2:
        rbc_count = len(tree_df[tree_df['Account_Type'] == 'RBC'])
        st.metric("RBC Holdings", rbc_count)
    
    with col3:
        benefits_count = len(tree_df[tree_df['Account_Type'] == 'Benefits'])
        st.metric("Benefits Accounts", benefits_count)
    
    with col4:
        dividend_count = len(tree_df[tree_df['Dividend_Status'] == 'Paying'])
        st.metric("Dividend Payers", dividend_count)

def create_dividend_summary(data):
    """Section 3: Dividend Summary"""
    st.header("💰 Dividend Summary")
    st.markdown("**Annual and quarterly dividend income analysis**")
    
    # Get dividend data
    holdings = data['holdings']
    dividend_holdings = [h for h in holdings if h.get('Indicated_Annual_Income', 0) > 0]
    
    if not dividend_holdings:
        st.info("No dividend data available.")
        return
    
    # Calculate totals
    total_annual = sum(h.get('Indicated_Annual_Income', 0) for h in dividend_holdings)
    total_quarterly = sum(h.get('Quarterly_Dividend', 0) for h in dividend_holdings)
    
    # Portfolio yield calculation
    total_portfolio_value = data['metadata']['total_portfolio_value_cad']
    portfolio_yield = (total_annual / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Annual Dividends", f"${total_annual:,.0f}")
    
    with col2:
        st.metric("Quarterly Dividends", f"${total_quarterly:,.0f}")
    
    with col3:
        st.metric("Dividend Payers", len(dividend_holdings))
    
    with col4:
        st.metric("Portfolio Yield", f"{portfolio_yield:.2f}%")
    
    with col5:
        avg_yield = sum(h.get('Indicated_Yield_on_Market', 0) * 100 for h in dividend_holdings) / len(dividend_holdings)
        st.metric("Avg Yield", f"{avg_yield:.2f}%")
    
    # Dividend visualization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create dividend bar chart
        dividend_df = pd.DataFrame(dividend_holdings)
        dividend_df = dividend_df.sort_values('Indicated_Annual_Income', ascending=False)
        
        fig = px.bar(
            dividend_df.head(15),  # Top 15 dividend payers
            x='Symbol',
            y='Indicated_Annual_Income',
            title="Top 15 Dividend Payers (Annual)",
            color='Indicated_Yield_on_Market',
            color_continuous_scale='Greens',
            text='Indicated_Yield_on_Market'
        )
        
        # Format the text on bars to show yield percentage
        fig.update_traces(
            texttemplate='%{text:.1%}',
            textposition='outside'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Symbol",
            yaxis_title="Annual Dividend (CAD)",
            showlegend=False
        )
        fig.update_coloraxes(colorbar_title="Yield %")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Dividend summary table
        st.subheader("Top Dividend Payers")
        top_dividends = dividend_df.head(10)[['Symbol', 'Name', 'Indicated_Annual_Income', 'Quarterly_Dividend', 'Indicated_Yield_on_Market']].copy()
        top_dividends['Indicated_Annual_Income'] = top_dividends['Indicated_Annual_Income'].apply(lambda x: f"${x:,.0f}")
        top_dividends['Quarterly_Dividend'] = top_dividends['Quarterly_Dividend'].apply(lambda x: f"${x:,.0f}")
        top_dividends['Indicated_Yield_on_Market'] = (top_dividends['Indicated_Yield_on_Market'] * 100).apply(lambda x: f"{x:.2f}%")
        top_dividends.columns = ['Symbol', 'Name', 'Annual', 'Quarterly', 'Yield']
        st.dataframe(top_dividends, use_container_width=True)
    
    # Detailed dividend table
    st.subheader("📊 Complete Dividend Details")
    
    dividend_details = dividend_df[['Symbol', 'Name', 'Account_Number', 'Sector', 'Quantity', 'Indicated_Annual_Income', 'Quarterly_Dividend', 'Indicated_Yield_on_Market', 'Market_Value_CAD']].copy()
    dividend_details['Indicated_Annual_Income'] = dividend_details['Indicated_Annual_Income'].apply(lambda x: f"${x:,.2f}")
    dividend_details['Quarterly_Dividend'] = dividend_details['Quarterly_Dividend'].apply(lambda x: f"${x:,.2f}")
    dividend_details['Indicated_Yield_on_Market'] = (dividend_details['Indicated_Yield_on_Market'] * 100).apply(lambda x: f"{x:.2f}%")
    dividend_details['Market_Value_CAD'] = dividend_details['Market_Value_CAD'].apply(lambda x: f"${x:,.0f}")
    dividend_details['Quantity'] = dividend_details['Quantity'].apply(lambda x: f"{x:,.0f}")
    
    dividend_details.columns = ['Symbol', 'Name', 'Account', 'Sector', 'Quantity', 'Annual Dividend', 'Quarterly Dividend', 'Yield', 'Market Value']
    
    st.dataframe(dividend_details, use_container_width=True)

def create_detailed_holdings_table(data):
    """Section 4: Detailed Holdings Table"""
    st.header("📋 Complete Holdings Table")
    st.markdown("**Detailed view of all holdings with filtering capabilities**")
    
    # Create comprehensive holdings table
    holdings_data = []
    
    # Add RBC holdings
    for holding in data['holdings']:
        holdings_data.append({
            'Symbol': holding.get('Symbol', ''),
            'Name': holding.get('Name', ''),
            'Account_Number': holding.get('Account_Number', ''),
            'Sector': holding.get('Sector', ''),
            'Industry': holding.get('Industry', ''),
            'Region': holding.get('Issuer_Region', ''),
            'Currency': holding.get('Currency', ''),
            'Quantity': holding.get('Quantity', 0),
            'Last_Price': holding.get('Last_Price', 0),
            'Market_Value_CAD': holding.get('Market_Value_CAD', 0),
            'Annual_Dividend': holding.get('Indicated_Annual_Income', 0),
            'Dividend_Yield': holding.get('Indicated_Yield_on_Market', 0),
            'Account_Type': 'RBC'
        })
    
    # Add cash balances
    cash_balances = [acc for acc in data['cash_balances'] if acc.get('Account_Type') != 'Benefits']
    for cash in cash_balances:
        holdings_data.append({
            'Symbol': 'CASH',
            'Name': f"Cash - {cash['Currency']}",
            'Account_Number': cash.get('Account_Number', ''),
            'Sector': 'Cash',
            'Industry': 'Cash',
            'Region': 'Canada',
            'Currency': cash.get('Currency', ''),
            'Quantity': 1,
            'Last_Price': cash.get('Amount', 0),
            'Market_Value_CAD': cash.get('Amount_CAD', 0),
            'Annual_Dividend': 0,
            'Dividend_Yield': 0,
            'Account_Type': 'RBC'
        })
    
    # Add benefits accounts
    benefits_accounts = [acc for acc in data['cash_balances'] if acc.get('Account_Type') == 'Benefits']
    for acc in benefits_accounts:
        holdings_data.append({
            'Symbol': acc['Account_Name'].replace(' ', '_'),
            'Name': acc['Account_Name'],
            'Account_Number': acc.get('Account_Number', ''),
            'Sector': 'Benefits',
            'Industry': 'Benefits',
            'Region': 'Canada',
            'Currency': 'CAD',
            'Quantity': 1,
            'Last_Price': acc.get('Amount', 0),
            'Market_Value_CAD': acc.get('Amount_CAD', 0),
            'Annual_Dividend': 0,
            'Dividend_Yield': 0,
            'Account_Type': 'Benefits'
        })
    
    holdings_df = pd.DataFrame(holdings_data)
    
    # Filters
    st.subheader("🔍 Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        account_types = ['All'] + sorted(holdings_df['Account_Type'].unique().tolist())
        selected_account_type = st.selectbox("Account Type", account_types)
    
    with col2:
        sectors = ['All'] + sorted(holdings_df['Sector'].unique().tolist())
        selected_sector = st.selectbox("Sector", sectors)
    
    with col3:
        industries = ['All'] + sorted(holdings_df['Industry'].unique().tolist())
        selected_industry = st.selectbox("Industry", industries)
    
    with col4:
        currencies = ['All'] + sorted(holdings_df['Currency'].unique().tolist())
        selected_currency = st.selectbox("Currency", currencies)
    
    # Apply filters
    filtered_df = holdings_df.copy()
    
    if selected_account_type != 'All':
        filtered_df = filtered_df[filtered_df['Account_Type'] == selected_account_type]
    
    if selected_sector != 'All':
        filtered_df = filtered_df[filtered_df['Sector'] == selected_sector]
    
    if selected_industry != 'All':
        filtered_df = filtered_df[filtered_df['Industry'] == selected_industry]
    
    if selected_currency != 'All':
        filtered_df = filtered_df[filtered_df['Currency'] == selected_currency]
    
    # Format the display
    display_df = filtered_df.copy()
    display_df['Market_Value_CAD'] = display_df['Market_Value_CAD'].apply(lambda x: f"${x:,.2f}")
    display_df['Annual_Dividend'] = display_df['Annual_Dividend'].apply(lambda x: f"${x:,.2f}" if x > 0 else "N/A")
    display_df['Dividend_Yield'] = (display_df['Dividend_Yield'] * 100).apply(lambda x: f"{x:.2f}%" if x > 0 else "N/A")
    display_df['Last_Price'] = display_df['Last_Price'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
    display_df['Quantity'] = display_df['Quantity'].apply(lambda x: f"{x:,.0f}" if x > 0 else "N/A")
    
    # Remove Account_Type column for display
    display_df = display_df.drop('Account_Type', axis=1)
    
    st.dataframe(display_df, use_container_width=True)
    
    # Summary of filtered data
    if not filtered_df.empty:
        total_filtered_value = filtered_df['Market_Value_CAD'].sum()
        st.metric(f"Total Value ({len(filtered_df)} holdings)", f"${total_filtered_value:,.2f} CAD")

def main():
    st.set_page_config(
        page_title="Final Portfolio Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Final Portfolio Dashboard")
    st.markdown("**Complete portfolio analysis with RBC holdings and Benefits accounts**")
    
    # Load data
    data, filename = load_comprehensive_data()
    if not data:
        return
    
    st.sidebar.info(f"📁 Data Source: {filename}")
    
    # Display the four sections
    create_asset_class_overview(data)
    st.divider()
    
    create_tree_map(data)
    st.divider()
    
    create_dividend_summary(data)
    st.divider()
    
    create_detailed_holdings_table(data)

if __name__ == "__main__":
    main()
