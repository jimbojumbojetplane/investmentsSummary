# RBC Portfolio Data Processing Pipeline

## Overview

This document describes the complete end-to-end data processing pipeline for converting raw RBC holdings CSV files into a comprehensive, enriched portfolio dashboard. The pipeline transforms unstructured CSV data into a sophisticated portfolio analysis system with automated enrichment, currency conversion, and interactive visualization.

## Table of Contents

1. [Data Sources](#data-sources)
2. [Pipeline Architecture](#pipeline-architecture)
3. [Stage 1: Raw Data Consolidation](#stage-1-raw-data-consolidation)
4. [Stage 2: Automated Enrichment](#stage-2-automated-enrichment)
5. [Stage 3: Benefits Integration](#stage-3-benefits-integration)
6. [Stage 4: Dividend Processing](#stage-4-dividend-processing)
7. [Stage 5: Dashboard Generation](#stage-5-dashboard-generation)
8. [File Naming Conventions](#file-naming-conventions)
9. [Key Data Transformations](#key-data-transformations)
10. [Error Handling & Validation](#error-handling--validation)

---

## Data Sources

### Input Files
- **Location**: `data/input/downloaded_files/`
- **Format**: CSV files with non-standard structure
- **Files**: 
  - `Holdings 26674346 September 10, 2025.csv`
  - `Holdings 49813791 September 10, 2025.csv`
  - `Holdings 68000157 September 10, 2025.csv`
  - `Holdings 69539728 September 10, 2025.csv`
  - `Holdings 69549834 September 10, 2025.csv`

### CSV Structure
Each CSV contains multiple sections:
```
"Holdings Export as of Sep 10, 2025 1:37:34 PM ET"
[Account Information Section]
[Cash Balances Section]
[Holdings Section]
[Summary Section]
```

---

## Pipeline Architecture

The pipeline consists of 6 sequential stages:

```
Raw CSVs → Consolidation → Enrichment → Benefits → Dividends → Local Dashboard → Cloud Deployment
    ↓           ↓            ↓           ↓          ↓            ↓              ↓
  Stage 1    Stage 2      Stage 3     Stage 4    Stage 5     Stage 6        Final
```

### Data Flow
```
Individual CSV Files
    ↓ (consolidate_rbc_holdings.py)
consolidated_holdings_RBC_YYYYMMDD_HHMMSS.json
    ↓ (update_holdings_with_automated_enrichment.py)
consolidated_holdings_RBC_enriched_YYYYMMDD_HHMMSS.json
    ↓ (create_comprehensive_holdings.py)
consolidated_holdings_RBC_enriched_benefits_YYYYMMDD_HHMMSS.json
    ↓ (fix_dividend_currency_conversion.py)
consolidated_holdings_RBC_enriched_benefits_dividends_YYYYMMDD_HHMMSS.json
    ↓ (app_final_portfolio_structure.py)
Local Dashboard (Streamlit)
    ↓ (deploy_to_github.py)
GitHub Repository → Streamlit Cloud Dashboard
```

---

## Stage 1: Raw Data Consolidation

**Script**: `consolidate_rbc_holdings.py`

### Purpose
Converts 5 individual RBC CSV files into a single, structured JSON file with standardized data format.

### Key Functions

#### `parse_rbc_csv(file_path)`
- **Input**: Individual CSV file path
- **Process**: 
  - Extracts account number from filename using regex
  - Parses holdings section (starts with "Product,Symbol,Name,Quantity")
  - Parses cash balances section (starts with "Cash Balances")
  - Handles quoted fields and multi-line entries
- **Output**: List of holdings, cash balances, account info

#### `consolidate_holdings()`
- **Process**:
  - Loads all 5 CSV files
  - Generates unique IDs for each holding
  - Standardizes field names and data types
  - Combines into single JSON structure
- **Output**: `consolidated_holdings_RBC_YYYYMMDD_HHMMSS.json`

### Data Structure Created
```json
{
  "metadata": {
    "created_at": "2025-09-13T14:34:47",
    "source_files": [...],
    "total_holdings": 150,
    "total_cash_balances": 5
  },
  "holdings": [
    {
      "id": "uuid-string",
      "Account_Number": "26674346",
      "Symbol": "AAPL",
      "Name": "Apple Inc",
      "Quantity": 100,
      "Last_Price": 175.43,
      "Market_Value_USD": 17543.00,
      "Market_Value_CAD": 23858.48,
      "Currency": "USD",
      "Unrealized_Gain_Loss_Pct": 5.2,
      "Annual_Dividend": 0.96
    }
  ],
  "cash_balances": [
    {
      "Cash_ID": "uuid-string",
      "Account_Number": "26674346",
      "Currency": "CAD",
      "Amount": 1500.00,
      "Account_Name": "RBC Direct Investing"
    }
  ]
}
```

### Key Transformations
- **Currency Conversion**: USD values converted to CAD using exchange rate
- **Unique IDs**: UUID generation for each holding and cash balance
- **Standardized Fields**: Consistent naming across all accounts
- **Data Validation**: Handles missing values and malformed entries

---

## Stage 2: Automated Enrichment

**Script**: `update_holdings_with_automated_enrichment.py`

### Purpose
Adds comprehensive sector, industry, region, and listing country information to holdings using multiple data sources and intelligent fallback strategies.

### Key Components

#### `AutomatedETFEnricher` Class
Located in `automated_etf_enrichment.py`

**Enrichment Strategies (in order of preference)**:
1. **Curated Database**: Pre-built database of 50+ known ETFs
2. **ETFdb.com Search**: Web scraping for ETF information
3. **Yahoo Finance**: Detailed financial data retrieval
4. **Alpha Vantage**: Alternative financial data source
5. **Name Parsing**: Intelligent extraction from ETF names
6. **Morningstar**: Final fallback for Canadian ETFs

#### Enrichment Process
```python
def enrich_holdings(holdings_data):
    enricher = AutomatedETFEnricher()
    enriched_holdings = []
    
    for holding in holdings_data:
        # Try multiple strategies
        enriched_data = enricher.enrich_holding(holding)
        enriched_holdings.append(enriched_data)
    
    return enriched_holdings
```

### Fields Added
- `Sector`: Business sector classification
- `Industry`: Specific industry classification  
- `Region`: Geographic region (Canada, US, International, etc.)
- `Listing_Country`: Country of primary listing
- `Product_Type`: ETF, Stock, Bond, etc.
- `Enrichment_Source`: Which strategy provided the data

### Example Enrichment
```json
{
  "Symbol": "XIC",
  "Name": "iShares Core S&P/TSX Capped Composite Index ETF",
  "Sector": "Equity",
  "Industry": "Broad Market ETF", 
  "Region": "Canada",
  "Listing_Country": "Canada",
  "Product_Type": "ETF",
  "Enrichment_Source": "curated_database"
}
```

### Output
`consolidated_holdings_RBC_enriched_YYYYMMDD_HHMMSS.json`

---

## Stage 3: Benefits Integration

**Script**: `create_comprehensive_holdings.py`

### Purpose
Combines RBC holdings with benefits account data (DC Pension and RRSP) to create a complete portfolio view.

### Benefits Data Sources
- **DC Pension**: Defined Contribution pension plan (managed externally)
- **RRSP**: Registered Retirement Savings Plan (Bell RRSP managed externally)

### Benefits Data Extraction Process

#### Data Collection
Benefits data is collected through web scraping from online portals:
- **DC Pension Portal**: Automated extraction of pension account values
- **Bell RRSP Portal**: Automated extraction of RRSP account values
- **Data Format**: Structured JSON with account details and current values

#### Benefits Data Structure
```json
{
  "dc_pension_plan": {
    "account_name": "Defined Contribution Pension Plan",
    "current_value": "$674,025.96",
    "currency": "CAD",
    "last_updated": "2025-09-12T11:49:21"
  },
  "bell_rrsp": {
    "account_name": "Bell RRSP",
    "current_value": "$125,432.10", 
    "currency": "CAD",
    "last_updated": "2025-09-12T11:49:21"
  }
}
```

### Integration Process
```python
def create_comprehensive_holdings():
    # Load RBC holdings
    rbc_data = load_latest_enriched_holdings()
    
    # Load benefits data from web scraping results
    benefits_data = load_benefits_data()
    
    # Create benefits account entries in same format as RBC cash balances
    benefits_accounts = create_benefits_accounts(benefits_data)
    
    # Combine all data
    comprehensive_data = {
        "holdings": rbc_data["holdings"],
        "cash_balances": rbc_data["cash_balances"] + benefits_accounts,
        "metadata": {...}
    }
```

#### Benefits Account Creation
```python
def create_benefits_accounts(benefits_data):
    """Convert benefits data to cash balance format"""
    benefits_accounts = []
    
    # Parse currency amounts
    def parse_amount(amount_str):
        return float(amount_str.replace('$', '').replace(',', ''))
    
    # Create DC Pension account
    if 'dc_pension_plan' in benefits_data:
        dc_data = benefits_data['dc_pension_plan']
        benefits_accounts.append({
            "Cash_ID": str(uuid.uuid4()),
            "Account_Number": "DC_PENSION",
            "Account_Name": dc_data['account_name'],
            "Currency": "CAD",
            "Amount": parse_amount(dc_data['current_value']),
            "Account_Type": "DC_Pension"
        })
    
    # Create Bell RRSP account
    if 'bell_rrsp' in benefits_data:
        rrsp_data = benefits_data['bell_rrsp']
        benefits_accounts.append({
            "Cash_ID": str(uuid.uuid4()),
            "Account_Number": "BELL_RRSP",
            "Account_Name": rrsp_data['account_name'],
            "Currency": "CAD", 
            "Amount": parse_amount(rrsp_data['current_value']),
            "Account_Type": "RRSP"
        })
    
    return benefits_accounts
```

### Benefits Account Structure
```json
{
  "Cash_ID": "uuid-string",
  "Account_Number": "DC_PENSION",
  "Account_Name": "Defined Contribution Pension Plan",
  "Currency": "CAD",
  "Amount": 674025.96,
  "Account_Type": "DC_Pension"
}
```

### Output
`consolidated_holdings_RBC_enriched_benefits_YYYYMMDD_HHMMSS.json`

---

## Stage 4: Dividend Processing

**Script**: `fix_dividend_currency_conversion.py`

### Purpose
Processes dividend information by converting USD dividends to CAD, calculating comprehensive dividend metrics, and ensuring all dividend data is properly formatted and converted.

### Key Functions

#### `fix_dividend_conversion()`
- **Input**: Comprehensive holdings file with ETF dividends
- **Process**: 
  - Identifies USD holdings with dividend information
  - Converts USD dividends to CAD using market value exchange rates
  - Stores original USD dividend amounts for reference
  - Calculates dividend yields and metrics
- **Output**: Enhanced holdings with proper dividend currency conversion

#### Dividend Processing Logic
```python
def process_dividends(holding):
    # Convert per-share dividend to total annual dividend
    Indicated_Annual_Income = Annual_Dividend * Quantity
    
    # Calculate quarterly dividend
    Quarterly_Dividend = Indicated_Annual_Income / 4
    
    # Calculate dividend yield
    Indicated_Yield_on_Market = Indicated_Annual_Income / Market_Value_CAD
    
    # Determine dividend status
    Dividend_Status = "Dividend Payer" if Annual_Dividend > 0 else "Non-Dividend"
    
    # Currency conversion for USD holdings
    if holding["Currency"] == "USD":
        # Store original USD amount
        holding["Original_Dividend_USD"] = usd_dividend
        # Convert to CAD using same rate as market value
        holding["Indicated_Annual_Income"] = usd_dividend * exchange_rate
```

#### ETF Dividend Estimation
The system includes estimated dividend yields for ETFs that don't report dividends in original CSVs:
```python
# Typical ETF yields by category
ETF_YIELDS = {
    "Dividend ETF": 0.035,      # 3.5%
    "Broad Market ETF": 0.020,  # 2.0%
    "Real Estate ETF": 0.040,   # 4.0%
    "Bond ETF": 0.030,          # 3.0%
}

# Calculate estimated annual dividend
Estimated_Annual_Dividend = Market_Value_CAD * ETF_YIELD
```

### Output
`consolidated_holdings_RBC_enriched_benefits_dividends_YYYYMMDD_HHMMSS.json`

---

## Stage 5: Local Dashboard Generation

**Script**: `app_final_portfolio_structure.py`

### Purpose
Creates an interactive Streamlit dashboard with comprehensive portfolio analysis and visualization. The same dashboard code works both locally and on Streamlit Cloud.

### Smart Data Loading
The dashboard automatically detects its environment and loads the appropriate data file:

```python
def load_comprehensive_data():
    # Check if we're running on Streamlit Cloud (look for cloud data file first)
    cloud_data_file = Path('data/consolidated_holdings_RBC_enriched_benefits_dividends_latest.json')
    if cloud_data_file.exists():
        # Running on Streamlit Cloud - use deployed data file
        return load_cloud_data(cloud_data_file)
    
    # Otherwise, load from local development directory
    return load_local_data()
```

**Local Environment**: Loads from `data/output/` directory with timestamped files
**Cloud Environment**: Loads from `data/` directory with `_latest.json` file

### Dashboard Sections

#### Section 1: Total Portfolio - All Accounts
- **Total Portfolio Value**: Large display of total value
- **Account Summary Table**: CAD/USD breakdown by account
- **Account Metrics**: Individual account values and holdings count

#### Section 2: Asset Class Overview  
- **Pie Chart**: Visual breakdown by asset class
- **Asset Class Table**: Detailed CAD/USD breakdown with percentages

#### Section 3: Detailed Holdings by Asset Class
- **Interactive Treemap**: Hierarchical visualization of holdings
- **Click Navigation**: Click holdings to filter detailed table
- **3-Level Structure**: Group → SubGroup → Individual Holding

#### Section 4: Dividends Summary
- **Total Annual Dividends**: Complete dividend income
- **USD/CAD Breakdown**: Currency conversion details
- **Dividend Payers Chart**: Visual breakdown by account

#### Section 5: Detailed Holdings Table
- **Comprehensive Table**: All holdings with full details
- **Advanced Filtering**: Group, SubGroup, Region filters
- **Treemap Integration**: Click treemap to filter table

#### Section 6: Individual Holding Detail View
- **Detailed Metrics**: Symbol, name, value, shares, dividend, yield, gain
- **Additional Information**: Account, sector, industry, currency
- **Placeholder Sections**: Future features (charts, news, analysis)

### Dashboard Navigation System

#### Session State Management
The dashboard uses Streamlit's `st.session_state` for navigation:

```python
# Session state variables
st.session_state.selected_holding = None  # Stores clicked holding data
st.session_state.treemap_filter = None    # Stores treemap navigation filter
```

#### Treemap Click Detection
```python
def handle_treemap_clicks(selected_data):
    if selected_data and 'selection' in selected_data:
        selected_points = selected_data['selection']['points']
        if selected_points:
            clicked_path = selected_points[0]['path']
            
            # Level 3 holding click (individual stock)
            if len(clicked_path) == 3:
                clicked_symbol = clicked_path[2]
                holding_data = find_holding_data(clicked_symbol)
                
                # Store in session state for detail view
                st.session_state.selected_holding = {
                    'symbol': holding_data['Symbol'],
                    'name': holding_data['Name'],
                    'value': holding_data['Market_Value_CAD'],
                    'shares': holding_data['Quantity'],
                    'dividend': holding_data['Indicated_Annual_Income'],
                    'yield': holding_data['Indicated_Yield_on_Market'],
                    'gain': holding_data['Unrealized_Gain_Loss_Pct'],
                    'account': holding_data['Account_Number'],
                    'sector': holding_data['Sector'],
                    'industry': holding_data['Industry'],
                    'currency': holding_data['Currency'],
                    'last_price': holding_data['Last_Price']
                }
                st.rerun()  # Trigger navigation to detail view
```

#### Navigation Flow
```
Main Dashboard
    ↓ (Click Level 3 treemap box)
Individual Holding Detail View
    ↓ (Click "← Back to Dashboard")
Main Dashboard (same state)
```

#### Detail View Implementation
```python
def create_holding_detail_view():
    if 'selected_holding' not in st.session_state:
        return False
    
    holding = st.session_state.selected_holding
    
    # Back button
    if st.button("← Back to Dashboard"):
        del st.session_state.selected_holding
        st.rerun()
    
    # Display holding details
    st.header(f"📊 {holding['symbol']} - {holding['name']}")
    # ... rest of detail view
```

#### Conditional Rendering
```python
def main():
    # Check if we should show holding detail view
    if create_holding_detail_view():
        return  # Exit early if showing detail view
    
    # Otherwise show main dashboard
    create_section_1_total_portfolio(data)
    create_section_2_asset_class_overview(data)
    # ... rest of dashboard
```

### Portfolio Classification Logic

#### `classify_holding(holding)` Function
```python
def classify_holding(holding):
    # Cash balances
    if 'Cash_ID' in holding:
        return 'Cash'
    
    # Specific symbol classifications
    if holding.get('Symbol') in ['MNY', 'HISU.U']:
        return 'Cash Alternatives'
    if holding.get('Symbol') == 'CDZ':
        return 'Dividend Focused Equity'
    
    # Sector-based classifications
    if holding.get('Sector') == 'Real Estate':
        return 'Real Estate'
    if holding.get('Product_Type') == 'Bond':
        return 'Fixed Income'
    
    # Default equity classification
    return 'Equity'
```

### Asset Class Buckets
1. **DC Pension**: Separate bucket for pension assets
2. **RRSP**: Separate bucket for RRSP assets  
3. **Equity**: All equity holdings (sector, regional, dividend, broad market)
4. **Fixed Income**: Bonds and bond ETFs
5. **Cash & Cash Equivalents**: Cash balances and money market funds
6. **Real Estate**: REITs and real estate ETFs

---

## Stage 6: GitHub and Streamlit Cloud Deployment

### Purpose
Deploy the local dashboard to GitHub and Streamlit Cloud for automated public access and sharing.

### Deployment Process

#### Step 6a: Prepare Files for GitHub
**Script**: `deploy_to_github.py`

```python
def prepare_for_github_deployment():
    """Prepare files for GitHub deployment"""
    
    # 1. Copy latest data file to GitHub data directory
    latest_data_file = get_latest_comprehensive_file()
    copy_to_github_data_dir(latest_data_file)
    
    # 2. Create requirements.txt for Streamlit Cloud
    create_requirements_file()
    
    # 3. Create .streamlit/config.toml for cloud configuration
    create_streamlit_config()
    
    # 4. Update README.md with deployment instructions
    update_readme_for_deployment()
    
    # 5. Commit and push to GitHub
    git_commit_and_push()
```

#### Step 6b: Streamlit Cloud Configuration
**Files Created**:

1. **`requirements.txt`**:
```
streamlit>=1.28.0
plotly>=5.15.0
pandas>=2.0.0
numpy>=1.24.0
```

2. **`.streamlit/config.toml`**:
```toml
[server]
port = 8501
headless = true

[browser]
gatherUsageStats = false
```

3. **`data/`** directory with latest comprehensive file:
```
data/
└── consolidated_holdings_RBC_enriched_benefits_dividends_latest.json
```

#### Step 6c: Automated Deployment Script
**Script**: `deploy_to_github.py`

```python
#!/usr/bin/env python3
"""
Deploy dashboard to GitHub for Streamlit Cloud hosting
"""

import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def deploy_to_github():
    """Deploy latest dashboard to GitHub"""
    
    print("🚀 Starting GitHub deployment process...")
    
    # 1. Find latest comprehensive data file
    output_dir = Path('data/output')
    data_files = list(output_dir.glob('consolidated_holdings_RBC_enriched_benefits_dividends_*.json'))
    if not data_files:
        raise FileNotFoundError("No comprehensive data files found!")
    
    latest_file = max(data_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Using data file: {latest_file.name}")
    
    # 2. Create GitHub data directory
    github_data_dir = Path('data')
    github_data_dir.mkdir(exist_ok=True)
    
    # 3. Copy latest data file as 'latest.json'
    dest_file = github_data_dir / 'consolidated_holdings_RBC_enriched_benefits_dividends_latest.json'
    shutil.copy2(latest_file, dest_file)
    print(f"✅ Copied data to: {dest_file}")
    
    # 4. Create requirements.txt
    requirements_content = """streamlit>=1.28.0
plotly>=5.15.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
yfinance>=0.2.18
"""
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)
    print("✅ Created requirements.txt")
    
    # 5. Create .streamlit directory and config
    streamlit_dir = Path('.streamlit')
    streamlit_dir.mkdir(exist_ok=True)
    
    config_content = """[server]
port = 8501
headless = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
"""
    with open(streamlit_dir / 'config.toml', 'w') as f:
        f.write(config_content)
    print("✅ Created .streamlit/config.toml")
    
    # 6. Update README.md
    update_readme()
    
    # 7. Git operations
    git_commit_and_push()

def update_readme():
    """Update README.md for deployment"""
    readme_content = """# RBC Portfolio Dashboard

Interactive portfolio analysis dashboard for RBC holdings.

## Live Dashboard
🚀 **[View Live Dashboard on Streamlit Cloud](https://your-app.streamlit.app)**

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run local dashboard
streamlit run app_final_portfolio_structure.py --server.port 8507
```

## Data Pipeline
See `RBC_PORTFOLIO_DATA_PIPELINE.md` for complete data processing pipeline.

## Features
- Total portfolio overview
- Asset class breakdown
- Interactive treemap visualization
- Dividend analysis
- Individual holding details
"""
    with open('README.md', 'w') as f:
        f.write(readme_content)

def git_commit_and_push():
    """Commit changes and push to GitHub"""
    try:
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Deploy dashboard - {timestamp}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push to GitHub
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("✅ Successfully pushed to GitHub")
        print("🌐 Dashboard will be available on Streamlit Cloud shortly")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        raise

if __name__ == "__main__":
    deploy_to_github()
```

### GitHub Repository Setup

#### Repository Structure
```
rbc-portfolio-dashboard/
├── app_final_portfolio_structure.py    # Main dashboard app
├── requirements.txt                     # Python dependencies
├── .streamlit/
│   └── config.toml                     # Streamlit configuration
├── data/
│   └── consolidated_holdings_RBC_enriched_benefits_dividends_latest.json
├── README.md                           # Project documentation
└── RBC_PORTFOLIO_DATA_PIPELINE.md     # Technical documentation
```

#### Streamlit Cloud Configuration
1. **Connect GitHub Repository**: Link your GitHub repo to Streamlit Cloud
2. **Set Main File Path**: `app_final_portfolio_structure.py`
3. **Configure Branch**: `main` (or your default branch)
4. **Set App URL**: Custom subdomain (e.g., `your-name-rbc-portfolio`)

### Deployment Commands

#### Manual Deployment
```bash
# Run deployment script
python3 deploy_to_github.py

# Or manual steps:
# 1. Copy latest data file
cp data/output/consolidated_holdings_RBC_enriched_benefits_dividends_*.json data/latest.json

# 2. Commit and push
git add .
git commit -m "Update dashboard data"
git push origin main
```

#### Automated Deployment
```bash
# Add to crontab for daily updates
0 9 * * * cd /path/to/rbc-portfolio && python3 deploy_to_github.py
```

### Streamlit Cloud Features
- **Identical to Local**: Cloud dashboard is exactly the same as local dashboard
- **Automatic Updates**: Dashboard updates when GitHub repo changes
- **Public Access**: Shareable URL for portfolio viewing
- **No Server Management**: Fully managed by Streamlit
- **Custom Domain**: Optional custom subdomain
- **Environment Variables**: Secure configuration management

### Output
- **GitHub Repository**: Updated with latest data and configuration
- **Streamlit Cloud URL**: `https://your-app.streamlit.app`
- **Public Dashboard**: Accessible worldwide with latest portfolio data

---

## File Naming Conventions

### Timestamp Format
All output files use format: `YYYYMMDD_HHMMSS`

### File Types
- `consolidated_holdings_RBC_*.json`: Stage 1 output
- `consolidated_holdings_RBC_enriched_*.json`: Stage 2 output
- `consolidated_holdings_RBC_enriched_benefits_*.json`: Stage 3 output
- `consolidated_holdings_RBC_enriched_benefits_dividends_*.json`: Stage 4 output (final)

### Dashboard Access
- **Local Dashboard**: `http://localhost:8507`
- **Cloud Dashboard**: `https://your-app.streamlit.app`
- **Local Command**: `streamlit run app_final_portfolio_structure.py --server.port 8507`

---

## Key Data Transformations

### Currency Conversion
```python
# USD to CAD conversion using exchange rate
market_value_cad = market_value_usd * exchange_rate
```

### Unique ID Generation
```python
import uuid
holding_id = str(uuid.uuid4())
```

### Data Standardization
```python
# Standardize field names
field_mapping = {
    'Product': 'Product_Type',
    'Symbol': 'Symbol', 
    'Name': 'Name',
    'Quantity': 'Quantity',
    'Last Price': 'Last_Price',
    'Market Value': 'Market_Value_USD'
}
```

### Portfolio Classification
```python
# Multi-level classification system
Group = classify_holding(holding)  # Top-level bucket
SubGroup = determine_subgroup(holding)  # Sector/type
Holding = holding['Symbol']  # Individual security
```

---

## Error Handling & Validation

### CSV Parsing Errors
- **Malformed Entries**: Skip and log problematic lines
- **Missing Sections**: Graceful handling of incomplete files
- **Encoding Issues**: UTF-8 encoding with fallback handling

### API Failures
- **Rate Limiting**: Built-in delays between API calls
- **Network Timeouts**: Retry logic with exponential backoff
- **Data Validation**: Verify API responses before use

### Data Validation
- **Required Fields**: Check for essential data presence
- **Data Types**: Validate numeric fields and currencies
- **Range Checks**: Ensure values are within reasonable bounds

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Usage throughout pipeline
logger.info(f"Processing {len(holdings)} holdings")
logger.warning(f"Missing data for symbol: {symbol}")
logger.error(f"Failed to enrich holding: {holding['Symbol']}")
```

---

## Usage Instructions

### Running the Complete Pipeline

1. **Place CSV files** in `data/input/downloaded_files/`

2. **Run consolidation**:
   ```bash
   python3 consolidate_rbc_holdings.py
   ```

3. **Run enrichment**:
   ```bash
   python3 update_holdings_with_automated_enrichment.py
   ```

4. **Create comprehensive file**:
   ```bash
   python3 create_comprehensive_holdings.py
   ```

5. **Process dividends and fix currency conversion**:
   ```bash
   python3 fix_dividend_currency_conversion.py
   ```

6. **Launch local dashboard**:
   ```bash
   streamlit run app_final_portfolio_structure.py --server.port 8507
   ```

7. **Deploy to GitHub and Streamlit Cloud**:
   ```bash
   python3 deploy_to_github.py
   ```

### File Dependencies
- Each stage requires the output of the previous stage
- Scripts automatically find the most recent input files
- Timestamps ensure proper file ordering

### Dashboard Features
- **Interactive Navigation**: Click treemap elements to filter data
- **Real-time Updates**: Local dashboard reloads when data files change
- **Cloud Synchronization**: Cloud dashboard updates when GitHub repo changes
- **Responsive Design**: Works on desktop and mobile devices
- **Export Capabilities**: Data can be exported for further analysis
- **Public Sharing**: Cloud dashboard provides shareable URL

---

## Technical Architecture

### Data Flow Diagram
```
CSV Files → JSON Consolidation → Enrichment → Benefits → Dividends → Dashboard
    ↓              ↓               ↓          ↓          ↓          ↓
Raw Data    Structured Data   Enhanced   Complete   Financial   Interactive
           with Cash Balances   Data     Portfolio   Data      Visualization
```

### Key Technologies
- **Python 3.12**: Core processing language
- **Pandas**: Data manipulation and analysis
- **Streamlit**: Interactive web dashboard
- **Plotly**: Advanced data visualization
- **Requests**: Web scraping and API calls
- **YFinance**: Financial data retrieval

### Performance Considerations
- **Caching**: API responses cached to avoid repeated calls
- **Parallel Processing**: Multiple API calls processed concurrently
- **Memory Management**: Large datasets processed in chunks
- **Error Recovery**: Robust error handling prevents pipeline failures

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. CSV Parsing Errors
**Problem**: `Error tokenizing data. C error: Expected 1 fields in line X, saw Y`
**Solution**: 
- RBC CSV files have non-standard structure with multiple sections
- Use the robust parser in `consolidate_rbc_holdings.py`
- Check for malformed entries and handle quoted fields properly

**Problem**: `No holdings section found`
**Solution**:
- Verify CSV file contains the expected header: `"Product,Symbol,Name,Quantity"`
- Check file encoding (should be UTF-8)
- Ensure file is not corrupted during download

#### 2. API Enrichment Failures
**Problem**: `Rate limit exceeded` or `Connection timeout`
**Solution**:
- Built-in delays between API calls (2-3 seconds)
- Retry logic with exponential backoff
- Fallback to alternative data sources (ETFdb, Morningstar)

**Problem**: `No enrichment data found for symbol`
**Solution**:
- Check if symbol exists in curated database
- Verify symbol format (no extra spaces or characters)
- Use name parsing as fallback strategy

#### 3. Currency Conversion Issues
**Problem**: `USD dividends not converted to CAD`
**Solution**:
- Run `fix_dividend_currency_conversion.py` after enrichment
- Verify exchange rates are properly applied
- Check that `Original_Dividend_USD` field is populated

**Problem**: `Market values don't match expected totals`
**Solution**:
- Verify exchange rates are current
- Check for missing holdings in consolidation
- Validate cash balance extraction

#### 4. Dashboard Display Issues
**Problem**: `StreamlitInvalidColumnSpecError`
**Solution**:
- Check `st.columns()` specifications - no zero values allowed
- Use `st.columns(3)` instead of `st.columns([1, 1, 1, 0])`

**Problem**: `KeyError: 'field_name' not in index`
**Solution**:
- Verify data file contains expected fields
- Check field name spelling and case sensitivity
- Run data validation scripts

**Problem**: Treemap not displaying holdings
**Solution**:
- Verify treemap data structure has required fields
- Check that `Holding_Data` is properly populated
- Ensure 3-level structure is maintained

#### 5. File Loading Issues
**Problem**: `No comprehensive holdings files found`
**Solution**:
- Verify files exist in `data/output/` directory
- Check file naming conventions match expected patterns
- Run earlier stages of pipeline if files missing

**Problem**: `Port 8507 is already in use`
**Solution**:
```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Or use different port
streamlit run app_final_portfolio_structure.py --server.port 8508
```

### Data Validation Scripts

#### Validate CSV Parsing
```bash
python3 consolidate_rbc_holdings.py
# Check output for parsing warnings and errors
```

#### Validate Enrichment
```bash
python3 analyze_enrichment_process.py
# Review enrichment statistics and missing data
```

#### Validate Currency Conversion
```bash
python3 analyze_dividend_currency_conversion.py
# Check USD dividend conversion accuracy
```

#### Validate Final Data
```bash
python3 analyze_comprehensive_holdings.py
# Verify total values and data completeness
```

### Performance Optimization

#### Large Dataset Handling
- Process holdings in batches for API enrichment
- Use caching for repeated API calls
- Monitor memory usage during consolidation

#### Dashboard Performance
- Limit treemap data to essential fields
- Use efficient filtering in detailed table
- Implement pagination for large datasets

### Logging and Debugging

#### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

#### Check Log Files
- `data/rbc_automation.log`: RBC data collection
- `data/processing.log`: Pipeline processing
- `data/benefits_extraction.log`: Benefits data collection

#### Common Debug Commands
```bash
# Check file timestamps
ls -la data/output/*.json

# Verify data structure
python3 -c "import json; data=json.load(open('data/output/latest_file.json')); print(len(data['holdings']))"

# Test dashboard loading
python3 -c "from app_final_portfolio_structure import load_comprehensive_data; print(load_comprehensive_data() is not None)"
```

### Recovery Procedures

#### Partial Pipeline Failure
1. Identify last successful stage output file
2. Resume from that stage with correct input file
3. Verify data integrity before proceeding

#### Complete Data Loss
1. Re-run CSV consolidation from raw files
2. Re-run enrichment process
3. Re-create comprehensive holdings
4. Verify all stages complete successfully

#### Dashboard Corruption
1. Restart Streamlit server
2. Clear browser cache
3. Verify data file is accessible
4. Check for JavaScript errors in browser console

---

This comprehensive pipeline transforms raw RBC holdings data into a sophisticated portfolio analysis system, providing automated enrichment, currency conversion, and interactive visualization capabilities. The modular design allows for easy maintenance and future enhancements while ensuring data accuracy and reliability throughout the entire process.
