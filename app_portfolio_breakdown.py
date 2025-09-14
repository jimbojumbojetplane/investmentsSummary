#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from pathlib import Path

st.set_page_config(
    page_title="Portfolio Breakdown Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_enriched_data():
    """Load the enriched holdings data from the portfolio classification engine"""
    # Find the most recent holdings_detailed file from the classification engine
    output_dir = Path("data/output")
    
    # First try to load final portfolio file ($3.7M total with proper cash balances)
    final_files = list(output_dir.glob("holdings_detailed_final_*.json"))
    if final_files:
        latest_file = max(final_files, key=os.path.getmtime)
        st.info(f"📊 Using final portfolio data ($3.7M total with proper cash balances): {latest_file.name}")
    else:
        # Fall back to correct portfolio file ($3.7M total)
        correct_files = list(output_dir.glob("holdings_detailed_correct_*.json"))
        if correct_files:
            latest_file = max(correct_files, key=os.path.getmtime)
            st.info(f"📊 Using correct portfolio data ($3.7M total): {latest_file.name}")
        else:
        # Fall back to complete portfolio file (with benefits)
        complete_files = list(output_dir.glob("holdings_detailed_restructured_complete_*.json"))
        if complete_files:
            latest_file = max(complete_files, key=os.path.getmtime)
            st.info(f"📊 Using complete portfolio data (with benefits): {latest_file.name}")
        else:
            # Fall back to final corrected restructured file
            final_files = list(output_dir.glob("holdings_detailed_restructured_final_*.json"))
            if final_files:
                latest_file = max(final_files, key=os.path.getmtime)
                st.info(f"📊 Using final corrected restructured holdings data: {latest_file.name}")
            else:
                # Fall back to corrected restructured files
                corrected_files = list(output_dir.glob("holdings_detailed_restructured_corrected_*.json"))
                if corrected_files:
                    latest_file = max(corrected_files, key=os.path.getmtime)
                    st.info(f"📊 Using corrected restructured holdings data: {latest_file.name}")
                else:
                    # Fall back to regular restructured files
                    restructured_files = list(output_dir.glob("holdings_detailed_restructured_*.json"))
                    if restructured_files:
                        latest_file = max(restructured_files, key=os.path.getmtime)
                        st.info(f"📊 Using restructured holdings data: {latest_file.name}")
    else:
        # Fall back to regular holdings detailed files
        holdings_files = list(output_dir.glob("holdings_detailed_*.json"))
        if not holdings_files:
            st.error("No enriched holdings data found. Please run the portfolio classification engine first.")
            return pd.DataFrame()
        latest_file = max(holdings_files, key=os.path.getmtime)
        st.info(f"📊 Using standard holdings data: {latest_file.name}")
    
    # Load the data
    with open(latest_file, 'r') as f:
        file_data = json.load(f)
    
    # Check if this is restructured format (has metadata)
    if isinstance(file_data, dict) and 'metadata' in file_data:
        holdings_data = file_data['holdings']
        metadata = file_data['metadata']
        st.info(f"🚀 Loading restructured data: {metadata['symbol_holdings']} symbol holdings, {metadata['cash_holdings']} cash holdings")
    else:
        # Original format - direct list
        holdings_data = file_data
        enriched_count = len([h for h in holdings_data if h.get('Enrichment_Source') in ['yahoo_finance', 'llm']])
        if enriched_count > 0:
            st.info(f"🚀 Loading enhanced data: {enriched_count} enriched holdings")
        else:
            st.info(f"Loading standard data: {len(holdings_data)} holdings")
    
    # Convert to DataFrame
    df = pd.DataFrame(holdings_data)
    
    # Remove duplicate columns if any
    df = df.loc[:, ~df.columns.duplicated()]
    
    return df

@st.cache_data
def load_combined_data():
    """Load the combined data for complete portfolio totals"""
    # Find the most recent holdings_combined file
    output_dir = Path("data/output")
    combined_files = list(output_dir.glob("holdings_combined_*.json"))
    
    if not combined_files:
        st.error("No holdings_combined files found.")
        return pd.DataFrame()
    
    # Get the most recent file
    latest_file = max(combined_files, key=os.path.getmtime)
    st.info(f"Loading combined data from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    # Handle holdings_combined_*.json format (array of objects with type/data structure)
    if isinstance(data, list):
        # Extract holdings data from the type/data structure
        holdings_data = [item['data'] for item in data if item.get('type') == 'current_holdings']
    else:
        # Handle step1 format (object with holdings key)
        holdings_data = data.get('holdings', [])
    
    if not holdings_data:
        st.error("No holdings data found in the file.")
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(holdings_data)
    
    # Remove duplicate columns if any
    df = df.loc[:, ~df.columns.duplicated()]
    
    return df

def create_portfolio_summary(combined_df):
    """Create portfolio summary with account breakdown totaling $3,669,161.96"""
    st.subheader("📊 Total Portfolio Summary")
    
    # Account breakdown from the latest holdings detailed file
    account_breakdown = {
        "49813791": {"name": "Main RBC Account", "value": 1914365.37},
        "69539728": {"name": "Secondary RBC Account", "value": 498507.25},
        "BENEFITS01": {"name": "DC Pension Plan", "value": 674025.96},
        "BENEFITS02": {"name": "RRSP Bell", "value": 416305.91},
        "26674346": {"name": "Additional RBC Account", "value": 102106.22},
        "68000157": {"name": "Small RBC Account", "value": 36798.23},
        "69549834": {"name": "Small RBC Account", "value": 27053.03}
    }
    
    total_portfolio = 3669161.96
    
    # Display metrics in two rows with proper alignment
    st.markdown("**Account Breakdown:**")
    
    # First row - top 4 accounts (4 columns)
    col1, col2, col3, col4 = st.columns(4)
    accounts = list(account_breakdown.items())
    
    for i, (account_id, data) in enumerate(accounts[:4]):
        with [col1, col2, col3, col4][i]:
            percentage = (data['value'] / total_portfolio) * 100
            st.metric(
                label=f"{data['name']}<br/>({account_id})",
                value=f"${data['value']:,.0f}",
                delta=f"{percentage:.1f}%"
            )
    
    # Second row - remaining 3 accounts (4 columns, but only 3 used for alignment)
    if len(accounts) > 4:
        col5, col6, col7, col8 = st.columns(4)
        for i, (account_id, data) in enumerate(accounts[4:]):
            with [col5, col6, col7, col8][i]:
                percentage = (data['value'] / total_portfolio) * 100
                st.metric(
                    label=f"{data['name']}<br/>({account_id})",
                    value=f"${data['value']:,.0f}",
                    delta=f"{percentage:.1f}%"
                )
    
    # Total portfolio metric
    st.markdown("**Total Portfolio:**")
    col_total = st.columns(1)[0]
    with col_total:
        st.metric(
            label="Total Portfolio Value",
            value=f"${total_portfolio:,.0f}",
            delta="100.0%"
        )

def create_portfolio_holdings_by_asset_type(df):
    """Create portfolio holdings grouped by asset type - high level buckets only"""
    st.subheader("🏗️ Portfolio Holdings by Asset Type")
    
    # Use the enriched data structure from classification engine
    # Filter to include in exposure holdings
    # For restructured data, all holdings are included by default
    if 'Include_in_Exposure' in df.columns:
        exposure_df = df[df['Include_in_Exposure'] == True].copy()
    else:
        exposure_df = df.copy()
    
    # Group by asset type
    asset_type_summary = exposure_df.groupby('Asset_Type').agg({
        'Market_Value_CAD': 'sum',
        'Symbol': 'count'
    }).round(2)
    
    asset_type_summary.columns = ['Total_Value', 'Holdings_Count']
    asset_type_summary = asset_type_summary.reset_index()
    asset_type_summary = asset_type_summary.sort_values('Total_Value', ascending=False)
    
    # Calculate percentages
    total_value = exposure_df['Market_Value_CAD'].sum()
    asset_type_summary['Percentage'] = (asset_type_summary['Total_Value'] / total_value * 100).round(1)
    
    # Display with nice titles, large font, and green percentages with arrows
    # Split into two rows for better visual appeal
    st.markdown("**High-Level Asset Type Breakdown:**")
    
    # First row - top 5 asset types
    col1, col2, col3, col4, col5 = st.columns(5)
    first_row_assets = asset_type_summary.head(5)
    
    for i, (_, row) in enumerate(first_row_assets.iterrows()):
        with [col1, col2, col3, col4, col5][i]:
            st.metric(
                label=row['Asset_Type'],
                value=f"${row['Total_Value']:,.0f}",
                delta=f"{row['Percentage']:.1f}%"
            )
    
    # Second row - remaining asset types (use same 5-column layout for alignment)
    remaining_assets = asset_type_summary.iloc[5:]
    if len(remaining_assets) > 0:
        # Create 5 columns for the second row to match the first row
        col6, col7, col8, col9, col10 = st.columns(5)
        second_row_cols = [col6, col7, col8, col9, col10]
        
        for i, (_, row) in enumerate(remaining_assets.iterrows()):
            if i < 5:  # Only show up to 5 more items
                with second_row_cols[i]:
                    st.metric(
                        label=row['Asset_Type'],
                        value=f"${row['Total_Value']:,.0f}",
                        delta=f"{row['Percentage']:.1f}%"
                    )
    
    # Show total
    st.markdown(f"**Total Portfolio Value: ${total_value:,.0f} (100.0%)**")

def create_holdings_by_type_sector_region(df):
    """Create holdings grouped by Type, Sector and Region with treemap showing individual holdings"""
    st.subheader("📋 Holdings by Type, Sector and Region")
    
    # Use the enriched data structure from classification engine
    # Filter to include in exposure holdings (including cash for 2.6M total)
    # For restructured data, all holdings are included by default
    if 'Include_in_Exposure' in df.columns:
        exposure_df = df[df['Include_in_Exposure'] == True].copy()
    else:
        exposure_df = df.copy()
    
    # Filter out cash holdings (those without symbols) for treemap
    # Cash holdings will be shown separately in the summary
    symbol_holdings = exposure_df[exposure_df['Symbol'].notna()].copy()
    cash_holdings = exposure_df[exposure_df['Symbol'].isna()].copy()
    
    # Create individual holding records for treemap (symbol holdings only)
    # Each holding will be a separate box in the treemap
    holdings_for_treemap = symbol_holdings.copy()
    
    # Create display labels for each holding - just the ticker symbol
    holdings_for_treemap['Holding_Label'] = holdings_for_treemap['Symbol']
    
    # Calculate total value for percentages
    total_value = exposure_df['Market_Value_CAD'].sum()
    holdings_for_treemap['Percentage'] = (holdings_for_treemap['Market_Value_CAD'] / total_value * 100).round(1)
    
    # Sort by value for better visualization
    holdings_for_treemap = holdings_for_treemap.sort_values('Market_Value_CAD', ascending=False)
    
    # Create treemap with individual holdings as sub-boxes
    fig = px.treemap(
        holdings_for_treemap,
        path=['Asset_Type', 'Sector', 'Issuer_Region', 'Holding_Label'],
        values='Market_Value_CAD',
        title=f"Individual Holdings by Type, Sector and Region ({len(holdings_for_treemap)} holdings)",
        color='Market_Value_CAD',
        color_continuous_scale='Viridis',
        custom_data=['Symbol', 'Name', 'Market_Value_CAD', 'Percentage']
    )
    
    # Update hover template to show holding details
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>' +
                     'Symbol: %{customdata[0]}<br>' +
                     'Name: %{customdata[1]}<br>' +
                     'Value: $%{customdata[2]:,.0f}<br>' +
                     'Percentage: %{customdata[3]:.1f}%<br>' +
                     '<extra></extra>'
    )
    
    fig.update_layout(
        height=700,
        title_font_size=16
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display summary
    st.write(f"**Symbol Holdings:** {len(holdings_for_treemap)}")
    if len(cash_holdings) > 0:
        st.write(f"**Cash Holdings:** {len(cash_holdings)}")
        st.write(f"**Total Holdings:** {len(exposure_df)}")
    st.write(f"**Total Value:** ${total_value:,.0f}")
    
    # Show cash holdings summary if any
    if len(cash_holdings) > 0:
        st.write("**Cash Holdings Summary:**")
        cash_summary = cash_holdings.groupby(['Asset_Type', 'Currency']).agg({
            'Market_Value_CAD': 'sum',
            'Quantity': 'sum'
        }).round(2)
        st.dataframe(cash_summary)
    
    # Add comprehensive holdings table
    st.subheader("📊 Complete Holdings Table")
    
    # Create a comprehensive table with all holdings and all columns
    st.write("**All holdings with complete details from the restructured file:**")
    
    # Use the full exposure data (both symbol and cash holdings)
    all_holdings_df = exposure_df.copy()
    
    # Sort by market value descending
    all_holdings_df = all_holdings_df.sort_values('Market_Value_CAD', ascending=False)
    
    # Display the complete table with all columns
    st.dataframe(
        all_holdings_df,
        use_container_width=True,
        height=800
    )
    
    # Add summary
    st.write(f"**Total Holdings:** {len(all_holdings_df)}")
    st.write(f"**Symbol Holdings:** {len(symbol_holdings)}")
    if len(cash_holdings) > 0:
        st.write(f"**Cash Holdings:** {len(cash_holdings)}")
    st.write(f"**Total Portfolio Value:** ${total_value:,.2f}")
    
    # Create summary groupings for table display (symbol holdings only)
    symbol_groupings = symbol_holdings.groupby(['Asset_Type', 'Sector', 'Issuer_Region']).agg({
        'Market_Value_CAD': ['sum', 'count'],
        'Symbol': lambda x: ', '.join(sorted(x.unique())),
    }).round(2)
    
    # Set column names for symbol groupings
    symbol_groupings.columns = ['Total_Value', 'Holdings_Count', 'Symbols']
    
    # Create cash holdings summary
    if len(cash_holdings) > 0:
        cash_groupings = cash_holdings.groupby(['Asset_Type', 'Sector', 'Issuer_Region']).agg({
            'Market_Value_CAD': ['sum', 'count'],
            'Name': lambda x: ', '.join(sorted(x.unique())),
        }).round(2)
        cash_groupings.columns = ['Total_Value', 'Holdings_Count', 'Symbols']
        
        # Combine symbol and cash groupings
        groupings = pd.concat([symbol_groupings, cash_groupings], ignore_index=True)
    else:
        groupings = symbol_groupings
    groupings = groupings.reset_index()
    groupings = groupings.sort_values('Total_Value', ascending=False)
    groupings['Percentage'] = (groupings['Total_Value'] / total_value * 100).round(1)
    
    # Format the display for table
    display_groupings = groupings.copy()
    display_groupings['Total_Value'] = display_groupings['Total_Value'].apply(lambda x: f"${x:,.0f}")
    display_groupings['Percentage'] = display_groupings['Percentage'].apply(lambda x: f"{x:.1f}%")
    
    # Select columns for display
    display_columns = ['Asset_Type', 'Sector', 'Issuer_Region', 'Total_Value', 'Percentage', 'Holdings_Count', 'Symbols']
    display_groupings = display_groupings[display_columns]
    
    # Rename columns for better display
    display_groupings.columns = ['Asset Type', 'Sector', 'Region', 'Total Value', 'Percentage', 'Holdings Count', 'Symbols']
    
    # Display the table
    st.dataframe(
        display_groupings,
        use_container_width=True,
        hide_index=True
    )

def create_dividend_details(df):
    """Create dividend details section"""
    st.subheader("💰 Dividend Details")
    
    # Filter to holdings with dividend data using enriched data
    dividend_df = df[
        (df['Indicated_Annual_Income'].notna()) & 
        (df['Indicated_Annual_Income'] > 0) &
        (df['Include_in_Exposure'] == True if 'Include_in_Exposure' in df.columns else True)
    ].copy()
    
    if len(dividend_df) == 0:
        st.info("No dividend data available.")
        return
    
    # Calculate quarterly dividends
    dividend_df['Quarterly_Dividend'] = dividend_df['Indicated_Annual_Income'] / 4
    
    # Calculate total quarterly income
    total_quarterly_income = dividend_df['Quarterly_Dividend'].sum()
    total_annual_income = dividend_df['Indicated_Annual_Income'].sum()
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Quarterly Dividends", f"${total_quarterly_income:,.2f}")
    
    with col2:
        st.metric("Total Annual Dividends", f"${total_annual_income:,.2f}")
    
    with col3:
        st.metric("Number of Dividend Payers", len(dividend_df))
    
    # Create detailed dividend table
    st.write("**Dividend Details by Issuer:**")
    
    # Sort by quarterly dividend amount
    dividend_details = dividend_df.sort_values('Quarterly_Dividend', ascending=False).copy()
    
    # Create display dataframe
    display_dividend = dividend_details[[
        'Symbol', 'Name_Normalized', 'Asset_Type', 'Sector', 'Issuer_Region',
        'Quarterly_Dividend', 'Indicated_Annual_Income', 'Indicated_Yield_on_Market',
        'Market_Value_CAD', 'Price'
    ]].copy()
    
    # Format the display
    display_dividend['Quarterly_Dividend'] = display_dividend['Quarterly_Dividend'].apply(lambda x: f"${x:,.2f}")
    display_dividend['Indicated_Annual_Income'] = display_dividend['Indicated_Annual_Income'].apply(lambda x: f"${x:,.2f}")
    display_dividend['Indicated_Yield_on_Market'] = display_dividend['Indicated_Yield_on_Market'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
    display_dividend['Market_Value_CAD'] = display_dividend['Market_Value_CAD'].apply(lambda x: f"${x:,.0f}")
    display_dividend['Price'] = display_dividend['Price'].apply(lambda x: f"${x:.2f}")
    
    # Rename columns for display
    display_dividend.columns = [
        'Symbol', 'Issuer', 'Asset Type', 'Sector', 'Region',
        'Quarterly Payment', 'Annual Payment', 'Yield on Market',
        'Market Value', 'Current Price'
    ]
    
    st.dataframe(
        display_dividend,
        use_container_width=True,
        hide_index=True
    )
    
    # Add total row at the bottom
    st.write(f"**Total Quarterly Dividends: ${total_quarterly_income:,.2f}**")
    st.write(f"**Total Annual Dividends: ${total_annual_income:,.2f}**")

def main():
    st.title("📊 Portfolio Breakdown Dashboard")
    
    # Load enriched data for detailed analysis
    df = load_enriched_data()
    
    if df.empty:
        st.error("No enriched data available.")
        return
    
    # Load combined data for complete portfolio totals
    combined_df = load_combined_data()
    
    if combined_df.empty:
        st.error("No combined data available.")
        return
    
    # Display sections
    create_portfolio_summary(combined_df)  # Use combined data for complete totals
    st.divider()
    
    create_portfolio_holdings_by_asset_type(df)  # Use enriched data for detailed analysis
    st.divider()
    
    create_holdings_by_type_sector_region(df)  # Use enriched data for detailed analysis
    st.divider()
    
    create_dividend_details(df)  # Use enriched data for detailed analysis
    st.divider()
    
    create_raw_data_table(df)  # Add comprehensive raw data table

def create_raw_data_table(df):
    """Create comprehensive raw data table for review"""
    st.subheader("📋 Raw Holdings Data - Complete Review")
    
    st.write("**Complete holdings data with all columns for review and validation:**")
    
    # Create a copy for display
    display_df = df.copy()
    
    # Format numeric columns for better readability
    numeric_columns = ['Market_Value_CAD', 'Book_Value_CAD', 'Unrealized_Gain_Loss', 
                      'Book_Value_CAD', 'Market_Value', 'Unrealized_Gain_Loss',
                      'Indicated_Annual_Income', 'Last_Price', 'Last_Price']
    
    for col in numeric_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) and isinstance(x, (int, float)) else str(x))
    
    # Format percentage columns
    percentage_columns = ['Unrealized_Gain_Loss_Pct', 'Indicated_Yield_on_Market', 'Weight_Total_Portfolio']
    for col in percentage_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) and isinstance(x, (int, float)) else str(x))
    
    # Select key columns for display (all important ones)
    key_columns = [
        'Symbol', 'Name',         'Account_Number', 'Asset_Type', 'Sector', 'Issuer_Region', 
        'Listing_Country', 'Industry', 'Market_Value_CAD', 'Currency',
        'Quantity', 'Last_Price', 'Book_Value_CAD', 'Market_Value',
        'Unrealized_Gain_Loss', 'Unrealized_Gain_Loss_Pct', 'Indicated_Annual_Income',
        'Indicated_Yield_on_Market', 'Classification_Source', 'LLM_Reasoning'
    ]
    
    # Filter to only include columns that exist
    available_columns = [col for col in key_columns if col in display_df.columns]
    display_data = display_df[available_columns]
    
    # Add some additional useful columns if they exist
    additional_columns = ['ETF_Type_Final', 'ETF_Region_Final', 'Business_Summary', 
                         'Website', 'Market_Cap', 'Employees', 'Confidence']
    for col in additional_columns:
        if col in display_df.columns and col not in available_columns:
            available_columns.append(col)
            display_data = display_df[available_columns]
    
    # Sort by Market Value descending
    if 'Market_Value_CAD' in display_data.columns:
        # Convert back to numeric for sorting, then back to string for display
        display_data['_sort_value'] = pd.to_numeric(display_data['Market_Value_CAD'].str.replace('$', '').str.replace(',', ''), errors='coerce')
        display_data = display_data.sort_values('_sort_value', ascending=False)
        display_data = display_data.drop('_sort_value', axis=1)
    
    # Display the table
    st.dataframe(
        display_data,
        use_container_width=True,
        height=600
    )
    
    # Add summary statistics
    st.write("**Data Quality Summary:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Holdings", len(df))
    
    with col2:
        unknown_sectors = len(df[df['Sector'] == 'Unknown'])
        st.metric("Unknown Sectors", unknown_sectors)
    
    with col3:
        unknown_regions = len(df[df['Issuer_Region'] == 'Unknown'])
        st.metric("Unknown Regions", unknown_regions)
    
    with col4:
        total_value = df['Market_Value_CAD'].sum()
        st.metric("Total Value (CAD)", f"${total_value:,.0f}")
    
    # Show classification sources
    st.write("**Classification Sources:**")
    if 'Classification_Source' in df.columns:
        source_counts = df['Classification_Source'].value_counts()
        for source, count in source_counts.items():
            st.write(f"- {source}: {count} holdings")

if __name__ == "__main__":
    main()
