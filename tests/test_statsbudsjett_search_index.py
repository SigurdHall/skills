import importlib.util
from pathlib import Path

import pymupdf


SCRIPT = Path(__file__).parents[1] / 'skills/knowledge-management/uit-statsbudsjett-analyse/scripts/build_search_index.py'
spec = importlib.util.spec_from_file_location('search_index', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_index_keeps_all_matching_pages_and_avoids_substring_name_match(tmp_path):
    source = tmp_path / 'source.pdf'
    with pymupdf.open() as doc:
        doc.new_page().insert_text((50,70), 'Kontinuitet er viktig')
        doc.new_page().insert_text((50,70), 'UiT mottar et tilskudd')
        doc.new_page().insert_text((50,70), 'Ogsaa UiT her')
        doc.save(source)
    records = module.index_pdf(source, [r'\bUiT\b'])
    assert [record['pdf_page'] for record in records] == [2,3]
    assert all(record['source'] == 'source.pdf' for record in records)
    assert 'UiT mottar' in records[0]['excerpts'][0]
