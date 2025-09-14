#!/usr/bin/env python3
"""
Check what amount is missing from the portfolio total
"""

def main():
    # Check the difference
    expected_total = 3700000
    actual_total = 3407471.91
    difference = expected_total - actual_total
    
    print(f'Expected portfolio total: ${expected_total:,.2f}')
    print(f'Actual portfolio total: ${actual_total:,.2f}')
    print(f'Missing amount: ${difference:,.2f}')
    print(f'Missing percentage: {(difference/expected_total)*100:.1f}%')
    
    # Check if this matches the benefits data
    print(f'\nThis missing amount (${difference:,.2f}) might be the benefits data.')
    print(f'Original cash balance: $283,676.15')
    print(f'If benefits data is ~$261,690, then:')
    print(f'  $283,676.15 + $261,690 = $545,366.15')
    print(f'  But we only have $283,676.15 in cash balances')
    print(f'  So we might be missing the benefits data entirely!')

if __name__ == "__main__":
    main()
