"""Bygg Excel-arbeidsboken som forklarer UiTs ramme i budsjettforslaget.

Samme faste ark hvert år, etter mønster fra UiTs arbeidsbøker 2018–2019:
  Sektor        institusjon, saldert året før, forslag, nominell endring i prosent, sum
  UiT-bro       saldert året før, hver justering fra blått heftes UiT-rad, forslag (SUM), kontroll mot tabellen
  Mot foreløpig UiTs foreløpige fordeling mot forslaget per komponent, avvik (bare når input har «preliminary»)
  Kilder        dokument, URL, SHA-256, PDF-side, kolonnetolkning, kontroller

Input er én JSON-fil (se INPUT_EXAMPLE) som fylles fra parse_blaatt_hefte_table.py og
kolonnetolkningen. Formler skrives med beregnet verdi, slik at tallene vises også
uten omberegning. Beløp i 1 000 kroner.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

INPUT_EXAMPLE = {
    "year": 2024,
    "stage": "regjeringens opprinnelige forslag",
    "source": {"title": "Orientering om forslag til statsbudsjettet 2024", "url": "https://...", "sha256": "…", "pdf_page": 16, "fetched_at_utc": "…"},
    "columns": [
        {"key": "saldert", "label": "Saldert budsjett 2023"},
        {"key": "pris", "label": "Pris- og lønnsjustering inkl. videreført RNB"},
        {"key": "forslag", "label": "Forslag 2024"},
    ],
    "institutions": [{"name": "UiT", "values": [3806533, 250434, 4045822]}],
    "uit_name": "UiT",
    "previous_year": {"vedtatt_total": 3806533, "source": "Orientering om statsbudsjettet 2023 etter vedtak i Stortinget, UiT-raden, PDF-side 16", "url": "https://..."},
    "price": {"column_key": "pris", "rate_pct": 4.4, "note": "inkluderer videreført RNB-kompensasjon", "source_page": 14},
    "preliminary": {
        "source": "UiT S 18/23 vedlegg 1 s. 3",
        "expected_total": 3959565,
        "rows": [{"tema": "Pris og videreført RNB", "uit": 208631, "forslag": 250434}],
    },
    "checks": {"reconcile_status": "avstemt"},
}


def load_writer():
    try:
        import xlsxwriter  # noqa: WPS433
    except ImportError as error:  # pragma: no cover
        raise SystemExit("xlsxwriter mangler i miljøet; installer fra requirements-observed.txt") from error
    return xlsxwriter


def col(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def build(data: dict, output: Path) -> dict:
    xlsxwriter = load_writer()
    year = data["year"]
    columns = data["columns"]
    institutions = data["institutions"]
    uit_name = data.get("uit_name", "UiT")
    if len(columns) < 2:
        raise ValueError("columns må ha minst saldert og forslag")
    for inst in institutions:
        if len(inst["values"]) != len(columns):
            raise ValueError(f"{inst['name']}: {len(inst['values'])} verdier, {len(columns)} kolonner")
    uit = next((i for i in institutions if i["name"] == uit_name), None)
    if uit is None:
        raise ValueError(f"finner ikke {uit_name} blant institusjonene")

    output.parent.mkdir(parents=True, exist_ok=True)
    book = xlsxwriter.Workbook(str(output))
    bold = book.add_format({"bold": True})
    head = book.add_format({"bold": True, "bottom": 1, "text_wrap": True, "valign": "top"})
    num = book.add_format({"num_format": "# ##0"})
    num_bold = book.add_format({"num_format": "# ##0", "bold": True})
    pct = book.add_format({"num_format": "0.0 %"})
    pct_bold = book.add_format({"num_format": "0.0 %", "bold": True})
    hilite = book.add_format({"bold": True, "bg_color": "#FFF2CC"})
    hilite_num = book.add_format({"bold": True, "bg_color": "#FFF2CC", "num_format": "# ##0"})
    hilite_pct = book.add_format({"bold": True, "bg_color": "#FFF2CC", "num_format": "0.0 %"})
    wrap = book.add_format({"text_wrap": True, "valign": "top"})
    summary = {}

    # --- Sektor -----------------------------------------------------------------
    sheet = book.add_worksheet("Sektor")
    sheet.set_column(0, 0, 34)
    sheet.set_column(1, 3, 18)
    sheet.write(0, 0, f"Statsbudsjettet {year}: {data.get('stage', '')}. Beløp i 1 000 kroner. Kilde: {data['source'].get('title', '')}, PDF-side {data['source'].get('pdf_page', '')}.", wrap)
    sheet.write_row(2, 0, ["Institusjon", columns[0]["label"], columns[-1]["label"], "Nominell endring"], head)
    first_row = 3
    for offset, inst in enumerate(institutions):
        r = first_row + offset
        is_uit = inst["name"] == uit_name
        saldert, forslag = inst["values"][0] or 0, inst["values"][-1] or 0
        change = (forslag - saldert) / saldert if saldert else 0
        sheet.write(r, 0, inst["name"], hilite if is_uit else None)
        sheet.write_number(r, 1, saldert, hilite_num if is_uit else num)
        sheet.write_number(r, 2, forslag, hilite_num if is_uit else num)
        sheet.write_formula(r, 3, f"=IF(B{r + 1}=0,0,(C{r + 1}-B{r + 1})/B{r + 1})", hilite_pct if is_uit else pct, change)
    last_row = first_row + len(institutions) - 1
    total_row = last_row + 2
    sum_saldert = sum(i["values"][0] or 0 for i in institutions)
    sum_forslag = sum(i["values"][-1] or 0 for i in institutions)
    sheet.write(total_row, 0, "Sum", bold)
    sheet.write_formula(total_row, 1, f"=SUM(B{first_row + 1}:B{last_row + 1})", num_bold, sum_saldert)
    sheet.write_formula(total_row, 2, f"=SUM(C{first_row + 1}:C{last_row + 1})", num_bold, sum_forslag)
    sheet.write_formula(total_row, 3, f"=IF(B{total_row + 1}=0,0,(C{total_row + 1}-B{total_row + 1})/B{total_row + 1})", pct_bold, (sum_forslag - sum_saldert) / sum_saldert if sum_saldert else 0)
    uit_saldert, uit_forslag = uit["values"][0] or 0, uit["values"][-1] or 0
    summary["uit_saldert"] = uit_saldert
    summary["uit_forslag"] = uit_forslag
    summary["uit_change_pct"] = round((uit_forslag - uit_saldert) / uit_saldert * 100, 3) if uit_saldert else None
    summary["sector_change_pct"] = round((sum_forslag - sum_saldert) / sum_saldert * 100, 3) if sum_saldert else None

    # --- UiT-bro ----------------------------------------------------------------
    sheet = book.add_worksheet("UiT-bro")
    sheet.set_column(0, 0, 58)
    sheet.set_column(1, 2, 18)
    sheet.write(0, 0, f"Budsjettforslag {year} for {uit_name} inkl. justeringer. Beløp i 1 000 kroner.", bold)
    sheet.write_row(2, 0, ["Post", "Beløp", "Merknad"], head)
    sheet.write(3, 0, columns[0]["label"])
    sheet.write_number(3, 1, uit_saldert, num)
    price = data.get("price") or {}
    price_key = price.get("column_key", "pris")
    row = 4
    for index in range(1, len(columns) - 1):
        value = uit["values"][index]
        note = columns[index].get("note", "") or ("strek i tabellen" if value is None else "")
        if price and columns[index].get("key") == price_key and price.get("rate_pct") is not None:
            note = f"Sats {price['rate_pct']} %" + (f", {price['note']}" if price.get("note") else "") + (f" (PDF-side {price['source_page']})" if price.get("source_page") else "")
        sheet.write(row, 0, columns[index]["label"])
        sheet.write_number(row, 1, value or 0, num)
        sheet.write(row, 2, note)
        row += 1
    components_sum = uit_saldert + sum(v or 0 for v in uit["values"][1:-1])
    sheet.write(row, 0, columns[-1]["label"], bold)
    sheet.write_formula(row, 1, f"=SUM(B4:B{row})", num_bold, components_sum)
    sheet.write(row + 1, 0, "Forslag ifølge tabellen i blått hefte")
    sheet.write_number(row + 1, 1, uit_forslag, num)
    sheet.write(row + 2, 0, "Kontroll: sum av justeringer minus tabellens forslag (skal være 0)")
    sheet.write_formula(row + 2, 1, f"=B{row + 1}-B{row + 2}", num_bold, components_sum - uit_forslag)
    summary["bridge_residual"] = components_sum - uit_forslag
    previous = data.get("previous_year")
    if previous and previous.get("vedtatt_total") is not None:
        vedtatt = int(previous["vedtatt_total"])
        sheet.write(row + 4, 0, f"Vedtatt budsjett {year - 1} ifølge blått hefte etter vedtak i Stortinget")
        sheet.write_number(row + 4, 1, vedtatt, num)
        sheet.write(row + 4, 2, previous.get("source", ""))
        sheet.write(row + 5, 0, f"Kontroll: saldert {year - 1} i tabellen minus vedtatt {year - 1} (skal være 0)")
        sheet.write_formula(row + 5, 1, f"=B4-B{row + 5}", num_bold, uit_saldert - vedtatt)
        summary["previous_year_residual"] = uit_saldert - vedtatt
    if price.get("rate_pct") is not None:
        summary["price_rate_pct"] = price["rate_pct"]

    # --- Mot foreløpig ----------------------------------------------------------
    preliminary = data.get("preliminary")
    if preliminary:
        sheet = book.add_worksheet("Mot foreløpig")
        sheet.set_column(0, 0, 48)
        sheet.set_column(1, 3, 18)
        sheet.set_column(4, 4, 50)
        sheet.write(0, 0, f"UiTs foreløpige fordeling mot forslaget {year}. Positivt avvik = høyere bevilgning enn UiT la til grunn. Kilde UiT: {preliminary.get('source', '')}.", wrap)
        sheet.write_row(2, 0, ["Komponent", "UiT foreløpig", "Forslag", "Avvik", "Kilde / merknad"], head)
        r = 3
        for item in preliminary["rows"]:
            sheet.write(r, 0, item["tema"])
            sheet.write_number(r, 1, item.get("uit") or 0, num)
            sheet.write_number(r, 2, item.get("forslag") or 0, num)
            sheet.write_formula(r, 3, f"=C{r + 1}-B{r + 1}", num, (item.get("forslag") or 0) - (item.get("uit") or 0))
            sheet.write(r, 4, item.get("kilde", ""), wrap)
            r += 1
        expected_total = preliminary.get("expected_total")
        sheet.write(r + 1, 0, "Sum komponenter", bold)
        sheet.write_formula(r + 1, 1, f"=SUM(B4:B{r})", num_bold, sum(i.get("uit") or 0 for i in preliminary["rows"]))
        sheet.write_formula(r + 1, 2, f"=SUM(C4:C{r})", num_bold, sum(i.get("forslag") or 0 for i in preliminary["rows"]))
        sheet.write_formula(r + 1, 3, f"=SUM(D4:D{r})", num_bold, sum((i.get("forslag") or 0) - (i.get("uit") or 0) for i in preliminary["rows"]))
        if expected_total is not None:
            sheet.write(r + 3, 0, "UiTs foreløpige KD-ramme", bold)
            sheet.write_number(r + 3, 1, expected_total, num_bold)
            sheet.write(r + 4, 0, "Forslag", bold)
            sheet.write_number(r + 4, 2, uit_forslag, num_bold)
            sheet.write(r + 5, 0, "Avvik ramme", bold)
            sheet.write_formula(r + 5, 3, f"=C{r + 5}-B{r + 4}", num_bold, uit_forslag - expected_total)
            summary["preliminary_total"] = expected_total
            summary["difference_vs_preliminary"] = uit_forslag - expected_total

    # --- Kilder -----------------------------------------------------------------
    sheet = book.add_worksheet("Kilder")
    sheet.set_column(0, 0, 32)
    sheet.set_column(1, 1, 100)
    source = data["source"]
    rows = [
        ("Dokument", source.get("title", "")),
        ("Stadium", data.get("stage", "")),
        ("URL", source.get("url", "")),
        ("SHA-256", source.get("sha256", "")),
        ("PDF-side for tabellen", str(source.get("pdf_page", ""))),
        ("Hentet (UTC)", source.get("fetched_at_utc", "")),
        ("Generert av", "build_frame_workbook.py; tall fra parse_blaatt_hefte_table.py, kolonner tolket og kontrollert visuelt mot PDF-siden"),
    ]
    if previous:
        rows.append((f"Vedtatt {year - 1}", f"{previous.get('vedtatt_total', '')} fra {previous.get('source', '')}" + (f", URL {previous['url']}" if previous.get("url") else "")))
    if price:
        rows.append(("Prisjustering", f"sats {price.get('rate_pct', 'ukjent')} %" + (f"; {price['note']}" if price.get("note") else "") + (f"; PDF-side {price['source_page']}" if price.get("source_page") else "")))
    for index, column in enumerate(columns):
        rows.append((f"Kolonne {index + 1}", f"{column['label']}" + (f" ({column.get('header_text')})" if column.get("header_text") else "")))
    for key, value in (data.get("checks") or {}).items():
        rows.append((f"Kontroll: {key}", str(value)))
    for r, (k, v) in enumerate(rows):
        sheet.write(r, 0, k, bold)
        sheet.write(r, 1, v, wrap)
    book.close()
    summary["output"] = str(output)
    summary["sheets"] = ["Sektor", "UiT-bro"] + (["Mot foreløpig"] if preliminary else []) + ["Kilder"]
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("input", type=Path, help="JSON-fil, se INPUT_EXAMPLE i skriptet")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--example", action="store_true", help="skriv eksempelinput til stdout og avslutt")
    args = parser.parse_args(argv)
    if args.example:
        print(json.dumps(INPUT_EXAMPLE, ensure_ascii=False, indent=2))
        return 0
    summary = build(json.loads(args.input.read_text(encoding="utf-8")), args.output)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["bridge_residual"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
