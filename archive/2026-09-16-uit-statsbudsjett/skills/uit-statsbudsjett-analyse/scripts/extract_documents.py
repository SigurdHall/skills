"""Trekk ut tekst og lagrede Office-celler uten å endre eller beregne kildene."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import posixpath
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zipfile


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def relationships(archive: zipfile.ZipFile, part: str) -> dict:
    """Slå opp lokale deler; eksterne lenker skal aldri hentes av uttrekket."""
    folder, name = posixpath.split(part)
    rel_path = posixpath.join(folder, "_rels", name + ".rels")
    if rel_path not in archive.namelist():
        return {}
    result = {}
    for rel in ET.fromstring(archive.read(rel_path)):
        external = rel.get("TargetMode") == "External"
        target = rel.attrib["Target"]
        if not external:
            target = posixpath.normpath(posixpath.join(folder, unquote(target))).lstrip("/")
        result[rel.attrib["Id"]] = {
            "target": target,
            "kind": rel.attrib["Type"].rsplit("/", 1)[-1],
            "external": external,
        }
    return result


def paragraph_text(element: ET.Element) -> str:
    fragments = []
    for node in element.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag == "t":
            fragments.append(node.text or "")
        elif tag in ("br", "cr"):
            fragments.append("\n")
        elif tag == "tab":
            fragments.append("\t")
    return "".join(fragments)


def xml_paragraphs(archive: zipfile.ZipFile, part: str) -> list[str]:
    root = ET.fromstring(archive.read(part))
    result = []
    paragraph_tags = (f"{{{NS['a']}}}p", f"{{{NS['w']}}}p")
    paragraphs = [node for node in root.iter() if node.tag in paragraph_tags]
    for index, paragraph in enumerate(paragraphs, 1):
        text = paragraph_text(paragraph)
        if text:
            result.append(f"Avsnitt {index}: {text}")
    return result


def spreadsheet_cell(cell: ET.Element, strings: list[str]) -> dict:
    value_node = cell.find("s:v", NS)
    raw = value_node.text if value_node is not None else None
    cell_type = cell.get("t", "n")
    value = raw
    if cell_type == "s" and raw is not None:
        value = strings[int(raw)]
    elif cell_type == "inlineStr":
        value = paragraph_text(cell)
    formula = cell.find("s:f", NS)
    return {
        "cell": cell.attrib["r"],
        "type": cell_type,
        "style": cell.get("s"),
        "raw": raw,
        "value": value,
        "formula": formula.text if formula is not None else None,
        "formula_attributes": dict(formula.attrib) if formula is not None else None,
        "cached_value": raw if formula is not None else None,
    }


def extract_workbook(data: bytes) -> list[str]:
    result = ["Lagrede celleverdier; formler er ikke beregnet på nytt."]
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_strings = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = [paragraph_text(item) for item in shared_strings]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        ole_size = workbook.find("s:oleSize", NS)
        if ole_size is not None:
            result.append(f"OLE-visningsområde: {ole_size.get('ref')}")
        links = relationships(archive, "xl/workbook.xml")
        for sheet in workbook.findall("s:sheets/s:sheet", NS):
            link = links[sheet.attrib[f"{{{NS['r']}}}id"]]
            if link["external"]:
                raise ValueError("Arbeidsboken viser til et eksternt ark; innholdet er ikke hentet.")
            path = link["target"]
            state = sheet.get("state", "visible")
            result.append(f"#### Ark: {sheet.attrib['name']} · {path} · state={state}")
            root = ET.fromstring(archive.read(path))
            for cell in root.findall("s:sheetData/s:row/s:c", NS):
                if len(cell):
                    result.append(json.dumps(spreadsheet_cell(cell, strings), ensure_ascii=False))
    return result


def related_assets(archive: zipfile.ZipFile, part: str, visited: set) -> list[str]:
    """Bevar koblingen lysark → diagram → arbeidsbok, også for OLE-objekter."""
    result = []
    visited.add(part)
    for link in relationships(archive, part).values():
        target = link["target"]
        if link["external"]:
            result.append(f"Ekstern lenke, ikke hentet: {target}")
        elif target in visited:
            continue
        elif target.lower().endswith(".xlsx"):
            result.append(f"### Innebygd arbeidsbok: {part} -> {target}")
            result.extend(extract_workbook(archive.read(target)))
        elif link["kind"] == "chart":
            result.append(f"### Diagram: {part} -> {target}")
            result.extend(xml_paragraphs(archive, target))
            result.extend(related_assets(archive, target, visited))
        elif link["kind"] in ("notesSlide", "header", "footer"):
            result.append(f"### Tekstdel ({link['kind']}): {part} -> {target}")
            result.extend(xml_paragraphs(archive, target))
        elif link["kind"] in ("image", "oleObject", "package", "footnotes", "endnotes"):
            result.append(
                f"Innhold ikke lest ({link['kind']}): {part} -> {target}. "
                "Krever manuell kontroll; ingen parsing/OCR utført."
            )
    return result


def extract_presentation(archive: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(archive.read("ppt/presentation.xml"))
    links = relationships(archive, "ppt/presentation.xml")
    result = []
    # Bruk lysarkrekkefølgen i dokumentet, ikke alfabetisk orden på XML-filnavn.
    for number, slide in enumerate(root.findall("p:sldIdLst/p:sldId", NS), 1):
        link = links[slide.attrib[f"{{{NS['r']}}}id"]]
        if link["external"]:
            raise ValueError("Presentasjonen viser til et eksternt lysark; innholdet er ikke hentet.")
        path = link["target"]
        result.append(f"## Lysark {number} · {path}")
        result.extend(xml_paragraphs(archive, path))
        result.extend(related_assets(archive, path, set()))
    return result


def word_table(table: ET.Element, number: int) -> list[str]:
    result = []
    for row_number, row in enumerate(table.findall("w:tr", NS), 1):
        for cell_number, cell in enumerate(row.findall("w:tc", NS), 1):
            paragraphs = [paragraph_text(p) for p in cell.iter(f"{{{NS['w']}}}p")]
            location = f"Tabell {number}, rad {row_number}, celle {cell_number}"
            result.append(f"{location}: " + " / ".join(paragraphs))
    return result


def extract_word(archive: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(archive.read("word/document.xml"))
    result = ["## word/document.xml (avsnitt og tabellceller, ikke Word-sidenummer)"]
    paragraph_number = 0
    table_number = 0
    for block in root.find("w:body", NS):
        if block.tag == f"{{{NS['w']}}}p":
            paragraph_number += 1
            result.append(f"Avsnitt {paragraph_number}: {paragraph_text(block)}")
        elif block.tag == f"{{{NS['w']}}}tbl":
            table_number += 1
            result.extend(word_table(block, table_number))
    result.extend(related_assets(archive, "word/document.xml", set()))
    return result


def extract_pdf(data: bytes) -> list[str]:
    try:
        import pymupdf
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError("PDF-uttrekk krever pymupdf: python -m pip install pymupdf") from error
    result = ["PDF-side er plass i filen fra 1; trykt sidetall må kontrolleres i teksten."]
    with pymupdf.open(stream=data, filetype="pdf") as document:
        for number, page in enumerate(document, 1):
            result.append(f"## PDF-side {number}")
            text = page.get_text(sort=True)
            result.append(text if text.strip() else "Ingen søkbar tekst. Krever visuell kontroll/OCR.")
    return result


def extract_document(source: Path) -> str:
    source = Path(source).resolve()
    data = source.read_bytes()
    suffix = source.suffix.lower()
    result = [f"# Kilde: {source}", f"SHA-256: {hashlib.sha256(data).hexdigest()}"]
    if suffix == ".pdf":
        result.extend(extract_pdf(data))
    elif suffix == ".xlsx":
        result.extend(extract_workbook(data))
    elif suffix in (".pptx", ".docx"):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            if suffix == ".pptx":
                result.extend(extract_presentation(archive))
            else:
                result.extend(extract_word(archive))
    else:
        raise ValueError(f"Ustøttet filtype: {suffix}. Bruk PDF, DOCX, PPTX eller XLSX.")
    return "\n\n".join(result) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path, nargs="+", help="Velg kildefiler eksplisitt.")
    parser.add_argument(
        "--output", required=True, type=Path,
        help="Samlet tekstuttrekk; eksisterende uttrekk erstattes.",
    )
    args = parser.parse_args(argv)
    sources = [source.resolve() for source in args.sources]
    output = args.output.resolve()
    if output in sources:
        raise ValueError("Uttrekket kan ikke skrives over en kildefil.")
    text = "\n".join(extract_document(source) for source in sources)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
