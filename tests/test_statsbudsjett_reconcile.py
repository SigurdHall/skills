import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / 'skills/knowledge-management/uit-statsbudsjett-analyse/scripts/reconcile_budget.py'
spec = importlib.util.spec_from_file_location('budget_reconcile', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def budget():
    return {
        'unit': 'NOK_thousand', 'opening': '1000.5',
        'expected_total': '1010.5', 'proposed_total': '1015.5',
        'rows': [
            {'id': 'pris', 'expected': '30', 'proposed': '40'},
            {'id': 'kutt', 'expected': '-20', 'proposed': '-25'},
        ],
    }


def test_reconciles_both_totals_and_signed_changes_exactly():
    result = module.reconcile(budget())
    assert result['status'] == 'avstemt'
    assert result['total_difference'] == '5.0'
    assert [row['difference'] for row in result['rows']] == ['10', '-5']
    assert result['expected_residual'] == result['proposed_residual'] == '0.0'


def test_exposes_rounding_residual_instead_of_adjusting_source():
    data = budget()
    data['expected_total'] = '1011.5'
    result = module.reconcile(data)
    assert result['status'] == 'avvik'
    assert result['expected_residual'] == '1.0'
    assert result['difference_residual'] == '-1.0'


def test_unknown_never_becomes_zero():
    data = budget()
    data['rows'][0]['expected'] = None
    result = module.reconcile(data)
    assert result['status'] == 'ufullstendig'
    assert result['rows'][0]['difference'] is None
    assert result['expected_residual'] is None
    assert result['proposed_residual'] == '0.0'


def test_duplicate_components_are_rejected():
    data = budget()
    data['rows'].append(data['rows'][0])
    with pytest.raises(ValueError, match='Duplikat'):
        module.reconcile(data)


@pytest.mark.parametrize('value', [0.1, True, 'NaN', 'Infinity', '1,5'])
def test_rejects_ambiguous_or_nonfinite_numbers(value):
    data = budget()
    data['opening'] = value
    with pytest.raises(ValueError):
        module.reconcile(data)
