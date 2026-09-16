"""Kjør hele kjeden finn → hent → les → bygg → status i én prosess med tidsbudsjett.

    kjor_blaatt_hefte.py --year 2027 [--stage forslag] [--budget 120] [--rnb N]
    kjor_blaatt_hefte.py --pdf <lokal fil> --year 2026 --stage forslag   (hopper over finn og hent)

Returkoder: 0 ark levert og alle kontroller grønne; 10 ark levert med merknad
(kontroll C-avvik hos 1–2 institusjoner, prisjustering ikke ren sats, eller to
kandidater der koden valgte); 9 kontrollfeil i les, ingen ark (forrang foran 8);
8 budsjettbrudd, ingen ark; ellers finn-koden (2 ikke publisert, 3 ukjent lenke,
4 nettfeil, 5 strukturbrudd, 7 fil funnet uten lenke). Statusprompten skrives
alltid, også ved avbrudd, til stdout og til leveransemappen.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER))

import bygg_rammeark  # noqa: E402
import finn_blaatt_hefte  # noqa: E402
import hent_blaatt_hefte  # noqa: E402
import les_blaatt_hefte  # noqa: E402

SKILL = HER.parent
PROSJEKT = Path("/home/sihal7953/repos/uit-statsbudsjett")
STATUS_MAL = SKILL / "assets" / "status.md"
KJENTE = SKILL / "references" / "kjente-utgaver.json"
INSTITUSJONER = SKILL / "references" / "institusjoner.json"
VERSJON = "1.0"

# Budsjett per steg i sekunder (planen: finn 25, hent 30, les 15, bygg 5, status 1).
STEGBUDSJETT = {"finn": 25, "hent": 30, "les": 15, "bygg": 5, "status": 1}


class Budsjettbrudd(Exception):
    pass


class Klokke:
    """Absolutt frist og tid per steg."""

    def __init__(self, budsjett: float):
        self.start = time.perf_counter()
        self.frist = self.start + budsjett
        self.tider: dict[str, float] = {}

    def igjen(self) -> float:
        return self.frist - time.perf_counter()

    def krev(self, steg: str) -> float:
        """Returner tiden steget får: minste av stegbudsjettet og det som er igjen."""
        igjen = self.igjen()
        if igjen <= 0:
            raise Budsjettbrudd(f"budsjettet var brukt opp før {steg}")
        return min(STEGBUDSJETT[steg], igjen)

    def maal(self, steg: str, start: float) -> None:
        self.tider[steg] = round(time.perf_counter() - start, 2)
        if self.igjen() < 0:
            raise Budsjettbrudd(f"budsjettet ble brukt opp under {steg}")

    def total(self) -> float:
        return round(time.perf_counter() - self.start, 2)


def naa_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fmt_kr(v) -> str:
    return "ikke levert" if v is None else f"{v:,}".replace(",", " ")


def fmt_pst(v) -> str:
    return "ikke levert" if v is None else f"{v:+.2f} %".replace(".", ",")


def hovedtall(dok: dict | None, rnb: int | None) -> dict:
    """Hovedtall for UiT fra kontraktdokumentet; realvekst = (endring − prisjustering) / utgangspunkt."""
    tom = dict(utgangspunkt=None, forslag=None, endring_kr=None, nominell_pst=None,
               prissats=None, realvekst_uten_rnb=None, realvekst_med_rnb=None)
    if dok is None:
        return tom
    h = dok["hovedtabell"]
    uit = next(r for r in h["rader"] if r["kortkode_norm"] == "UIT")
    utg, forslag = uit["verdier"][0], uit["verdier"][h["sum_indeks"]]
    pris_idx = dok["prisjustering"]["kolonne_indeks"]
    pris = uit["verdier"][pris_idx] if pris_idx is not None else None
    endring = forslag - utg
    tall = dict(tom)
    tall.update(utgangspunkt=utg, forslag=forslag, endring_kr=endring, nominell_pst=100 * endring / utg,
                prissats=dok["prisjustering"]["sats_prosent"])
    if pris is not None:
        tall["realvekst_uten_rnb"] = 100 * (endring - pris) / utg
        if rnb:
            tall["realvekst_med_rnb"] = 100 * (endring - pris) / (utg + rnb)
    return tall


def skriv_status(felter: dict, sti: Path | None) -> str:
    mal = STATUS_MAL.read_text(encoding="utf-8")
    tekst = mal.format(**felter)
    if sti is not None:
        sti.parent.mkdir(parents=True, exist_ok=True)
        sti.write_text(tekst, encoding="utf-8")
    sys.stdout.write(tekst)
    sys.stdout.flush()
    return tekst


def kjor(args: argparse.Namespace) -> int:
    klokke = Klokke(args.budget)
    ut = Path(args.output_dir)
    utgave = args.stage
    status_sti = Path(args.status_output) if args.status_output else ut / f"status-{args.year}-{utgave}.md"
    returkode = 0
    dom, handling, merknader = "", [], []
    rnb_brukt, rnb_kilde = args.rnb, ("oppgitt med --rnb" if args.rnb is not None else "ikke oppgitt")
    finn_rapport: dict | None = None
    pdf: Path | None = Path(args.pdf) if args.pdf else None
    kilde: dict | None = None
    dok: dict | None = None
    ark_sti: Path | None = None
    json_sti: Path | None = None

    try:
        # finn
        if pdf is None:
            t = time.perf_counter()
            tillatt = klokke.krev("finn")
            finn_rapport = finn_blaatt_hefte.finn(
                args.year, utgave, Path(args.known),
                timeouts=dict(get=min(8, tillatt), retry=min(12, max(0.0, tillatt - 8)), head=min(5, tillatt)),
            )
            klokke.maal("finn", t)
            returkode = finn_rapport["returkode"]
            dom = finn_rapport["begrunnelse"]
            if returkode != 0:
                if finn_rapport.get("soekestreng"):
                    handling.append("Websøk manuelt: " + finn_rapport["soekestreng"])
                if returkode == 7:
                    handling.append("Fil funnet uten lenke fra temasiden; bekreft URL og hash før bruk.")
                if returkode in (3, 5):
                    handling.append("Vis finn-rapporten til brukeren; ikke velg selv.")
                raise SystemExit(returkode)
            if finn_rapport.get("merknad"):
                merknader.append(finn_rapport["merknad"])
            valgt = finn_rapport["valgt"]
            if utgave in valgt:  # rapporten for «alle» er nøklet på utgave
                valgt = valgt[utgave]

            # hent
            t = time.perf_counter()
            tillatt = klokke.krev("hent")
            kilde = hent_blaatt_hefte.hent(
                valgt["url"], Path(args.kilder_dir), args.year, utgave,
                known=Path(args.known), connect_timeout=min(5, tillatt), read_timeout=min(15, max(1.0, tillatt - 5)),
            )
            klokke.maal("hent", t)
            pdf = Path(kilde["sti"])
            merknader.extend(kilde.get("advarsler", []))
        else:
            dom = "lokal fil oppgitt med --pdf; finn og hent hoppet over"
            klokke.tider["finn"] = 0.0
            klokke.tider["hent"] = 0.0

        # les
        t = time.perf_counter()
        klokke.krev("les")
        referanse = finn_referanse(pdf, args.year, Path(args.kilder_dir))
        try:
            dok = les_blaatt_hefte.les(pdf, kilde=kilde, referanse_pdf=referanse)
        except SystemExit as e:
            klokke.maal("les", t)
            dom = dom or "heftet er lest, men kontrollen feilet"
            handling.append(f"Kontrollfeil i les: {e}")
            raise SystemExit(9)
        klokke.maal("les", t)
        json_sti = ut / f"blaatt-hefte-{args.year}-{utgave}.json"
        json_sti.parent.mkdir(parents=True, exist_ok=True)
        json_sti.write_text(json.dumps(dok, ensure_ascii=False, indent=1), encoding="utf-8")

        k = dok["hovedtabell"]["kontroll"]
        if not k["alle_rader_summerer"]:
            merknader.append("Kontroll A: én rad i hovedtabellen summerer ikke til heftets sluttkolonne "
                             "(trolig trykkfeil i heftet); se JSON.")
        merknader.extend(universitetsavvik(dok))
        if k["kryss"]["status"] == "avvik":
            merknader.append(f"Kontroll C: {len(k['kryss']['avvik'])} institusjon(er) avviker fra forrige hefte: "
                             + ", ".join(a["kortkode_norm"] for a in k["kryss"]["avvik"]))
        if dok["prisjustering"]["ren_sats"] is False:
            merknader.append(f"Prisjusteringskolonnen er ikke ren sats (avvik {fmt_kr(dok['prisjustering']['avvik'])}); "
                             "se sitatet i arket Kilder.")

        # bygg
        t = time.perf_counter()
        klokke.krev("bygg")
        ark_sti = Path(args.output) if args.output else ut / f"uit-ramme-{args.year}-{utgave}.xlsx"
        bygget = bygg_rammeark.bygg(dok, ark_sti, rnb=args.rnb, finn_rapport=finn_rapport)
        rnb_brukt, rnb_kilde = bygget["rnb"], bygget["rnb_kilde"]
        klokke.maal("bygg", t)
        dom = dom or f"publisert; {utgave}sutgaven for {args.year} er hentet og lest"
        returkode = 10 if merknader else 0

    except Budsjettbrudd as e:
        returkode = 8
        dom = dom or "avbrutt"
        handling.append(f"Budsjettbrudd: {e}. Ingen ark levert; kjør igjen med --pdf på lokal fil.")
    except SystemExit as e:
        returkode = int(e.code) if isinstance(e.code, int) else 1

    # status
    t = time.perf_counter()
    handling = merknader + handling
    tall = hovedtall(dok, rnb_brukt)
    klokke.tider["status"] = round(time.perf_counter() - t, 2)
    felter = dict(
        budsjettaar=args.year, utgave=utgave, dom=dom or "ikke levert", returkode=returkode,
        kilde_linje=(f"URL {kilde['url']}" if kilde and kilde.get("url") else (f"Lokal fil {pdf}" if pdf else "ingen kilde")),
        handling="; ".join(handling) if handling else "ingen",
        utgangspunkt=fmt_kr(tall["utgangspunkt"]), forslag=fmt_kr(tall["forslag"]), endring_kr=fmt_kr(tall["endring_kr"]),
        nominell_pst=fmt_pst(tall["nominell_pst"]),
        prissats=("ikke levert" if tall["prissats"] is None else f"{tall['prissats']:.1f} %".replace(".", ",")),
        realvekst_uten_rnb=fmt_pst(tall["realvekst_uten_rnb"]),
        realvekst_med_rnb=("ikke oppgitt" if rnb_brukt is None
                           else fmt_pst(tall["realvekst_med_rnb"]) + f" (RNB {args.year - 1}: {fmt_kr(rnb_brukt)})"),
        kontroll_a=kontrolltekst(dok, "alle_rader_summerer"), kontroll_b=kontroll_b_tekst(dok),
        kontroll_c=(dok["hovedtabell"]["kontroll"]["kryss"]["status"] if dok else "ikke levert"),
        ren_sats=("ikke levert" if dok is None else str(dok["prisjustering"]["ren_sats"])),
        sti_ark=ark_sti or "ikke levert", sti_json=json_sti or "ikke levert",
        sti_kilde=(pdf or "ikke levert"), sti_status=status_sti,
        tid_finn=klokke.tider.get("finn", "ikke kjørt"), tid_hent=klokke.tider.get("hent", "ikke kjørt"),
        tid_les=klokke.tider.get("les", "ikke kjørt"), tid_bygg=klokke.tider.get("bygg", "ikke kjørt"),
        tid_status=klokke.tider["status"], tid_total=klokke.total(), budsjett=args.budget,
    )
    skriv_status(felter, status_sti)
    (status_sti.parent / f"tid-{args.year}-{utgave}.json").write_text(
        json.dumps({"tider": klokke.tider, "total": klokke.total(), "returkode": returkode, "kjort_utc": naa_utc()}, indent=1),
        encoding="utf-8")
    return returkode


def universitetsavvik(dok: dict) -> list[str]:
    """Merknad når heftets universitetsliste avviker fra references/institusjoner.json."""
    if not INSTITUSJONER.exists():
        return []
    aar = dok["kilde"]["budsjettaar"]
    kjent = {u["kortkode"].upper() for u in json.loads(INSTITUSJONER.read_text(encoding="utf-8")).get("universiteter", [])
             if u.get("fra_budsjettaar", 0) <= aar}
    i_heftet = {i["kortkode_norm"] for i in dok["institusjoner"]["liste"] if i["universitet"] and i["statlig"]}
    nye, borte = sorted(i_heftet - kjent), sorted(kjent - i_heftet)
    if not nye and not borte:
        return []
    deler = []
    if nye:
        deler.append("nye universiteter i heftet: " + ", ".join(nye))
    if borte:
        deler.append("mangler i heftet: " + ", ".join(borte))
    return ["Universitetslisten avviker fra institusjoner.json (" + "; ".join(deler) + "); heftet er brukt i arket Sektor."]


def kontrolltekst(dok: dict | None, felt: str) -> str:
    if dok is None:
        return "ikke levert"
    return "ok" if dok["hovedtabell"]["kontroll"][felt] else "FEIL"


def kontroll_b_tekst(dok: dict | None) -> str:
    if dok is None:
        return "ikke levert"
    k = dok["hovedtabell"]["kontroll"]
    ok = k["antall_band"] == k["antall_overskrifter"] and k["utgangspunkt_gjenkjent"] and k["sum_gjenkjent"]
    return f"ok ({k['antall_band']} kolonner)" if ok else "FEIL"


def finn_referanse(pdf: Path, year: int, kilder_dir: Path) -> Path | None:
    """Forrige års vedtaksutgave fra kildemappen, for kontroll C."""
    for kandidat in (kilder_dir / str(year - 1)).glob("blaatt-hefte-*-vedtak*.pdf"):
        if kandidat != pdf:
            return kandidat
    return None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--year", type=int, required=True, help="budsjettår")
    p.add_argument("--stage", default="forslag", choices=["forslag", "vedtak"])
    p.add_argument("--budget", type=float, default=120)
    p.add_argument("--pdf", help="lokal PDF; hopper over finn og hent")
    p.add_argument("--rnb", type=int, help="tillegg i RNB året før, 1 000 kroner")
    p.add_argument("--output", help="sti til xlsx (standard leveranser/rammeark/uit-ramme-<år>-<utgave>.xlsx)")
    p.add_argument("--status-output", help="sti til statusfilen")
    p.add_argument("--output-dir", default=str(PROSJEKT / "leveranser" / "rammeark"))
    p.add_argument("--kilder-dir", default=str(PROSJEKT / "analyse" / "kilder" / "blaatt-hefte"))
    p.add_argument("--known", default=str(KJENTE))
    args = p.parse_args(argv)
    if args.output and not args.status_output:
        args.status_output = str(Path(args.output).with_name(f"status-{args.year}-{args.stage}.md"))
    return kjor(args)


if __name__ == "__main__":
    raise SystemExit(main())
