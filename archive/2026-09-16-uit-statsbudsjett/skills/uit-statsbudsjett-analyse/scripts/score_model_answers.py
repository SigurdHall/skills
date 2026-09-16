"""Kontrollerer avtalte tall og finner kandidater til faglig vurdering i modelltester."""

import argparse
import json
from pathlib import Path


def numeric_check(expected, facts):
    matches = [fact for fact in facts if fact.get('key') == expected['key']]
    if len(matches) != 1:
        return {**expected, 'status': 'missing' if not matches else 'duplicate', 'actual': matches}
    fact = matches[0]
    value = fact.get('value')
    correct = type(value) in (int, float) and value == expected['value'] and fact.get('unit') == expected['unit']
    return {**expected, 'status': 'pass' if correct else 'incorrect', 'actual': fact}


def discovery_check(expected, facts):
    matches = []
    for fact in facts:
        text = ' '.join(str(fact.get(key, '')) for key in ['key', 'statement', 'recipient', 'conditions']).casefold()
        if any(term.casefold() in text for term in expected['terms']):
            matches.append(fact)
    accepted_values = [expected['value']]
    if 'alternative_change' in expected:
        accepted_values.append(expected['alternative_change'])
    value_matches = [fact for fact in matches if fact.get('value') in accepted_values]
    scope_match = any(fact.get('scope') == expected['scope'] for fact in value_matches)
    status = 'missing'
    if matches:
        status = 'candidate_match' if value_matches and scope_match else 'needs_manual_review'
    return {**expected, 'status': status, 'value_match': bool(value_matches),
            'scope_match': scope_match, 'candidates': matches}


def score_answer(answer, gold):
    facts = answer.get('facts', [])
    numeric = [numeric_check(expected, facts) for expected in gold.get('numeric', [])]
    discovery = [discovery_check(expected, facts) for expected in gold.get('discovery', [])]
    return {
        'automatic_passed': sum(check['status'] == 'pass' for check in numeric),
        'automatic_total': len(numeric),
        'discovery_candidates': sum(check['status'] == 'candidate_match' for check in discovery),
        'discovery_total': len(discovery),
        'checks': numeric + discovery,
        'manual_review_required': True,
        'scope': 'Eksakte strukturerte tall og søkehjelp. Kildebelegg, vilkår, nye funn og faktisk riktighet vurderes faglig.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('answer', type=Path)
    parser.add_argument('--gold', type=Path, required=True)
    parser.add_argument('--case', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    answer = json.loads(args.answer.read_text(encoding='utf-8'))
    gold = json.loads(args.gold.read_text(encoding='utf-8'))['cases'][args.case]
    result = score_answer(answer, gold)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Tall: {result["automatic_passed"]}/{result["automatic_total"]}; faglig kontroll gjenstår.')
