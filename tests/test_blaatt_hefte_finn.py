"""Offline-tester for finn_blaatt_hefte.py og hent_blaatt_hefte.py (fase 2)."""

from __future__ import annotations

import importlib.util
import io
import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(REPO, "skills", "knowledge-management", "blatt-hefte")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "blaatt-hefte")


def _last(navn):
    sti = os.path.join(SKILL, "scripts", navn + ".py")
    spec = importlib.util.spec_from_file_location(navn, sti)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


F = _last("finn_blaatt_hefte")
H = _last("hent_blaatt_hefte")

KJENTE = os.path.join(SKILL, "references", "kjente-utgaver.json")
PDF = b"%PDF-1.7\n% testfil\n"


def fixtur(navn):
    with open(os.path.join(FIXTURES, navn), encoding="utf-8") as fil:
        return fil.read()


@pytest.fixture(scope="module")
def kjente():
    with open(KJENTE, encoding="utf-8") as fil:
        return json.load(fil)["utgaver"]


# --- falske klienter -------------------------------------------------------

class FalskKlient:
    """Skriptet nettklient: `sider` er svar eller unntak per GET, `prob_svar` per HEAD."""

    def __init__(self, sider=(), prob_svar=None):
        self.sider = list(sider)
        self.prob_svar = prob_svar or {"status": 404, "content_type": "", "content_length": None}
        self.get_kall = []
        self.head_kall = []

    def hent_side(self, url, timeout):
        self.get_kall.append((url, timeout))
        svar = self.sider.pop(0) if self.sider else {"status": 404, "content_type": "", "kropp": ""}
        if isinstance(svar, Exception):
            raise svar
        return svar

    def prob(self, url, timeout):
        self.head_kall.append((url, timeout))
        svar = dict(self.prob_svar)
        svar.setdefault("content_length", None)
        return svar


def side(html):
    return {"status": 200, "content_type": "text/html", "kropp": html}


# --- A1 mot den ekte temasiden --------------------------------------------

def test_a1_finner_alle_utgaver_2021_2026(kjente):
    tolket = F.tolk_lenker(F.samle_pdf_lenker(fixtur("temaside-2026-09-16.html")))
    funnet = {(t["aar"], t["utgave"]) for t in tolket}
    for aar in range(2021, 2027):
        assert (aar, "forslag") in funnet, aar
        assert (aar, "vedtak") in funnet, aar
    lenket = {(u["budsjettaar"], u["utgave"], u["url"]) for u in kjente if u["lenketekst"]}
    urler = {(t["aar"], t["utgave"], t["url"]) for t in tolket}
    assert lenket <= urler


def test_a1_tar_2023_filen_med_avvikende_navn():
    tolket = F.tolk_lenker(F.samle_pdf_lenker(fixtur("temaside-2026-09-16.html")))
    treff = [t for t in tolket if t["url"].endswith("2022.09.28-forslag-til-orientering-2023-samlefil.pdf")]
    assert len(treff) == 1
    assert treff[0]["aar"] == 2023 and treff[0]["utgave"] == "forslag"


def test_aar_tar_hoyeste_arstall_i_lenketeksten():
    tekst = "Orientering om statsbudsjettet 2026 … etter vedtak i Stortinget 18. desember 2025"
    assert F.finn_aar(tekst, "https://x/fil.pdf") == 2026


def test_utgave_naar_teksten_nevner_bade_forslag_og_vedtak():
    tekst = "Orientering om forslag til statsbudsjettet 2027 … oppdatert etter vedtak i Stortinget"
    assert F.finn_utgave(tekst, "https://x/fil.pdf") == "forslag"
    assert F.finn_utgave("Etter vedtak i Stortinget", "https://x/fil.pdf") == "vedtak"


def test_lenketekst_tar_med_nostet_markup():
    html = '<a href="x.pdf"><span>Orientering om <b>forslag</b> til</span> statsbudsjettet 2027</a>'
    lenker = F.samle_pdf_lenker(html, "https://www.regjeringen.no/")
    assert lenker[0]["tekst"] == "Orientering om forslag til statsbudsjettet 2027"


# --- returkoder ------------------------------------------------------------

