"""Finn og parse hovedtabellen i blått hefte (institusjon per rad, beløp i 1 000 kroner).

Input er tekstuttrekket fra extract_documents.py med sidemarkører "=== PDF-side N ===".
Tabellsiden er den første siden der en linje begynner med UiT-navnet og har minst
--min-columns tall. Alle institusjonsrader på siden parses; en strek betyr null.
Kolonneoverskriftene varierer fra år til år og må leses av en person eller agent,
derfor legges linjene over tabellen ved som header_lines. Skriptet tolker ikke
kolonnene og kontrollerer bare at siste tall er summen av de foregående.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PAGE_MARK = re.compile(r"^=== PDF-side (\d+) ===\s*$")
NUMBER = re.compile(r"^-?\d{1,3}(?: \d{3})*$|^-$")
UIT_NAMES = ("UiT", "Universitetet i Tromsø", "Universitetet i Tromsö", "UiT Noregs arktiske universitet")


def split_pages(text: str) -> dict[int, list[str]]:
    pages: dict[int, list[str]] = {}
    current = 0
    for line in text.splitlines():
        match = PAGE_MARK.match(line)
        if match:
            current = int(match.group(1))
            pages.setdefault(current, [])
            continue
        pages.setdefault(current, []).append(line)
    return pages


def parse_row(line: str) -> tuple[str, list[int | None]] | None:
    """«UiT   3 806 533   250 434  ...  -   8 742   4 045 822» -> (navn, tall). Tall skilles av minst to mellomrom."""
    tokens = [t.strip() for t in re.split(r"\s{2,}", line.strip()) if t.strip()]
    if len(tokens) < 3:
        return None
    name = tokens[0]
    values = tokens[1:]
    if not all(NUMBER.match(v) for v in values) or NUMBER.match(name):
        return None
    numbers = [None if v == "-" else int(v.replace(" ", "")) for v in values]
    return name, numbers


def is_uit(name: str) -> bool:
    return any(name.startswith(n) for n in UIT_NAMES)


def find_table(pages: dict[int, list[str]], min_columns: int, min_total: int = 100_000) -> dict:
    """Hovedtabellen kjennetegnes av en UiT-rad der siste tall (forslaget) er minst min_total
    tusen kroner og er summen av kolonnene foran. Kandidattall- og indikatortabeller har små tall."""
    for page in sorted(pages):
        lines = pages[page]
        rows = []
        first_row_index = None
        for index, line in enumerate(lines):
            parsed = parse_row(line)
            if parsed and len(parsed[1]) >= min_columns:
                if first_row_index is None:
                    first_row_index = index
                rows.append({"institution": parsed[0], "values": parsed[1], "line": index})
        uit_rows = [r for r in rows if is_uit(r["institution"])]
        if not any(
            (r["values"][-1] or 0) >= min_total and sum(v or 0 for v in r["values"][:-1]) == r["values"][-1]
            for r in uit_rows
        ):
            continue
        header_lines = [l.strip() for l in lines[max(0, (first_row_index or 0) - 12):first_row_index] if l.strip()]
        column_count = len(next(r for r in uit_rows if (r["values"][-1] or 0) >= min_total)["values"])
        rows = [r for r in rows if len(r["values"]) == column_count]
        for row in rows:
            values = row["values"]
            components = [v or 0 for v in values[:-1]]
            row["sum_check"] = sum(components) == values[-1]
            row.pop("line", None)
        uit = next(r for r in rows if is_uit(r["institution"]))
        return {
            "pdf_page": page,
            "column_count": column_count,
            "header_lines": header_lines,
            "rows": rows,
            "uit": uit,
            "all_rows_sum_to_last_column": all(r["sum_check"] for r in rows),
            "note": "Første kolonne er normalt saldert budsjett året før, siste er forslaget; kolonnene imellom må navngis fra header_lines og kontrolleres mot PDF-siden.",
        }
    return {"pdf_page": None, "rows": [], "uit": None, "error": "Fant ingen side med en UiT-rad med nok tallkolonner."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("extract", type=Path, help="tekstuttrekk av blått hefte")
    parser.add_argument("--min-columns", type=int, default=6)
    parser.add_argument("--min-total", type=int, default=100_000, help="minste forslag i 1 000 kroner for UiT-raden")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = find_table(split_pages(args.extract.read_text(encoding="utf-8")), args.min_columns, args.min_total)
    result["source_extract"] = str(args.extract)
    content = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content + "\n", encoding="utf-8")
    print(content)
    return 0 if result.get("uit") else 2


if __name__ == "__main__":
    sys.exit(main())
