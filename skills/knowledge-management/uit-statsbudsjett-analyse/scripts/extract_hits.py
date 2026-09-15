"""Programmatisk søk i tekstuttrekkene: treff med avsnittet før og etter, per del.

Input er arbeidsdelingen (roller med deler og søkeord) og mappen med .txt-uttrekk fra
extract_documents.py ("=== PDF-side N ===" som sidemarkører). For hver del skrives
<del>-treff.json og <del>-treff.md med treffavsnitt, ett avsnitt før og ett etter,
PDF-side og søkeord. Dette er mekaniske treff for faglig tolkning; skriptet vurderer
ikke relevans, og fravær av treff beviser ikke fravær av tiltak.

Avsnitt er tekstblokker skilt av blanke linjer. Sider uten blanke linjer deles i
vinduer på --window linjer. Korte søkeord (til og med fire tegn) krever ordgrense,
slik at «UiT» ikke treffer «kontinuitet».
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PAGE_MARK = re.compile(r"^=== PDF-side (\d+) ===\s*$")
# «Tromsø» alene står ikke her: det ga hundrevis av treff om by og politi i JD. Roller som
# trenger stedsnavnet, legger det i sine egne søkeord.
GLOBAL_KEYWORDS = [
    "UiT", "Universitetet i Tromsø", "Universitetet i Tromsö", "Noregs arktiske universitet", "Norges arktiske universitet",
    "Norges arktiske universitetsmuseum", "Tromsø Museum",
]
# Hvilke uttrekk hver del leser. <del>-prop-<år>.txt er standard.
SOURCE_FILES = {
    "ramme": ["blaatt-hefte-forslag-{year}.txt", "kd-prop-{year}.txt"],
    "kd": ["kd-prop-{year}.txt"],
    "fin": ["fin-skatt-prop-{year}.txt"],
}


def split_pages(text: str) -> list[tuple[int, list[str]]]:
    pages: list[tuple[int, list[str]]] = []
    current = 0
    lines: list[str] = []
    for line in text.splitlines():
        match = PAGE_MARK.match(line)
        if match:
            if lines or pages:
                pages.append((current, lines))
            current = int(match.group(1))
            lines = []
            continue
        lines.append(line)
    pages.append((current, lines))
    return [(p, l) for p, l in pages if any(s.strip() for s in l)]


def paragraphs(lines: list[str], window: int) -> list[str]:
    blocks: list[str] = []
    block: list[str] = []
    for line in lines:
        if line.strip():
            block.append(line.rstrip())
        elif block:
            blocks.append("\n".join(block))
            block = []
    if block:
        blocks.append("\n".join(block))
    if len(blocks) <= 1 and len(lines) > window * 2:
        text_lines = [l.rstrip() for l in lines if l.strip()]
        blocks = ["\n".join(text_lines[i:i + window]) for i in range(0, len(text_lines), window)]
    return blocks


def pattern_for(keyword: str) -> re.Pattern:
    escaped = re.escape(keyword).replace(r"\ ", r"\s+")
    if len(keyword) <= 4:
        return re.compile(rf"(?<![\wæøåÆØÅ]){escaped}(?![\wæøåÆØÅ])", re.IGNORECASE)
    return re.compile(escaped, re.IGNORECASE)


def find_hits(text: str, keywords: list[str], window: int = 4) -> list[dict]:
    patterns = [(k, pattern_for(k)) for k in keywords]
    hits: list[dict] = []
    for page, lines in split_pages(text):
        blocks = paragraphs(lines, window)
        seen: set[int] = set()
        for index, block in enumerate(blocks):
            matched = [k for k, p in patterns if p.search(block)]
            if not matched or index in seen:
                continue
            seen.add(index)
            hits.append({
                "pdf_page": page,
                "keywords": matched,
                "before": blocks[index - 1] if index > 0 else "",
                "hit": block,
                "after": blocks[index + 1] if index + 1 < len(blocks) else "",
            })
    return hits


def sources_for(part: str, year: int) -> list[str]:
    return [name.format(year=year) for name in SOURCE_FILES.get(part, [f"{part}-prop-{year}.txt"])]


def render_markdown(part: str, year: int, hits_by_file: dict[str, list[dict]], keywords: list[str]) -> str:
    out = [f"# Programmatiske treff: {part}, budsjettår {year}", "",
           f"Søkeord: {', '.join(keywords)}.", "",
           "Mekaniske treff med avsnittet før og etter. Relevans, mottaker, beløp og vilkår må tolkes mot PDF-siden. Fravær av treff beviser ikke fravær av tiltak.", ""]
    for filename, hits in hits_by_file.items():
        out.append(f"## {filename}: {len(hits)} treff")
        out.append("")
        for n, h in enumerate(hits, 1):
            out.append(f"### Treff {n}, PDF-side {h['pdf_page']}, søkeord: {', '.join(h['keywords'])}")
            out.append("")
            if h["before"]:
                out.append("> " + h["before"].replace("\n", "\n> "))
                out.append(">")
            out.append("> **" + h["hit"].replace("\n", "**\n> **") + "**")
            if h["after"]:
                out.append(">")
                out.append("> " + h["after"].replace("\n", "\n> "))
            out.append("")
    return "\n".join(out) + "\n"


def run(config: dict, sources_dir: Path, output: Path, year: int, window: int, extra: list[str]) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    summary = {"year": year, "parts": {}, "missing_sources": []}
    for role in config["roles"]:
        keywords = list(dict.fromkeys(GLOBAL_KEYWORDS + list(role.get("keywords", [])) + extra))
        for part in role["parts"]:
            hits_by_file: dict[str, list[dict]] = {}
            for filename in sources_for(part, year):
                path = sources_dir / filename
                if not path.exists():
                    summary["missing_sources"].append(f"{part}: {filename}")
                    continue
                hits_by_file[filename] = find_hits(path.read_text(encoding="utf-8", errors="replace"), keywords, window)
            (output / f"{part}-treff.json").write_text(json.dumps({"part": part, "role": role["id"], "year": year, "keywords": keywords, "files": hits_by_file}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (output / f"{part}-treff.md").write_text(render_markdown(part, year, hits_by_file, keywords), encoding="utf-8")
            summary["parts"][part] = {name: len(h) for name, h in hits_by_file.items()}
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("config", type=Path, help="arbeidsdeling.json")
    parser.add_argument("--sources-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--year", type=int)
    parser.add_argument("--window", type=int, default=4, help="linjer per vindu på sider uten avsnittsskille")
    parser.add_argument("--extra-keyword", action="append", default=[], help="ekstra søkeord for alle deler")
    args = parser.parse_args(argv)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    year = args.year or config["budget_year"]
    summary = run(config, args.sources_dir, args.output, year, args.window, args.extra_keyword)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not summary["missing_sources"] else 3


if __name__ == "__main__":
    sys.exit(main())
