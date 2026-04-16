"""
Utility: parse a Frequency model's label string into a month count.

Admin may enter labels like:
  "Monthly", "1 Month", "Bi-Monthly", "Quarterly", "3 Months",
  "6 Months", "Half Yearly", "Yearly", "1 Year", "Annual",
  "2 Years", "24 Months", "Weekly", "Daily"

Returns an integer month count, or None if it cannot be parsed
(weekly/daily publications don't have a "months" equivalent
 and are treated as 1 month for billing purposes).
"""

import re

_WORD_TO_MONTHS = {
    # single month
    'monthly': 1, '1 month': 1, 'one month': 1,
    # 2 months
    'bi-monthly': 2, 'bimonthly': 2, '2 months': 2, 'two months': 2,
    # 3 months / quarter
    'quarterly': 3, 'quarter': 3, '3 months': 3, 'three months': 3,
    # 4 months
    '4 months': 4, 'four months': 4,
    # 6 months / half year
    'half yearly': 6, 'half-yearly': 6, 'semi-annual': 6, 'semi annual': 6,
    '6 months': 6, 'six months': 6,
    # 12 months / year
    'yearly': 12, 'annual': 12, 'annually': 12, '1 year': 12,
    'one year': 12, '12 months': 12, 'twelve months': 12,
    # 24 months / 2 years
    '2 years': 24, 'two years': 24, '24 months': 24,
    # weekly / daily → treat as 1 month for billing
    'weekly': 1, 'daily': 1, 'fortnightly': 1,
}


def label_to_months(label: str) -> int:
    """
    Convert a Frequency label string to a month count.
    Falls back to 1 if nothing matches.
    """
    key = label.strip().lower()
    if key in _WORD_TO_MONTHS:
        return _WORD_TO_MONTHS[key]

    # Try "N months" / "N years" patterns
    m = re.search(r'(\d+)\s*month', key)
    if m:
        return int(m.group(1))

    m = re.search(r'(\d+)\s*year', key)
    if m:
        return int(m.group(1)) * 12

    return 1   # safe default


def frequencies_for_product(product) -> list:
    """
    Returns a list of dicts for a product's linked Frequency objects,
    sorted ascending by month count.

    Each dict:
        { 'id': int, 'label': str, 'months': int }
    """
    result = []
    for freq in product.frequency.all():
        months = label_to_months(freq.frequency)
        result.append({
            'id': freq.id,
            'label': freq.frequency,
            'months': months,
        })
    # Sort by duration so the cheapest option appears first
    result.sort(key=lambda x: x['months'])
    return result