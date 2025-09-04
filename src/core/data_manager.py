import json
import os
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from pathlib import Path

class DataManager:
    """Manages data loading and processing for the RBC Holdings Dashboard."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent.parent
        self.data_dirs = [
            self.base_dir / "data" / "output",
            self.base_dir / "data",
            self.base_dir
        ]
        self.logger = logging.getLogger(__name__)
    
    def find_data_files(self) -> list:
        """Find all available JSON data files."""
        json_files = []
        for directory in self.data_dirs:
            if directory.exists():
                # Look for holdings files
                holdings_pattern = directory / "holdings_combined_*.json"
                json_files.extend(directory.glob("holdings_combined_*.json"))
        return [str(f) for f in json_files]
    
    def extract_date_from_filename(self, filename: str) -> datetime:
        """Extract date from filename."""
        basename = os.path.basename(filename)
        
        # Skip backup files with timestamp suffix
        if '_backup_' in basename:
            return datetime.min
        
        # Extract date part (before any additional suffixes)
        date_str = basename.split('_')[-1].split('.')[0]
        try:
            return datetime.strptime(date_str, '%d%m%Y')
        except ValueError:
            return datetime.min
    
    def get_latest_data_file(self) -> Optional[str]:
        """Get the path to the most recent data file."""
        files = self.find_data_files()
        if not files:
            return None
        return max(files, key=self.extract_date_from_filename)
    
    def load_data(self, file_path: str = None) -> Optional[pd.DataFrame]:
        """Load data from JSON file and return as DataFrame."""
        if file_path is None:
            file_path = self.get_latest_data_file()
        
        if not file_path or not os.path.exists(file_path):
            self.logger.error(f"Data file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Store raw data for financial summaries access
            self._raw_data = data
            
            # Extract exchange rates from financial summaries
            exchange_rates = {}
            holdings_data = []
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        if item.get('type') == 'financial_summary':
                            account = item['data']['Account #']
                            currency = item['data']['Currency']
                            rate = float(item['data']['Exchange Rate to CAD'])
                            exchange_rates[f"{account}_{currency}"] = rate
                        elif item.get('type') == 'current_holdings':
                            holdings_data.append(item.get('data', {}))
            else:
                # If it's already a simple list/dict format
                holdings_data = data
            
            if not holdings_data:
                self.logger.warning(f"No holdings data found in {file_path}")
                return None
            
            df = pd.DataFrame(holdings_data)
            
            # Convert USD holdings to CAD using exchange rates
            if not df.empty:
                df = self.convert_usd_to_cad(df, exchange_rates)
            
            return self.process_dataframe(df)
        
        except Exception as e:
            self.logger.error(f"Error loading data from {file_path}: {str(e)}")
            return None
    
    def convert_usd_to_cad(self, df: pd.DataFrame, exchange_rates: Dict[str, float]) -> pd.DataFrame:
        """Convert USD holdings to CAD using exchange rates from the file."""
        if df.empty:
            return df
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Track conversion for debugging
        conversions_made = 0
        total_usd_converted = 0
        
        # Convert USD holdings to CAD
        for index, row in df.iterrows():
            if row.get('Currency') == 'USD':
                account = row.get('Account #')
                rate_key = f"{account}_USD"
                
                if rate_key in exchange_rates:
                    rate = exchange_rates[rate_key]
                    conversions_made += 1
                    
                    # Convert monetary values to CAD
                    monetary_columns = [
                        'Total Book Cost', 'Total Market Value', 'Unrealized Gain/Loss $',
                        'Last Price', 'Average Cost', 'Annual Dividend Amount $'
                    ]
                    
                    for col in monetary_columns:
                        if col in df.columns and pd.notna(row[col]):
                            try:
                                # Convert to float if it's a string
                                value = float(row[col]) if isinstance(row[col], str) else row[col]
                                if value != 0:  # Only convert non-zero values
                                    original_value = value
                                    converted_value = value * rate
                                    df.at[index, col] = converted_value
                                    
                                    # Track total market value conversion
                                    if col == 'Total Market Value':
                                        total_usd_converted += converted_value
                                        
                            except (ValueError, TypeError):
                                # Skip conversion if value can't be converted to float
                                pass
                    
                    # Update currency to CAD
                    df.at[index, 'Currency'] = 'CAD'
                    
                    # Update change $ to CAD
                    if 'Change $' in df.columns and pd.notna(row['Change $']):
                        try:
                            change_value = float(row['Change $']) if isinstance(row['Change $'], str) else row['Change $']
                            df.at[index, 'Change $'] = change_value * rate
                        except (ValueError, TypeError):
                            pass
                else:
                    self.logger.warning(f"No exchange rate found for {rate_key}")
        
        self.logger.info(f"USD to CAD conversion: {conversions_made} holdings converted, total USD market value converted to CAD: ${total_usd_converted:,.2f}")
        return df
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process the DataFrame."""
        if df.empty:
            return df
        
        # Map column names to standard format
        column_mapping = {
            'Account #': 'Account',
            'Total Market Value': 'Market Value',
            'Total Book Cost': 'Book Value',
            'Unrealized Gain/Loss $': 'Unrealized Gain/Loss',
            'Unrealized Gain/Loss %': 'Unrealized %',
            'Product': 'Asset Type',
            'Name': 'Description'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Convert numeric columns
        numeric_columns = ['Quantity', 'Book Value', 'Market Value', 'Unrealized Gain/Loss', 'Last Price']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert percentage columns (remove % sign if present)
        percentage_columns = ['Unrealized %', 'Change %']
        for col in percentage_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.rstrip('%').astype(float, errors='ignore')
        
        # Fill NaN values
        if 'Market Value' in df.columns:
            df['Market Value'] = df['Market Value'].fillna(0)
        if 'Book Value' in df.columns:
            df['Book Value'] = df['Book Value'].fillna(0)
        if 'Unrealized Gain/Loss' in df.columns:
            df['Unrealized Gain/Loss'] = df['Unrealized Gain/Loss'].fillna(0)
        
        # Add calculated fields
        if 'Market Value' in df.columns and 'Book Value' in df.columns:
            df['Total Return %'] = ((df['Market Value'] - df['Book Value']) / df['Book Value'] * 100).round(2)
        
        return df
    
    def get_portfolio_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate portfolio summary statistics."""
        if df.empty:
            return {}
        
        summary = {
            'total_positions': len(df),
            'total_market_value': df['Market Value'].sum() if 'Market Value' in df.columns else 0,
            'total_book_value': df['Book Value'].sum() if 'Book Value' in df.columns else 0,
            'total_unrealized_gain_loss': df['Unrealized Gain/Loss'].sum() if 'Unrealized Gain/Loss' in df.columns else 0,
            'unique_accounts': df['Account'].nunique() if 'Account' in df.columns else 0,
            'unique_symbols': df['Symbol'].nunique() if 'Symbol' in df.columns else 0,
        }
        
        # Calculate overall return percentage
        if summary['total_book_value'] > 0:
            summary['overall_return_pct'] = (summary['total_unrealized_gain_loss'] / summary['total_book_value']) * 100
        else:
            summary['overall_return_pct'] = 0
        
        return summary
    
    def get_total_portfolio_value_from_summaries(self) -> float:
        """Get the correct total portfolio value from financial summaries (includes cash)."""
        if not hasattr(self, '_raw_data') or not self._raw_data:
            return 0.0
        
        total_value = 0.0
        for item in self._raw_data:
            if isinstance(item, dict) and item.get('type') == 'financial_summary':
                total_cad = item.get('data', {}).get('Total (CAD)', 0)
                if total_cad:
                    total_value += float(total_cad)
        
        return total_value
    
    def get_account_summaries(self) -> Dict[str, Dict]:
        """Get account-level financial summaries."""
        if not hasattr(self, '_raw_data') or not self._raw_data:
            return {}
        
        summaries = {}
        for item in self._raw_data:
            if isinstance(item, dict) and item.get('type') == 'financial_summary':
                account = item['data']['Account #']
                currency = item['data']['Currency']
                
                if account not in summaries:
                    summaries[account] = {'total_cad': 0, 'currencies': []}
                
                summaries[account]['currencies'].append({
                    'currency': currency,
                    'cash': item['data'].get('Cash', '0'),
                    'investments': item['data'].get('Investments', '0'),
                    'total': item['data'].get('Total', '0'),
                    'total_cad': float(item['data'].get('Total (CAD)', 0))
                })
                summaries[account]['total_cad'] += float(item['data'].get('Total (CAD)', 0))
        
        return summaries
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export DataFrame to CSV."""
        if filename is None:
            filename = f"holdings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.base_dir / filename
        df.to_csv(filepath, index=False)
        return str(filepath)
    
    def export_to_json(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export DataFrame to JSON."""
        if filename is None:
            filename = f"holdings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.base_dir / filename
        df.to_json(filepath, orient='records', indent=2)
        return str(filepath)