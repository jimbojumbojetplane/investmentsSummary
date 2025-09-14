#!/usr/bin/env python3
"""
Fix dividend currency conversion in comprehensive holdings file
Convert USD dividends to CAD using the same exchange rates as market values
"""

import json
from pathlib import Path
from datetime import datetime

def fix_dividend_conversion():
    """Fix dividend currency conversion for USD holdings"""
    
    # Load comprehensive data
    output_dir = Path('data/output')
    comprehensive_files = list(output_dir.glob('comprehensive_holdings_with_etf_dividends_*.json'))
    
    if not comprehensive_files:
        print("No comprehensive holdings files found!")
        return
    
    latest_file = max(comprehensive_files, key=lambda f: f.stat().st_mtime)
    print(f"Loading: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    holdings = data['holdings']
    
    print("\n=== FIXING DIVIDEND CURRENCY CONVERSION ===")
    
    # Track changes
    usd_holdings_fixed = 0
    total_usd_dividends_converted = 0
    
    for holding in holdings:
        if (holding.get('Currency') == 'USD' and 
            holding.get('Indicated_Annual_Income', 0) > 0):
            
            symbol = holding.get('Symbol', 'N/A')
            original_dividend_usd = holding.get('Indicated_Annual_Income', 0)
            
            # Calculate exchange rate from market values
            market_value_usd = holding.get('Market_Value', 0)
            market_value_cad = holding.get('Market_Value_CAD', 0)
            
            if market_value_usd > 0:
                exchange_rate = market_value_cad / market_value_usd
            else:
                exchange_rate = 1.38535  # Default rate used in consolidation
            
            # Convert dividend to CAD
            dividend_cad = original_dividend_usd * exchange_rate
            
            # Update the holding
            holding['Indicated_Annual_Income'] = dividend_cad
            
            # Also update quarterly dividend if it exists
            if 'Quarterly_Dividend' in holding:
                holding['Quarterly_Dividend'] = dividend_cad / 4
            
            # Add metadata about the conversion
            holding['Dividend_Conversion_Applied'] = True
            holding['Original_Dividend_USD'] = original_dividend_usd
            holding['Dividend_Exchange_Rate'] = exchange_rate
            
            usd_holdings_fixed += 1
            total_usd_dividends_converted += original_dividend_usd
            
            print(f"Fixed {symbol}: ${original_dividend_usd:.2f} USD → ${dividend_cad:.2f} CAD (rate: {exchange_rate:.4f})")
    
    # Calculate new totals
    total_annual_dividends = sum(h.get('Indicated_Annual_Income', 0) for h in holdings if h.get('Indicated_Annual_Income', 0) > 0)
    total_quarterly_dividends = sum(h.get('Quarterly_Dividend', 0) for h in holdings if h.get('Quarterly_Dividend', 0) > 0)
    
    # Update metadata
    data['metadata']['total_annual_dividends'] = total_annual_dividends
    data['metadata']['total_quarterly_dividends'] = total_quarterly_dividends
    data['metadata']['dividend_currency_conversion_applied'] = True
    data['metadata']['dividend_conversion_date'] = datetime.now().isoformat()
    data['metadata']['usd_holdings_converted'] = usd_holdings_fixed
    data['metadata']['total_usd_dividends_converted'] = total_usd_dividends_converted
    
    print(f"\nSUMMARY:")
    print(f"USD holdings fixed: {usd_holdings_fixed}")
    print(f"Total USD dividends converted: ${total_usd_dividends_converted:,.2f}")
    print(f"New total annual dividends (all CAD): ${total_annual_dividends:,.2f}")
    print(f"New total quarterly dividends (all CAD): ${total_quarterly_dividends:,.2f}")
    
    # Save corrected file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    corrected_filename = f"comprehensive_holdings_dividends_cad_corrected_{timestamp}.json"
    corrected_filepath = output_dir / corrected_filename
    
    with open(corrected_filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nSaved corrected file: {corrected_filename}")
    
    return corrected_filepath

if __name__ == "__main__":
    fix_dividend_conversion()
