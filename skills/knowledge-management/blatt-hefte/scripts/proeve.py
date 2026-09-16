"""Prøvemodus: kjør kjeden for et år som om det var budsjettdagen, uten tilgang til fasit.

Brukes av kjor_blaatt_hefte.py --proeve. Gjør fire ting:

1. Filvakt: en audit-hook som stopper prosessen (PermissionError) hvis den åpner en fil
   under fasitmappene for året, og logger alle filer den leser under prosjektet og
   skillen. Loggen med sha256 legges i manifestet, så det kan etterprøves at fasit ikke
   ble rørt.
2. Kjente utgaver filtreres til budsjettår før prøveåret, så oppdagelsen må finne årets
   hefte selv (som på en ekte budsjettdag).
3. Budsjettbasen filtreres til år før prøveåret (RNB til og med Y−1 er lov, ingen forslag
   eller vedtatt for Y).
4. Leveransen går til leveranser/proeve/<tidsstempel>-<år>-<utgave>/ med tom kildecache,
   og manifest.json med hash av alt som ble skrevet og lest.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HER = Path(__file__).resolve().parent
SKILL = HER.parent
REPO = SKILL.parent.parent.parent
PROSJEKT = Path("/home/sihal7953/repos/uit-statsbudsjett")


def forbudte_stier(aar: int, proeve_dir: Path) -> list[Path]:
    """Alt som kan inneholde svaret for året, eller er avledet av det."""
    return [
        PROSJEKT / str(aar),                                  # UiTs eget materiale for året
        PROSJEKT / "leveranser",                              # tidligere kjøringer (proeve_dir unntas i vakten)
        PROSJEKT / "analyse" / "kilder" / "blaatt-hefte" / str(aar),  # heftet må hentes på nytt
        PROSJEKT / "analyse" / "kilder" / "rnb" / str(aar),
        SKILL / "assets" / "fasit-2024.json",
        REPO / "tests" / "fixtures",
    ]


class Vakt:
    def __init__(self, forbudte: list[Path], tillatt: Path):
        self.forbudte = [str(p) for p in forbudte]
        self.tillatt = str(tillatt)
        self.leste: set[str] = set()
        self.brudd: list[str] = []

    def __call__(self, hendelse: str, args: tuple) -> None:
        if hendelse != "open" or not args or args[0] is None:
            return
        sti = str(args[0])
        if not sti.startswith(str(PROSJEKT)) and not sti.startswith(str(SKILL)) and not sti.startswith(str(REPO)):
            return
        if sti.startswith(self.tillatt):
            return
        for f in self.forbudte:
            if sti.startswith(f):
                self.brudd.append(sti)
                raise PermissionError(f"prøvemodus: forsøkte å åpne fasitfil {sti}")
        modus = args[1] if len(args) > 1 else "r"
        if modus is None or "r" in str(modus):
            self.leste.add(sti)


def installer_vakt(aar: int, proeve_dir: Path) -> Vakt:
    """Audit-hook for Pythons open(), og en innpakning av pymupdf.open, som åpner filer i C
    og derfor ikke utløser audit-hendelsen."""
    vakt = Vakt(forbudte_stier(aar, proeve_dir), proeve_dir)
    sys.addaudithook(vakt)
    import pymupdf
    original = pymupdf.open

    def vaktet_open(*args, **kwargs):
        sti = args[0] if args else kwargs.get("filename")
        if isinstance(sti, (str, Path)):
            vakt("open", (str(sti), "r"))
        return original(*args, **kwargs)

    pymupdf.open = vaktet_open
    return vakt


def filtrer_kjente(known: Path, aar: int, ut: Path) -> Path:
    data = json.loads(Path(known).read_text(encoding="utf-8"))
    utgaver = data["utgaver"] if isinstance(data, dict) else data
    beholdt = [u for u in utgaver if int(u["budsjettaar"]) < aar]
    ut.write_text(json.dumps(beholdt, ensure_ascii=False, indent=1), encoding="utf-8")
    return ut


def filtrer_base(base: dict, aar: int) -> dict:
    return {**base, "aar": {a: p for a, p in base.get("aar", {}).items() if int(a) < aar},
            "proeve": f"filtrert til budsjettår før {aar}"}


def ny_proeve_dir(aar: int, utgave: str) -> tuple[Path, Path]:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    proeve_dir = PROSJEKT / "leveranser" / "proeve" / f"{ts}-{aar}-{utgave}"
    proeve_dir.mkdir(parents=True, exist_ok=False)
    cache = Path(tempfile.mkdtemp(prefix=f"blaatt-hefte-proeve-{aar}-"))
    return proeve_dir, cache


def sha256(sti: Path) -> str:
    h = hashlib.sha256()
    with open(sti, "rb") as f:
        for blokk in iter(lambda: f.read(1 << 20), b""):
            h.update(blokk)
    return h.hexdigest()


def skriv_manifest(proeve_dir: Path, vakt: Vakt, aar: int, utgave: str, returkode: int, cache: Path) -> Path:
    skrevet = {p.name: sha256(p) for p in sorted(proeve_dir.iterdir()) if p.is_file() and p.name != "manifest.json"}
    leste = {}
    for sti in sorted(vakt.leste):
        p = Path(sti)
        if p.is_file():
            leste[sti] = sha256(p)
    hentet = {str(p.relative_to(cache)): sha256(p) for p in sorted(cache.rglob("*")) if p.is_file()}
    manifest = {
        "proeve": {"budsjettaar": aar, "utgave": utgave, "returkode": returkode,
                   "fryst_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "forbudte_stier": [str(p) for p in forbudte_stier(aar, proeve_dir)],
        "brudd": vakt.brudd,
        "skrevet": skrevet,
        "hentet_til_cache": hentet,
        "lest_under_prosjekt_og_skill": leste,
        "regel": "Filene under «skrevet» er frosset. Fasit åpnes først etter at dette manifestet finnes, og sammenligningen skrives i en egen fil ved siden av.",
    }
    ut = proeve_dir / "manifest.json"
    ut.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return ut
