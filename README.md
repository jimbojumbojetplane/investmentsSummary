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

## Data Updates

To update the portfolio data:

1. Download new CSV files from RBC to `data/input/downloaded_files/`
2. Run the processing script: `python3 src/extractors/direct_csv_parser.py`
3. Dashboard automatically uses the latest data

## Security

- Password protection via Streamlit secrets
- No sensitive data stored in repository
- Private deployment recommended

---

*This dashboard provides portfolio insights for personal use only. Investment data is processed locally and securely.*