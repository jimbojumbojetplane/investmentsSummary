import os
import re
import json
import csv
import datetime
import logging
from io import StringIO
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
PROJECT_ROOT = Path(__file__).parent.parent.parent
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "data" / "processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define directories
DOWNLOAD_DIR = PROJECT_ROOT / "data" / "input" / "downloaded_files"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def safe_float(value: str) -> float:
    """Convert a value to float safely, handling quotes and commas."""
    if not value or value in ['N/A', '', 'null']:
        return 0.0
    try:
        # Remove quotes, commas, and whitespace
        cleaned = str(value).strip().strip('"').replace(',', '')
        if cleaned == '' or cleaned == 'N/A':
            return 0.0
        return float(cleaned)
    except (TypeError, ValueError):
        return 0.0

def safe_int(value: str) -> int:
    """Convert a value to int safely."""
    try:
        return int(safe_float(value))
    except (TypeError, ValueError):
        return 0

def clean_string(value: str) -> str:
    """Clean string values, removing quotes and extra whitespace."""
    if not value:
        return ""
    return str(value).strip().strip('"').strip()

def parse_filename(filename: str) -> tuple[Optional[str], Optional[datetime.datetime]]:
    """Parse account and date from filename."""
    base_name, ext = os.path.splitext(filename)
    if ext.lower() != ".csv":
        return None, None
    
    pattern = r"^Holdings\s+(\d+)\s+([A-Za-z]+\s+\d+,\s+\d{4})$"
    match = re.match(pattern, base_name)
    if not match:
        return None, None
    
    account = match.group(1)
    date_str = match.group(2)
    try:
        dt = datetime.datetime.strptime(date_str, "%B %d, %Y")
        return account, dt
    except ValueError:
        return account, None

def parse_csv_line(line: str) -> List[str]:
    """Parse a CSV line properly handling quoted fields."""
    # Use Python's CSV parser to handle quoted fields correctly
    reader = csv.reader(StringIO(line))
    try:
        return next(reader)
    except:
        # Fallback to simple split if CSV parsing fails
        return line.split(',')

