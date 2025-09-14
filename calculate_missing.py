#!/usr/bin/env python3

def main():
    current_total = 3669161.96
    expected_total = 3700000
    missing = expected_total - current_total

    print(f'Current total: ${current_total:,.2f}')
    print(f'Expected total: ${expected_total:,.2f}')
    print(f'Missing: ${missing:,.2f}')

    # Benefits data shows RRSP = $416,305.91
    rrsp_benefits = 416305.91
    print(f'RRSP Benefits: ${rrsp_benefits:,.2f}')

    if missing < rrsp_benefits:
        print(f'Missing amount is smaller than RRSP benefits')
        print(f'Maybe RRSP benefits are partially included or missing')
    else:
        print(f'Missing amount matches RRSP benefits')

if __name__ == "__main__":
    main()