def test_returkode_2_ikke_publisert(kjente):
    rapport = F.finn(2027, "forslag", kjente, offline_html=fixtur("temaside-uten-2027.html"),
                     klient=FalskKlient())
    assert rapport["returkode"] == 2
    assert rapport["soekestreng"].startswith("site:regjeringen.no/contentassets")
    assert len(rapport["veier"]["A2"]["forslag"]["prober"]) == 2


def test_returkode_5_strukturbrudd(kjente):
    rapport = F.finn(2026, "forslag", kjente, offline_html=fixtur("temaside-uten-kjente.html"),
                     klient=FalskKlient())
    assert rapport["returkode"] == 5
    assert rapport["veier"]["A3"]["gjenfunnet"] == 0


def test_returkode_7_pdf_uten_lenke(kjente):
    klient = FalskKlient(prob_svar={"status": 200, "content_type": "application/pdf",
                                    "content_length": 1122587})
    rapport = F.finn(2027, "forslag", kjente, offline_html=fixtur("temaside-uten-2027.html"),
                     klient=klient)
    assert rapport["returkode"] == 7
    assert rapport["valgt"]["url"].endswith(".pdf")
    assert rapport["valgt"]["lenketekst"] is None


def test_returkode_3_ukjent_lenke_ma_vurderes(kjente):
    html = fixtur("temaside-uten-2027.html").replace(
        "</ul>",
        '  <li><a href="https://www.regjeringen.no/contentassets/'
        '31af8e2c3a224ac2829e48cc91d89083/orientering-2027-ny-form.pdf">'
        'Orientering til institusjonane 2027</a></li>\n</ul>')
    rapport = F.finn(2027, "forslag", kjente, offline_html=html, klient=FalskKlient())
    assert rapport["returkode"] == 3
    assert len(rapport["veier"]["A3"]["maa_vurderes"]) == 1


def test_flertydighet_gir_0_med_merknad_og_deterministisk_valg(kjente):
    rapport = F.finn(2027, "forslag", kjente,
                     offline_html=fixtur("temaside-to-2027-forslag.html"), klient=FalskKlient())
    assert rapport["returkode"] == 0
    assert rapport["merknad"] and "2 kandidater" in rapport["merknad"]
    assert len(rapport["kandidater"]) == 2
    assert rapport["valgt"]["url"].endswith("korrigert-12.-oktober-2026.pdf")
    igjen = F.finn(2027, "forslag", kjente,
                   offline_html=fixtur("temaside-to-2027-forslag.html"), klient=FalskKlient())
    assert igjen["valgt"] == rapport["valgt"]


def test_velg_kandidat_uten_dato_tar_den_siste_paa_siden():
    kandidater = [{"dato": None, "posisjon": 3, "url": "a"}, {"dato": None, "posisjon": 9, "url": "b"}]
    assert F.velg_kandidat(kandidater)["url"] == "b"


def test_ett_feilet_forsok_saa_suksess_gir_0(kjente):
    klient = FalskKlient(sider=[F.NettFeil("timeout"), side(fixtur("temaside-uten-2027.html"))])
    rapport = F.finn(2026, "forslag", kjente, klient=klient)
    assert rapport["returkode"] == 0
    assert len(klient.get_kall) == 2
    assert [t for _, t in klient.get_kall] == [8.0, 12.0]


def test_to_feilede_forsok_gir_4(kjente):
    klient = FalskKlient(sider=[F.NettFeil("timeout"), F.NettFeil("timeout")])
    rapport = F.finn(2026, "forslag", kjente, klient=klient)
    assert rapport["returkode"] == 4
    assert rapport["soekestreng"]
    assert len(klient.get_kall) == 2


def test_stage_alle_gir_0_for_2026(kjente):
    rapport = F.finn(2026, "alle", kjente, offline_html=fixtur("temaside-2026-09-16.html"),
                     klient=FalskKlient())
    assert rapport["returkode"] == 0
    assert set(rapport["valgt"]) == {"forslag", "vedtak"}


# --- hent ------------------------------------------------------------------

class FalskNedlaster:
    def __init__(self, kropp=PDF, feil_etter=None, content_type="application/pdf"):
        self.kropp = kropp
        self.feil_etter = feil_etter
        self.content_type = content_type

    def aapne(self, url, connect_timeout, read_timeout):
        strom = io.BytesIO(self.kropp) if self.feil_etter is None else _Sprekk(self.feil_etter)
        return {"status": 200, "content_type": self.content_type,
                "content_length": len(self.kropp),
                "filnavn_paa_serveren": url.rsplit("/", 1)[-1], "strom": strom}


