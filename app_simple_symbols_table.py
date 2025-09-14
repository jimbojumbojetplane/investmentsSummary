#!/usr/bin/env python3
"""
Simple table view of enriched RBC symbol holdings - one row per holding
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="RBC Symbols Data Table",
    page_icon="📋",
    layout="wide"
)

def load_enriched_data():
    """Load the enriched RBC holdings data"""
    output_dir = Path('data/output')
    
    # Find the most recent enriched file (prioritize automated enriched files)
    automated_files = list(output_dir.glob('consolidated_holdings_RBC_only_automated_enriched_*.json'))
    enriched_files = list(output_dir.glob('consolidated_holdings_RBC_only_enriched_*.json'))
    
    # Use automated enriched files if available, otherwise fall back to regular enriched files
    if automated_files:
        enriched_files = automated_files
    
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
    
    return pd.DataFrame(holdings_data), metadata

def reorder_columns(df):
    """Reorder columns to show key identification and classification fields first"""
    
    # Priority columns in order
    priority_columns = [
        'Symbol', 'Name', 'Asset_Type', 'Sector', 'Industry', 
        'Issuer_Region', 'Listing_Country', 'Currency'
    ]
    
    # Get existing columns that match our priority list
    existing_priority = [col for col in priority_columns if col in df.columns]
    
    # Get remaining columns (excluding the priority ones)
    remaining_columns = [col for col in df.columns if col not in existing_priority]
    
    # Reorder: priority columns first, then remaining columns
    reordered_columns = existing_priority + remaining_columns
    
    return df[reordered_columns]

def format_dataframe(df):
    """Format the dataframe for better display"""
    display_df = df.copy()
    
    # Format numeric columns
    if 'Market_Value_CAD' in display_df.columns:
        display_df['Market_Value_CAD'] = display_df['Market_Value_CAD'].apply(lambda x: f"${x:,.2f}")
    
    if 'Weight_Total_Portfolio' in display_df.columns:
        display_df['Weight_Total_Portfolio'] = display_df['Weight_Total_Portfolio'].apply(lambda x: f"{x*100:.4f}%")
    
    if 'Indicated_Yield_on_Market' in display_df.columns:
        display_df['Indicated_Yield_on_Market'] = display_df['Indicated_Yield_on_Market'].apply(
            lambda x: f"{x*100:.4f}%" if pd.notna(x) and x > 0 else "N/A"
        )
    
    if 'Yield_on_Cost' in display_df.columns:
        display_df['Yield_on_Cost'] = display_df['Yield_on_Cost'].apply(
            lambda x: f"{x*100:.4f}%" if pd.notna(x) and x > 0 else "N/A"
        )
    
    if 'Market_Cap' in display_df.columns:
        display_df['Market_Cap'] = display_df['Market_Cap'].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) and x > 0 else "N/A"
        )
    
    if 'Employees' in display_df.columns:
        display_df['Employees'] = display_df['Employees'].apply(
            lambda x: f"{x:,.0f}" if pd.notna(x) and x > 0 else "N/A"
        )
    
    if 'Enrichment_Confidence' in display_df.columns:
        display_df['Enrichment_Confidence'] = display_df['Enrichment_Confidence'].apply(
            lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A"
        )
    
    # Format other numeric columns
    numeric_cols = ['Quantity', 'Last_Price', 'Book_Value', 'Book_Value_CAD', 'Market_Value', 
                   'Unrealized_Gain_Loss', 'Unrealized_Gain_Loss_Pct', 'Annual_Dividend']
    
    for col in numeric_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A"
            )
    
    return display_df

def main():
    st.title("📋 RBC Automated Enriched Symbols Data Table")
    st.markdown("Complete table view with automated ETF enrichment - one row per symbol")
    
    # Load data
    df, metadata = load_enriched_data()
    
    if df is None:
        st.stop()
    
    # Show basic info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Holdings", len(df))
    
    with col2:
        total_value = df['Market_Value_CAD'].sum()
        st.metric("Total Value", f"${total_value:,.2f}")
    
    with col3:
        st.metric("Fields per Row", len(df.columns))
    
    with col4:
        st.metric("Data File", metadata.get('original_file', 'Unknown')[:20] + "...")
    
    st.markdown("---")
    
    # Reorder columns to show key fields first
    df_reordered = reorder_columns(df)
    
    # Format the dataframe
    display_df = format_dataframe(df_reordered)
    
    # Show the complete table
    st.subheader("📊 Complete Holdings Data")
    st.markdown("**Key identification fields first: Symbol → Name → Asset Type → Sector → Industry → Region → Country**")
    
    # Display the table with reordered columns
    st.dataframe(
        display_df,
        use_container_width=True,
        height=800,
        hide_index=True
    )
    
    # Show column information
    st.markdown("---")
    st.subheader("📝 Column Information")
    
    col_info = []
    for col in df.columns:
        non_null_count = df[col].count()
        null_count = len(df) - non_null_count
        col_info.append({
            'Column': col,
            'Non-Null Values': non_null_count,
            'Null Values': null_count,
            'Data Type': str(df[col].dtype)
        })
    
    col_info_df = pd.DataFrame(col_info)
    st.dataframe(col_info_df, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Data Source:** {metadata.get('original_file', 'Unknown')}")
    st.markdown(f"**Last Updated:** {metadata.get('created_at', 'Unknown')}")
    st.markdown(f"**Enrichment Fields:** {metadata.get('enrichment_fields', 'Unknown')}")

if __name__ == "__main__":
    main()