def parse_rbc_csv(file_path: str) -> List[Dict[str, Any]]:
    """Parse RBC CSV file directly without AI."""
    logger.info(f"Parsing CSV file: {file_path}")
    
    # Extract account number from filename
    filename = os.path.basename(file_path)
    account_number, file_date = parse_filename(filename)
    if not account_number:
        logger.error(f"Could not extract account number from filename: {filename}")
        return []
    
    results = []
    exchange_rates = {}  # Store exchange rates for this file
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Find Financial Summary section
            if line.startswith('Currency,Cash,Investments'):
                logger.info(f"Found financial summary section at line {i+1}")
                headers = parse_csv_line(line)
                
                # Exchange rate is always in the last column
                exchange_rate_col = len(headers) - 1
                total_col = -1
                for idx, header in enumerate(headers):
                    if "Total" in header:
                        total_col = idx
                
                logger.info(f"Exchange rate column: {exchange_rate_col}, Total column: {total_col}")
                i += 1
                
                while i < len(lines):
                    line = lines[i].strip()
                    if not line or line.startswith(',Product') or line.startswith('Important Information'):
                        break
                    
                    row = parse_csv_line(line)
                    if len(row) >= 4 and row[0]:  # Must have currency
                        # Get exchange rate from last column
                        exchange_rate = "1"
                        if len(row) > 0:
                            exchange_rate = clean_string(row[-1])  # Always use last column
                        
                        # Get total from correct column
                        total_value = ""
                        if total_col >= 0 and len(row) > total_col:
                            total_value = clean_string(row[total_col])
                        
                        currency = clean_string(row[0])
                        financial_data = {
                            "type": "financial_summary",
                            "data": {
                                "Account #": account_number,
                                "Currency": currency,
                                "Cash": clean_string(row[1]) if len(row) > 1 else "",
                                "Investments": clean_string(row[2]) if len(row) > 2 else "",
                                "Total": total_value,
                                "Exchange Rate to CAD": exchange_rate
                            }
                        }
                        results.append(financial_data)
                        
                        # Store exchange rate for USD conversion later
                        if currency == "USD":
                            exchange_rates["USD"] = safe_float(exchange_rate)
                        
                        logger.info(f"Added financial summary for {currency}")
                    i += 1
                continue
            
            # Find Holdings section
            elif line.startswith(',Product,Symbol,Name') or 'Product,Symbol,Name' in line:
                logger.info(f"Found holdings section at line {i+1}")
                headers = parse_csv_line(line)
                i += 1
                holdings_count = 0
                
                while i < len(lines):
                    line = lines[i].strip()
                    if not line or line.startswith('Important Information') or line.startswith('Disclaimer'):
                        break
                    
                    row = parse_csv_line(line)
                    
                    # Skip lines that don't have holdings data
                    if len(row) < 10 or not row[2]:  # Must have at least symbol
                        i += 1
                        continue
                    
                    # Check if this is a holdings line (CAD Holdings, USD Holdings, or direct data)
                    if (row[0] in ['CAD Holdings', 'USD Holdings'] or 
                        (len(row) >= 24 and row[1] and row[2])):  # Product and Symbol exist
                        
                        try:
                            currency = clean_string(row[6]) if len(row) > 6 else ""
                            
                            # Get base values
                            last_price = safe_float(row[5]) if len(row) > 5 else 0.0
                            change_dollar = safe_float(row[7]) if len(row) > 7 else 0.0
                            book_cost = safe_float(row[9]) if len(row) > 9 else 0.0
                            market_value = safe_float(row[10]) if len(row) > 10 else 0.0
                            gain_loss = safe_float(row[11]) if len(row) > 11 else 0.0
                            avg_cost = safe_float(row[13]) if len(row) > 13 else 0.0
                            dividend_amount = safe_float(row[14]) if len(row) > 14 else None
                            
                            # Convert USD to CAD if needed
                            if currency == "USD" and "USD" in exchange_rates:
                                usd_rate = exchange_rates["USD"]
                                last_price = last_price * usd_rate
                                change_dollar = change_dollar * usd_rate
                                book_cost = book_cost * usd_rate
                                market_value = market_value * usd_rate
                                gain_loss = gain_loss * usd_rate
                                avg_cost = avg_cost * usd_rate
                                if dividend_amount is not None:
                                    dividend_amount = dividend_amount * usd_rate
                                currency = "CAD"  # Update currency after conversion
                            
                            holding_data = {
                                "type": "current_holdings",
                                "data": {
                                    "Account #": account_number,
                                    "Product": clean_string(row[1]) if len(row) > 1 else "",
                                    "Symbol": clean_string(row[2]) if len(row) > 2 else "",
                                    "Name": clean_string(row[3]) if len(row) > 3 else "",
                                    "Quantity": safe_int(row[4]) if len(row) > 4 else 0,
                                    "Last Price": last_price,
                                    "Currency": currency,
                                    "Change $": change_dollar,
                                    "Change %": clean_string(row[8]) if len(row) > 8 else "",
                                    "Total Book Cost": book_cost,
                                    "Total Market Value": market_value,
                                    "Unrealized Gain/Loss $": gain_loss,
                                    "Unrealized Gain/Loss %": clean_string(row[12]) if len(row) > 12 else "",
                                    "Average Cost": avg_cost,
                                    "Annual Dividend Amount $": dividend_amount,
                                    "Dividend Ex Date": clean_string(row[15]) if len(row) > 15 else "",
                                    "Load Type": clean_string(row[16]) if len(row) > 16 else "",
                                    "RSP Eligibility": clean_string(row[17]) if len(row) > 17 else "",
                                    "Automatic Investment Plan": clean_string(row[18]) if len(row) > 18 else "",
                                    "DRIP Eligibility": clean_string(row[19]) if len(row) > 19 else "",
                                    "Coupon Rate": safe_float(row[20]) if len(row) > 20 and row[20].strip() else None,
                                    "Maturity Date": clean_string(row[21]) if len(row) > 21 else None,
                                    "Expiration Date": clean_string(row[22]) if len(row) > 22 else None,
                                    "Open Interest": safe_float(row[23]) if len(row) > 23 and row[23].strip() else None
                                }
                            }
                            
                            # Only add if we have a valid symbol
                            if holding_data["data"]["Symbol"]:
                                results.append(holding_data)
                                holdings_count += 1
                                logger.info(f"Added holding: {holding_data['data']['Symbol']} ({holding_data['data']['Currency']})")
                        
                        except Exception as e:
                            logger.warning(f"Error parsing holding on line {i+1}: {e}")
                    
                    i += 1
                
                logger.info(f"Processed {holdings_count} holdings from file")
                continue
            
            else:
                i += 1
        
        logger.info(f"Successfully parsed {len(results)} total entries from {filename}")
        return results
        
    except Exception as e:
        logger.error(f"Error parsing CSV file {file_path}: {e}")
        return []

