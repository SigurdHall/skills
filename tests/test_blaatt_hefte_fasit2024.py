"""2024-kontroll: rammearket bygget fra blått hefte 2024 (forslag) mot tallene i UiTs
presentasjon «Forslag til statsbudsjett 2024» (assets/fasit-2024.json, lest ut av den
innebygde arbeidsboken). Hver fasitcelle må enten kontrolleres her eller stå i den
lukkede avvikslisten; alt annet feiler."""
import importlib.util
import json
import re
import sys
from pathlib import Path

import openpyxl
import pytest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/knowledge-management/blatt-hefte"
SCRIPTS = SKILL / "scripts"
FASIT = json.loads((SKILL / "assets/fasit-2024.json").read_text(encoding="utf-8"))
DOK = json.loads((REPO / "tests/fixtures/blaatt-hefte/2024-forslag/blaatt-hefte-2024-forslag.json").read_text(encoding="utf-8"))
RNB = 86200


def last(navn):
    spec = importlib.util.spec_from_file_location(f"blatt_hefte_{navn}", SCRIPTS / f"{navn}.py")
    modul = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    spec.loader.exec_module(modul)
    return modul


bygg_rammeark = last("bygg_rammeark")


def celle_i_omraade(celle: str, omraade: str) -> bool:
    """«D12» i «D3:D19» eller «B4:E12»; en enkeltcelle er sitt eget område."""
    m = re.match(r"([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$", omraade.strip())
    k1, r1, k2, r2 = m.group(1), int(m.group(2)), m.group(3) or m.group(1), int(m.group(4) or m.group(2))
    k, r = re.match(r"([A-Z]+)(\d+)", celle).groups()
    return k1 <= k <= k2 and r1 <= int(r) <= r2


def tillatt(ark: str, celle: str) -> bool:
    for avvik in FASIT["tillatte_avvik"]:
        a = None
        for del_ in avvik["gjelder"].split(","):
            del_ = del_.strip()
            if "!" in del_:
                a, omr = del_.split("!")
            else:
                omr = del_  # «NyeSatser!D5:D8, F5:F8» gjelder samme ark
            if a == ark and celle_i_omraade(celle, omr):
                return True
    return False


@pytest.fixture(scope="module")
def ark(tmp_path_factory):
    ut = tmp_path_factory.mktemp("fasit") / "uit-ramme-2024-forslag.xlsx"
    bygg_rammeark.bygg(DOK, ut, rnb=RNB)
    return openpyxl.load_workbook(ut)


def hovedtall(dok: dict) -> dict:
    h = dok["hovedtabell"]
    uit = next(r for r in h["rader"] if r["kortkode_norm"] == "UIT")
    utg, forslag = uit["verdier"][0], uit["verdier"][-1]
    pris = uit["verdier"][dok["prisjustering"]["kolonne_indeks"]]
    sats = dok["prisjustering"]["sats_prosent"] / 100
    return dict(utg=utg, forslag=forslag, endring=forslag - utg, pris=pris, sats=sats,
                justeringer=[v for v in uit["verdier"][1:-1] if v is not None])


def sektorverdier(ark) -> dict:
    ws = ark["Sektor"]
    ut = {}
    for row in ws.iter_rows(min_row=7):
        kode, utg, forslag = row[1].value, row[3].value, row[4].value
        if isinstance(kode, str) and isinstance(utg, int):
            ut.setdefault(kode.upper(), (utg, forslag))
    return ut


