import importlib.util
import json
import re
import zipfile
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/knowledge-management/uit-statsbudsjett-analyse/scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(f"statsbudsjett_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


parse = load("parse_blaatt_hefte_table")

PAGE = """=== PDF-side 10 ===
Kandidatmåltal
UiT       50    20    20    12    25    33    20    97    32    39    24    289
=== PDF-side 15 ===
Innleiing
=== PDF-side 16 ===
Tabell 1 Endringar i budsjettramma frå saldert budsjett 2023 til forslag 2024 (i 1 000 kroner)
                Saldert    Pris-      Studie-   Rekrutt.   Resultat  Inndekning  Ukraina  HK-dir   Studie-   Nye    Andre     Forslag
                2023       justering  plassar   stillingar                                          avgift    plassar endringar 2024
NTNU      7 106 019    465 000     12 000      -20 000     30 000      -78 000      -1 000    90 000     -25 000    5 000    2 000    7 586 019
UiT       3 806 533    250 434      2 839      -11 684        -5 085      -42 056        -734     47 724      -10 891                  -      8 742     4 045 822
UiB       4 000 000    260 000      1 000      -10 000       2 000      -44 000        -500     50 000     -12 000        -    1 000    4 247 500
Sum       14 912 552   975 434     15 839     -41 684      26 915     -164 056     -2 234    187 724    -47 891     5 000   11 742   15 879 341
=== PDF-side 17 ===
Forklaring
"""


def test_parse_finds_uit_row_and_checks_sums(tmp_path):
    extract = tmp_path / "blaatt.txt"
    extract.write_text(PAGE, encoding="utf-8")
    result = parse.find_table(parse.split_pages(PAGE), 6)
    # PDF-side 10 har en UiT-rad med små kandidattall og hoppes over; hovedtabellen står på side 16.
    assert result["pdf_page"] == 16 and result["column_count"] == 12
    assert result["uit"]["institution"] == "UiT"
    assert result["uit"]["values"] == [3806533, 250434, 2839, -11684, -5085, -42056, -734, 47724, -10891, None, 8742, 4045822]
    assert result["uit"]["sum_check"] is True
    assert [r["institution"] for r in result["rows"]] == ["NTNU", "UiT", "UiB", "Sum"]
    assert result["all_rows_sum_to_last_column"] is True
    assert any("Saldert" in line for line in result["header_lines"])

    out = tmp_path / "tabell.json"
    assert parse.main([str(extract), "--output", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["uit"]["values"][-1] == 4045822


def test_parse_accepts_current_extractor_page_markers(tmp_path):
    current_format = PAGE.replace("=== PDF-side 10 ===", "## PDF-side 10").replace("=== PDF-side 15 ===", "## PDF-side 15").replace("=== PDF-side 16 ===", "## PDF-side 16").replace("=== PDF-side 17 ===", "## PDF-side 17")
    result = parse.find_table(parse.split_pages(current_format), 6)
    assert result["pdf_page"] == 16 and result["uit"]["values"][-1] == 4045822


def test_parse_reports_missing_table(tmp_path):
    extract = tmp_path / "x.txt"
    extract.write_text("=== PDF-side 1 ===\nIngen tabell her\n", encoding="utf-8")
    assert parse.main([str(extract)]) == 2


def workbook_input(with_preliminary=True):
    columns = [
        {"key": "saldert", "label": "Saldert budsjett 2023"},
        {"key": "pris", "label": "Pris- og lønnsjustering"},
        {"key": "studieplasser", "label": "Studieplassar 2019–2023"},
        {"key": "forslag", "label": "Forslag 2024"},
    ]
    data = {
        "year": 2024,
        "stage": "regjeringens opprinnelige forslag",
        "source": {"title": "Orientering om forslag til statsbudsjettet 2024", "url": "https://example.test/blaatt.pdf", "sha256": "abc", "pdf_page": 16, "fetched_at_utc": "2026-09-15T08:00:00Z"},
        "columns": columns,
        "institutions": [
            {"name": "NTNU", "values": [7000000, 400000, 10000, 7410000]},
            {"name": "UiT", "values": [3806533, 250434, 2839, 4059806]},
        ],
        "uit_name": "UiT",
        "previous_year": {"vedtatt_total": 3806533, "source": "blått hefte 2023 etter vedtak, PDF-side 16"},
        "price": {"column_key": "pris", "rate_pct": 4.4, "note": "inkl. videreført RNB", "source_page": 14},
        "preliminary": {
            "source": "UiT S 18/23 vedlegg 1 s. 3",
            "expected_total": 3959565,
            "rows": [
                {"tema": "Pris og videreført RNB", "uit": 208631, "forslag": 250434, "kilde": "UiT s. 3 / blått s. 15"},
                {"tema": "Studieplasser netto", "uit": 3514, "forslag": 2839},
            ],
        } if with_preliminary else None,
        "checks": {"reconcile_status": "avstemt"},
    }
    return data


def sheet_xml(path, index):
    with zipfile.ZipFile(path) as z:
        return z.read(f"xl/worksheets/sheet{index}.xml").decode("utf-8"), z.read("xl/workbook.xml").decode("utf-8"), z.read("xl/sharedStrings.xml").decode("utf-8")


def test_workbook_has_fixed_sheets_formulas_and_uit_values(tmp_path):
    pytest.importorskip("xlsxwriter")
    build = load("build_frame_workbook")
    out = tmp_path / "uit-ramme-2024.xlsx"
    summary = build.build(workbook_input(), out)
    assert summary["sheets"] == ["Sektor", "UiT-bro", "Mot foreløpig", "Kilder"]
    assert summary["uit_forslag"] == 4059806 and summary["bridge_residual"] == 0
    assert summary["difference_vs_preliminary"] == 4059806 - 3959565
    sektor, workbook, strings = sheet_xml(out, 1)
    assert all(name in workbook for name in ("Sektor", "UiT-bro", "Mot foreløpig", "Kilder"))
    assert "UiT" in strings and "NTNU" in strings
    assert "<f>SUM(B4:B5)</f>" in sektor and "(C4-B4)/B4" in sektor
    assert "<v>3806533</v>" in sektor and "<v>4059806</v>" in sektor
    bro, _, strings2 = sheet_xml(out, 2)
    assert "<f>SUM(B4:B6)</f>" in bro and "<v>4059806</v>" in bro
    assert summary["previous_year_residual"] == 0 and summary["price_rate_pct"] == 4.4
    assert "Sats 4.4 %, inkl. videreført RNB (PDF-side 14)" in strings2
    assert "Vedtatt budsjett 2023 ifølge blått hefte etter vedtak i Stortinget" in strings2
    assert "<f>B4-B11</f>" in bro
    mot, _, _ = sheet_xml(out, 3)
    assert "<f>C4-B4</f>" in mot and "<v>3959565</v>" in mot


def test_workbook_without_preliminary_and_residual_exit_code(tmp_path):
    pytest.importorskip("xlsxwriter")
    build = load("build_frame_workbook")
    data = workbook_input(with_preliminary=False)
    data["institutions"][1]["values"][-1] = 4059807  # tabellen avviker med 1
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(data), encoding="utf-8")
    out = tmp_path / "x.xlsx"
    assert build.main([str(inp), "--output", str(out)]) == 2
    _, workbook, _ = sheet_xml(out, 1)
    assert "Mot foreløpig" not in workbook and "Kilder" in workbook


def test_workbook_rejects_column_mismatch(tmp_path):
    pytest.importorskip("xlsxwriter")
    build = load("build_frame_workbook")
    data = workbook_input()
    data["institutions"][0]["values"].pop()
    with pytest.raises(ValueError):
        build.build(data, tmp_path / "y.xlsx")


def test_parse_on_real_2024_extract_if_present():
    extract = Path("/home/sihal7953/repos/uit-statsbudsjett/analyse/kilder/2024/blaatt-hefte-forslag-2024.txt")
    if not extract.exists():
        pytest.skip("2024-uttrekket finnes bare i WSL-prosjektet")
    result = parse.find_table(parse.split_pages(extract.read_text(encoding="utf-8")), 6)
    assert result["pdf_page"] == 16
    assert result["uit"]["values"][0] == 3806533 and result["uit"]["values"][-1] == 4045822
    assert result["uit"]["sum_check"] is True
    assert re.match(r"UiT", result["uit"]["institution"])
