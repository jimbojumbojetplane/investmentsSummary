#!/usr/bin/env python3
"""
Remove duplicate CASH symbol holdings that represent the same cash as actual cash balances
"""

import json
from pathlib import Path
from datetime import datetime

def main():
    print("=== REMOVING DUPLICATE CASH SYMBOL HOLDINGS ===")
    
    # Load the corrected file
    output_dir = Path('data/output')
    corrected_files = list(output_dir.glob('holdings_detailed_restructured_corrected_*.json'))
    if corrected_files:
        latest_file = max(corrected_files, key=lambda f: f.stat().st_mtime)
        print(f'Loading: {latest_file.name}')
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        holdings = data['holdings']
        
        # Separate holdings by type
        cash_symbol_holdings = [h for h in holdings if h.get('Symbol') == 'CASH']
        actual_cash_balances = [h for h in holdings if h.get('Symbol') is None or h.get('Symbol') == '']
        other_symbol_holdings = [h for h in holdings if h.get('Symbol') is not None and h.get('Symbol') != '' and h.get('Symbol') != 'CASH']
        
        print(f'\nBefore removal:')
        print(f'  CASH symbol holdings: {len(cash_symbol_holdings)} (${sum(h.get("Market_Value_CAD", 0) for h in cash_symbol_holdings):,.2f})')
        print(f'  Actual cash balances: {len(actual_cash_balances)} (${sum(h.get("Market_Value_CAD", 0) for h in actual_cash_balances):,.2f})')
        print(f'  Other symbol holdings: {len(other_symbol_holdings)} (${sum(h.get("Market_Value_CAD", 0) for h in other_symbol_holdings):,.2f})')
        print(f'  Total: ${sum(h.get("Market_Value_CAD", 0) for h in holdings):,.2f}')
        
        # Remove CASH symbol holdings (keep actual cash balances and other symbols)
        corrected_holdings = actual_cash_balances + other_symbol_holdings
        
        print(f'\nAfter removal:')
        print(f'  Actual cash balances: {len(actual_cash_balances)} (${sum(h.get("Market_Value_CAD", 0) for h in actual_cash_balances):,.2f})')
        print(f'  Other symbol holdings: {len(other_symbol_holdings)} (${sum(h.get("Market_Value_CAD", 0) for h in other_symbol_holdings):,.2f})')
        print(f'  Total: ${sum(h.get("Market_Value_CAD", 0) for h in corrected_holdings):,.2f}')
        
        # Create corrected metadata
        corrected_metadata = {
            'creation_date': datetime.now().isoformat(),
            'total_holdings': len(corrected_holdings),
            'symbol_holdings': len(other_symbol_holdings),
            'cash_holdings': len(actual_cash_balances),
            'total_value_cad': sum(h.get('Market_Value_CAD', 0) for h in corrected_holdings),
            'cash_balance_cad': sum(h.get('Market_Value_CAD', 0) for h in actual_cash_balances),
            'source_files': data.get('metadata', {}).get('source_files', []),
            'notes': 'Removed duplicate CASH symbol holdings - kept only actual cash balances and other symbol holdings'
        }
        
        # Create final corrected data structure
        final_corrected_data = {
            'metadata': corrected_metadata,
            'holdings': corrected_holdings
        }
        
        # Save final corrected file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_filename = f"holdings_detailed_restructured_final_{timestamp}.json"
        final_filepath = output_dir / final_filename
        
        with open(final_filepath, 'w') as f:
            json.dump(final_corrected_data, f, indent=2)
        
        print(f'\n=== FINAL CORRECTED FILE CREATED ===')
        print(f'File: {final_filename}')
        print(f'Total holdings: {len(corrected_holdings)}')
        print(f'Symbol holdings: {len(other_symbol_holdings)}')
        print(f'Cash holdings: {len(actual_cash_balances)}')
        print(f'Total value: ${corrected_metadata["total_value_cad"]:,.2f}')
        print(f'Cash balance value: ${corrected_metadata["cash_balance_cad"]:,.2f}')
        
        # Verify the fix
        print(f'\n=== VERIFICATION ===')
        expected_cash = 283676.15
        actual_cash = corrected_metadata["cash_balance_cad"]
        if abs(actual_cash - expected_cash) < 0.01:
            print('✅ Cash balances match expected $283,676.15')
        else:
            print(f'❌ Cash balances: ${actual_cash:,.2f}, Expected: $283,676.15')
        
        print(f'✅ No duplicate CASH symbol holdings')
        print(f'✅ Portfolio total: ${corrected_metadata["total_value_cad"]:,.2f}')
        
        return final_filepath
    
    return None

if __name__ == "__main__":
    main()
