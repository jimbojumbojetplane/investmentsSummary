# RBC Portfolio Dashboard

A comprehensive portfolio management dashboard that processes RBC investment account data and provides interactive visualizations.

## Features

- **Portfolio Overview**: Total portfolio value, account breakdown, and asset allocation
- **Currency Analysis**: USD/CAD exposure breakdown by account
- **Dividend Tracking**: Quarterly dividend schedule projection
- **Interactive Filtering**: Filter by account, asset type, and more
- **Secure Access**: Password-protected dashboard

## Live Dashboard

🔗 **Access the dashboard**: [Your Streamlit URL will appear here]

**Login credentials:**
- Password: `portfolio2024!`

## Data Processing

The dashboard processes:
- RBC account CSV exports
- Financial summaries with currency conversion
- Dividend information and projections
- Asset allocation and cash balances

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

## MCP Integration Requirements

For the MCP-based automation to work, you need:

1. **Cursor IDE** with MCP Browser extension
2. **RBC Direct Investing** logged in and active session
3. **MCP Browser Tools** connected and working

The MCP automation will:
- Generate a JavaScript script for Cursor to execute
- Use MCP browser tools to navigate and download files
- Automatically organize downloaded files into the project structure

## MCP Runbook

The complete MCP automation runbook is included in this project:
- **`RBC_HOLDINGS_DOWNLOAD_SCRIPT.md`** - Detailed instructions and JavaScript code for MCP automation
- Contains step-by-step instructions for downloading from all 6 RBC investment accounts
- Includes error recovery strategies and verification procedures

## Data Updates

### **Option 1: Two-Stage MCP Workflow (Recommended)**

The new two-stage workflow separates data collection from processing for better reliability:

#### **Stage 1: MCP Data Collection**
```bash
# Run Stage 1: Download RBC holdings files
python3 stage1_mcp_data_collection.py
```

**What Stage 1 does:**
- Generates MCP script for Cursor agent
- Downloads holdings CSV files from all RBC accounts
- Organizes files into `data/input/downloaded_files/`

#### **Stage 2: Data Processing**
```bash
# Run Stage 2: Process files and update dashboard
python3 stage2_data_processing.py
```

**What Stage 2 does:**
- Processes CSV files into JSON format
- Integrates Bell benefits data (optional)
- Combines all data sources
- Pushes updates to GitHub
- Updates the Streamlit dashboard

#### **Run Both Stages Together**
```bash
# Run complete two-stage workflow
python3 run_two_stage_workflow.py
```

#### **Benefits of Two-Stage Approach:**
- **🔄 Separation of Concerns** - Data collection separate from processing
- **🐛 Easier Debugging** - Can run stages independently to isolate issues
- **⚡ Faster Iteration** - Can re-run Stage 2 without re-downloading data
- **🛡️ Better Error Handling** - Each stage can fail independently
- **📊 Progress Tracking** - Clear visibility into which stage succeeded/failed

### **Option 2: Legacy Single-Stage Workflow**

The original single-stage workflow is still available:

```bash
# Run the complete MCP workflow (single stage)
python3 run_mcp_workflow.py
```

### **Option 3: Manual CSV Processing**

If you have CSV files already downloaded:

1. Place CSV files in `data/input/downloaded_files/`
2. Run Stage 2 only: `python3 stage2_data_processing.py`
3. Dashboard automatically uses the latest data

### **Option 4: Legacy Workflow (Fallback)**

The original workflow is still available as a fallback:

```bash
python3 run_complete_workflow.py
```

**Note:** This uses the updated MCP automation, not the old browser automation.

## Security

- Password protection via Streamlit secrets
- No sensitive data stored in repository
- Private deployment recommended

---

*This dashboard provides portfolio insights for personal use only. Investment data is processed locally and securely.*