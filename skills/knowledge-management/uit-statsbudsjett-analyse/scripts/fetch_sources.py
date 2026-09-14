#!/usr/bin/env python3
"""Henter identifiserte PDF-kilder. År og dokumentstatus er oppgitt, ikke verifisert."""

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit


SOURCE_FIELDS = {"id", "url", "budget_year", "stage", "title"}


def validate_source(source):
    if not isinstance(source, dict) or set(source) != SOURCE_FIELDS:
        raise ValueError("Hver kilde må ha id, url, budget_year, stage og title.")
    if type(source["budget_year"]) is not int:
        raise ValueError("budget_year må være et heltall.")
    for key in ["stage", "title"]:
        if not isinstance(source[key], str) or not source[key].strip():
            raise ValueError(f"{key} må være tekst.")
    validate_url(source["url"])


def validate_sources(sources):
    if not isinstance(sources, list) or not sources:
        raise ValueError("Inndata må være en ikke-tom JSON-liste med kilder.")
    source_ids = set()
    for source in sources:
        validate_source(source)
        source_id = source["id"]
        if not isinstance(source_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,99}", source_id):
            raise ValueError("Ugyldig id: bruk små bokstaver, tall, bindestrek eller understrek.")
        if source_id in source_ids:
            raise ValueError("Duplikat id i kildelisten.")
        source_ids.add(source_id)


def validate_url(url):
    if not isinstance(url, str):
        raise ValueError("Kilden må ha en HTTPS-adresse uten brukernavn og passord.")
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username is not None:
        raise ValueError("Kilden må ha en HTTPS-adresse uten brukernavn og passord.")


def download_pdf(source, path):
    # Skriver nedlastingen midlertidig til hele kjøringen er kontrollert.
    command = [
        "curl", "--fail", "--silent", "--show-error", "--location",
        "--proto", "=https", "--proto-redir", "=https", "--max-time", "90",
        "--output", str(path), "--write-out", "%{url_effective}",
        "--url", source["url"],
    ]
    try:
        response = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise ValueError(f"Henting feilet for {source['id']}: {error.stderr.strip()}") from error
    data = path.read_bytes()
    if not data.startswith(b"%PDF-"):
        raise ValueError(f"Kilden {source['id']} returnerte ikke en PDF.")
    effective_url = response.stdout.strip()
    validate_url(effective_url)
    return {
        **source,
        "file": f"{source['id']}.pdf",
        "effective_url": effective_url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "classification_verified": False,
    }


def check_existing(source, record, output_dir):
    target = output_dir / record["file"]
    if target.is_symlink():
        raise ValueError(f"Kan ikke skrive via symbolsk lenke: {target.name}.")
    if target.exists():
        existing_hash = hashlib.sha256(target.read_bytes()).hexdigest()
        if existing_hash != record["sha256"]:
            raise ValueError(f"Beholder avvikende eksisterende fil: {target.name}.")
    if source is not None:
        if any(source.get(key) != record[key] for key in SOURCE_FIELDS):
            raise ValueError(f"Eksisterende metadata avviker for {record['id']}.")
        if source["sha256"] != record["sha256"]:
            raise ValueError(f"Nedlastingen har avvikende innhold for {record['id']}.")


def read_manifest(manifest_path):
    if manifest_path.is_symlink():
        raise ValueError("sources.json kan ikke være en symbolsk lenke.")
    records = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    existing = {record["id"]: record for record in records}
    if len(existing) != len(records):
        raise ValueError("Duplikat id i eksisterende sources.json.")
    return records, existing


def save_downloads(downloads, records, output_dir):
    existing_ids = {record["id"] for record in records}
    # Beholder første hentetid og metadata ved identisk ny kjøring.
    for path, record in downloads:
        target = output_dir / record["file"]
        if not target.exists():
            with target.open("xb") as file:
                file.write(path.read_bytes())
        if record["id"] not in existing_ids:
            records.append(record)

    manifest_path = output_dir / "sources.json"
    content = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    previous_content = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else None
    if content != previous_content:
        staged_manifest = downloads[0][0].parent / "sources.json"
        staged_manifest.write_text(content, encoding="utf-8")
        staged_manifest.replace(manifest_path)


def fetch_sources(sources, output_dir):
    validate_sources(sources)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    records, existing = read_manifest(output_dir / "sources.json")
    with TemporaryDirectory(prefix=".fetch-", dir=output_dir) as temporary_dir:
        temporary_dir = Path(temporary_dir)
        downloads = []
        for source in sources:
            path = temporary_dir / f"{source['id']}.pdf"
            record = download_pdf(source, path)
            check_existing(existing.get(source["id"]), record, output_dir)
            downloads.append((path, record))
        save_downloads(downloads, records, output_dir)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON-liste med identifiserte PDF-kilder")
    parser.add_argument("output_dir", type=Path, help="Mappe for PDF-er og sources.json")
    args = parser.parse_args()
    sources = json.loads(args.input.read_text(encoding="utf-8"))
    try:
        records = fetch_sources(sources, args.output_dir)
    except ValueError as error:
        parser.error(str(error))
    print(f"Kontrollert {len(sources)} kilder; {len(records)} registrert i {args.output_dir / 'sources.json'}")


if __name__ == "__main__":
    main()
