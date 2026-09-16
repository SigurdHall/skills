import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / 'skills/knowledge-management/uit-statsbudsjett-analyse/scripts/prepare_blind_review.py'
spec = importlib.util.spec_from_file_location('blind_review', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(tmp_path, status='succeeded'):
    run = tmp_path / 'run'
    job = run / 'jobs' / 'sol-priority'
    job.mkdir(parents=True)
    (job / 'metrics.json').write_text(json.dumps({'case_id':'ramme', 'status':status, 'job_id':'sol-priority'}))
    (job / 'answer.txt').write_text('{"summary":"Ramme","facts":[]}')
    (job / 'stderr.txt').write_text('model=sol')
    inputs = tmp_path / 'sources'
    inputs.mkdir()
    (inputs / 'source.txt').write_text('Offentlig kilde')
    gold = tmp_path / 'gold.json'
    gold.write_text(json.dumps({'cases':{'ramme':{'numeric':[]}, 'other':{'secret':'not relevant'}}}))
    return run, inputs, gold


def test_review_package_contains_answers_sources_and_case_gold_only(tmp_path):
    run, inputs, gold = fixture(tmp_path)
    out, mapping = tmp_path / 'blind', tmp_path / 'mapping.json'
    module.prepare(run, 'ramme', inputs, gold, out, mapping, 'fixed')
    assert (out / 'candidate-001.json').read_bytes() == (run / 'jobs/sol-priority/answer.txt').read_bytes()
    assert (out / 'input/source.txt').read_text() == 'Offentlig kilde'
    assert json.loads((out / 'gold.json').read_text()) == {'numeric':[]}
    assert not (out / 'metrics.json').exists()
    assert 'sol-priority' not in '\n'.join(str(p.relative_to(out)) for p in out.rglob('*'))
    assert json.loads(mapping.read_text())['candidates']['candidate-001']['job_id'] == 'sol-priority'


def test_hidden_mapping_must_be_outside_review_package(tmp_path):
    run, inputs, gold = fixture(tmp_path)
    out = tmp_path / 'blind'
    with pytest.raises(ValueError, match='utenfor'):
        module.prepare(run, 'ramme', inputs, gold, out, out / 'map.json', 'fixed')
    assert not out.exists()


def test_failed_jobs_are_recorded_as_excluded_not_successful_answers(tmp_path):
    run, inputs, gold = fixture(tmp_path, status='timeout')
    out, mapping = tmp_path / 'blind', tmp_path / 'mapping.json'
    module.prepare(run, 'ramme', inputs, gold, out, mapping, 'fixed')
    saved = json.loads(mapping.read_text())
    assert saved['candidates'] == {}
    assert saved['excluded'][0]['status'] == 'timeout'


def test_destination_inside_input_is_rejected_before_copy(tmp_path):
    run, inputs, gold = fixture(tmp_path)
    out = inputs / 'blind'
    with pytest.raises(ValueError, match='kilde'):
        module.prepare(run, 'ramme', inputs, gold, out, tmp_path / 'map.json', 'fixed')
    assert not out.exists()
