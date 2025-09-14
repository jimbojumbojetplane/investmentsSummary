#!/usr/bin/env python3
"""
Map the end-to-end process from RBC CSV files to final holdings
"""

import json
import pandas as pd
from pathlib import Path

def main():
    print("=== END-TO-END PROCESS MAPPING ===")
    
    # Step 1: Check the 5 RBC holding files
    print("\n=== STEP 1: 5 RBC HOLDING FILES ===")
    downloads_dir = Path('downloads/session_files')
    rbc_files = list(downloads_dir.glob('*.csv'))
    
    print(f"Found {len(rbc_files)} RBC CSV files:")
    for file in rbc_files:
        print(f"  - {file.name}")
    
    # Step 2: Check what consolidation process exists
    print("\n=== STEP 2: CONSOLIDATION PROCESS ===")
    
    # Look for existing consolidation scripts
    consolidation_scripts = [
        'run_complete_workflow.py',
        'rbc_downloads.py', 
        'process_and_view.py',
        'run_extraction_chrome.py'
    ]
    
    print("Existing consolidation scripts:")
    for script in consolidation_scripts:
        if Path(script).exists():
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script}")
    
    # Step 3: Check what consolidated files exist
    print("\n=== STEP 3: CONSOLIDATED FILES ===")
    output_dir = Path('data/output')
    
    # Look for combined/consolidated files
    consolidated_files = list(output_dir.glob('combined_*.json')) + \
                       list(output_dir.glob('holdings_detailed_*.json'))
    
    print("Consolidated files found:")
    for file in sorted(consolidated_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
        print(f"  - {file.name} ({file.stat().st_size} bytes)")
    
    # Step 4: Analyze the most recent consolidated file
    print("\n=== STEP 4: ANALYZE MOST RECENT CONSOLIDATED FILE ===")
    
    if consolidated_files:
        latest_file = max(consolidated_files, key=lambda f: f.stat().st_mtime)
        print(f"Analyzing: {latest_file.name}")
        
        with open(latest_file, 'r') as f:
            if latest_file.suffix == '.json':
                try:
                    data = json.load(f)
                    if isinstance(data, dict) and 'holdings' in data:
                        holdings_data = data['holdings']
                        metadata = data.get('metadata', {})
                        print(f"  Structure: Dictionary with metadata")
                        print(f"  Holdings count: {len(holdings_data)}")
                        print(f"  Metadata: {metadata}")
                    else:
                        holdings_data = data
                        print(f"  Structure: Direct list")
                        print(f"  Holdings count: {len(holdings_data)}")
                    
                    # Analyze holdings
                    symbol_holdings = [h for h in holdings_data if h.get('Symbol') and h.get('Symbol') != 'None']
                    cash_holdings = [h for h in holdings_data if not h.get('Symbol') or h.get('Symbol') == 'None']
                    
                    print(f"  Holdings with symbols: {len(symbol_holdings)}")
                    print(f"  Holdings without symbols (cash): {len(cash_holdings)}")
                    
                    # Calculate totals
                    total_value = sum(h.get('Market_Value_CAD', 0) for h in holdings_data)
                    symbol_total = sum(h.get('Market_Value_CAD', 0) for h in symbol_holdings)
                    cash_total = sum(h.get('Market_Value_CAD', 0) for h in cash_holdings)
                    
                    print(f"  Total value: ${total_value:,.2f}")
                    print(f"  Symbol holdings total: ${symbol_total:,.2f}")
                    print(f"  Cash holdings total: ${cash_total:,.2f}")
                    
                    # Show symbol holdings
                    print(f"\n  Symbol holdings:")
                    for h in symbol_holdings[:10]:  # Show first 10
                        print(f"    - {h.get('Symbol')} - {h.get('Name', 'Unknown')[:50]} - ${h.get('Market_Value_CAD', 0):,.2f}")
                    if len(symbol_holdings) > 10:
                        print(f"    ... and {len(symbol_holdings) - 10} more")
                    
                    # Show cash holdings
                    print(f"\n  Cash holdings:")
                    for h in cash_holdings[:5]:  # Show first 5
                        print(f"    - {h.get('Name', 'Unknown')} - {h.get('Asset_Type', 'Unknown')} - ${h.get('Market_Value_CAD', 0):,.2f}")
                    if len(cash_holdings) > 5:
                        print(f"    ... and {len(cash_holdings) - 5} more")
                        
                except Exception as e:
                    print(f"  Error reading file: {e}")
    
    # Step 5: Check benefits data
    print("\n=== STEP 5: BENEFITS DATA ===")
    benefits_files = list(output_dir.glob('benefits_data_*.json'))
    
    if benefits_files:
        latest_benefits = max(benefits_files, key=lambda f: f.stat().st_mtime)
        print(f"Latest benefits file: {latest_benefits.name}")
        
        with open(latest_benefits, 'r') as f:
            benefits_data = json.load(f)
        
        print("Benefits data:")
        for key, value in benefits_data.items():
            print(f"  {key}: {value}")
    else:
        print("No benefits data files found")
    
    # Step 6: Check enrichment process
    print("\n=== STEP 6: ENRICHMENT PROCESS ===")
    
    enrichment_scripts = [
        'portfolio_classification_engine.py',
        'src/external_data_enricher.py',
        'apply_comprehensive_classifications.py'
    ]
    
    print("Enrichment scripts:")
    for script in enrichment_scripts:
        if Path(script).exists():
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script}")
    
    # Step 7: Expected vs Actual
    print("\n=== STEP 7: EXPECTED VS ACTUAL ===")
    print("Expected breakdown:")
    print("  5 RBC accounts: ~$2,600,000")
    print("  Cash balances: ~$283,000")
    print("  2 Bell accounts: ~$1,100,000")
    print("  Total: ~$3,700,000")
    
    if consolidated_files:
        print(f"\nActual breakdown:")
        print(f"  Total value: ${total_value:,.2f}")
        print(f"  Symbol holdings: ${symbol_total:,.2f}")
        print(f"  Cash holdings: ${cash_total:,.2f}")
        
        # Check if benefits are included
        benefits_in_file = [h for h in holdings_data if 'pension' in h.get('Name', '').lower() or 'rrsp' in h.get('Name', '').lower()]
        if benefits_in_file:
            benefits_total = sum(h.get('Market_Value_CAD', 0) for h in benefits_in_file)
            print(f"  Benefits included: ${benefits_total:,.2f}")
        else:
            print(f"  Benefits included: $0 (not in file)")

if __name__ == "__main__":
    main()
