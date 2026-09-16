"""Tester for skills/knowledge-management/blatt-hefte/scripts/les_blaatt_hefte.py.

Alle testene er offline og les berre fixtures under tests/fixtures/blaatt-hefte/.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent
SKRIPT = ROT / "skills" / "knowledge-management" / "blatt-hefte" / "scripts"
FIXTURES = ROT / "tests" / "fixtures" / "blaatt-hefte"
HEILT = FIXTURES / "2025-forslag" / "blaatt-hefte-2025-forslag.pdf"


def _last(navn: str):
    spec = importlib.util.spec_from_file_location(navn, SKRIPT / f"{navn}.py")
    modul = importlib.util.module_from_spec(spec)
    sys.modules[navn] = modul
    spec.loader.exec_module(modul)
    return modul


sys.path.insert(0, str(SKRIPT))
les_modul = _last("les_blaatt_hefte")
kontrakt = _last("kontrakt")


def utsnitt() -> list[Path]:
    """Hefte per fixture-mappe: utsnitt-PDF om den finst, elles heile heftet i analyseprosjektet (WSL).
    Utsnitta vart ikkje committa (1,4–2,6 MB kvar); manglar begge, blir testen hoppa over."""
    valgte = []
    for f in sorted(FIXTURES.glob("*/forventet.json")):
        venta = json.loads(f.read_text(encoding="utf-8"))
        lokal = next(iter(f.parent.glob("blaatt-hefte-*.pdf")), None)
        prosjekt = Path(venta.get("prosjekt_pdf", ""))
        valgte.append(lokal if lokal else (prosjekt if prosjekt.exists() else pytest.param(f.parent, marks=pytest.mark.skip(reason="heftet finst ikkje lokalt"))))
    return valgte


def rad(rader: list[dict], kortkode: str) -> list:
    return next(r["verdier"] for r in rader if r["kortkode_norm"] == kortkode)


@pytest.fixture(scope="module")
def dokument_2025() -> dict:
    return les_modul.les(HEILT)


def test_heilt_hefte_følger_kontrakten(dokument_2025):
    assert kontrakt.valider(dokument_2025) == []
    assert dokument_2025["kilde"]["budsjettaar"] == 2025
    assert dokument_2025["kilde"]["utgave"] == "forslag"


def test_heilt_hefte_uit_rad_og_kolonnar(dokument_2025):
    h = dokument_2025["hovedtabell"]
    assert h["kolonner"][0] == "Saldert budsjett 2024"
    assert h["kolonner"][-1] == "Forslag rammeløyving 2025"
    assert len(h["kolonner"]) == 13
    assert rad(h["rader"], "UIT") == [4061059, 157470, -17034, -24255, -25307, 20487,
                                      -17329, -5653, -1091, 20800, 520, -14214, 4155453]
    assert h["kontroll"]["alle_rader_summerer"] is True
    assert h["kontroll"]["antall_rader"] == h["kontroll"]["forventet_rader"] == 21
    assert h["kontroll"]["antall_band"] == h["kontroll"]["antall_overskrifter"] == 13


def test_heilt_hefte_prissats_og_resultat(dokument_2025):
    p = dokument_2025["prisjustering"]
    assert p["sats_prosent"] == 3.8
    assert p["ren_sats"] is False          # kolonnen inneheld òg tilbakeføringa frå forliket
    assert "3,8" in p["sitat"]
    assert rad(dokument_2025["resultat"]["rader"], "UIT") == [-21307, -2996, -1881, -25307]
    assert dokument_2025["resultat"]["kolonner"] == ["Studiepoeng", "Doktorgradar", "Fullføring", "Sum"]
    assert dokument_2025["resultat"]["sumkolonner"] == [3]


def test_heilt_hefte_satsar_og_universitet(dokument_2025):
    assert dokument_2025["satser"]["lukket_ramme"] is None      # avvikla frå 2025
    assert dokument_2025["satser"]["open_ramme"]["tabeller"]
    universitet = [i["kortkode_norm"] for i in dokument_2025["institusjoner"]["liste"]
                   if i["universitet"]]
    assert sorted(universitet) == ["NMBU", "NTNU", "NU", "OM", "UIA", "UIB", "UIO", "UIS",
                                   "UIT", "USN"]


@pytest.mark.parametrize("pdf", utsnitt(), ids=lambda p: p.parent.name if isinstance(p, Path) else str(p))
def test_utsnitt_gir_forventa_verdiar(pdf: Path):
    """Enkeltsider skorne ut med fitz: leseren finn tabellane på innhald, ikkje på sidetal."""
    mappe = pdf.parent if pdf.parent.parent == FIXTURES else next(d for d in FIXTURES.iterdir() if (d / "forventet.json").exists() and json.loads((d / "forventet.json").read_text(encoding="utf-8")).get("prosjekt_pdf") == str(pdf))
    venta = json.loads((mappe / "forventet.json").read_text(encoding="utf-8"))
    dok = les_modul.les(pdf)
    assert kontrakt.valider(dok) == []
    assert dok["kilde"]["budsjettaar"] == venta["budsjettaar"]
    assert dok["kilde"]["utgave"] == venta["utgave"]
    assert dok["hovedtabell"]["kolonner"] == venta["kolonner"]
    assert dok["hovedtabell"]["kontroll"]["antall_rader"] == venta["antall_rader"]
    assert rad(dok["hovedtabell"]["rader"], "UIT") == venta["uit_rad"]
    assert dok["prisjustering"]["sats_prosent"] == venta["sats_prosent"]
    assert dok["prisjustering"]["ren_sats"] == venta["ren_sats"]
    assert rad(dok["resultat"]["rader"], "UIT") == venta["resultat_uit"]
    assert dok["resultat"]["kolonner"] == venta["resultat_kolonner"]
    universitet = sorted(i["kortkode_norm"] for i in dok["institusjoner"]["liste"]
                         if i["universitet"])
    assert universitet == venta["universiteter"]


def test_kontroll_b_feiler_naar_to_band_smeltar_saman():
    feil = FIXTURES / "feil-sammensmelta-band" / "to-kolonnar-smelta.pdf"
    with pytest.raises(SystemExit) as stopp:
        les_modul.les(feil)
    assert stopp.value.code == 9


REFERANSE_2024V = Path("/home/sihal7953/repos/uit-statsbudsjett/analyse/kilder/blaatt-hefte/2024/blaatt-hefte-2024-vedtak.pdf")


@pytest.mark.skipif(not REFERANSE_2024V.exists(), reason="2024 etter vedtak finst ikkje lokalt (analyseprosjektet i WSL)")
def test_kontroll_c_mot_2024_etter_vedtak():
    referanse = REFERANSE_2024V
    kryss = les_modul.les(HEILT, referanse_pdf=referanse)["hovedtabell"]["kontroll"]["kryss"]
    assert kryss["status"] == "ok"
    assert kryss["avvik"] == []
    assert kryss["referanse"] == referanse.name


def test_kontroll_c_utan_referanse(dokument_2025):
    assert dokument_2025["hovedtabell"]["kontroll"]["kryss"] == {
        "status": "ikke_mulig", "referanse": None, "avvik": []}
