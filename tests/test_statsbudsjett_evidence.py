import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pymupdf
import pytest


SCRIPT = Path(__file__).parents[1] / 'skills/knowledge-management/uit-statsbudsjett-analyse/scripts/build_evidence.py'
spec = importlib.util.spec_from_file_location('budget_evidence', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def source_pdf(tmp_path):
    path = tmp_path / 'kilde.pdf'
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_text((60, 70), 'Tromso: 7,3 mill. til undersokelsen')
        page.insert_text((60, 100), 'Annen virksomhet: 99 mill.')
        doc.new_page().insert_text((60, 70), 'En helt annen side')
        doc.save(path)
    return path


def finding():
    return {'id': 'hod-1', 'title': 'Undersokelse', 'claim': '7,3 mill.',
            'source': 'kilde.pdf', 'pdf_page': 1, 'printed_page': '88',
            'anchors': ['Tromso: 7,3 mill. til undersokelsen']}


def test_preserves_full_source_page_and_marks_selected_evidence(tmp_path):
    path = source_pdf(tmp_path)
    original = path.read_bytes()
    records = module.build_evidence([finding()], tmp_path, tmp_path / 'resultat')
    with pymupdf.open(tmp_path / 'resultat/kildeutdrag.pdf') as doc:
        page = doc[0]
        assert len(doc) == 1
        assert 'Annen virksomhet' in doc[0].get_text()
        assert len(list(doc[0].annots())) == 1
        assert 'Tromso' in page.get_textbox(list(page.annots())[0].rect)
    assert records[0]['source_pdf_page'] == 1
    assert records[0]['printed_page'] == '88'
    assert records[0]['highlight_count'] == 1
    assert path.read_bytes() == original
    assert (tmp_path / 'resultat/bilder/hod-1.png').exists()


def test_wrong_page_or_missing_anchor_fails_without_finished_package(tmp_path):
    source_pdf(tmp_path)
    item = {**finding(), 'pdf_page': 2}
    with pytest.raises(ValueError, match='ikke funnet'):
        module.build_evidence([item], tmp_path, tmp_path / 'resultat')
    assert not (tmp_path / 'resultat/kildeutdrag.pdf').exists()


def test_ambiguous_anchor_must_be_narrowed(tmp_path):
    source_pdf(tmp_path)
    item = {**finding(), 'anchors': ['mill.']}
    with pytest.raises(ValueError, match='flere treff'):
        module.build_evidence([item], tmp_path, tmp_path / 'resultat')


def test_empty_parts_have_explicit_empty_result(tmp_path):
    records = module.build_evidence([], tmp_path, tmp_path / 'resultat')
    assert records == []
    assert 'Ingen kildebelagte funn' in (tmp_path / 'resultat/kildeutdrag.md').read_text()
    assert not (tmp_path / 'resultat/kildeutdrag.pdf').exists()


def test_existing_package_is_not_silently_replaced(tmp_path):
    source_pdf(tmp_path)
    module.build_evidence([finding()], tmp_path, tmp_path / 'resultat')
    with pytest.raises(ValueError, match='eksisterende'):
        module.build_evidence([], tmp_path, tmp_path / 'resultat')


def test_one_phrase_in_adjacent_pdf_spans_is_one_selection(tmp_path):
    # Gjenskaper fire tekstspenn på samme linje, observert i HOD-PDF-en.
    rects = [pymupdf.Rect(100, 559, 136, 573), pymupdf.Rect(139, 559, 173, 573),
             pymupdf.Rect(176, 559, 182, 573), pymupdf.Rect(185, 559, 272, 573)]
    page = SimpleNamespace(search_for=lambda anchor: rects,
                           get_textbox=lambda rect: '20 mill. kroner i engangsbevilgning')
    result = module.find_anchor(page, '20 mill. kroner i engangsbevilgning', 'hod-1')
    assert result == pymupdf.Rect(100, 559, 272, 573)
