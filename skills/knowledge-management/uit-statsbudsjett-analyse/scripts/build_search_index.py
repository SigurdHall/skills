"""Lager en mekanisk sideindeks fra avtalte søkeord; vurderer ikke relevans."""

import argparse
import json
from pathlib import Path
import re

import pymupdf


def index_pdf(source, patterns):
    source = Path(source)
    regexes = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    records = []
    with pymupdf.open(source) as document:
        for number, page in enumerate(document, 1):
            lines = page.get_text().splitlines()
            matched = set()
            selected = set()
            for index, line in enumerate(lines):
                hits = [pattern.pattern for pattern in regexes if pattern.search(line)]
                if hits:
                    matched.update(hits)
                    selected.update(range(max(0, index - 1), min(len(lines), index + 4)))
            if matched:
                records.append({'source': source.name, 'pdf_page': number,
                                'patterns': sorted(matched),
                                'excerpts': [lines[index] for index in sorted(selected)]})
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdfs', nargs='+', type=Path)
    parser.add_argument('--patterns', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    patterns = json.loads(args.patterns.read_text(encoding='utf-8'))
    records = []
    for source in args.pdfs:
        records.extend(index_pdf(source, patterns))
    lines = ['# Mekanisk søkeindeks',
             'Indeksen viser alle sider med treff på avtalte mønstre. Den er ikke en vurdering av betydning eller en uttømmende funnliste. Kontroller hele originalsiden før en påstand brukes.']
    for record in records:
        lines += [f'\n## {record["source"]} – PDF-side {record["pdf_page"]}',
                  'Treff: ' + ', '.join(record['patterns']), '\n'.join(record['excerpts'])]
    args.output.write_text('\n\n'.join(lines) + '\n', encoding='utf-8')
    args.output.with_suffix('.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(records)} sider med treff indeksert; ingen faglig klassifisering utført.')