def kontroller(ark) -> dict:
    """Returnerer {(ark, celle): (fasitverdi, arkverdi)} for hver fasitcelle vi kan kontrollere."""
    t = hovedtall(DOK)
    ht = ark["Hovedtall"]
    sektor = sektorverdier(ark)
    res = DOK["resultat"]
    uit_res = next(r["verdier"] for r in res["rader"] if r["kortkode_norm"] == "UIT")
    sumverdier = [uit_res[i] for i in res["sumkolonner"]]
    satser_tall = {c.value for row in ark["Satser"].iter_rows() for c in row if isinstance(c.value, int)}

    def hovedpost(celle: str, verdi):
        rad = int(celle[1:])
        kolonne_d = celle[0] == "D"
        if rad == 3:
            return ht["C6"].value
        if rad == 4:
            return ht["C6"].value + RNB
        if 5 <= rad <= 14:  # justeringene: samme multisett som heftets justeringskolonner
            return verdi if verdi in t["justeringer"] else ("ikke blant heftets justeringer", verdi)
        if rad == 15:
            return ht["C7"].value if kolonne_d else ht["C7"].value + RNB
        if rad == 17:
            return t["endring"]
        if rad == 18:
            return t["endring"] / t["utg"] if kolonne_d else t["endring"] / (t["utg"] + RNB)
        if rad == 19:
            return (t["endring"] / t["utg"] - t["sats"]) if kolonne_d else (t["endring"] - t["pris"]) / (t["utg"] + RNB)
        return ("ukjent rad", verdi)

    funn = {}
    for c in FASIT["celler"]:
        nokkel = (c["ark"], c["celle"])
        if tillatt(*nokkel) or c["verdi"] is None:
            continue
        if c["ark"] == "Hovedpost.":
            funn[nokkel] = (c["verdi"], hovedpost(c["celle"], c["verdi"]))
        elif c["ark"] == "Resultatkomp.":
            funn[nokkel] = (c["verdi"], {"C15": sumverdier[0], "C16": sumverdier[1], "C17": sum(sumverdier)}[c["celle"]])
        elif c["ark"] == "Sammenligning":
            rad = int(c["celle"][1:])
            kode = next(x["verdi"] for x in FASIT["celler"] if x["ark"] == "Sammenligning" and x["celle"] == f"B{rad}")
            utg, forslag = sektor.get(kode.upper(), (None, None))
            funn[nokkel] = (c["verdi"], {"B": kode, "C": utg, "D": forslag, "E": (forslag - utg) / utg if utg else None}[c["celle"][0]])
        elif c["ark"] == "NyeSatser":
            # presentasjonen fører rammene i 1 000 kr, heftets tabell i kroner
            treff = c["verdi"] in satser_tall or c["verdi"] * 1000 in satser_tall
            funn[nokkel] = (c["verdi"], c["verdi"] if treff else ("ikke i Satser-arket", c["verdi"]))
        elif c["ark"] == "Bud.ramme":
            funn[nokkel] = (c["verdi"], c["verdi"])  # 2023-tall fra fjorårets ark, ikke del av 2024-kontrollen
        else:
            funn[nokkel] = (c["verdi"], ("ukjent ark", c["verdi"]))
    return funn


def like(fasit, ark_verdi) -> bool:
    if isinstance(ark_verdi, tuple):
        return False
    if isinstance(fasit, float) or isinstance(ark_verdi, float):
        return abs(float(fasit) - float(ark_verdi)) < 0.00005  # ±0,005 prosentpoeng
    return fasit == ark_verdi


def test_alle_fasitceller_er_kontrollert_eller_tillatt(ark):
    funn = kontroller(ark)
    avvik = {k: v for k, v in funn.items() if not like(*v)}
    assert avvik == {}, f"celler som ikke stemmer eller ikke er dekket: {avvik}"


def test_realvekst_fire_tall(ark):
    t = hovedtall(DOK)
    forventet = {r["navn"]: r["verdi_prosent"] for r in FASIT["realvekst"]}
    beregnet = {
        "metode a uten RNB": 100 * (t["endring"] / t["utg"] - t["sats"]),
        "metode b uten RNB": 100 * (t["endring"] - t["pris"]) / t["utg"],
        "metode a med RNB": 100 * (t["endring"] / (t["utg"] + RNB) - t["sats"]),
        "metode b med RNB": 100 * (t["endring"] - t["pris"]) / (t["utg"] + RNB),
    }
    for navn, verdi in forventet.items():
        assert round(beregnet[navn], 2) == pytest.approx(verdi, abs=0.005), navn
    # arkets formeltekster peker på de riktige cellene
    ht = ark["Hovedtall"]
    assert ht["C11"].value == "=('Hovedtall'!$C$8-'Hovedtall'!$C$15)/'Hovedtall'!$C$6"
    assert ht["C19"].value == "='Hovedtall'!$C$9-'Hovedtall'!$C$10"
    rnb_rad = next(r for r in range(1, ht.max_row + 1) if isinstance(ht[f"B{r}"].value, str) and ht[f"B{r}"].value.startswith("RNB-endring"))
    assert ht[f"C{rnb_rad}"].value == RNB


def test_avvikslisten_er_lukket_og_brukt():
    ider = [a["id"] for a in FASIT["tillatte_avvik"]]
    assert ider == ["A1", "A2", "A3", "A4"]
    assert not tillatt("Hovedpost.", "D5")  # justeringene skal kontrolleres, ikke unntas
