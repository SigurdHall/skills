import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / 'skills/knowledge-management/uit-statsbudsjett-analyse/scripts/score_model_answers.py'
spec = importlib.util.spec_from_file_location('score_model_answers', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_missing_value_is_not_scored_as_zero_or_correct():
    expected = {'numeric': [{'key': 'delta', 'value': 0, 'unit': 'NOK', 'critical': True}]}
    result = module.score_answer({'facts': [{'key': 'delta', 'value': None, 'unit': 'NOK'}]}, expected)
    assert result['automatic_passed'] == 0
    assert result['checks'][0]['status'] == 'incorrect'


def test_boolean_value_is_not_scored_as_a_number():
    for value in (False, True):
        expected = {'numeric': [{'key': 'delta', 'value': int(value), 'unit': 'NOK'}]}
        answer = {'facts': [{'key': 'delta', 'value': value, 'unit': 'NOK'}]}
        result = module.score_answer(answer, expected)
        assert result['automatic_passed'] == 0
        assert result['checks'][0]['status'] == 'incorrect'


def test_exact_value_with_wrong_unit_fails():
    expected = {'numeric': [{'key': 'delta', 'value': 5, 'unit': 'NOK', 'critical': True}]}
    result = module.score_answer({'facts': [{'key': 'delta', 'value': 5, 'unit': 'percent'}]}, expected)
    assert result['automatic_passed'] == 0


def test_discovery_flags_ui_t_assignment_of_shared_money():
    expected = {'discovery': [{'topic': 'Shared pot', 'terms': ['forskning'], 'value': 50, 'scope': 'shared', 'critical': True}]}
    answer = {'facts': [{'key': 'x', 'statement': 'Forskning får midler', 'conditions': '', 'value': 50, 'unit': 'NOK', 'scope': 'UiT'}]}
    result = module.score_answer(answer, expected)
    assert result['checks'][0]['status'] == 'needs_manual_review'
    assert result['checks'][0]['scope_match'] is False
    assert result['manual_review_required'] is True


def test_discovery_never_claims_semantic_verification_from_terms_alone():
    expected = {'discovery': [{'topic': 'Shared pot', 'terms': ['forskning'], 'value': 50, 'scope': 'shared', 'critical': False}]}
    answer = {'facts': [{'key': 'x', 'statement': 'Forskning', 'conditions': '', 'value': 50, 'unit': 'NOK', 'scope': 'shared'}]}
    result = module.score_answer(answer, expected)
    assert result['checks'][0]['status'] == 'candidate_match'
    assert result['manual_review_required'] is True
