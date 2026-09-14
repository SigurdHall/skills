import importlib.util
import json
from pathlib import Path

import pymupdf


SCRIPT = Path(__file__).parents[1] / 'skills/knowledge-management/uit-statsbudsjett-analyse/scripts/assemble_evidence.py'
spec = importlib.util.spec_from_file_location('assemble_evidence', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_merge_preserves_annotations_and_maps_source_to_package_page(tmp_path):
    parts = []
    for number in [1, 2]:
        folder = tmp_path / str(number)
        folder.mkdir()
        with pymupdf.open() as doc:
            page = doc.new_page()
            page.insert_text((60, 70), f'Kilde {number}')
            page.add_highlight_annot(page.search_for(f'Kilde {number}')[0])
            doc.save(folder / 'kildeutdrag.pdf')
        records = [{'id': f'funn-{number}', 'output_page': 1, 'source_pdf_page': 90 + number}]
        (folder / 'kildeutdrag.json').write_text(json.dumps(records))
        parts.append({'role': 'fag', 'part': str(number), 'directory': folder})
    records = module.assemble(parts, tmp_path / 'samlet.pdf')
    assert [record['package_page'] for record in records] == [1, 2]
    assert [record['source_pdf_page'] for record in records] == [91, 92]
    with pymupdf.open(tmp_path / 'samlet.pdf') as doc:
        assert len(doc) == 2
        assert all(len(list(page.annots())) == 1 for page in doc)
        assert len(doc.get_toc()) == 4