def update_financial_summaries_to_cad(parsed_json: List[Dict[str, Any]]) -> None:
    """
    For every item with type 'financial_summary', calculate CAD equivalents.
    """
    for item in parsed_json:
        if item.get("type") == "financial_summary":
            data = item.get("data", {})
            currency = data.get("Currency", "CAD").upper()
            cash = safe_float(data.get("Cash", 0))
            investments = safe_float(data.get("Investments", 0))
            total = safe_float(data.get("Total", 0))
            ex_rate = safe_float(data.get("Exchange Rate to CAD", 1))
            
            # If exchange rate is missing or zero, default to 1
            if ex_rate == 0.0:
                ex_rate = 1.0
            
            if currency == "CAD":
                # Already in CAD
                data["Cash (CAD)"] = round(cash, 2)
                data["Investments (CAD)"] = round(investments, 2)
                data["Total (CAD)"] = round(total, 2)
            else:
                # Convert to CAD
                data["Cash (CAD)"] = round(cash * ex_rate, 2)
                data["Investments (CAD)"] = round(investments * ex_rate, 2)
                data["Total (CAD)"] = round(total * ex_rate, 2)

def process_csv_files():
    """Process all CSV files using direct parsing and combine results."""
    # Dictionary to track the most recent file for each account
    latest_files = {}
    all_csv_files = []
    
    # Find all valid CSV files and track the latest for each account
    for filename in os.listdir(DOWNLOAD_DIR):
        account, date = parse_filename(filename)
        if account and date:
            all_csv_files.append((filename, account, date))
            logger.info(f"Found valid CSV file: {filename} - Account: {account}, Date: {date.strftime('%Y-%m-%d')}")
            
            # Update the latest file for this account if needed
            if account not in latest_files or date > latest_files[account][1]:
                latest_files[account] = (filename, date)
    
    if not all_csv_files:
        logger.info("No valid CSV files found.")
        return
    
    # Convert the dictionary of latest files to a list format
    csv_files = [(filename, account, date) 
                for account, (filename, date) in latest_files.items()]
    
    # Sort files by date (newest first)
    csv_files.sort(key=lambda x: x[2], reverse=True)
    
    # Log information about the selected files
    logger.info(f"Found {len(all_csv_files)} total CSV files, selected {len(csv_files)} most recent files (one per account).")
    for filename, account, date in csv_files:
        logger.info(f"Selected most recent CSV file for account {account}: {filename} - Date: {date.strftime('%Y-%m-%d')}")
    
    # Show the files to be processed
    if csv_files:
        print("\nFound the following most recent CSV files to process:")
        for i, (file, acc, dt) in enumerate(csv_files, 1):
            print(f"{i}. {file} - Account: {acc}, Date: {dt.strftime('%Y-%m-%d')}")
        
        logger.info("Proceeding with direct CSV parsing automatically...")
    
    combined_data = []
    
    for filename, account, date in csv_files:
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        
        # Parse CSV file directly
        parsed_data = parse_rbc_csv(file_path)
        
        if parsed_data:
            # Convert financial summaries to CAD
            update_financial_summaries_to_cad(parsed_data)
            
            # Append results
            combined_data.extend(parsed_data)
            logger.info(f"Successfully processed {filename}: {len(parsed_data)} entries")
        else:
            logger.warning(f"No data extracted from {filename}")
    
    # Save combined JSON file using the current date
    final_filename = f"holdings_combined_{datetime.datetime.now().strftime('%d%m%Y')}.json"
    final_path = os.path.join(OUTPUT_DIR, final_filename)
    
    with open(final_path, "w", encoding="utf-8") as out_file:
        json.dump(combined_data, out_file, indent=2)
    
    logger.info(f"All files processed using direct CSV parsing. Combined JSON saved at: {final_path}")
    
    # Print summary
    financial_summaries = [item for item in combined_data if item.get('type') == 'financial_summary']
    current_holdings = [item for item in combined_data if item.get('type') == 'current_holdings']
    
    print(f"\nProcessing Summary:")
    print(f"Total entries: {len(combined_data)}")
    print(f"Financial summaries: {len(financial_summaries)}")
    print(f"Current holdings: {len(current_holdings)}")
    
    # Count by account
    accounts = {}
    for item in current_holdings:
        account = item['data']['Account #']
        if account not in accounts:
            accounts[account] = 0
        accounts[account] += 1
    
    print("\nHoldings by account:")
    for account, count in sorted(accounts.items()):
        print(f"  Account {account}: {count} holdings")

# Run the script
if __name__ == "__main__":
    process_csv_files()