"""Tester for bygg_rammeark.py og kjor_blaatt_hefte.py (skillen blatt-hefte)."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import openpyxl
import pytest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/knowledge-management/blatt-hefte"
SCRIPTS = SKILL / "scripts"
EKSEMPEL = SKILL / "assets/eksempel-2025-forslag.json"
HELT_HEFTE = REPO / "tests/fixtures/blaatt-hefte/2025-forslag/blaatt-hefte-2025-forslag.pdf"


def last(navn):
    spec = importlib.util.spec_from_file_location(f"blatt_hefte_{navn}", SCRIPTS / f"{navn}.py")
    modul = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    spec.loader.exec_module(modul)
    return modul


bygg_rammeark = last("bygg_rammeark")


def rnb_celle(ws):
    """RNB-inndatacellen: raden i Hovedtall der etiketten begynner med «RNB-endring»."""
    for row in ws.iter_rows(min_col=2, max_col=3):
        if isinstance(row[0].value, str) and row[0].value.startswith("RNB-endring"):
            return row[1]
    raise AssertionError("fant ikke RNB-cellen")


@pytest.fixture(scope="module")
def dok():
    return json.loads(EKSEMPEL.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ark_uten_rnb(dok, tmp_path_factory):
    ut = tmp_path_factory.mktemp("bygg") / "uten.xlsx"
    bygg_rammeark.bygg(dok, ut)
    return openpyxl.load_workbook(ut)


@pytest.fixture(scope="module")
def ark_med_rnb(dok, tmp_path_factory):
    ut = tmp_path_factory.mktemp("bygg") / "med.xlsx"
    bygg_rammeark.bygg(dok, ut, rnb=1000)
    return openpyxl.load_workbook(ut)


def test_seks_ark_i_rekkefolge(ark_uten_rnb):
    synlige = [ws.title for ws in ark_uten_rnb.worksheets if ws.sheet_state == "visible"]
    assert synlige == ["Hovedtall", "Budsjettløp", "Hovedposter", "Resultat", "Sektor", "Satser", "Kilder"]


def test_hovedposter_har_heftets_kolonner(dok, ark_uten_rnb):
    ws = ark_uten_rnb["Hovedposter"]
    kolonner = dok["hovedtabell"]["kolonner"]
    etiketter = [ws[f"B{6 + i}"].value for i in range(len(kolonner))]
    assert etiketter == kolonner
    uit = next(r for r in dok["hovedtabell"]["rader"] if r["kortkode_norm"] == "UIT")
    verdier = [ws[f"D{6 + i}"].value for i in range(len(kolonner))]
    assert verdier == uit["verdier"]


def test_kontrollcelle_er_null_ved_egen_beregning(dok, ark_uten_rnb):
    ws = ark_uten_rnb["Hovedposter"]
    n = len(dok["hovedtabell"]["kolonner"])
    sumrad, forslagrad = 6 + n, 6 + n - 1
    assert ws[f"D{sumrad}"].value == f"=SUM(D6:D{forslagrad - 1})"
    assert ws[f"D{sumrad + 1}"].value == f"=D{sumrad}-D{forslagrad}"
    verdier = [ws[f"D{6 + i}"].value or 0 for i in range(n)]
    assert sum(verdier[:-1]) - verdier[-1] == 0


def test_hovedtall_etiketter_og_verdier(dok, ark_uten_rnb):
    ws = ark_uten_rnb["Hovedtall"]
    assert ws["B6"].value == dok["hovedtabell"]["kolonner"][0]
    assert ws["B7"].value == dok["hovedtabell"]["kolonner"][-1]
    assert ws["C6"].value == 4061059 and ws["C7"].value == 4155453
    assert ws["C10"].value == pytest.approx(0.038)
    assert ws["C15"].value == 157470
    assert "nei" in ws["C18"].value
    assert rnb_celle(ws).value == 8300  # RNB 2024 fra budsjettbasen (supplerende tildelingsbrev 25.06.2024)
    assert "ikke oppgitt" in ws["C12"].value  # formelen har fallback-teksten når cellen tømmes


def test_rnb_fylles_naar_oppgitt(ark_med_rnb):
    assert rnb_celle(ark_med_rnb["Hovedtall"]).value == 1000  # --rnb overstyrer basen


def test_budsjettloep_har_aarene_til_og_med_heftets(ark_uten_rnb):
    ws = ark_uten_rnb["Budsjettløp"]
    aar = [ws[f"B{6 + i}"].value for i in range(6)]
    assert aar == ["2021", "2022", "2023", "2024", "2025", None]
    rad_2025 = 6 + aar.index("2025")
    assert ws[f"C{rad_2025}"].value == 4155453 and ws[f"D{rad_2025}"].value == 4175449 and ws[f"E{rad_2025}"].value == -907
    rad_2024 = 6 + aar.index("2024")
    assert ws[f"E{rad_2024}"].value == 8300 and "tildelingsbrev" in ws[f"G{rad_2024}"].value
    rad_2023 = 6 + aar.index("2023")
    assert ws[f"E{rad_2023}"].value == 86200 and "(uverifisert)" in ws[f"G{rad_2023}"].value
    assert ws["E5"].value == "RNB-endring, kap. 260 post 50"


def test_rnb_etikett_og_regime(ark_uten_rnb):
    ws = ark_uten_rnb["Hovedtall"]
    tekster = {c.value for row in ws.iter_rows() for c in row if isinstance(c.value, str)}
    assert not any("RNB-proposisjonen" in t for t in tekster)
    assert any("RNB-endring 2024" in t for t in tekster)
    assert any("Realvekst (metode b, med RNB 2024 i utgangspunktet)" == t for t in tekster)
    assert any("RNB-regime" in t for t in tekster)


def test_base_port_gir_merknad_ved_avvik(dok, tmp_path):
    base = bygg_rammeark.last_base()
    import copy
    b = copy.deepcopy(base)
    b["aar"]["2024"]["vedtatt"]["ramme"] += 1
    res = bygg_rammeark.bygg(dok, tmp_path / "x.xlsx", base=b)
    assert res["base_merknad"] and "4 061 059" in res["base_merknad"]
    res_ok = bygg_rammeark.bygg(dok, tmp_path / "y.xlsx", base=base)
    assert res_ok["base_merknad"] is None


def test_satser_uten_lukket_ramme_har_tekst(ark_uten_rnb):
    ws = ark_uten_rnb["Satser"]
    tekster = [c.value for row in ws.iter_rows() for c in row if isinstance(c.value, str)]
    assert any("Lukket ramme finnes ikke" in t for t in tekster)
    assert any("Open ramme" == t for t in tekster)
    assert not any("Open ramme finst ikkje" in t for t in tekster)


def test_sektor_universiteter_forst_og_uit_fet(dok, ark_uten_rnb):
    ws = ark_uten_rnb["Sektor"]
    univ = sorted((i["kortkode"] for i in dok["institusjoner"]["liste"] if i["universitet"] and i["statlig"]), key=str.upper)
    koder = [ws[f"B{7 + i}"].value for i in range(len(univ))]
    assert koder == univ
    uit_rad = 7 + koder.index("UiT")
    assert ws[f"B{uit_rad}"].font.bold
    assert ws[f"H{uit_rad}"].value == f"=(E{uit_rad}-D{uit_rad}-G{uit_rad})/D{uit_rad}"


def test_kilder_har_sha_og_sitat(dok, ark_uten_rnb):
    ws = ark_uten_rnb["Kilder"]
    verdier = {c.value for row in ws.iter_rows() for c in row if c.value is not None}
    assert dok["kilde"]["sha256"] in verdier
    assert dok["prisjustering"]["sitat"] in verdier


@pytest.mark.skipif(not HELT_HEFTE.exists(), reason="det komplette 2025-heftet er ikke lagt som fixture")
def test_kjor_tid_og_status(tmp_path):
    """Kjeden på lokal fil: returkode 0/10, status i seks deler, stdout lik fil, kjedens tid under 60 s."""
    python = sys.executable
    beste = None
    for _ in range(2):
        ut = tmp_path / "uit-ramme-2025-test.xlsx"
        status = tmp_path / "status-2025-forslag.md"
        res = subprocess.run(
            [python, str(SCRIPTS / "kjor_blaatt_hefte.py"), "--pdf", str(HELT_HEFTE), "--year", "2025",
             "--stage", "forslag", "--output", str(ut), "--status-output", str(status),
             "--output-dir", str(tmp_path), "--kilder-dir", str(tmp_path / "kilder")],
            capture_output=True, text=True, encoding="utf-8")
        assert res.returncode in (0, 10), res.stdout + res.stderr
        assert ut.exists()
        tekst = status.read_text(encoding="utf-8")
        assert res.stdout == tekst
        assert [f"{i}. " in tekst for i in range(1, 7)] == [True] * 6
        assert len(tekst.splitlines()) <= 25
        tid = json.loads((tmp_path / "tid-2025-forslag.json").read_text(encoding="utf-8"))
        kjede = sum(tid["tider"].get(s, 0) for s in ("les", "bygg", "status"))
        beste = kjede if beste is None else min(beste, kjede)
    assert beste < 60, f"kjeden brukte {beste} s"
    if beste > 21:
        print(f"ADVARSEL: kjeden brukte {beste} s, over stegbudsjettet 21 s")
