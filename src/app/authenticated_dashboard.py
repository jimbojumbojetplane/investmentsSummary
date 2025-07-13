import pandas as pd
import streamlit as st
import os
import json
import hashlib
from datetime import datetime
import plotly.express as px
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="RBC Portfolio Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication configuration
USERS = {}

# Add User 1 (Admin) if environment variables are set
user1_name = os.getenv("USER1_USERNAME", "admin")
user1_hash = os.getenv("USER1_PASSWORD_HASH", "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9")  # default: admin123
if user1_name and user1_hash:
    USERS[user1_name] = user1_hash

# Add User 2 (Viewer) if environment variables are set  
user2_name = os.getenv("USER2_USERNAME")
user2_hash = os.getenv("USER2_PASSWORD_HASH")
if user2_name and user2_hash:
    USERS[user2_name] = user2_hash

def hash_password(password):
    """Hash password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(username, password):
    """Verify username and password"""
    # Debug info for Railway
    if os.getenv("ENVIRONMENT") == "development":
        st.write(f"Debug - USERS dict: {USERS}")
        st.write(f"Debug - Looking for username: {repr(username)}")
        st.write(f"Debug - Username in USERS: {username in USERS}")
        if username in USERS:
            generated_hash = hash_password(password)
            stored_hash = USERS[username]
            st.write(f"Debug - Generated hash: {generated_hash}")
            st.write(f"Debug - Stored hash: {stored_hash}")
            st.write(f"Debug - Hashes match: {generated_hash == stored_hash}")
    
    if username not in USERS:
        return False
    password_hash = hash_password(password)
    return USERS[username] == password_hash

def show_login_form():
    """Display login form"""
    st.markdown("""
    <style>
        .login-form {
            max-width: 400px;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 0.5rem;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
        }
        .login-header {
            text-align: center;
            color: #1f77b4;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-form">', unsafe_allow_html=True)
    st.markdown('<h2 class="login-header">🔐 RBC Portfolio Dashboard</h2>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if verify_password(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show demo credentials in development
    if os.getenv("ENVIRONMENT") == "development":
        st.info("Demo credentials: admin / admin123")

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get("authenticated", False)

def show_logout_button():
    """Show logout button in sidebar"""
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

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
    .data-status {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    .data-status.success {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .data-status.error {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .data-status.stale {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .user-info {
        background: #e3f2fd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class DashboardDataLoader:
    def __init__(self):
        # Look for data file in multiple locations for Railway deployment
        possible_paths = [
            Path("data/dashboard_data.json"),
            Path("./dashboard_data.json"),
            Path("/app/data/dashboard_data.json")
        ]
        
        self.definitive_file = None
        for path in possible_paths:
            if path.exists():
                self.definitive_file = path
                break
        
        self.data = None
        self.metadata = None
        
    def load_data(self):
        """Load data from the single definitive file"""
        if not self.definitive_file:
            return None, None, "No dashboard data file found. Data file should be uploaded to Railway."
        
        try:
            with open(self.definitive_file, 'r') as f:
                dashboard_data = json.load(f)
            
            self.metadata = dashboard_data.get("metadata", {})
            self.data = dashboard_data.get("data", [])
            
            return self.data, self.metadata, None
            
        except Exception as e:
            return None, None, f"Error loading dashboard data: {str(e)}"

    def get_data_status(self):
        """Determine data status and create status message"""
        if not self.metadata:
            return "error", "No metadata available"
        
        status = self.metadata.get("status", "unknown")
        
        if status == "error":
            error_msg = self.metadata.get("error_message", "Unknown error")
            last_attempt = self.metadata.get("last_update_attempt", "Unknown")
            last_success = self.metadata.get("last_successful_update")
            
            if last_success:
                return "error", f"Update failed: {error_msg}. Last successful update: {self.format_datetime(last_success)}"
            else:
                return "error", f"Update failed: {error_msg}. No previous successful data."
        
        elif status == "success":
            last_update = self.metadata.get("last_update")
            if last_update:
                update_time = datetime.fromisoformat(last_update)
                age_hours = (datetime.now() - update_time).total_seconds() / 3600
                
                if age_hours > 24:
                    return "stale", f"Data is {age_hours:.0f} hours old. Last updated: {self.format_datetime(last_update)}"
                else:
                    return "success", f"Data current as of: {self.format_datetime(last_update)}"
            else:
                return "success", "Data loaded successfully"
        
        else:
            return "error", f"Unknown status: {status}"

    def format_datetime(self, iso_string):
        """Format ISO datetime string for display"""
        try:
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return iso_string

@st.cache_data
def load_dashboard_data():
    """Load data with caching"""
    loader = DashboardDataLoader()
    return loader.load_data()

def show_data_status(metadata):
    """Show data status banner"""
    if not metadata:
        st.markdown('<div class="data-status error">❌ No data available</div>', 
                   unsafe_allow_html=True)
        return
    
    loader = DashboardDataLoader()
    loader.metadata = metadata
    status_type, status_message = loader.get_data_status()
    
    if status_type == "success":
        icon = "✅"
    elif status_type == "stale":
        icon = "⚠️"
    else:
        icon = "❌"
    
    st.markdown(f'<div class="data-status {status_type}">{icon} {status_message}</div>', 
               unsafe_allow_html=True)

def get_portfolio_summary_from_data(data):
    """Calculate portfolio summary from data structure"""
    if not data:
        return {}
    
    # Calculate totals from financial summaries
    total_market_value_cad = 0
    cad_original_value = 0
    usd_original_value = 0
    account_totals = {}
    
    # Get totals from financial summaries
    for item in data:
        if item.get('type') == 'financial_summary':
            summary_data = item.get('data', {})
            account_num = summary_data.get('Account #')
            total_cad = float(summary_data.get('Total (CAD)', 0))
            currency = summary_data.get('Currency', 'CAD')
            
            if account_num not in account_totals:
                account_totals[account_num] = 0
            account_totals[account_num] += total_cad
            
            # Track original currency values for percentage calculation
            if currency == 'CAD':
                cad_original_value += total_cad
            elif currency == 'USD':
                usd_original_value += total_cad
    
    # Sum up all accounts
    total_market_value_cad = sum(account_totals.values())
    
    # Calculate totals from holdings data
    total_positions = 0
    total_book_value = 0
    total_unrealized_gain_loss = 0
    
    for item in data:
        if item.get('type') == 'current_holdings':
            total_positions += 1
            holding_data = item.get('data', {})
            
            book_value = float(holding_data.get('Total Book Cost', 0))
            unrealized = float(holding_data.get('Unrealized Gain/Loss $', 0))
            currency = holding_data.get('Currency', 'CAD')
            
            # Convert to CAD if needed
            if currency == 'USD':
                book_value *= 1.36645
                unrealized *= 1.36645
            
            total_book_value += book_value
            total_unrealized_gain_loss += unrealized
    
    return {
        'total_positions': total_positions,
        'total_market_value': total_market_value_cad,
        'total_book_value': total_book_value,
        'total_unrealized_gain_loss': total_unrealized_gain_loss,
        'cad_percentage': (cad_original_value / total_market_value_cad * 100) if total_market_value_cad > 0 else 0,
        'usd_percentage': (usd_original_value / total_market_value_cad * 100) if total_market_value_cad > 0 else 0
    }

def create_summary_metrics(data, metadata):
    """Create summary metrics cards"""
    if not data:
        st.error("No holdings data available")
        return
    
    summary = get_portfolio_summary_from_data(data)
    
    # Find benefits data in the data structure
    benefits_summary = None
    dc_pension = None
    rrsp = None
    
    for item in data:
        if item.get('type') == 'current_holdings':
            holding_data = item.get('data', {})
            if holding_data.get('Product') == 'DC Pension Plan':
                dc_pension = holding_data.get('Total Market Value', 0)
            elif holding_data.get('Product') == 'RRSP':
                rrsp = holding_data.get('Total Market Value', 0)
            elif holding_data.get('Product') == 'Benefits Summary':
                benefits_summary = holding_data.get('Total Market Value', 0)
    
    # RBC Holdings Summary
    st.subheader("📊 RBC Holdings Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Positions", summary['total_positions'])
    
    with col2:
        st.metric("Total Market Value", f"${summary['total_market_value']:,.2f}")
    
    with col3:
        st.metric("Total Book Value", f"${summary['total_book_value']:,.2f}")
    
    with col4:
        color = "normal" if summary['total_unrealized_gain_loss'] >= 0 else "inverse"
        st.metric("Total Unrealized Gain/Loss", f"${summary['total_unrealized_gain_loss']:,.2f}", delta_color=color)
    
    # Currency breakdown
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🇨🇦 CAD Holdings: {summary['cad_percentage']:.1f}%**")
    with col2:
        st.markdown(f"**🇺🇸 USD Holdings: {summary['usd_percentage']:.1f}%**")
    
    # Benefits section
    if dc_pension or rrsp or benefits_summary:
        st.markdown("---")
        st.subheader("🏢 Benefits Portal Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if dc_pension:
                st.metric("DC Pension Plan", f"${dc_pension:,.2f}")
            else:
                st.metric("DC Pension Plan", "Not available")
        
        with col2:
            if rrsp:
                st.metric("RRSP", f"${rrsp:,.2f}")
            else:
                st.metric("RRSP", "Not available")
        
        with col3:
            benefits_date = metadata.get('benefits_extraction_date')
            if benefits_date:
                try:
                    date_obj = datetime.fromisoformat(benefits_date)
                    st.metric("Benefits Updated", date_obj.strftime("%m/%d/%Y"))
                except:
                    st.metric("Benefits Updated", "Unknown")
            else:
                st.metric("Benefits Updated", "Unknown")

def create_portfolio_charts(data):
    """Create portfolio visualization charts"""
    if not data:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Product type pie chart
        product_data = {}
        for item in data:
            if item.get('type') == 'current_holdings':
                holding_data = item.get('data', {})
                product_type = holding_data.get('Product', 'Unknown')
                market_value = float(holding_data.get('Total Market Value', 0))
                
                if product_type in product_data:
                    product_data[product_type] += market_value
                else:
                    product_data[product_type] = market_value
        
        if product_data:
            product_df = pd.DataFrame(list(product_data.items()), columns=['Product Type', 'Market Value'])
            fig = px.pie(
                product_df, 
                values='Market Value', 
                names='Product Type',
                title='Portfolio by Product Type'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Currency breakdown pie chart
        currency_data = {'CAD': 0, 'USD': 0}
        for item in data:
            if item.get('type') == 'current_holdings':
                holding_data = item.get('data', {})
                currency = holding_data.get('Currency', 'CAD')
                market_value = float(holding_data.get('Total Market Value', 0))
                
                if currency in currency_data:
                    currency_data[currency] += market_value
        
        if any(currency_data.values()):
            currency_df = pd.DataFrame(list(currency_data.items()), columns=['Currency', 'Market Value'])
            currency_df = currency_df[currency_df['Market Value'] > 0]
            
            if not currency_df.empty:
                fig = px.pie(
                    currency_df, 
                    values='Market Value', 
                    names='Currency',
                    title='Portfolio by Currency',
                    color_discrete_map={'CAD': '#FF6B6B', 'USD': '#4ECDC4'}
                )
                st.plotly_chart(fig, use_container_width=True)

def convert_to_dataframe(data):
    """Convert holdings data to DataFrame for display"""
    if not data:
        return pd.DataFrame()
    
    holdings_records = []
    for item in data:
        if item.get('type') == 'current_holdings':
            holdings_records.append(item['data'])
    
    if holdings_records:
        return pd.DataFrame(holdings_records)
    else:
        return pd.DataFrame()

def main():
    """Main dashboard application with authentication"""
    
    # Check authentication
    if not check_authentication():
        show_login_form()
        return
    
    # Show user info and logout in sidebar
    username = st.session_state.get("username", "Unknown")
    st.sidebar.markdown(f'<div class="user-info">👤 Logged in as: <strong>{username}</strong></div>', 
                       unsafe_allow_html=True)
    show_logout_button()
    
    # Main header
    st.markdown('<h1 class="main-header">RBC Portfolio Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    data, metadata, error = load_dashboard_data()
    
    # Show data status
    if error:
        st.markdown(f'<div class="data-status error">❌ {error}</div>', unsafe_allow_html=True)
        return
    
    show_data_status(metadata)
    
    # Manual refresh option
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()
    
    if not data:
        st.error("No data available.")
        return
    
    # Summary metrics
    st.subheader("📈 Portfolio Summary")
    create_summary_metrics(data, metadata)
    
    # Charts
    st.subheader("📊 Portfolio Visualizations") 
    create_portfolio_charts(data)
    
    # Convert to DataFrame for filtering and display
    df = convert_to_dataframe(data)
    
    if df.empty:
        st.warning("No holdings data found in the data file.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Account filter
    if 'Account #' in df.columns:
        accounts = ['All'] + sorted(df['Account #'].unique().tolist())
        selected_account = st.sidebar.selectbox("Select Account", accounts)
        
        if selected_account != 'All':
            df = df[df['Account #'] == selected_account]
    
    # Product filter
    if 'Product' in df.columns:
        products = ['All'] + sorted(df['Product'].unique().tolist())
        selected_product = st.sidebar.selectbox("Select Product Type", products)
        
        if selected_product != 'All':
            df = df[df['Product'] == selected_product]
    
    # Main data table
    st.subheader("📋 Holdings Details")
    
    if not df.empty:
        # Format display DataFrame
        display_df = df.copy()
        
        # Format currency columns
        currency_columns = ['Total Market Value', 'Total Book Cost', 'Unrealized Gain/Loss $']
        for col in currency_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda x: f"${float(x):,.2f}" if pd.notna(x) and str(x) != 'N/A' else str(x)
                )
        
        # Format percentage columns
        percentage_columns = ['Unrealized Gain/Loss %', 'Change %']
        for col in percentage_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda x: f"{float(x):.2f}%" if pd.notna(x) and str(x) != 'N/A' and str(x).replace('.','').replace('-','').isdigit() else str(x)
                )
        
        st.dataframe(display_df, use_container_width=True, height=600)
    
    # Export functionality
    st.subheader("💾 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download as CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"holdings_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Download as JSON"):
            json_str = df.to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"holdings_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    # Footer with metadata
    if metadata:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"**Data source:** {os.path.basename(metadata.get('data_source', 'Unknown'))}")
        with col2:
            st.caption(f"**Total entries:** {metadata.get('total_entries', 'Unknown')}")

if __name__ == "__main__":
    main()