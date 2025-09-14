#!/usr/bin/env python3
"""
Simple dashboard to view enriched RBC symbol holdings data
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Enriched RBC Symbols Viewer",
    page_icon="📊",
    layout="wide"
)

def load_enriched_data():
    """Load the enriched RBC holdings data"""
    output_dir = Path('data/output')
    
    # Find the most recent enriched file
    enriched_files = list(output_dir.glob('consolidated_holdings_RBC_only_enriched_*.json'))
    
    if not enriched_files:
        st.error("No enriched RBC holdings files found!")
        return None
    
    latest_file = max(enriched_files, key=lambda f: f.stat().st_mtime)
    st.info(f"📊 Loading: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    holdings_data = data.get('holdings', [])
    metadata = data.get('metadata', {})
    
    st.success(f"✅ Loaded {len(holdings_data)} enriched holdings")
    st.info(f"📈 Enrichment fields: {metadata.get('enrichment_fields', 'Unknown')}")
    
    return pd.DataFrame(holdings_data), metadata

def create_portfolio_summary(df):
    """Create portfolio summary"""
    st.subheader("📊 Portfolio Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_value = df['Market_Value_CAD'].sum()
    total_holdings = len(df)
    
    with col1:
        st.metric("Total Value", f"${total_value:,.2f}")
    
    with col2:
        st.metric("Total Holdings", total_holdings)
    
    with col3:
        avg_weight = df['Weight_Total_Portfolio'].mean() * 100
        st.metric("Avg Weight", f"{avg_weight:.2f}%")
    
    with col4:
        avg_yield = df['Indicated_Yield_on_Market'].mean() * 100
        st.metric("Avg Yield", f"{avg_yield:.2f}%")

def create_asset_type_breakdown(df):
    """Create asset type breakdown"""
    st.subheader("🏗️ Asset Type Breakdown")
    
    asset_breakdown = df.groupby('Asset_Type').agg({
        'Market_Value_CAD': 'sum',
        'Weight_Total_Portfolio': 'sum',
        'Symbol': 'count'
    }).reset_index()
    
    asset_breakdown['Weight_Total_Portfolio'] = asset_breakdown['Weight_Total_Portfolio'] * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        fig = px.pie(asset_breakdown, 
                    values='Market_Value_CAD', 
                    names='Asset_Type',
                    title="Portfolio by Asset Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart
        fig = px.bar(asset_breakdown, 
                    x='Asset_Type', 
                    y='Market_Value_CAD',
                    title="Value by Asset Type")
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    st.subheader("Asset Type Summary")
    asset_breakdown_display = asset_breakdown.copy()
    asset_breakdown_display['Market_Value_CAD'] = asset_breakdown_display['Market_Value_CAD'].apply(lambda x: f"${x:,.2f}")
    asset_breakdown_display['Weight_Total_Portfolio'] = asset_breakdown_display['Weight_Total_Portfolio'].apply(lambda x: f"{x:.2f}%")
    asset_breakdown_display.columns = ['Asset Type', 'Value', 'Weight %', 'Count']
    
    st.dataframe(asset_breakdown_display, use_container_width=True)

def create_sector_breakdown(df):
    """Create sector breakdown"""
    st.subheader("🏭 Sector Breakdown")
    
    sector_breakdown = df.groupby('Sector').agg({
        'Market_Value_CAD': 'sum',
        'Weight_Total_Portfolio': 'sum',
        'Symbol': 'count'
    }).reset_index()
    
    sector_breakdown['Weight_Total_Portfolio'] = sector_breakdown['Weight_Total_Portfolio'] * 100
    sector_breakdown = sector_breakdown.sort_values('Market_Value_CAD', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Horizontal bar chart
        fig = px.bar(sector_breakdown.head(10), 
                    x='Market_Value_CAD', 
                    y='Sector',
                    orientation='h',
                    title="Top 10 Sectors by Value")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sector table
        st.subheader("Sector Details")
        sector_display = sector_breakdown.copy()
        sector_display['Market_Value_CAD'] = sector_display['Market_Value_CAD'].apply(lambda x: f"${x:,.2f}")
        sector_display['Weight_Total_Portfolio'] = sector_display['Weight_Total_Portfolio'].apply(lambda x: f"{x:.2f}%")
        sector_display.columns = ['Sector', 'Value', 'Weight %', 'Count']
        
        st.dataframe(sector_display.head(10), use_container_width=True)

def create_geographic_breakdown(df):
    """Create geographic breakdown"""
    st.subheader("🌍 Geographic Breakdown")
    
    geo_breakdown = df.groupby('Issuer_Region').agg({
        'Market_Value_CAD': 'sum',
        'Weight_Total_Portfolio': 'sum',
        'Symbol': 'count'
    }).reset_index()
    
    geo_breakdown['Weight_Total_Portfolio'] = geo_breakdown['Weight_Total_Portfolio'] * 100
    geo_breakdown = geo_breakdown.sort_values('Market_Value_CAD', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        fig = px.pie(geo_breakdown, 
                    values='Market_Value_CAD', 
                    names='Issuer_Region',
                    title="Portfolio by Region")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Geographic table
        st.subheader("Regional Details")
        geo_display = geo_breakdown.copy()
        geo_display['Market_Value_CAD'] = geo_display['Market_Value_CAD'].apply(lambda x: f"${x:,.2f}")
        geo_display['Weight_Total_Portfolio'] = geo_display['Weight_Total_Portfolio'].apply(lambda x: f"{x:.2f}%")
        geo_display.columns = ['Region', 'Value', 'Weight %', 'Count']
        
        st.dataframe(geo_display, use_container_width=True)

def create_holdings_table(df):
    """Create detailed holdings table"""
    st.subheader("📋 Detailed Holdings")
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        asset_types = ['All'] + list(df['Asset_Type'].unique())
        selected_asset_type = st.selectbox("Filter by Asset Type", asset_types)
    
    with col2:
        sectors = ['All'] + list(df['Sector'].unique())
        selected_sector = st.selectbox("Filter by Sector", sectors)
    
    with col3:
        regions = ['All'] + list(df['Issuer_Region'].unique())
        selected_region = st.selectbox("Filter by Region", regions)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_asset_type != 'All':
        filtered_df = filtered_df[filtered_df['Asset_Type'] == selected_asset_type]
    
    if selected_sector != 'All':
        filtered_df = filtered_df[filtered_df['Sector'] == selected_sector]
    
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['Issuer_Region'] == selected_region]
    
    st.info(f"Showing {len(filtered_df)} of {len(df)} holdings")
    
    # Display table
    display_df = filtered_df.copy()
    
    # Format numeric columns
    numeric_cols = ['Market_Value_CAD', 'Weight_Total_Portfolio', 'Indicated_Yield_on_Market']
    for col in numeric_cols:
        if col in display_df.columns:
            if col == 'Weight_Total_Portfolio':
                display_df[col] = display_df[col].apply(lambda x: f"{x*100:.2f}%")
            elif col == 'Indicated_Yield_on_Market':
                display_df[col] = display_df[col].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
            else:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")
    
    # Select columns to display
    display_columns = [
        'Symbol', 'Name', 'Asset_Type', 'Sector', 'Industry', 
        'Issuer_Region', 'Market_Value_CAD', 'Weight_Total_Portfolio',
        'Indicated_Yield_on_Market', 'Exchange', 'Market_Cap'
    ]
    
    available_columns = [col for col in display_columns if col in display_df.columns]
    display_df = display_df[available_columns]
    
    st.dataframe(display_df, use_container_width=True, height=600)

def create_enrichment_quality_analysis(df):
    """Create enrichment quality analysis"""
    st.subheader("🔍 Enrichment Quality Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Classification sources
        source_counts = df['Classification_Source'].value_counts()
        fig = px.pie(values=source_counts.values, 
                    names=source_counts.index,
                    title="Classification Sources")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Confidence levels
        confidence_ranges = pd.cut(df['Enrichment_Confidence'], 
                                 bins=[0, 0.6, 0.8, 0.9, 1.0], 
                                 labels=['<60%', '60-80%', '80-90%', '90-100%'])
        conf_counts = confidence_ranges.value_counts()
        
        fig = px.bar(x=conf_counts.index, 
                    y=conf_counts.values,
                    title="Enrichment Confidence Levels")
        st.plotly_chart(fig, use_container_width=True)
    
    # Quality summary
    st.subheader("Quality Summary")
    quality_summary = {
        'Total Holdings': len(df),
        'High Confidence (≥80%)': len(df[df['Enrichment_Confidence'] >= 0.8]),
        'Yahoo Finance Success': len(df[df['Classification_Source'] == 'yahoo_finance']),
        'Avg Confidence': f"{df['Enrichment_Confidence'].mean()*100:.1f}%"
    }
    
    for metric, value in quality_summary.items():
        st.metric(metric, value)

def main():
    st.title("📊 Enriched RBC Symbols Viewer")
    st.markdown("View and analyze enriched RBC holdings data with streamlined fields")
    
    # Load data
    df, metadata = load_enriched_data()
    
    if df is None:
        st.stop()
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Portfolio Summary", 
        "🏗️ Asset Types", 
        "🏭 Sectors", 
        "🌍 Geography",
        "📋 Holdings Table"
    ])
    
    with tab1:
        create_portfolio_summary(df)
        create_enrichment_quality_analysis(df)
    
    with tab2:
        create_asset_type_breakdown(df)
    
    with tab3:
        create_sector_breakdown(df)
    
    with tab4:
        create_geographic_breakdown(df)
    
    with tab5:
        create_holdings_table(df)
    
    # Footer
    st.markdown("---")
    st.markdown(f"📁 **Data Source:** {metadata.get('original_file', 'Unknown')}")
    st.markdown(f"🕒 **Last Updated:** {metadata.get('created_at', 'Unknown')}")
    st.markdown(f"🔧 **Enrichment Fields:** {metadata.get('enrichment_fields', 'Unknown')}")

if __name__ == "__main__":
    main()
