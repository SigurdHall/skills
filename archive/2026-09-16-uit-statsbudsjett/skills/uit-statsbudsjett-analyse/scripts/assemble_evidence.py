"""Samler delenes markerte PDF-utdrag med bokmerker og sporbar sideindeks."""

import argparse
import json
from pathlib import Path

import pymupdf


def assemble(parts, output):
    output = Path(output)
    if any(output.resolve() == (Path(part['directory']) / 'kildeutdrag.pdf').resolve() for part in parts):
        raise ValueError('Samlefilen kan ikke overskrive et delvedlegg.')
    document = pymupdf.open()
    index, toc = [], []
    for part in parts:
        folder = Path(part['directory'])
        records = json.loads((folder / 'kildeutdrag.json').read_text(encoding='utf-8'))
        if not records:
            continue
        offset = len(document)
        with pymupdf.open(folder / 'kildeutdrag.pdf') as source:
            document.insert_pdf(source, annots=True)
        toc.append([1, f'{part["role"]} / {part["part"]}', offset + 1])
        for record in records:
            package_page = offset + record['output_page']
            if not offset < package_page <= len(document):
                raise ValueError(f'Ugyldig sidereferanse i {folder}')
            toc.append([2, record['id'], package_page])
            index.append({**record, 'role': part['role'], 'part': part['part'], 'package_page': package_page})
    output.parent.mkdir(parents=True, exist_ok=True)
    if len(document):
        document.set_toc(toc)
        document.save(output, garbage=4, deflate=True)
    document.close()
    output.with_suffix('.json').write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return index


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    run = args.project / 'leveranser' / config['run_id']
    parts = []
    for role in config['roles']:
        for part in role['parts']:
            parts.append({'role': role['id'], 'part': part, 'directory': run / 'deler' / role['id'] / part / 'belegg'})
    index = assemble(parts, args.output)
    print(f'{len(index)} funn samlet i {args.output}')
