"""Valider et kontraktdokument mot assets/blaatt-hefte.schema.json uten eksterne pakker.

Dekker den delen av JSON Schema som skjemaet bruker: type (inkl. liste av typer),
required, additionalProperties, properties, items, enum, const, minItems, minLength,
minimum, maximum, pattern og $ref til #/$defs. Feil rapporteres med JSON-sti.

Bruk:
    from kontrakt import valider, last_skjema
    feil = valider(dokument)           # liste av strenger, tom = gyldig
Kommandolinje:
    kontrakt.py <dokument.json>        # returkode 0 gyldig, 1 ugyldig
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKJEMA_STI = Path(__file__).resolve().parent.parent / "assets" / "blaatt-hefte.schema.json"

TYPER = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def last_skjema(sti: Path = SKJEMA_STI) -> dict:
    return json.loads(sti.read_text(encoding="utf-8"))


def _ref(skjema: dict, ref: str) -> dict:
    node = skjema
    for del_ in ref.lstrip("#/").split("/"):
        node = node[del_]
    return node


def _sjekk(verdi, regel: dict, skjema: dict, sti: str, feil: list[str]) -> None:
    if "$ref" in regel:
        regel = {**_ref(skjema, regel["$ref"]), **{k: v for k, v in regel.items() if k != "$ref"}}

    if "const" in regel and verdi != regel["const"]:
        feil.append(f"{sti}: forventet {regel['const']!r}, fikk {verdi!r}")
        return
    if "enum" in regel and verdi not in regel["enum"]:
        feil.append(f"{sti}: {verdi!r} er ikke blant {regel['enum']}")
        return

    typer = regel.get("type")
    if typer is not None:
        if isinstance(typer, str):
            typer = [typer]
        if not any(TYPER[t](verdi) for t in typer):
            feil.append(f"{sti}: forventet type {typer}, fikk {type(verdi).__name__}")
            return
        if verdi is None:
            return

    if isinstance(verdi, dict):
        for krav in regel.get("required", []):
            if krav not in verdi:
                feil.append(f"{sti}: mangler feltet {krav!r}")
        egenskaper = regel.get("properties", {})
        if regel.get("additionalProperties") is False:
            for nokkel in verdi:
                if nokkel not in egenskaper:
                    feil.append(f"{sti}: ukjent felt {nokkel!r}")
        for nokkel, underregel in egenskaper.items():
            if nokkel in verdi:
                _sjekk(verdi[nokkel], underregel, skjema, f"{sti}.{nokkel}", feil)

    elif isinstance(verdi, list):
        if "minItems" in regel and len(verdi) < regel["minItems"]:
            feil.append(f"{sti}: minst {regel['minItems']} elementer, fikk {len(verdi)}")
        if "items" in regel:
            for i, element in enumerate(verdi):
                _sjekk(element, regel["items"], skjema, f"{sti}[{i}]", feil)

    elif isinstance(verdi, str):
        if "minLength" in regel and len(verdi) < regel["minLength"]:
            feil.append(f"{sti}: for kort streng")
        if "pattern" in regel and not re.search(regel["pattern"], verdi):
            feil.append(f"{sti}: {verdi!r} matcher ikke {regel['pattern']}")

    elif isinstance(verdi, (int, float)) and not isinstance(verdi, bool):
        if "minimum" in regel and verdi < regel["minimum"]:
            feil.append(f"{sti}: {verdi} er under {regel['minimum']}")
        if "maximum" in regel and verdi > regel["maximum"]:
            feil.append(f"{sti}: {verdi} er over {regel['maximum']}")


def valider(dokument: dict, skjema: dict | None = None) -> list[str]:
    """Returner en liste med feil. Tom liste betyr at dokumentet følger kontrakten."""
    skjema = skjema or last_skjema()
    feil: list[str] = []
    _sjekk(dokument, skjema, skjema, "$", feil)
    if not feil:
        feil.extend(_semantikk(dokument))
    return feil


def _semantikk(d: dict) -> list[str]:
    """Regler skjemaet ikke kan uttrykke: lengder som må stemme og indekser som må peke riktig."""
    feil = []
    h = d["hovedtabell"]
    n = len(h["kolonner"])
    if h["sum_indeks"] != n - 1:
        feil.append(f"$.hovedtabell.sum_indeks: {h['sum_indeks']} er ikke siste kolonne ({n - 1})")
    for i, rad in enumerate(h["rader"]):
        if len(rad["verdier"]) != n:
            feil.append(f"$.hovedtabell.rader[{i}]: {len(rad['verdier'])} verdier mot {n} kolonner")
    if not any(r["kortkode_norm"] == "UIT" for r in h["rader"]):
        feil.append("$.hovedtabell.rader: ingen rad med kortkode_norm UIT")
    p = d["prisjustering"]
    if p["kolonne_indeks"] is not None and not (0 < p["kolonne_indeks"] < n - 1):
        feil.append("$.prisjustering.kolonne_indeks: peker ikke på en justeringskolonne")
    r = d["resultat"]
    if r is not None:
        m = len(r["kolonner"])
        for i, rad in enumerate(r["rader"]):
            if len(rad["verdier"]) != m:
                feil.append(f"$.resultat.rader[{i}]: {len(rad['verdier'])} verdier mot {m} kolonner")
        for s in r["sumkolonner"]:
            if not (0 <= s < m):
                feil.append(f"$.resultat.sumkolonner: {s} utenfor kolonnene")
    return feil


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    dokument = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    feil = valider(dokument)
    for linje in feil:
        print(linje)
    print("gyldig" if not feil else f"{len(feil)} feil")
    return 0 if not feil else 1


if __name__ == "__main__":
    raise SystemExit(main())
