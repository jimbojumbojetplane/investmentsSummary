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
    
    # Try the new naming convention first
    data_files = list(output_dir.glob('consolidated_holdings_RBC_enriched_benefits_dividends_*.json'))
    if not data_files:
        # Fallback to old naming convention
        data_files = list(output_dir.glob('comprehensive_holdings_dividends_cad_corrected_*.json'))
    
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
    
    # 4. Copy main dashboard file as app.py for Streamlit Cloud
    if Path('app_final_portfolio_structure.py').exists():
        shutil.copy2('app_final_portfolio_structure.py', 'app.py')
        print("✅ Created app.py for Streamlit Cloud")
    
    # 5. Create requirements.txt
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
streamlit run app.py --server.port 8507
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
