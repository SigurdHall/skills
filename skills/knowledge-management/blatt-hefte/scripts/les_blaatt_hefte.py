"""Les eitt blått hefte (PDF) og lever eit kontraktdokument (blaatt-hefte.schema.json).

Ingen årsspesifikk kode: radtalet kjem frå heftets eiga forkortingsliste, sidene blir
funne på innhald (ikkje sidetal), og kolonnenamna er heftets eigne.

Bruk:
    from les_blaatt_hefte import les
    dok = les(Path("blaatt-hefte-2025-forslag.pdf"))
Kommandolinje:
    les_blaatt_hefte.py <pdf> [--output d.json] [--kilde kilder.json] [--referanse forrige.pdf]
                        [--institusjoner institusjoner.json]

Returkode 9 = kontroll A eller B feila (eller strukturen blei ikkje funnen).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pymupdf as fitz  # «import fitz» skriver en deprecation-advarsel til stdout

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kontrakt import valider  # noqa: E402

NAVN = "les_blaatt_hefte.py"
VERSJON = "1.0"

LUKE_ORD = 4.0      # punkt mellom ord som høyrer til same celle
LUKE_BAND = 6.0     # punkt mellom høgrekantar i ulike kolonnar
LINJE_Y = 3.0       # punkt loddrett innanfor same linje
BREI_PROSA = 250.0  # ei linje med éi celle breiare enn dette er brødtekst, ikkje overskrift


class Lesefeil(SystemExit):
    """Kontroll A eller B feila. Meldinga går til stderr, returkoden er 9."""

    def __init__(self, melding: str):
        print(f"FEIL {NAVN}: {melding}", file=sys.stderr)
        super().__init__(9)


# ---------------------------------------------------------------- tekst og celler

def reint(tekst: str) -> str:
    """Minusteikn blir ASCII. Tankestrek i årstalsintervall (2020–2024) blir ståande."""
    return tekst.replace("−", "-").replace(" ", " ").replace("*", "").strip()


def er_tom(tekst: str) -> bool:
    return tekst in ("", "-", "–", "—")


def er_tall(tekst: str) -> bool:
    return bool(re.fullmatch(r"-?\d[\d ]*", tekst))


def som_tall(tekst: str) -> int:
    return int(tekst.replace(" ", ""))


def celler(side) -> list[list[tuple]]:
    """Orda på sida som linjer av celler: (tekst, x0, x1, y). Naboord med luke < 4 pt blir limte."""
    ord_ = sorted(side.get_text("words"), key=lambda o: (round(o[1], 1), o[0]))
    linjer: list[list[tuple]] = []
    for x0, y0, x1, _y1, tekst, *_ in ord_:
        if linjer and abs(y0 - linjer[-1][0][3]) < LINJE_Y:
            linjer[-1].append((tekst, x0, x1, linjer[-1][0][3]))
        else:
            linjer.append([(tekst, x0, x1, y0)])
    ut = []
    for linje in linjer:
        linje.sort(key=lambda c: c[1])
        slått: list[tuple] = []
        for tekst, x0, x1, y in linje:
            if slått and x0 - slått[-1][2] < LUKE_ORD:
                forrige = slått.pop()
                slått.append((f"{forrige[0]} {tekst}", forrige[1], x1, y))
            else:
                slått.append((tekst, x0, x1, y))
        ut.append([(reint(t), x0, x1, y) for t, x0, x1, y in slått])
    return ut


def trykt_sidetal(linjer: list[list[tuple]]) -> int | None:
    for linje in reversed(linjer):
        if len(linje) == 1 and re.fullmatch(r"\d{1,3}", linje[0][0]):
            return int(linje[0][0])
    return None


# ---------------------------------------------------------------- forkortingsliste

def les_forkortingsliste(doc) -> tuple[int | None, dict[str, tuple[str, str]]]:
    """{kortkode_norm: (kortkode slik heftet skriv han, fullt namn)} frå sida med kortnamn."""
    for nr in range(min(12, doc.page_count)):
        tekst = doc[nr].get_text("text").lower()
        if not any(o in tekst for o in ("kortnamn", "kortnavn", "forkorting", "forkortelse")):
            continue
        koder = _par_fra_liste(celler(doc[nr]))
        if len(koder) >= 20:
            return nr + 1, koder
    raise Lesefeil("fann ingen forkortingsliste med minst 20 kortnamn på dei 12 første sidene")


def _par_fra_liste(linjer: list[list[tuple]]) -> dict[str, tuple[str, str]]:
    koder: dict[str, tuple[str, str]] = {}
    enkle: list[str] = []
    for linje in linjer:
        tekster = [c[0] for c in linje if c[0]]
        if len(tekster) == 2 and _kortkode(tekster[1]):
            koder[tekster[1].upper()] = (tekster[1], tekster[0])
        elif len(tekster) == 1:
            enkle.append(tekster[0])
    if koder:
        return koder
    for navn, kode in zip(enkle[::2], enkle[1::2]):   # to spaltar lesne kvar for seg
        if _kortkode(kode):
            koder[kode.upper()] = (kode, navn)
    return koder


def _kortkode(tekst: str) -> bool:
    """Kortkodar er korte og for det meste store bokstavar: AHO, HiM, HGUt, KHiO, NMBU."""
    if not re.fullmatch(r"[A-ZÆØÅ][\wÆØÅæøå]{1,5}", tekst):
        return False
    return sum(t.isupper() for t in tekst) * 2 >= len(tekst)


def er_universitet(navn: str) -> bool:
    return "universitet" in navn.lower()


# ---------------------------------------------------------------- sidefinning

def koderader(linjer: list[list[tuple]], koder: dict) -> list[list[tuple]]:
    """Linjer der første celle er ein kortkode og resten er tal eller tomme celler."""
    rader = []
    for linje in linjer:
        if len(linje) < 3 or linje[0][0].upper() not in koder:
            continue
        resten = [c[0] for c in linje[1:]]
        if all(er_tall(t) or er_tom(t) for t in resten):
            rader.append(linje)
    return rader


def finn_sider(doc, koder: dict) -> dict[str, int | None]:
    """Sider med minst 15 koderader, sorterte på kva tabell dei er."""
    funn = {"hoved": None, "privat": None, "resultat": None}
    for nr in range(doc.page_count):
        tekst = doc[nr].get_text("text")
        lav = tekst.lower()
        if "post 50" not in lav and "post 70" not in lav and "utteljing" not in lav and "uttelling" not in lav:
            continue
        if len(koderader(celler(doc[nr]), koder)) < 15:
            continue
        if "post 50" in lav and funn["hoved"] is None:
            funn["hoved"] = nr + 1
        elif "post 70" in lav and funn["privat"] is None:
            funn["privat"] = nr + 1
        elif funn["resultat"] is None:
            funn["resultat"] = nr + 1
    if funn["hoved"] is None:
        raise Lesefeil("fann inga side med kap. 260 post 50 og minst 15 koderader")
    return funn


# ---------------------------------------------------------------- band og overskrifter

def finn_band(rader: list[list[tuple]]) -> list[tuple[float, float, float]]:
    """Kolonnebandi som (x0_min, x1_maks, x1_median), klustra på høgrekanten."""
    kanter = sorted((c[1], c[2]) for rad in rader for c in rad[1:])
    band: list[list[tuple]] = []
    for x0, x1 in sorted(kanter, key=lambda k: k[1]):
        if band and x1 - band[-1][-1][1] < LUKE_BAND:
            band[-1].append((x0, x1))
        else:
            band.append([(x0, x1)])
    ut = []
    for gruppe in band:
        x1ar = sorted(k[1] for k in gruppe)
        ut.append((min(k[0] for k in gruppe), max(x1ar), x1ar[len(x1ar) // 2]))
    return ut


def verdier_i_band(rad: list[tuple], band: list) -> tuple[list[int | None], bool]:
    """Verdiane til rada og om to celler hamna i same band (då har kolonnar smelta saman)."""
    verdier: list[int | None] = [None] * len(band)
    brukte = []
    for tekst, _x0, x1, _y in rad[1:]:
        i = min(range(len(band)), key=lambda j: abs(x1 - band[j][2]))
        brukte.append(i)
        if er_tall(tekst):
            verdier[i] = som_tall(tekst)
    return verdier, len(set(brukte)) != len(brukte)


def overskriftslinjer(linjer: list[list[tuple]], y_forste_rad: float) -> list[list[tuple]]:
    """Linjene mellom siste brødtekstlinje og første datarad."""
    over = [l for l in linjer if l[0][3] < y_forste_rad - LINJE_Y]
    start = 0
    for i, linje in enumerate(over):
        if len(linje) == 1 and linje[0][2] - linje[0][1] > BREI_PROSA:
            start = i + 1
    return over[start:]


def les_overskrifter(linjer: list[list[tuple]], band: list) -> tuple[list[str], list[int]]:
    """Overskrifter per band, og banda der to fragment frå same linje hamna saman
    (teikn på at to kolonnar har smelta til eitt band)."""
    biter: list[list[tuple]] = [[] for _ in band]
    for linje in linjer:
        for tekst, x0, x1, y in linje:
            if not tekst:
                continue
            treff, beste = None, 0.0
            for i, (bx0, bx1, _) in enumerate(band):
                dekning = min(x1, bx1) - max(x0, bx0)
                if dekning > beste:
                    treff, beste = i, dekning
            if treff is not None:
                biter[treff].append((y, x0, tekst))
    dobbelt = [i for i, b in enumerate(biter)
               if len({y for y, _x, _t in b}) != len(b)]
    return [_slaa_saman(sorted(b)) for b in biter], dobbelt


def _slaa_saman(biter: list[tuple]) -> str:
    ut = ""
    for _y, _x, tekst in biter:
        if not ut:
            ut = tekst
        elif ut.endswith("-"):
            liten = len(ut) > 1 and ut[-2].isalpha() and ut[-2].islower()
            ut = (ut[:-1] if liten else ut) + tekst   # «Pris-»+«justering»; «rekr.-»+«stillingar»
        else:
            ut = f"{ut} {tekst}"
    return ut.strip()


# ---------------------------------------------------------------- hovudtabellen

def les_bandtabell(side, koder: dict) -> dict:
    """Felles lesing for hovudtabellen og resultattabellen."""
    linjer = celler(side)
    rader = koderader(linjer, koder)
    if not rader:
        raise Lesefeil("fann ingen datarader på sida")
    band = finn_band(rader)
    overskrifter, dobbelt = les_overskrifter(overskriftslinjer(linjer, rader[0][0][3]), band)
    ut, kollisjoner = [], []
    for rad in rader:
        kortkode = rad[0][0]
        verdier, kollisjon = verdier_i_band(rad, band)
        ut.append({"kortkode": kortkode, "kortkode_norm": kortkode.upper(), "verdier": verdier})
        if kollisjon:
            kollisjoner.append(kortkode.upper())
    return {"kolonner": overskrifter, "rader": ut, "band": band,
            "kollisjoner": kollisjoner, "dobbelt": dobbelt,
            "trykt_side": trykt_sidetal(linjer)}


def kontroll_a(rader: list[dict], side: int) -> bool:
    """Sum(1..n-1) == n. Ei einsleg rad som ikkje summerer er ein trykkfeil i heftet
    (UiT i 2025 etter vedtak, 760); to eller fleire tyder på at kolonneband har smelta saman."""
    avvik = []
    for rad in rader:
        verdier = rad["verdier"]
        sum_ = sum(v or 0 for v in verdier[:-1])
        if verdier[-1] is None or sum_ != verdier[-1]:
            avvik.append(f"{rad['kortkode_norm']}: sum {sum_} mot siste kolonne {verdier[-1]} "
                         f"(verdier={verdier})")
    if len(avvik) > 1:
        raise Lesefeil(f"kontroll A: {len(avvik)} rader summerer ikkje på PDF-side {side}: "
                       + " | ".join(avvik[:3]))
    if avvik:
        print(f"ADVARSEL kontroll A: éi rad summerer ikkje på PDF-side {side}: {avvik[0]}",
              file=sys.stderr)
    return not avvik


def kontroll_b(kolonner: list[str], band: list, aar: int, side: int,
               kollisjoner: list[str], dobbelt: list[int]) -> tuple[bool, bool]:
    """Tilordninga: like mange band som overskrifter, ingen rad og inga overskriftslinje med
    to celler i same band, og første/siste overskrift gjenkjend.
    Rett sum beviser ikkje rett etikett."""
    if kollisjoner:
        raise Lesefeil(f"kontroll B: {len(kollisjoner)} rader har to celler i same kolonneband på "
                       f"PDF-side {side} (kolonnar har smelta saman): {kollisjoner[:5]}")
    if dobbelt:
        raise Lesefeil(f"kontroll B: band {dobbelt} på PDF-side {side} har to overskriftsfragment "
                       f"på same linje: {[kolonner[i] for i in dobbelt]}")
    ikke_tomme = [k for k in kolonner if k]
    if len(ikke_tomme) != len(band):
        raise Lesefeil(f"kontroll B: {len(band)} kolonneband, men {len(ikke_tomme)} overskrifter "
                       f"på PDF-side {side}; overskrifter={kolonner}")
    utgangspunkt = bool(re.search(r"(saldert|rammel[øo]yving|budsjett)", kolonner[0], re.I)
                        and str(aar - 1) in kolonner[0])
    sum_gjenkjent = bool(re.search(r"(rammel[øo]yving|budsjett)", kolonner[-1], re.I)
                         and str(aar) in kolonner[-1])   # 2021 heiter «Budsjettforslag 2021»
    if not utgangspunkt or not sum_gjenkjent:
        raise Lesefeil(f"kontroll B: første/siste overskrift ikkje gjenkjend på PDF-side {side}: "
                       f"{kolonner[0]!r} / {kolonner[-1]!r} for budsjettår {aar}")
    return utgangspunkt, sum_gjenkjent


def budsjettaar_fra_side(side) -> int | None:
    treff = re.search(r"fr[åa] (\d{4}) til (\d{4})", side.get_text("text"))
    return int(treff.group(2)) if treff else None


def utgave_fra_kolonne(siste: str) -> str:
    return "forslag" if re.search(r"forslag", siste, re.I) else "vedtak"


# ---------------------------------------------------------------- prisjustering

MONSTER_SATS = [
    r"[Ss]atsen for prisjustering(?: for \d{4})? er\s+(\d+(?:,\d+)?)\s*pst",
    r"prisjusteringsfaktor på\s+(\d+(?:,\d+)?)\s*pst",
]


def les_prisjustering(doc, hovedtabell: dict) -> dict:
    tom = {"sats_prosent": None, "sitat": None, "pdf_side": None, "kolonne_indeks": None,
           "uit_kolonne": None, "uit_beregnet": None, "avvik": None, "ren_sats": None}
    sats, sitat, side = _finn_sats(doc)
    indeks = next((i for i, k in enumerate(hovedtabell["kolonner"]) if re.search(r"prisjuster", k, re.I)), None)
    uit = next((r for r in hovedtabell["rader"] if r["kortkode_norm"] == "UIT"), None)
    tom.update({"sats_prosent": sats, "sitat": sitat, "pdf_side": side, "kolonne_indeks": indeks})
    if sats is None or indeks is None or uit is None:
        return tom
    utgangspunkt = uit["verdier"][0] or 0
    beregnet = round(sats / 100 * utgangspunkt)
    kolonne = uit["verdier"][indeks]
    tom.update({"uit_kolonne": kolonne, "uit_beregnet": beregnet})
    if kolonne is not None:
        tom["avvik"] = kolonne - beregnet
        tom["ren_sats"] = abs(kolonne - beregnet) <= 0.0005 * utgangspunkt
    return tom


def _finn_sats(doc) -> tuple[float | None, str | None, int | None]:
    for monster in MONSTER_SATS:
        for nr in range(doc.page_count):
            flat = re.sub(r"\s+", " ", doc[nr].get_text("text"))
            treff = re.search(monster, flat)
            if treff:
                return float(treff.group(1).replace(",", ".")), _sitat(flat, *treff.span()), nr + 1
    return None, None, None


def _sitat(flat: str, start: int, slutt: int) -> str:
    """Avsnittet som forklarer prisjusteringskolonnen, ordrett."""
    fra = flat.rfind("Kolonnen Prisjustering", max(0, start - 800), start)
    if fra < 0:                      # ingen kolonneforklaring: byrj på næraste setningsstart
        vindu = flat.rfind(". ", max(0, start - 300), start)
        fra = vindu + 2 if vindu >= 0 else max(0, start - 200)
    punktum = re.search(r"\.\s", flat[slutt:])
    return flat[fra:slutt + (punktum.end() if punktum else 0)].strip()


# ---------------------------------------------------------------- resultat og satsar

def les_resultat(doc, koder: dict, side_nr: int | None) -> dict | None:
    if side_nr is None:
        return None
    tabell = les_bandtabell(doc[side_nr - 1], koder)
    rader = tabell["rader"]
    if side_nr < doc.page_count and koderader(celler(doc[side_nr]), koder):
        neste = les_bandtabell(doc[side_nr], koder)    # tabellen held fram på neste side
        if len(neste["band"]) == len(tabell["band"]):
            rader = rader + neste["rader"]
    sum_indekser = [i for i, k in enumerate(tabell["kolonner"]) if re.search(r"\bsum\b", k, re.I)]
    return {"pdf_side": side_nr, "kolonner": tabell["kolonner"],
            "sumkolonner": sum_indekser, "rader": rader}


def les_satser(doc, fra_side: int) -> dict:
    """Satstabellane i finansieringskapittelet. Kvar tabell er ein bolk under ei bilettekst."""
    open_tabeller, open_side, lukket = [], None, None
    for nr in range(fra_side, doc.page_count):
        tekst = doc[nr].get_text("text")
        if "tal i kroner" not in tekst:
            continue
        for tittel, linjer in _bolker(doc[nr]):
            tabell = _les_bolk(tittel, linjer)
            if not tabell["rader"]:
                continue
            if re.search(r"lukka ramme", tittel, re.I):
                lukket = {"pdf_side": nr + 1, "kolonner": tabell["kolonner"], "rader": tabell["rader"]}
            else:
                open_tabeller.append(tabell)
                open_side = open_side or nr + 1
    return {"open_ramme": {"pdf_side": open_side, "tabeller": open_tabeller} if open_tabeller else None,
            "lukket_ramme": lukket}


def _bolker(side) -> list[tuple[str, list]]:
    """(bilettekst, linjene under) for kvar blokk som endar på «(tal i kroner)»."""
    titler = []
    for blokk in side.get_text("blocks"):
        flat = re.sub(r"\s+", " ", blokk[4]).strip()
        if flat.endswith("(tal i kroner)") or flat.endswith("(tall i kroner)"):
            titler.append((blokk[3], flat))       # y-botn på biletteksten
    linjer = celler(side)
    ut = []
    for i, (y, tittel) in enumerate(titler):
        slutt = titler[i + 1][0] if i + 1 < len(titler) else 10_000
        ut.append((tittel, [l for l in linjer if y - LINJE_Y < l[0][3] < slutt]))
    return ut


def _les_bolk(tittel: str, linjer: list[list[tuple]]) -> dict:
    """Kolonnar frå vassrett overlapp; ei rad er ei linje med tal, med ombroten tekst framfor."""
    linjer = _tabellinjer(linjer)
    forste = next((i for i, l in enumerate(linjer) if any(er_tall(c[0]) for c in l[1:])), None)
    if forste is None:
        return {"tittel": tittel, "kolonner": [], "rader": []}
    band = _tekstband(linjer[forste:])
    kolonner = _kolonnenavn(linjer[:forste], band)
    celler_ = [(_plasser(l, band), l[0][3]) for l in linjer[forste:]]
    data = [(c, y) for c, y in celler_ if any(er_tall(v or "") for v in c[1:])]
    for tekst, y in celler_:
        if any(er_tall(v or "") for v in tekst[1:]):
            continue
        i = min(range(len(data)), key=lambda j: abs(data[j][1] - y))   # ombroten tekst til næraste rad
        rad, y_rad = data[i]
        data[i] = ([_lim(*(t, r) if y < y_rad else (r, t)) for r, t in zip(rad, tekst)], y_rad)
    return {"tittel": tittel, "kolonner": kolonner,
            "rader": [[_verdi(v) for v in rad] for rad, _y in data]}


def _tabellinjer(linjer: list[list[tuple]]) -> list[list[tuple]]:
    """Frå første linje etter biletteksten til neste brødtekstlinje.

    Brødtekst er ei brei linje med éi celle som startar til venstre for tabellens første kolonne;
    ombroken celletekst startar inne i tabellen og blir dermed verande.
    """
    linjer = [l for l in linjer if l and not (len(l) == 1 and re.fullmatch(r"\d{1,3}", l[0][0]))]
    venstre = min((l[0][1] for l in linjer if len(l) >= 2), default=0.0)
    prosa = [i for i, l in enumerate(linjer)
             if len(l) == 1 and l[0][2] - l[0][1] > BREI_PROSA and l[0][1] < venstre + 1]
    start = 0
    for i in prosa:
        if i == start:
            start = i + 1
    slutt = next((i for i in prosa if i > start), len(linjer))
    return linjer[start:slutt]


def _lim(a: str | None, b: str | None) -> str | None:
    return f"{a} {b}" if a and b else (a or b)


def _tekstband(linjer: list[list[tuple]]) -> list[tuple[float, float]]:
    intervall = sorted((c[1], c[2]) for linje in linjer for c in linje)
    band: list[list[float]] = []
    for x0, x1 in intervall:
        if band and x0 <= band[-1][1]:
            band[-1][1] = max(band[-1][1], x1)
        else:
            band.append([x0, x1])
    return [(a, b) for a, b in band]


def _plasser(linje: list[tuple], band: list) -> list[str | None]:
    ut: list[str | None] = [None] * len(band)
    for tekst, x0, x1, _y in linje:
        i = min(range(len(band)), key=lambda j: abs((x0 + x1) / 2 - (band[j][0] + band[j][1]) / 2))
        ut[i] = f"{ut[i]} {tekst}".strip() if ut[i] else tekst
    return ut


def _kolonnenavn(linjer: list[list[tuple]], band: list) -> list[str]:
    biter: list[list[tuple]] = [[] for _ in band]
    for linje in linjer:
        for tekst, x0, x1, y in linje:
            i = min(range(len(band)), key=lambda j: abs((x0 + x1) / 2 - (band[j][0] + band[j][1]) / 2))
            biter[i].append((y, x0, tekst))
    return [_slaa_saman(sorted(b)) for b in biter]


def _verdi(tekst: str | None):
    if tekst is None or er_tom(tekst):
        return None
    return som_tall(tekst) if er_tall(tekst) else tekst


# ---------------------------------------------------------------- kontroll C

def kontroll_c(hovedtabell: dict, referanse_pdf: Path | None) -> dict:
    if referanse_pdf is None:
        return {"status": "ikke_mulig", "referanse": None, "avvik": []}
    forrige = _hovedtabell_fra_pdf(Path(referanse_pdf))
    fasit = {r["kortkode_norm"]: r["verdier"][-1] for r in forrige["rader"]}
    avvik = []
    for rad in hovedtabell["rader"]:
        gammel = fasit.get(rad["kortkode_norm"])
        if gammel is not None and gammel != rad["verdier"][0]:
            avvik.append({"kortkode_norm": rad["kortkode_norm"], "forrige": gammel, "naa": rad["verdier"][0]})
    if len(avvik) > 2:
        raise Lesefeil(f"kontroll C: {len(avvik)} institusjonar har anna utgangspunkt enn "
                       f"sluttkolonnen i {Path(referanse_pdf).name}: {avvik[:5]}")
    return {"status": "ok" if not avvik else "avvik",
            "referanse": Path(referanse_pdf).name, "avvik": avvik}


def _hovedtabell_fra_pdf(sti: Path) -> dict:
    doc = fitz.open(sti)
    try:
        _, koder = les_forkortingsliste(doc)
        sider = finn_sider(doc, koder)
        return les_bandtabell(doc[sider["hoved"] - 1], koder)
    finally:
        doc.close()


# ---------------------------------------------------------------- hovudfunksjonen

def les(pdf: Path, kilde: dict | None = None, referanse_pdf: Path | None = None,
        institusjoner_json: Path | None = None) -> dict:
    """Les heftet og returner eit dokument som følger blaatt-hefte.schema.json."""
    pdf = Path(pdf)
    doc = fitz.open(pdf)
    try:
        side_koder, koder = les_forkortingsliste(doc)
        sider = finn_sider(doc, koder)
        hoved_side = doc[sider["hoved"] - 1]
        tabell = les_bandtabell(hoved_side, koder)
        aar = (kilde or {}).get("budsjettaar") or budsjettaar_fra_side(hoved_side)
        if aar is None:
            raise Lesefeil(f"fann ikkje budsjettåret på PDF-side {sider['hoved']}")

        hovedtabell = {
            "pdf_side": sider["hoved"], "trykt_side": tabell["trykt_side"],
            "kolonner": [k for k in tabell["kolonner"]],
            "utgangspunkt_indeks": 0, "sum_indeks": len(tabell["kolonner"]) - 1,
            "rader": tabell["rader"], "kontroll": {},
        }
        private = _private_koder(doc, koder, sider["privat"])
        forventet = len(koder) - len(private) if private else len(tabell["rader"])
        if len(tabell["rader"]) != forventet:
            raise Lesefeil(f"kontroll: {len(tabell['rader'])} datarader på PDF-side {sider['hoved']}, "
                           f"venta {forventet} statlege institusjonar frå forkortingslista")
        utg, sum_ok = kontroll_b(hovedtabell["kolonner"], tabell["band"], aar, sider["hoved"],
                                 tabell["kollisjoner"], tabell["dobbelt"])
        hovedtabell["kontroll"] = {
            "alle_rader_summerer": kontroll_a(tabell["rader"], sider["hoved"]),
            "antall_rader": len(tabell["rader"]), "forventet_rader": forventet,
            "antall_band": len(tabell["band"]),
            "antall_overskrifter": len([k for k in hovedtabell["kolonner"] if k]),
            "utgangspunkt_gjenkjent": utg, "sum_gjenkjent": sum_ok,
            "kryss": kontroll_c(hovedtabell, referanse_pdf),
        }

        resultat = les_resultat(doc, koder, sider["resultat"])
        satser = les_satser(doc, sider["hoved"])
        dokument = {
            "kontrakt_versjon": "1",
            "kilde": _kilde(pdf, doc, kilde, aar, hovedtabell["kolonner"][-1]),
            "hovedtabell": hovedtabell,
            "prisjustering": les_prisjustering(doc, hovedtabell),
            "resultat": resultat,
            "satser": satser,
            "institusjoner": _institusjoner(side_koder, koder, private, institusjoner_json),
            "skript": {"navn": NAVN, "versjon": VERSJON,
                       "kjort_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        }
    finally:
        doc.close()
    feil = valider(dokument)
    if feil:
        raise Lesefeil("dokumentet bryt kontrakten: " + "; ".join(feil[:5]))
    return dokument


def _private_koder(doc, koder: dict, side_nr: int | None) -> set[str]:
    if side_nr is None:
        return set()
    return {r[0][0].upper() for r in koderader(celler(doc[side_nr - 1]), koder)}


def _kilde(pdf: Path, doc, kilde: dict | None, aar: int, siste_kolonne: str) -> dict:
    gitt = kilde or {}
    return {
        "budsjettaar": aar,
        "utgave": gitt.get("utgave") or utgave_fra_kolonne(siste_kolonne),
        "tittel": gitt.get("tittel") or (doc.metadata or {}).get("title") or None,
        "url": gitt.get("url"),
        "sha256": gitt.get("sha256") or hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "content_length": gitt.get("content_length", pdf.stat().st_size),
        "hentet_utc": gitt.get("hentet_utc"),
        "sider": doc.page_count,
        "filnavn": pdf.name,
    }


def _institusjoner(side: int | None, koder: dict, private: set[str], sti: Path | None) -> dict:
    universiteter = _universitetskoder(sti)
    liste = []
    for norm, (kortkode, navn) in sorted(koder.items()):
        er_uni = er_universitet(navn)          # heftet sitt eige namn vinn alltid
        if universiteter and er_uni != (norm in universiteter):
            print(f"ADVARSEL: {norm} er {'' if er_uni else 'ikkje '}universitet etter heftet, "
                  f"men institusjoner.json seier det motsette; heftet vinn", file=sys.stderr)
        liste.append({"kortkode": kortkode, "kortkode_norm": norm, "navn": navn,
                      "universitet": er_uni, "statlig": norm not in private,
                      "kilde": "navneregel"})
    return {"pdf_side": side, "liste": liste}


def _universitetskoder(sti: Path | None) -> set[str]:
    """institusjoner.json listar universiteta anten som kortkodar eller som objekt."""
    if not sti:
        return set()
    poster = json.loads(Path(sti).read_text(encoding="utf-8")).get("universiteter", [])
    return {(p if isinstance(p, str) else p["kortkode"]).upper() for p in poster}


# ---------------------------------------------------------------- kommandolinje

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Les eitt blått hefte til kontrakt-JSON.")
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--kilde", type=Path, help="kilder.json med oppslag på filnamn")
    ap.add_argument("--referanse", type=Path, help="førre vedtak-PDF for kontroll C")
    ap.add_argument("--institusjoner", type=Path)
    a = ap.parse_args(argv)

    kilde = _slaa_opp_kilde(a.kilde, a.pdf) if a.kilde else None
    dokument = les(a.pdf, kilde=kilde, referanse_pdf=a.referanse, institusjoner_json=a.institusjoner)
    tekst = json.dumps(dokument, ensure_ascii=False, indent=2)
    if a.output:
        a.output.write_text(tekst + "\n", encoding="utf-8")
        k = dokument["hovedtabell"]["kontroll"]
        print(f"{a.pdf.name}: side {dokument['hovedtabell']['pdf_side']}, "
              f"{len(dokument['hovedtabell']['kolonner'])} kolonnar, {k['antall_rader']} rader, "
              f"kryss {k['kryss']['status']} -> {a.output}")
    else:
        print(tekst)
    return 0


def _slaa_opp_kilde(sti: Path, pdf: Path) -> dict | None:
    """kilder.json er anten {filnamn: post} eller ei liste av postar."""
    data = json.loads(Path(sti).read_text(encoding="utf-8"))
    if isinstance(data, dict) and pdf.name in data:
        return data[pdf.name]
    poster = data if isinstance(data, list) else data.get("kilder", data.get("utgaver", []))
    for post in poster:
        if Path(str(post.get("filnavn") or post.get("sti") or "")).name == pdf.name:
            return post
    return None


if __name__ == "__main__":
    raise SystemExit(main())
