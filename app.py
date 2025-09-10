import pandas as pd
import streamlit as st
import os
from datetime import datetime
import plotly.express as px
from src.core.data_manager import DataManager
import hashlib

# Force refresh for benefits integration - Updated Sept 4, 2025

# Set page config
st.set_page_config(
    page_title="RBC Portfolio Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stDataFrame {
        background: white;
    }
</style>
""", unsafe_allow_html=True)

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

@st.cache_data
def load_data(cache_buster=None):
    """Load the most recent JSON data file using DataManager."""
    dm = DataManager()
    
    # Find the latest data file
    latest_file = dm.get_latest_data_file()
    if not latest_file:
        st.error("No data files found! Please ensure JSON files are in the data/output directory.")
        return None, None, None
    
    # Load and process data
    df = dm.load_data(latest_file)
    if df is None:
        st.error("Failed to load data from file.")
        return None, None, None
    
    return df, latest_file, dm

def create_summary_metrics(df, dm):
    """Create summary metrics cards with portfolio breakdown."""
    if df is None or df.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_positions = len(df)
        st.metric("Total Positions", total_positions)
    
    with col2:
        # Use the correct total from financial summaries (includes cash)
        total_portfolio_value = dm.get_total_portfolio_value_from_summaries()
        st.metric("Total Portfolio Value", f"${total_portfolio_value:,.2f}")
        
        # Show breakdown
        holdings_value = df['Market Value'].sum() if 'Market Value' in df.columns else 0
        cash_value = total_portfolio_value - holdings_value
        st.caption(f"Holdings: ${holdings_value:,.2f} + Cash: ${cash_value:,.2f}")
    
    with col3:
        if 'Book Value' in df.columns:
            total_book_value = df['Book Value'].sum()
            st.metric("Total Book Value", f"${total_book_value:,.2f}")
    
    with col4:
        if 'Unrealized Gain/Loss' in df.columns:
            total_gain_loss = df['Unrealized Gain/Loss'].sum()
            color = "normal" if total_gain_loss >= 0 else "inverse"
            st.metric("Total Unrealized Gain/Loss", f"${total_gain_loss:,.2f}", delta_color=color)

def create_portfolio_charts(df, dm):
    """Create portfolio visualization charts."""
    if df is None or df.empty:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Asset Type' in df.columns and 'Market Value' in df.columns:
            # Asset type breakdown including cash
            asset_summary = df.groupby('Asset Type')['Market Value'].sum().reset_index()
            
            # Add cash from financial summaries
            total_portfolio_value = dm.get_total_portfolio_value_from_summaries()
            holdings_value = df['Market Value'].sum()
            cash_value = total_portfolio_value - holdings_value
            
            # Add cash as an asset type
            cash_row = pd.DataFrame({
                'Asset Type': ['Cash'],
                'Market Value': [cash_value]
            })
            asset_summary = pd.concat([asset_summary, cash_row], ignore_index=True)
            
            fig = px.pie(
                asset_summary, 
                values='Market Value', 
                names='Asset Type',
                title='Holdings by Asset Type (CAD)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # USD/CAD breakdown by account
        create_usd_cad_breakdown(dm)

def create_usd_cad_breakdown(dm):
    """Create USD/CAD breakdown table by account."""
    st.subheader("💱 USD/CAD Breakdown by Account")
    
    account_summaries = dm.get_account_summaries()
    
    breakdown_rows = []
    total_cad_original = 0
    total_usd_original = 0
    
    for account_num, summary in account_summaries.items():
        cad_total = 0
        usd_total = 0
        
        for currency_data in summary['currencies']:
            if currency_data['currency'] == 'CAD':
                cad_total += float(currency_data['total'].replace(',', ''))
            elif currency_data['currency'] == 'USD':
                usd_total += float(currency_data['total'].replace(',', ''))
        
        total_cad_original += cad_total
        total_usd_original += usd_total
        
        breakdown_rows.append({
            'Account': account_num,
            'CAD Amount': f"${cad_total:,.2f}",
            'USD Amount': f"${usd_total:,.2f}",
            'Total (CAD)': f"${summary['total_cad']:,.2f}"
        })
    
    # Calculate percentages
    total_portfolio = total_cad_original + (total_usd_original * 1.37825)  # Approximate USD to CAD
    
    for row in breakdown_rows:
        usd_amount = float(row['USD Amount'].replace('$', '').replace(',', ''))
        usd_cad_value = usd_amount * 1.37825 if usd_amount > 0 else 0
        total_account_value = float(row['Total (CAD)'].replace('$', '').replace(',', ''))
        
        if total_account_value > 0:
            usd_percentage = (usd_cad_value / total_account_value) * 100
            row['% USD'] = f"{usd_percentage:.1f}%"
        else:
            row['% USD'] = "0.0%"
    
    # Add total row
    total_usd_cad_value = total_usd_original * 1.37825
    overall_usd_percentage = (total_usd_cad_value / total_portfolio) * 100 if total_portfolio > 0 else 0
    
    breakdown_rows.append({
        'Account': 'TOTAL',
        'CAD Amount': f"${total_cad_original:,.2f}",
        'USD Amount': f"${total_usd_original:,.2f}",
        'Total (CAD)': f"${total_portfolio:,.2f}",
        '% USD': f"{overall_usd_percentage:.1f}%"
    })
    
    breakdown_df = pd.DataFrame(breakdown_rows)
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

def create_quarterly_dividend_schedule(df):
    """Create quarterly dividend schedule with upcoming dividends and top contributors."""
    
    if df is None or df.empty:
        st.warning("No dividend data available")
        return
    
    # Filter holdings with dividend data
    dividend_holdings = df[
        (df['Annual Dividend Amount $'].notna()) & 
        (df['Annual Dividend Amount $'] > 0)
    ].copy()
    
    if dividend_holdings.empty:
        st.warning("No dividend-paying holdings found")
        return
    
    # Calculate quarterly dividends (assuming annual dividends are paid quarterly)
    dividend_holdings['Quarterly Dividend'] = dividend_holdings['Annual Dividend Amount $'] / 4
    dividend_holdings['Total Quarterly Dividend'] = (
        dividend_holdings['Quarterly Dividend'] * dividend_holdings['Quantity']
    )
    
    # Group by symbol and sum up
    quarterly_summary = dividend_holdings.groupby(['Symbol', 'Description']).agg({
        'Total Quarterly Dividend': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    
    # Calculate total quarterly dividend
    total_quarterly = quarterly_summary['Total Quarterly Dividend'].sum()
    
    # Title with total quarterly dividend amount
    st.subheader(f"📅 Upcoming Quarterly Dividends: ${total_quarterly:,.2f}")
    
    # All dividend contributors table
    st.write("**All Dividend Contributors:**")
    all_dividends = quarterly_summary.sort_values('Total Quarterly Dividend', ascending=False).copy()
    
    # Add expected payment date (assuming quarterly payments)
    all_dividends['Expected Payment'] = "Quarterly"
    
    # Format the quarterly amount
    all_dividends['Quarterly Amount'] = all_dividends['Total Quarterly Dividend'].apply(
        lambda x: f"${x:,.2f}"
    )
    
    # Display the table with requested columns
    display_columns = ['Symbol', 'Description', 'Quarterly Amount', 'Expected Payment']
    st.dataframe(
        all_dividends[display_columns], 
        use_container_width=True, 
        hide_index=True
    )

def create_account_summary_table(df, dm):
    """Create detailed account summary table."""
    if df is None or df.empty or 'Account' not in df.columns:
        return
    
    st.subheader("📋 Account Summary")
    
    # Get account summaries from financial data (includes cash)
    account_summaries = dm.get_account_summaries()
    
    # Create account summary with correct totals
    summary_rows = []
    for account_num, summary in account_summaries.items():
        # Get holdings count for this account
        holdings_count = len(df[df['Account'] == account_num])
        
        # Get book value and unrealized gain/loss from holdings
        account_holdings = df[df['Account'] == account_num]
        book_value = account_holdings['Book Value'].sum() if not account_holdings.empty and 'Book Value' in account_holdings.columns else 0
        gain_loss = account_holdings['Unrealized Gain/Loss'].sum() if not account_holdings.empty and 'Unrealized Gain/Loss' in account_holdings.columns else 0
        
        summary_rows.append({
            'Account Number': account_num,
            'Market Value (CAD)': f"${summary['total_cad']:,.2f}",
            'Book Value (CAD)': f"${book_value:,.2f}",
            'Unrealized Gain/Loss (CAD)': f"${gain_loss:,.2f}",
            'Number of Holdings': holdings_count
        })
    
    account_summary = pd.DataFrame(summary_rows)
    
    # Sort by market value
    account_summary['_sort_value'] = account_summary['Market Value (CAD)'].str.replace('$', '').str.replace(',', '').astype(float)
    account_summary = account_summary.sort_values('_sort_value', ascending=False)
    account_summary = account_summary.drop('_sort_value', axis=1)
    
    # Add total row using correct portfolio total
    total_portfolio_value = dm.get_total_portfolio_value_from_summaries()
    total_book_value = df['Book Value'].sum() if 'Book Value' in df.columns else 0
    total_gain_loss = df['Unrealized Gain/Loss'].sum() if 'Unrealized Gain/Loss' in df.columns else 0
    total_holdings = len(df)
    
    total_row = pd.DataFrame({
        'Account Number': ['TOTAL PORTFOLIO'],
        'Market Value (CAD)': [f"${total_portfolio_value:,.2f}"],
        'Book Value (CAD)': [f"${total_book_value:,.2f}"],
        'Unrealized Gain/Loss (CAD)': [f"${total_gain_loss:,.2f}"],
        'Number of Holdings': [total_holdings]
    })
    
    # Combine account summary and total
    final_summary = pd.concat([account_summary, total_row], ignore_index=True)
    
    st.dataframe(final_summary, use_container_width=True, hide_index=True)

def main():
    st.markdown('<h1 class="main-header">RBC Portfolio Dashboard</h1>', unsafe_allow_html=True)
    
    # Check password first
    if not check_password():
        st.stop()
    
    # Load data with cache buster based on file modification time
    dm = DataManager()
    latest_file = dm.get_latest_data_file()
    if latest_file and os.path.exists(latest_file):
        # Use file modification time as cache buster
        file_mtime = os.path.getmtime(latest_file)
        cache_buster = str(file_mtime)
    else:
        cache_buster = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    df, data_file, dm = load_data(cache_buster)
    
    if df is None:
        st.stop()
    
    # Show data source info
    if data_file:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"Data loaded from: {os.path.basename(data_file)}")
        with col2:
            if st.button("🔄 Refresh", help="Clear cache and reload latest data"):
                st.cache_data.clear()
                st.rerun()
    
    # Summary metrics
    st.subheader("📊 Portfolio Summary")
    create_summary_metrics(df, dm)
    
    # Charts
    st.subheader("📈 Portfolio Visualizations")
    create_portfolio_charts(df, dm)
    
    # Account summary table
    create_account_summary_table(df, dm)
    
    # Quarterly dividend schedule
    create_quarterly_dividend_schedule(df)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Account filter
    if 'Account' in df.columns:
        accounts = ['All'] + sorted(df['Account'].unique().tolist())
        selected_account = st.sidebar.selectbox("Select Account", accounts)
        
        filtered_df = df.copy()
        if selected_account != 'All':
            filtered_df = df[df['Account'] == selected_account]
    else:
        filtered_df = df.copy()
    
    # Asset type filter
    if 'Asset Type' in filtered_df.columns:
        asset_types = ['All'] + sorted(filtered_df['Asset Type'].unique().tolist())
        selected_asset_type = st.sidebar.selectbox("Select Asset Type", asset_types)
        
        if selected_asset_type != 'All':
            filtered_df = filtered_df[filtered_df['Asset Type'] == selected_asset_type]
    
    # Main data table
    st.subheader("📋 Holdings Details")
    
    # Format columns for better display
    if not filtered_df.empty:
        display_df = filtered_df.copy()
        
        # Format currency columns
        currency_columns = ['Market Value', 'Book Value', 'Unrealized Gain/Loss', 'Last Price']
        for col in currency_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")
        
        # Format percentage columns
        percentage_columns = ['Unrealized %', 'Change %']
        for col in percentage_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) and isinstance(x, (int, float)) else str(x) if x != 'N/A' else "")
        
        st.dataframe(display_df, use_container_width=True, height=600)
    else:
        st.warning("No data available for the selected filters.")
    
    # Download functionality
    st.subheader("💾 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download as CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"portfolio_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Download as JSON"):
            json_str = filtered_df.to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"portfolio_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()