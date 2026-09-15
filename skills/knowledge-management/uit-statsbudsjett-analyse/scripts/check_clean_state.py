"""Kontroller at prosjektet er rent før en ny årskjøring, og arkiver eventuelle rester.

Rester er filer en tidligere kjøring for samme år kan ha lagt igjen: leveransemappen,
hentede kilder, UiTs forutsetningsnotat, rammebro-filer og årets erfaringsnotater.
Fasitmappen <år>/ og arbeidsdelingen for året røres aldri. Med --archive flyttes
restene til arkiv/avbrutt/<tidsstempel>-<kjøring>/ med samme relative sti.

Returkode 0 = rent (eller arkivert), 3 = rester funnet uten --archive.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def leftover_paths(project: Path, year: int, run_id: str) -> list[Path]:
    candidates = [
        project / "leveranser" / run_id,
        project / "analyse" / "kilder" / str(year),
        project / "analyse" / "kilder" / f"uit-forutsetninger-{year}",
        project / "analyse" / f"uit-forutsetninger-{year}.md",
        project / "analyse" / f"{year}-rammebro-input.json",
        project / "analyse" / f"{year}-rammebro-kontroll.json",
    ]
    memory = project / "arbeidsminne"
    if memory.is_dir():
        candidates.extend(sorted(memory.glob(f"*/erfaringer-{year}-proeve.md")))
    return [p for p in candidates if p.exists()]


def other_runs_for_year(project: Path, year: int, run_id: str) -> list[str]:
    runs = project / "leveranser"
    if not runs.is_dir():
        return []
    return sorted(p.name for p in runs.iterdir() if p.is_dir() and p.name.startswith(f"{year}-") and p.name != run_id)


def archive(project: Path, paths: list[Path], run_id: str, stamp: str) -> Path:
    target = project / "arkiv" / "avbrutt" / f"{stamp}-{run_id}"
    for path in paths:
        destination = target / path.relative_to(project)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(destination))
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--archive", action="store_true", help="flytt restene til arkiv/avbrutt/")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    project = args.project.resolve()
    found = leftover_paths(project, args.year, args.run_id)
    report = {
        "project": str(project),
        "year": args.year,
        "run_id": args.run_id,
        "leftovers": [p.relative_to(project).as_posix() for p in found],
        "other_runs_for_year": other_runs_for_year(project, args.year, args.run_id),
        "archived_to": None,
        "clean": not found,
    }
    if found and args.archive:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        report["archived_to"] = archive(project, found, args.run_id, stamp).relative_to(project).as_posix()
        report["clean"] = True
    content = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content + "\n", encoding="utf-8")
    print(content)
    return 0 if report["clean"] else 3


if __name__ == "__main__":
    sys.exit(main())
