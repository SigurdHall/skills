import importlib.util
import io
import json
from pathlib import Path
import zipfile

import pytest


SCRIPT = Path(__file__).parents[1] / (
    "skills/knowledge-management/uit-statsbudsjett-analyse/scripts/extract_documents.py"
)
spec = importlib.util.spec_from_file_location("statsbudsjett_extract", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

REL = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SHEET = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DRAWING = "http://schemas.openxmlformats.org/drawingml/2006/main"
PRESENTATION = "http://schemas.openxmlformats.org/presentationml/2006/main"
WORD = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def zip_bytes(parts):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def workbook():
    return zip_bytes({
        "xl/workbook.xml": (
            f'<workbook xmlns="{SHEET}" xmlns:r="{OFFICE_REL}">'
            '<sheets><sheet name="Forutsetninger" sheetId="1" state="hidden" r:id="rId1"/>'
            '</sheets><oleSize ref="A1:C4"/></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            f'<Relationships xmlns="{REL}">'
            f'<Relationship Id="rId1" Type="{OFFICE_REL}/worksheet" '
            'Target="worksheets/sheet1.xml"/></Relationships>'
        ),
        "xl/sharedStrings.xml": (
            f'<sst xmlns="{SHEET}"><si><r><t>Foreløpig </t></r>'
            '<r><t>budsjett</t></r></si></sst>'
        ),
        "xl/worksheets/sheet1.xml": (
            f'<worksheet xmlns="{SHEET}"><sheetData><row r="4">'
            '<c r="A4" t="s"><v>0</v></c>'
            '<c r="B4" t="inlineStr"><is><t>Pris 3,3 %</t></is></c>'
            '<c r="C4"><v>120.50</v></c>'
            '<c r="D4"><f>SUM(C4:C5)</f><v>999.25</v></c>'
            '<c r="E4"><f t="shared" si="2"/></c>'
            '</row></sheetData></worksheet>'
        ),
    })


def test_pptx_preserves_slide_order_notes_and_chart_workbook(tmp_path):
    source = tmp_path / "presentasjon.pptx"
    source.write_bytes(zip_bytes({
        "ppt/presentation.xml": (
            f'<p:presentation xmlns:p="{PRESENTATION}" xmlns:r="{OFFICE_REL}">'
            '<p:sldIdLst><p:sldId id="2" r:id="rId2"/>'
            '<p:sldId id="10" r:id="rId10"/></p:sldIdLst></p:presentation>'
        ),
        "ppt/_rels/presentation.xml.rels": (
            f'<Relationships xmlns="{REL}">'
            f'<Relationship Id="rId10" Type="{OFFICE_REL}/slide" Target="slides/slide10.xml"/>'
            f'<Relationship Id="rId2" Type="{OFFICE_REL}/slide" Target="slides/slide2.xml"/>'
            '</Relationships>'
        ),
        "ppt/slides/slide10.xml": f'<a:p xmlns:a="{DRAWING}"><a:r><a:t>Siste lysark</a:t></a:r></a:p>',
        "ppt/slides/slide2.xml": f'<a:p xmlns:a="{DRAWING}"><a:r><a:t>Første lysark</a:t></a:r></a:p>',
        "ppt/slides/_rels/slide2.xml.rels": (
            f'<Relationships xmlns="{REL}">'
            f'<Relationship Id="n" Type="{OFFICE_REL}/notesSlide" Target="../notesSlides/notesSlide2.xml"/>'
            f'<Relationship Id="c" Type="{OFFICE_REL}/chart" Target="../charts/chart1.xml"/>'
            f'<Relationship Id="e" Type="{OFFICE_REL}/hyperlink" TargetMode="External" '
            'Target="https://example.invalid/skal-ikke-hentes.xlsx"/>'
            '</Relationships>'
        ),
        "ppt/notesSlides/notesSlide2.xml": f'<a:p xmlns:a="{DRAWING}"><a:r><a:t>Forutsetning i notat</a:t></a:r></a:p>',
        "ppt/charts/chart1.xml": '<chart/>',
        "ppt/charts/_rels/chart1.xml.rels": (
            f'<Relationships xmlns="{REL}">'
            f'<Relationship Id="book" Type="{OFFICE_REL}/package" '
            'Target="../embeddings/budsjett.xlsx"/></Relationships>'
        ),
        "ppt/embeddings/budsjett.xlsx": workbook(),
    }))

    result = module.extract_document(source)

    assert result.index("Første lysark") < result.index("Siste lysark")
    assert "Lysark 1" in result and "ppt/slides/slide2.xml" in result
    assert "Forutsetning i notat" in result
    assert "ppt/charts/chart1.xml -> ppt/embeddings/budsjett.xlsx" in result
    assert "Forutsetninger" in result and "Foreløpig budsjett" in result
    assert "Pris 3,3 %" in result
    assert "state=hidden" in result
    assert "OLE-visningsområde: A1:C4" in result
    cells = [json.loads(line) for line in result.splitlines() if line.startswith('{"cell":')]
    total = next(cell for cell in cells if cell["cell"] == "D4")
    assert total["raw"] == total["cached_value"] == "999.25"
    assert total["formula"] == "SUM(C4:C5)"
    assert total["value"] == "999.25"  # Lagret verdi skal ikke regnes om til 120,50
    missing_cache = next(cell for cell in cells if cell["cell"] == "E4")
    assert missing_cache["cached_value"] is None
    assert missing_cache["formula_attributes"] == {"t": "shared", "si": "2"}


def test_docx_preserves_paragraphs_and_table_cell_locations(tmp_path):
    source = tmp_path / "notat.docx"
    source.write_bytes(zip_bytes({
        "word/document.xml": (
            f'<w:document xmlns:w="{WORD}"><w:body>'
            '<w:p><w:r><w:t>Før tabellen</w:t></w:r></w:p>'
            '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Forutsetning</w:t></w:r></w:p></w:tc>'
            '<w:tc><w:p><w:r><w:t>3,3 %</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
            '<w:p><w:r><w:t>Etter tabellen</w:t></w:r></w:p>'
            '</w:body></w:document>'
        ),
    }))

    result = module.extract_document(source)

    assert result.index("Før tabellen") < result.index("3,3 %") < result.index("Etter tabellen")
    assert "Tabell 1, rad 1, celle 2" in result
    assert "Avsnitt 1" in result and "Avsnitt 2" in result
    assert str(source) in result


def test_pdf_preserves_page_numbers_and_source_without_editing_it(tmp_path):
    pymupdf = pytest.importorskip("pymupdf")
    source = tmp_path / "budsjett.pdf"
    with pymupdf.open() as document:
        document.new_page().insert_text((72, 72), "Side en")
        document.new_page().insert_text((72, 72), "Side to")
        document.save(source)
    original = source.read_bytes()

    result = module.extract_document(source)

    assert "PDF-side 1" in result and "PDF-side 2" in result
    assert result.index("Side en") < result.index("Side to")
    assert source.read_bytes() == original


def test_cli_refuses_to_overwrite_any_input(tmp_path):
    source = tmp_path / "bok.xlsx"
    source.write_bytes(workbook())
    original = source.read_bytes()

    with pytest.raises(ValueError, match="kilde"):
        module.main([str(source), "--output", str(source)])

    assert source.read_bytes() == original


def test_ole_binary_is_reported_with_source_and_manual_review():
    data = zip_bytes({
        "ppt/slides/_rels/slide4.xml.rels": (
            f'<Relationships xmlns="{REL}">'
            f'<Relationship Id="rId1" Type="{OFFICE_REL}/oleObject" '
            'Target="../embeddings/oleObject1.bin"/></Relationships>'
        ),
        "ppt/embeddings/oleObject1.bin": b"opaque legacy workbook",
    })
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        result = "\n".join(module.related_assets(archive, "ppt/slides/slide4.xml", set()))

    assert "ppt/slides/slide4.xml -> ppt/embeddings/oleObject1.bin" in result
    assert "ikke lest" in result
    assert "manuell kontroll" in result


def test_docx_preserves_header_footer_dates_and_reports_unread_footnotes(tmp_path):
    source = tmp_path / "datert-notat.docx"
    source.write_bytes(zip_bytes({
        "word/document.xml": (
            f'<w:document xmlns:w="{WORD}"><w:body>'
            '<w:p><w:r><w:t>Arbeidsdeling</w:t></w:r></w:p>'
            '</w:body></w:document>'
        ),
        "word/_rels/document.xml.rels": (
            f'<Relationships xmlns="{REL}">'
            f'<Relationship Id="rId1" Type="{OFFICE_REL}/header" Target="header1.xml"/>'
            f'<Relationship Id="rId2" Type="{OFFICE_REL}/footer" Target="footer1.xml"/>'
            f'<Relationship Id="rId3" Type="{OFFICE_REL}/footnotes" Target="footnotes.xml"/>'
            '</Relationships>'
        ),
        "word/header1.xml": (
            f'<w:hdr xmlns:w="{WORD}"><w:p><w:r><w:t>8. oktober 2018</w:t>'
            '</w:r></w:p></w:hdr>'
        ),
        "word/footer1.xml": (
            f'<w:ftr xmlns:w="{WORD}"><w:p><w:r><w:t>Foreløpig versjon</w:t>'
            '</w:r></w:p></w:ftr>'
        ),
        "word/footnotes.xml": f'<w:footnotes xmlns:w="{WORD}"/>',
    }))

    result = module.extract_document(source)

    assert "word/header1.xml" in result and "8. oktober 2018" in result
    assert "word/footer1.xml" in result and "Foreløpig versjon" in result
    assert "word/document.xml -> word/footnotes.xml" in result
    assert "ikke lest" in result
