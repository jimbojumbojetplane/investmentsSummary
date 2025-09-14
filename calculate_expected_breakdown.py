#!/usr/bin/env python3
"""
Calculate the expected breakdown to understand the $3.7M target
"""

import json
from pathlib import Path

def main():
    print("=== CALCULATING EXPECTED BREAKDOWN ===")
    
    # Load benefits data
    output_dir = Path('data/output')
    benefits_file = output_dir / 'benefits_data_20250912_114921.json'
    
    with open(benefits_file, 'r') as f:
        benefits_data = json.load(f)
    
    dc_pension = float(benefits_data['dc_pension_plan'].replace('$', '').replace(',', ''))
    rrsp = float(benefits_data['rrsp'].replace('$', '').replace(',', ''))
    total_benefits = dc_pension + rrsp
    
    print(f'=== BENEFITS DATA ===')
    print(f'DC Pension: ${dc_pension:,.2f}')
    print(f'RRSP: ${rrsp:,.2f}')
    print(f'Total Benefits: ${total_benefits:,.2f}')
    
    # Load original holdings file
    original_files = [f for f in output_dir.glob('holdings_detailed_*.json') 
                     if 'restructured' not in f.name and 'corrected' not in f.name and 'complete' not in f.name and 'final' not in f.name and 'correct' not in f.name and 'proper' not in f.name and 'fixed' not in f.name]
    
    original_file = max(original_files, key=lambda f: f.stat().st_mtime)
    
    with open(original_file, 'r') as f:
        original_data = json.load(f)
    
    # Calculate what's in the original file
    original_total = sum(h.get('Market_Value_CAD', 0) for h in original_data)
    
    # Check what benefits are already included
    benefits_in_file = [h for h in original_data if 
                       'pension' in h.get('Name', '').lower() or 
                       'rrsp' in h.get('Name', '').lower()]
    
    benefits_in_file_total = sum(h.get('Market_Value_CAD', 0) for h in benefits_in_file)
    
    print(f'\n=== ORIGINAL FILE ANALYSIS ===')
    print(f'Original file total: ${original_total:,.2f}')
    print(f'Benefits already in file: ${benefits_in_file_total:,.2f}')
    
    # Calculate what the total should be
    print(f'\n=== EXPECTED CALCULATIONS ===')
    
    # Scenario 1: Original file has no benefits
    if benefits_in_file_total == 0:
        expected_total_no_benefits = original_total
        expected_total_with_benefits = original_total + total_benefits
        print(f'Scenario 1 - No benefits in original file:')
        print(f'  Original file: ${expected_total_no_benefits:,.2f}')
        print(f'  With benefits: ${expected_total_with_benefits:,.2f}')
    
    # Scenario 2: Original file has some benefits
    elif benefits_in_file_total < total_benefits:
        missing_benefits = total_benefits - benefits_in_file_total
        expected_total_with_full_benefits = original_total + missing_benefits
        print(f'Scenario 2 - Partial benefits in original file:')
        print(f'  Original file: ${original_total:,.2f}')
        print(f'  Benefits in file: ${benefits_in_file_total:,.2f}')
        print(f'  Missing benefits: ${missing_benefits:,.2f}')
        print(f'  With full benefits: ${expected_total_with_full_benefits:,.2f}')
    
    # Scenario 3: Original file has all benefits
    else:
        print(f'Scenario 3 - All benefits already in original file:')
        print(f'  Original file: ${original_total:,.2f}')
        print(f'  Benefits in file: ${benefits_in_file_total:,.2f}')
    
    # User's stated target
    user_target = 3700000
    print(f'\n=== USER TARGET ANALYSIS ===')
    print(f'User stated target: ${user_target:,.2f}')
    print(f'Original file total: ${original_total:,.2f}')
    print(f'Difference: ${user_target - original_total:,.2f}')
    
    # Check if the difference matches missing benefits
    if abs((user_target - original_total) - (total_benefits - benefits_in_file_total)) < 1000:
        print(f'✅ The difference matches the missing benefits!')
        print(f'This suggests we need to add the missing benefits to reach $3.7M')
    else:
        print(f'❌ The difference does not match the missing benefits')
        print(f'There might be an error in the benefits data or the target amount')

if __name__ == "__main__":
    main()
