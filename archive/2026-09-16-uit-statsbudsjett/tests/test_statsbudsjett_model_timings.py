import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / 'skills/knowledge-management/uit-statsbudsjett-analyse/scripts/analyze_model_timings.py'
spec = importlib.util.spec_from_file_location('model_timings', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def message(elapsed, text):
    return {'elapsed_s': elapsed, 'event': {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': text}}}


def test_structured_commentary_counts_as_early_content_without_altering_time():
    events = [message(6, '{"summary":"Mottatt","facts":[]}'),
              message(40, '{"summary":"FORELOPIG: Kilden sier 7,3 mill.","facts":[]}'),
              message(70, '{"summary":"Ferdig","facts":[1]}')]
    result = module.content_times(events, {'summary': 'Ferdig', 'facts': [1]})
    assert result['first_provisional_s'] == 40
    assert result['final_content_s'] == 70
    assert result['final_time_basis'] == 'matching_final_answer_event'


def test_mention_of_marker_is_not_a_provisional_response():
    events = [message(7, '{"summary":"Jeg vil senere skrive FORELOPIG:","facts":[]}')]
    assert module.content_times(events, None)['first_provisional_s'] is None


def test_invalid_cli_line_is_reported_without_losing_later_valid_timing():
    events = [{'elapsed_s': 5, 'parse_error':'ugyldig JSON', 'raw_line':'warning'},
              message(40, '{"summary":"FORELOPIG: kilde funnet"}'),
              message(80, '{"summary":"Ferdig"}')]
    result = module.content_times(events, {'summary':'Ferdig'})
    assert result['invalid_event_records'] == 1
    assert result['first_provisional_s'] == 40
    assert result['final_content_s'] == 80


def test_review_deadline_includes_queue_after_luna_content():
    draft = {'status':'succeeded','started_monotonic_s':100,'final_content_s':40,'process_exit_elapsed_s':50}
    review = {'status':'succeeded','started_monotonic_s':155,'final_content_s':290}
    result = module.review_times(draft, review)
    assert result['review_wait_from_draft_s'] == 15
    assert result['review_after_draft_s'] == 305
    assert result['review_within_300s_of_draft'] is False


def test_missing_or_failed_review_never_meets_deadline():
    draft = {'status':'succeeded','started_monotonic_s':100,'final_content_s':40}
    review = {'status':'failed','started_monotonic_s':150,'final_content_s':None}
    assert module.review_times(draft, review)['review_within_300s_of_draft'] is False


def test_pair_clock_starts_at_earliest_actual_answer_and_includes_wait():
    luna = {'job_id':'luna', 'status':'succeeded', 'started_monotonic_s':100,
            'first_provisional_s':60, 'final_content_s':200}
    sol = {'job_id':'sol', 'status':'succeeded', 'started_monotonic_s':102,
           'first_provisional_s':30, 'final_content_s':100}
    review = {'status':'succeeded', 'started_monotonic_s':305, 'final_content_s':250}
    result = module.pair_times([luna, sol], review)
    assert result['first_draft_job_id'] == 'sol'
    assert result['pair_first_draft_s'] == 102
    assert result['pair_first_provisional_s'] == 32
    assert result['review_after_first_draft_s'] == 353
    assert result['review_after_first_provisional_s'] == 423
    assert result['pair_review_total_s'] == 455
    assert result['review_wait_from_both_drafts_s'] == 5
    assert result['review_within_300s_of_first_draft'] is False


def test_pair_with_failed_independent_job_does_not_claim_completed_review():
    drafts = [{'job_id':'luna', 'status':'succeeded', 'started_monotonic_s':100,
               'first_provisional_s':20, 'final_content_s':80},
              {'job_id':'sol', 'status':'failed', 'started_monotonic_s':100,
               'first_provisional_s':25, 'final_content_s':None}]
    review = {'status':'failed', 'started_monotonic_s':190, 'final_content_s':None}
    result = module.pair_times(drafts, review)
    assert result['pair_first_draft_s'] == 80
    assert result['pair_review_total_s'] is None
    assert result['review_within_300s_of_first_draft'] is False


def test_table_keeps_requested_and_observed_tier_separate_and_labels_missing_time():
    data = {'jobs':[{'job_id':'a', 'status':'failed',
                     'requested':{'model':'gpt-5.6-luna','effort':'max','service_tier':'priority'},
                     'actual_service_tier':None, 'first_provisional_s':10.24,
                     'final_content_s':None, 'usage':{'input_tokens':100,'cached_input_tokens':20,'output_tokens':30}}]}
    table = module.timing_table(data)
    assert '| priority | ukjent |' in table
    assert '| 10.2 | — |' in table
    assert '| failed |' in table
    assert 'Sekunder' in table
