#!/usr/bin/env python3
"""
Analyze how cash balances are being misclassified in the enhancement process
"""

import json
from pathlib import Path

def main():
    print("=== ANALYZING CASH CLASSIFICATION ISSUE ===")
    
    # Load the original holdings file
    output_dir = Path('data/output')
    original_files = [f for f in output_dir.glob('holdings_detailed_*.json') 
                     if 'restructured' not in f.name and 'corrected' not in f.name and 'complete' not in f.name and 'final' not in f.name and 'correct' not in f.name]
    
    if original_files:
        original_file = max(original_files, key=lambda f: f.stat().st_mtime)
        print(f'Original file: {original_file.name}')
        
        with open(original_file, 'r') as f:
            original_data = json.load(f)
        
        # Check cash-related holdings in original file
        print(f'\n=== ORIGINAL FILE CASH ANALYSIS ===')
        cash_related = [h for h in original_data if 
                       h.get('Symbol') is None or 
                       h.get('Symbol') == '' or
                       'cash' in h.get('Name', '').lower() or
                       h.get('Asset_Type', '').lower() in ['cash', 'cash cad', 'cash usd']]
        
        print(f'Cash-related holdings in original: {len(cash_related)}')
        for h in cash_related:
            print(f'  {h.get("Symbol", "No Symbol")} - {h.get("Name")} - {h.get("Asset_Type")} - ${h.get("Market_Value_CAD", 0):,.2f}')
    
    # Load the restructured file
    restructured_files = list(output_dir.glob('holdings_detailed_restructured_*.json'))
    if restructured_files:
        restructured_file = max(restructured_files, key=lambda f: f.stat().st_mtime)
        print(f'\nRestructured file: {restructured_file.name}')
        
        with open(restructured_file, 'r') as f:
            restructured_data = json.load(f)
        
        if isinstance(restructured_data, dict) and 'holdings' in restructured_data:
            holdings_data = restructured_data['holdings']
        else:
            holdings_data = restructured_data
        
        # Check cash-related holdings in restructured file
        print(f'\n=== RESTRUCTURED FILE CASH ANALYSIS ===')
        cash_related = [h for h in holdings_data if 
                       h.get('Symbol') is None or 
                       h.get('Symbol') == '' or
                       'cash' in h.get('Name', '').lower() or
                       h.get('Asset_Type', '').lower() in ['cash', 'cash cad', 'cash usd', 'cash unknown']]
        
        print(f'Cash-related holdings in restructured: {len(cash_related)}')
        for h in cash_related:
            print(f'  {h.get("Symbol", "No Symbol")} - {h.get("Name")} - {h.get("Asset_Type")} - ${h.get("Market_Value_CAD", 0):,.2f}')
    
    # Load the correct portfolio file
    correct_files = list(output_dir.glob('holdings_detailed_correct_*.json'))
    if correct_files:
        correct_file = max(correct_files, key=lambda f: f.stat().st_mtime)
        print(f'\nCorrect file: {correct_file.name}')
        
        with open(correct_file, 'r') as f:
            correct_data = json.load(f)
        
        # Check cash-related holdings in correct file
        print(f'\n=== CORRECT FILE CASH ANALYSIS ===')
        cash_related = [h for h in correct_data if 
                       h.get('Symbol') is None or 
                       h.get('Symbol') == '' or
                       'cash' in h.get('Name', '').lower() or
                       h.get('Asset_Type', '').lower() in ['cash', 'cash cad', 'cash usd', 'cash unknown', 'rrsp']]
        
        print(f'Cash-related holdings in correct: {len(cash_related)}')
        for h in cash_related:
            print(f'  {h.get("Symbol", "No Symbol")} - {h.get("Name")} - {h.get("Asset_Type")} - ${h.get("Market_Value_CAD", 0):,.2f}')
    
    print(f'\n=== SUMMARY ===')
    print(f'The issue is that cash balances from CSV files should be:')
    print(f'1. Holdings WITHOUT symbols')
    print(f'2. Asset Type: "Cash Balance" (not "ETF – Cash / Ultra-Short")')
    print(f'3. NOT processed through Yahoo Finance/LLM classification')
    print(f'4. Properly distinguished from CASH symbol ETFs')

if __name__ == "__main__":
    main()