class _Sprekk:
    """Strøm som ryker midt i nedlastingen."""

    def __init__(self, bytes_foer_feil):
        self.igjen = bytes_foer_feil

    def read(self, n=-1):
        if self.igjen <= 0:
            raise H.HentFeil("forbindelsen røk")
        blokk = b"%PDF-1.7" + b"x" * max(0, self.igjen - 8)
        self.igjen = 0
        return blokk

    def close(self):
        pass


def test_hent_skriver_fil_hash_og_kilder(tmp_path):
    res = H.hent("https://x/blatt.pdf", str(tmp_path), 2027, "forslag",
                 klient=FalskNedlaster())
    assert os.path.basename(res["sti"]) == "blaatt-hefte-2027-forslag.pdf"
    assert res["sha256"] == H.hashlib.sha256(PDF).hexdigest()
    kilder = json.load(open(tmp_path / "2027" / "kilder.json", encoding="utf-8"))
    assert kilder["blaatt-hefte-2027-forslag.pdf"]["url"] == "https://x/blatt.pdf"
    assert not list((tmp_path / "2027").glob("*.part"))


def test_avbrutt_nedlasting_sletter_part_filen(tmp_path):
    with pytest.raises(H.HentFeil):
        H.hent("https://x/blatt.pdf", str(tmp_path), 2027, "forslag",
               klient=FalskNedlaster(feil_etter=32))
    assert not list((tmp_path / "2027").glob("*.part"))
    assert not (tmp_path / "2027" / "blaatt-hefte-2027-forslag.pdf").exists()


def test_ikke_pdf_avvises(tmp_path):
    with pytest.raises(H.HentFeil):
        H.hent("https://x/blatt.pdf", str(tmp_path), 2027, "forslag",
               klient=FalskNedlaster(kropp=b"<html>feilside</html>"))
    assert not list((tmp_path / "2027").glob("*"))


def test_annen_hash_overskriver_aldri(tmp_path):
    H.hent("https://x/blatt.pdf", str(tmp_path), 2027, "forslag", klient=FalskNedlaster())
    res = H.hent("https://x/blatt.pdf", str(tmp_path), 2027, "forslag",
                 klient=FalskNedlaster(kropp=PDF + b"endret"))
    assert res["sti"].endswith("blaatt-hefte-2027-forslag-v2.pdf")
    assert res["advarsler"]
    original = tmp_path / "2027" / "blaatt-hefte-2027-forslag.pdf"
    assert original.read_bytes() == PDF


def test_hopper_over_naar_hash_stemmer(tmp_path):
    kjent = [{"budsjettaar": 2027, "utgave": "forslag", "url": "https://x/blatt.pdf",
              "sha256": H.hashlib.sha256(PDF).hexdigest(), "gjeldende": True}]
    H.hent("https://x/blatt.pdf", str(tmp_path), 2027, "forslag", known=kjent,
           klient=FalskNedlaster())
    res = H.hent("https://x/blatt.pdf", str(tmp_path), 2027, "forslag", known=kjent,
                 klient=None)
    assert res["hoppet_over"] is True


def test_verifiser_melder_fra_om_feil_hash(tmp_path):
    H.hent("https://x/blatt.pdf", str(tmp_path), 2027, "forslag", klient=FalskNedlaster())
    kjent = [{"budsjettaar": 2027, "utgave": "forslag", "sha256": "0" * 64,
              "lokalt_filnavn": "blaatt-hefte-2027-forslag.pdf"}]
    mangler = H.verifiser(kjent, str(tmp_path))
    assert len(mangler) == 1 and mangler[0]["grunn"] == "feil sha256"


def test_inventar_hasher_lokale_hefter(tmp_path):
    mappe = tmp_path / "2027"
    mappe.mkdir()
    (mappe / "blaatt-hefte-forslag.pdf").write_bytes(PDF)
    (mappe / "kd-prop-1-s.pdf").write_bytes(PDF)
    funn = H.inventar([str(mappe)])
    assert [f["filnavn"] for f in funn] == ["blaatt-hefte-forslag.pdf"]
    assert funn[0]["sha256"] == H.hashlib.sha256(PDF).hexdigest()
