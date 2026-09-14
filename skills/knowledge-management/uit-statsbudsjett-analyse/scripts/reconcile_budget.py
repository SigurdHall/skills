"""Kontrollerer en faglig harmonisert rammebro uten å endre kildetall."""

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path


def amount(value):
    """Godtar eksakte tall; null betyr ukjent, aldri null kroner."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError('Beløp må være heltall eller tekst med punktum som desimaltegn.')
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f'Ugyldig beløp: {value}') from error
    if not number.is_finite():
        raise ValueError('Beløp må være endelige tall.')
    return number


def residual(total, opening, changes):
    """Avstemmer bare når alle ledd er kjent."""
    if total is None or opening is None or any(value is None for value in changes):
        return None
    return str(total - opening - sum(changes))


def reconcile(data):
    if data['unit'] not in ('NOK', 'NOK_thousand'):
        raise ValueError('Enhet må være NOK eller NOK_thousand.')
    opening = amount(data['opening'])
    expected_total = amount(data['expected_total'])
    proposed_total = amount(data['proposed_total'])
    rows = []
    expected_changes = []
    proposed_changes = []
    differences = []
    identifiers = set()
    for row in data['rows']:
        if row['id'] in identifiers:
            raise ValueError(f'Duplikat komponent: {row["id"]}')
        identifiers.add(row['id'])
        expected = amount(row['expected'])
        proposed = amount(row['proposed'])
        difference = None if expected is None or proposed is None else proposed - expected
        expected_changes.append(expected)
        proposed_changes.append(proposed)
        differences.append(difference)
        rows.append({**row, 'difference': None if difference is None else str(difference)})
    checks = {
        'expected_residual': residual(expected_total, opening, expected_changes),
        'proposed_residual': residual(proposed_total, opening, proposed_changes),
        'difference_residual': residual(proposed_total, expected_total, differences),
    }
    status = 'avstemt'
    if any(value is None for value in checks.values()):
        status = 'ufullstendig'
    elif any(Decimal(value) != 0 for value in checks.values()):
        status = 'avvik'
    total_difference = residual(proposed_total, expected_total, [])
    return {**data, 'rows': rows, 'total_difference': total_difference, **checks, 'status': status}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8'))
    result = reconcile(data)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{result["status"]}: {args.output}')
    raise SystemExit(0 if result['status'] == 'avstemt' else 2)
