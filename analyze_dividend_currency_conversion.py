#!/usr/bin/env python3
"""
Analyze dividend currency conversion in comprehensive holdings file
"""

import json
from pathlib import Path

def analyze_dividend_conversion():
    """Analyze how dividends are being converted from USD to CAD"""
    
    # Load comprehensive data
    output_dir = Path('data/output')
    comprehensive_files = list(output_dir.glob('comprehensive_holdings_with_etf_dividends_*.json'))
    
    if not comprehensive_files:
        print("No comprehensive holdings files found!")
        return
    
    latest_file = max(comprehensive_files, key=lambda f: f.stat().st_mtime)
    print(f"Analyzing: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    holdings = data['holdings']
    
    print("\n=== DIVIDEND CURRENCY CONVERSION ANALYSIS ===")
    
    # Analyze USD holdings with dividends
    usd_dividend_holdings = []
    total_usd_dividends = 0
    total_cad_dividends = 0
    
    for holding in holdings:
        if holding.get('Currency') == 'USD' and holding.get('Indicated_Annual_Income', 0) > 0:
            symbol = holding.get('Symbol', 'N/A')
            name = holding.get('Name', '')
            quantity = holding.get('Quantity', 0)
            annual_dividend_per_share = holding.get('Annual_Dividend_Per_Share', 0)
            indicated_annual_income = holding.get('Indicated_Annual_Income', 0)
            market_value_cad = holding.get('Market_Value_CAD', 0)
            
            # Calculate what the dividend should be in CAD
            # The indicated_annual_income appears to be in USD (per share × quantity)
            # We need to convert it using the same rate as market value
            market_value_usd = holding.get('Market_Value', 0)
            if market_value_usd > 0:
                exchange_rate = market_value_cad / market_value_usd
                dividend_cad = indicated_annual_income * exchange_rate
            else:
                exchange_rate = 1.38535  # Default rate used in consolidation
                dividend_cad = indicated_annual_income * exchange_rate
            
            usd_dividend_holdings.append({
                'Symbol': symbol,
                'Name': name[:30],
                'Quantity': quantity,
                'Annual_Dividend_Per_Share_USD': annual_dividend_per_share,
                'Indicated_Annual_Income_USD': indicated_annual_income,
                'Indicated_Annual_Income_CAD_Calc': dividend_cad,
                'Exchange_Rate': exchange_rate,
                'Market_Value_USD': market_value_usd,
                'Market_Value_CAD': market_value_cad
            })
            
            total_usd_dividends += indicated_annual_income
            total_cad_dividends += dividend_cad
    
    print(f"\nFound {len(usd_dividend_holdings)} USD holdings with dividends:")
    print(f"{'Symbol':<8} {'Name':<30} {'Qty':<6} {'Div/Share':<10} {'Annual USD':<12} {'Annual CAD':<12} {'Rate':<8}")
    print("-" * 100)
    
    for holding in usd_dividend_holdings:
        print(f"{holding['Symbol']:<8} {holding['Name']:<30} {holding['Quantity']:<6} "
              f"${holding['Annual_Dividend_Per_Share_USD']:<9.2f} "
              f"${holding['Indicated_Annual_Income_USD']:<11.2f} "
              f"${holding['Indicated_Annual_Income_CAD_Calc']:<11.2f} "
              f"{holding['Exchange_Rate']:<7.4f}")
    
    print(f"\nSUMMARY:")
    print(f"Total USD Dividends: ${total_usd_dividends:,.2f}")
    print(f"Total CAD Dividends (converted): ${total_cad_dividends:,.2f}")
    print(f"Conversion Difference: ${total_cad_dividends - total_usd_dividends:,.2f}")
    print(f"Effective Exchange Rate: {total_cad_dividends / total_usd_dividends:.4f}")
    
    # Check current total from dashboard
    print(f"\n=== CURRENT DASHBOARD TOTAL ===")
    total_current_dividends = sum(h.get('Indicated_Annual_Income', 0) for h in holdings if h.get('Indicated_Annual_Income', 0) > 0)
    print(f"Current Dashboard Total: ${total_current_dividends:,.2f}")
    
    # Calculate what it should be with proper USD conversion
    corrected_total = 0
    for holding in holdings:
        if holding.get('Indicated_Annual_Income', 0) > 0:
            if holding.get('Currency') == 'USD':
                # Convert USD dividends to CAD
                market_value_usd = holding.get('Market_Value', 0)
                market_value_cad = holding.get('Market_Value_CAD', 0)
                if market_value_usd > 0:
                    exchange_rate = market_value_cad / market_value_usd
                    corrected_total += holding['Indicated_Annual_Income'] * exchange_rate
                else:
                    corrected_total += holding['Indicated_Annual_Income'] * 1.38535
            else:
                # Already in CAD
                corrected_total += holding['Indicated_Annual_Income']
    
    print(f"Corrected Total (with USD conversion): ${corrected_total:,.2f}")
    print(f"Difference: ${corrected_total - total_current_dividends:,.2f}")

if __name__ == "__main__":
    analyze_dividend_conversion()
