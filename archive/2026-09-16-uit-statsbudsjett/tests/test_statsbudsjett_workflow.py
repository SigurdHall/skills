import hashlib
import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / 'skills/knowledge-management/uit-statsbudsjett-analyse/scripts/manage_workflow.py'
spec = importlib.util.spec_from_file_location('budget_workflow', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def config():
    return {'budget_year': 2024, 'run_id': '2024-v2', 'stage': 'forslag',
            'history_years': [2023],
            'roles': [{'id': 'hod', 'parts': ['hod'], 'keywords': ['Tromso'],
                       'history': 'arbeidsminne/hod/historikk.md'}],
            'editor': {'id': 'redaktor', 'history': 'arbeidsminne/redaktor/historikk.md',
                       'deliverables': ['samlet-rapport.md', 'deck.pptx', 'melding.md']}}


def test_preparation_requires_saved_role_memory_and_does_not_fabricate_it(tmp_path):
    module.prepare_work_orders(config(), tmp_path)
    order = tmp_path / 'leveranser/2024-v2/oppdrag/hod.md'
    assert 'arbeidsminne/hod/historikk.md' in order.read_text()
    assert 'Tromso' in order.read_text()
    assert not (tmp_path / 'arbeidsminne/hod/historikk.md').exists()
    result = module.check_delivery(config(), tmp_path)
    assert not result['ready']
    assert any('historikk.md' in issue for issue in result['issues'])
    assert any('deck.pptx' in issue for issue in result['issues'])


def test_changed_memory_after_receipt_is_detected(tmp_path):
    memory = tmp_path / 'arbeidsminne/hod/historikk.md'
    memory.parent.mkdir(parents=True)
    memory.write_text('Historisk erfaring 2023 med kilder')
    receipt = tmp_path / 'leveranser/2024-v2/deler/hod/minne-lest.json'
    receipt.parent.mkdir(parents=True)
    receipt.write_text(json.dumps({'role': 'hod', 'sha256': hashlib.sha256(memory.read_bytes()).hexdigest()}))
    memory.write_text('En annen erfaring')
    result = module.check_delivery(config(), tmp_path)
    assert any('Minnet er endret' in issue for issue in result['issues'])


def test_part_requires_matching_highlighted_evidence(tmp_path):
    part = tmp_path / 'hod'
    part.mkdir()
    (part / 'notater.md').write_text('Sok og avviste treff')
    (part / 'rapport.md').write_text('Ferdig rapport')
    (part / 'funn.json').write_text(json.dumps([{'id': 'hod-funn'}]))
    (part / 'belegg').mkdir()
    (part / 'belegg/kildeutdrag.json').write_text('[]')
    issues = module.check_part(part)
    assert any('kildeutdrag' in issue for issue in issues)


def test_missing_hash_is_not_reported_as_changed_memory(tmp_path):
    memory = tmp_path / 'historikk.md'
    memory.write_text('Erfaring med kilder')
    receipt = tmp_path / 'minne.json'
    receipt.write_text(json.dumps({'role': 'hod', 'read_at_utc': '2026-09-14T08:00:00Z'}))
    issues = module.check_memory({'id': 'hod', 'history': 'historikk.md'}, tmp_path, receipt)
    assert any('Mangler sha256' in issue for issue in issues)
    assert not any('Minnet er endret' in issue for issue in issues)
