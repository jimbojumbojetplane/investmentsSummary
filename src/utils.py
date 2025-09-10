import csv
import json
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union
from .config import config

logger = logging.getLogger(__name__)

def sanitize_filename(base_name: str = "") -> str:
    """Generate a sanitized filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if base_name:
        safe_name = "".join(c for c in base_name if c.isalnum() or c in ('-', '_')).rstrip()
        return f"{safe_name}_{timestamp}"
    return timestamp

def save_data(data: List[List[str]], filename: str, format: str = 'csv') -> str:
    """Save data to file in specified format."""
    try:
        file_path = config.data_input_dir / filename
        
        if format.lower() == 'csv':
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(data)
                
        elif format.lower() == 'json':
            if data and len(data) > 1:
                headers = data[0]
                json_data = []
                for row in data[1:]:
                    json_data.append(dict(zip(headers, row)))
                
                with open(file_path.with_suffix('.json'), 'w', encoding='utf-8') as jsonfile:
                    json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
                    
        elif format.lower() == 'excel':
            if data and len(data) > 1:
                headers = data[0]
                df = pd.DataFrame(data[1:], columns=headers)
                df.to_excel(file_path.with_suffix('.xlsx'), index=False)
            
        logger.info(f"Data saved to {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Failed to save data: {str(e)}")
        return ""

def setup_logging(log_level: str = 'INFO', log_file: str = None) -> None:
    """Setup logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file or 'rbc_automation.log')
        ]
    )

def validate_file_path(file_path: Union[str, Path]) -> bool:
    """Validate if file path exists and is readable."""
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False

def clean_text(text: str) -> str:
    """Clean and normalize text data."""
    if not text:
        return ""
    
    return text.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

def parse_currency(currency_str: str) -> float:
    """Parse currency string to float."""
    if not currency_str:
        return 0.0
    
    try:
        cleaned = currency_str.replace('$', '').replace(',', '').replace('(', '-').replace(')', '').strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0

def format_account_data(raw_data: List[Dict]) -> List[Dict]:
    """Format and clean account data."""
    formatted_data = []
    
    for item in raw_data:
        formatted_item = {}
        for key, value in item.items():
            if isinstance(value, str):
                if '$' in value or key.lower() in ['balance', 'amount', 'value', 'price']:
                    formatted_item[key] = parse_currency(value)
                else:
                    formatted_item[key] = clean_text(value)
            else:
                formatted_item[key] = value
        formatted_data.append(formatted_item)
    
    return formatted_data

def create_summary_report(downloaded_files: List[str]) -> str:
    """Create a summary report of downloaded files."""
    try:
        report_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_files': len(downloaded_files),
            'files': []
        }
        
        for file_path in downloaded_files:
            path = Path(file_path)
            if path.exists():
                file_info = {
                    'filename': path.name,
                    'size_bytes': path.stat().st_size,
                    'created': datetime.fromtimestamp(path.stat().st_ctime).isoformat(),
                    'type': 'holdings' if 'holdings' in path.name else 'transactions'
                }
                report_data['files'].append(file_info)
        
        report_filename = f"export_summary_{sanitize_filename()}.json"
        report_path = config.data_output_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary report created: {report_path}")
        return str(report_path)
        
    except Exception as e:
        logger.error(f"Failed to create summary report: {str(e)}")
        return ""

def backup_existing_files() -> None:
    """Backup existing files in download directory."""
    try:
        backup_dir = config.data_input_dir / 'backups' / sanitize_filename()
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in config.data_input_dir.glob('*.csv'):
            if file_path.is_file():
                backup_path = backup_dir / file_path.name
                file_path.rename(backup_path)
                logger.info(f"Backed up {file_path.name} to {backup_path}")
                
    except Exception as e:
        logger.error(f"Failed to backup files: {str(e)}")

def get_download_stats() -> Dict[str, Any]:
    """Get statistics about downloaded files."""
    try:
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'holdings_files': 0,
            'transaction_files': 0,
            'oldest_file': None,
            'newest_file': None
        }
        
        files = list(config.data_input_dir.glob('*.csv'))
        stats['total_files'] = len(files)
        
        if files:
            total_size = sum(f.stat().st_size for f in files)
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            holdings_files = [f for f in files if 'holdings' in f.name]
            transaction_files = [f for f in files if 'transactions' in f.name]
            
            stats['holdings_files'] = len(holdings_files)
            stats['transaction_files'] = len(transaction_files)
            
            file_times = [(f, f.stat().st_mtime) for f in files]
            file_times.sort(key=lambda x: x[1])
            
            stats['oldest_file'] = {
                'name': file_times[0][0].name,
                'date': datetime.fromtimestamp(file_times[0][1]).isoformat()
            }
            stats['newest_file'] = {
                'name': file_times[-1][0].name,
                'date': datetime.fromtimestamp(file_times[-1][1]).isoformat()
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get download stats: {str(e)}")
        return {}