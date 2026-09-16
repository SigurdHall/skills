"""Les kontrollcellene fra UiTs budsjettpresentasjon 2024 og skriv assets/fasit-2024.json.

Kilden er den innebygde arbeidsboken fra presentasjonen «Forslag til statsbudsjett 2024»
(2024/_uttrekk/slide3-5-ole.xlsx i uit-statsbudsjett). Hver celle skrives med ark, celle,
etikett, verdi, formel og tallformat, slik at fase 5 kan sammenligne rammearket mot
presentasjonen uten å taste tall.

Skriptet er deterministisk: samme arbeidsbok gir byte-identisk JSON.

Bruk:
    lag_fasit_2024.py --kilde <slide3-5-ole.xlsx> [--output <fasit-2024.json>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import openpyxl

STANDARD_KILDE = Path("/home/sihal7953/repos/uit-statsbudsjett/2024/_uttrekk/slide3-5-ole.xlsx")
STANDARD_UT = Path(__file__).resolve().parent.parent / "assets" / "fasit-2024.json"

# Ark → celleområder som skal leses. Rekkefølgen bestemmer rekkefølgen i JSON-filen.
OMRAADER = [
    ("Hovedpost.", ["D3:D19", "I3:I19"]),
    ("Resultatkomp.", ["C15:C17"]),
    ("Sammenligning", ["B4:E12"]),
    ("NyeSatser", ["C5:C8"]),
]

REALVEKST = [
    {
        "navn": "metode a uten RNB",
        "verdi_prosent": 1.89,
        "kildecelle": "Hovedpost.!D19",
        "utregning": "D18 − 4,4 % = 6,29 % − 4,4 %",
        "forklaring": "Nominell endring minus prisjusteringssatsen. Presentasjonen viste dette som 1,9 %.",
    },
    {
        "navn": "metode b uten RNB",
        "verdi_prosent": -0.29,
        "kildecelle": None,
        "utregning": "(239 289 − 250 434) / 3 806 533",
        "forklaring": "Endring minus heftets prisjusteringsbeløp, delt på utgangspunktet. Ikke egen celle i arbeidsboken.",
    },
    {
        "navn": "metode a med RNB",
        "verdi_prosent": 1.75,
        "kildecelle": "Hovedpost.!I18",
        "utregning": "I18 − 4,4 % = 6,15 % − 4,4 %",
        "forklaring": "Som metode a, men nominell endring regnet mot utgangspunkt pluss RNB-tillegget 86 200.",
    },
    {
        "navn": "metode b med RNB",
        "verdi_prosent": -0.29,
        "kildecelle": "Hovedpost.!I19",
        "utregning": "(239 289 − 250 434) / 3 892 733",
        "forklaring": "Presentasjonen viste dette som «−0,3 % justert for RNB».",
    },
]

TILLATTE_AVVIK = [
    {
        "id": "A1",
        "gjelder": "Hovedpost.!D12, Hovedpost.!I12",
        "tekst": "Omfordeling Ukraina −734 står i forslagsheftet, men ikke som egen kolonne i rammearket.",
    },
    {
        "id": "A2",
        "gjelder": "Sammenligning!B4:E12",
        "tekst": "USN mangler i presentasjonens sektortabell. Rammearket har alle statlige institusjoner.",
    },
    {
        "id": "A3",
        "gjelder": "NyeSatser!D5:D8, F5:F8, H5:H8",
        "tekst": "Satskolonnen er ramme delt på DBH-produksjon og kan ikke avledes fra blått hefte. Bare rammekolonnene (C, E, G) er kontrollgrunnlag.",
    },
    {
        "id": "A4",
        "gjelder": "Hovedpost.!G5",
        "tekst": "Kjent feil i presentasjonen: blokk 2 er merket «3,0 %», men bruker 4,4 %-tallet 250 434 (samme verdi som D5).",
    },
]


def _etikett(ark, rad: int, kolonne: int) -> str | None:
    """Nærmeste tekstcelle til venstre på samme rad."""
    for k in range(kolonne - 1, 0, -1):
        verdi = ark.cell(row=rad, column=k).value
        if isinstance(verdi, str) and verdi.strip():
            return verdi.replace("\xa0", " ").strip()
    return None


def _celler(formler, verdier, navn: str, omraade: str) -> list[dict]:
    af, av = formler[navn], verdier[navn]
    ut = []
    for rad in af[omraade]:
        for celle in rad:
            formel = celle.value
            verdi = av[celle.coordinate].value
            if formel is None and verdi is None:
                continue
            ut.append({
                "ark": navn,
                "celle": celle.coordinate,
                "etikett": _etikett(af, celle.row, celle.column),
                "verdi": verdi,
                "formel": formel if isinstance(formel, str) and formel.startswith("=") else None,
                "tallformat": celle.number_format,
            })
    return ut


def lag_fasit(kilde: Path) -> dict:
    formler = openpyxl.load_workbook(kilde, data_only=False)
    verdier = openpyxl.load_workbook(kilde, data_only=True)
    celler = []
    for navn, omraader in OMRAADER:
        for omraade in omraader:
            celler.extend(_celler(formler, verdier, navn, omraade))
    return {
        "fasit_versjon": "1",
        "kilde": {
            "filnavn": kilde.name,
            "sha256": hashlib.sha256(kilde.read_bytes()).hexdigest(),
            "ark": formler.sheetnames,
            "beskrivelse": "Innebygd arbeidsbok fra «Presentasjon av statsbudsjett 2024 v.0.99.pptx» (lysark 3, 6, 7, 8).",
        },
        "omraader": [{"ark": navn, "omraader": o} for navn, o in OMRAADER],
        "celler": celler,
        "realvekst": REALVEKST,
        "tillatte_avvik": TILLATTE_AVVIK,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kilde", type=Path, default=STANDARD_KILDE)
    p.add_argument("--output", type=Path, default=STANDARD_UT)
    a = p.parse_args(argv)
    fasit = lag_fasit(a.kilde)
    a.output.write_text(json.dumps(fasit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(fasit['celler'])} celler skrevet til {a.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
