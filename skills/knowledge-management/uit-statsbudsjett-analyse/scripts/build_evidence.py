"""Lager kildeutdrag med markering fra faglig utvalgte PDF-sider og tekstankre."""

import argparse
import hashlib
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory

import pymupdf


def find_anchor(page, anchor, identifier):
    matches = page.search_for(anchor)
    if not matches:
        raise ValueError(f'{identifier}: tekstankeret er ikke funnet: {anchor!r}')
    if len(matches) == 1:
        return matches[0]
    # PDF-er kan dele én tekstlinje i flere tettliggende tekstspenn.
    matches = sorted(matches, key=lambda rect: rect.x0)
    same_line = max(rect.y0 for rect in matches) - min(rect.y0 for rect in matches) < 2
    adjacent = all(right.x0 - left.x1 < 8 for left, right in zip(matches, matches[1:]))
    rectangle = pymupdf.Rect(matches[0])
    for match in matches[1:]:
        rectangle |= match
    text = ' '.join(page.get_textbox(rectangle).split()).casefold()
    needle = ' '.join(anchor.split()).casefold()
    if not same_line or not adjacent or text.count(needle) != 1:
        raise ValueError(f'{identifier}: tekstankeret gir flere treff; velg kort, entydig tekst: {anchor!r}')
    return rectangle


def select_page(item, project):
    source = (project / item['source']).resolve()
    page_number = item['pdf_page']
    if type(page_number) is not int or page_number < 1:
        raise ValueError('pdf_page må være et sidetall fra 1.')
    if not item['anchors']:
        raise ValueError(f'{item["id"]}: mangler tekstankre.')
    with pymupdf.open(source) as original:
        if page_number > len(original):
            raise ValueError(f'{item["id"]}: PDF-siden finnes ikke.')
        document = pymupdf.open()
        document.insert_pdf(original, from_page=page_number - 1, to_page=page_number - 1)
    page = document[0]
    rectangles = []
    for anchor in item['anchors']:
        rectangles.append(find_anchor(page, anchor, item['id']))
    return source, document, rectangles


def mark_page(document, rectangles, item):
    page = document[0]
    for rectangle in rectangles:
        annotation = page.add_highlight_annot(rectangle)
        annotation.set_colors(stroke=(1, 0.8, 0))
        annotation.set_info(title=item['title'], content=f"{item['id']}: {item['claim']}")
        annotation.update()
    return page


def build_evidence(findings, project, output):
    project, output = Path(project), Path(output)
    if (output / 'kildeutdrag.json').exists():
        raise ValueError('Beholder eksisterende kildepakke; velg en ny outputmappe ved revisjon.')
    if any((project / item['source']).resolve() == (output / 'kildeutdrag.pdf').resolve() for item in findings):
        raise ValueError('Kildeutdraget kan ikke overskrive original-PDF-en.')
    output.mkdir(parents=True, exist_ok=True)
    identifiers = [item['id'] for item in findings]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError('Duplikat funn-ID.')
    if any(not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', name) for name in identifiers):
        raise ValueError('Funn-ID må bruke små bokstaver, tall, bindestrek eller understrek.')
    records, notes, toc = [], ['# Markerte kildeutdrag'], []
    with TemporaryDirectory(prefix='.belegg-', dir=output) as temporary:
        staged = Path(temporary)
        (staged / 'bilder').mkdir()
        package = pymupdf.open()
        for item in findings:
            source, document, rectangles = select_page(item, project)
            page = mark_page(document, rectangles, item)
            image_path = f'bilder/{item["id"]}.png'
            page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), annots=True).save(staged / image_path)
            package.insert_pdf(document, annots=True)
            output_page = len(package)
            toc.append([1, f'{item["id"]}: {item["title"]}', output_page])
            records.append({
                'id': item['id'], 'source': item['source'],
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'source_pdf_page': item['pdf_page'], 'printed_page': item.get('printed_page'),
                'output_page': output_page, 'image': image_path,
                'anchors': item['anchors'], 'highlight_count': len(rectangles),
            })
            notes.extend([
                f'\n## {item["id"]}: {item["title"]}', item['claim'],
                f'Kilde: `{item["source"]}`, PDF-side {item["pdf_page"]}, trykt side {item.get("printed_page", "ukjent")}.',
                f'Markert side: [PDF side {output_page}](kildeutdrag.pdf#page={output_page}) · [bilde]({image_path})',
                '\n### Tekst fra hele kildesiden\n', page.get_text(sort=True),
            ])
            document.close()
        if findings:
            package.set_toc(toc)
            package.save(staged / 'kildeutdrag.pdf', garbage=4, deflate=True)
        else:
            notes.append('Ingen kildebelagte funn valgt. Se delrapportens søkeomfang og negative funn.')
        package.close()
        (staged / 'kildeutdrag.md').write_text('\n\n'.join(notes) + '\n', encoding='utf-8')
        (staged / 'kildeutdrag.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        # Publiserer først etter at alle valgte sider er funnet og markert.
        for path in staged.rglob('*'):
            if path.is_file():
                target = output / path.relative_to(staged)
                target.parent.mkdir(parents=True, exist_ok=True)
                path.replace(target)
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('findings', type=Path)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    findings = json.loads(args.findings.read_text(encoding='utf-8'))
    records = build_evidence(findings, args.project, args.output)
    print(f'{len(records)} kildeutdrag kontrollert og lagret i {args.output}')
