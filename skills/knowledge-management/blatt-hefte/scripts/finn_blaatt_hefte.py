#!/usr/bin/env python3
"""Finn blått hefte (Orientering om statsbudsjettet for universitet og høgskular) på regjeringen.no.

Tre veier:
  A1  temasiden id619675 leses og alle PDF-lenker tolkes (primær, avgjør alene)
  A2  HEAD-probe på de to kjente filnavnvariantene (bekrefter, avgjør aldri)
  A3  diff av temasidens PDF-lenker mot references/kjente-utgaver.json

Returkoder: 0 funnet, 2 ikke publisert, 3 ukjent lenke må vurderes,
4 nettfeil, 5 strukturbrudd, 7 PDF uten lenke. Se kildekart-blaatt-hefte.md.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

VERSJON = "1.0"
BASE = "https://www.regjeringen.no/contentassets/31af8e2c3a224ac2829e48cc91d89083/"
TEMASIDE = (
    "https://www.regjeringen.no/no/tema/utdanning/hoyere-utdanning/"
    "orientering-om-forslag-til-statsbudsjett-for-universiteter-og-hoyskoler/id619675/"
)
BRUKERAGENT = "uit-blatt-hefte/1.0 (+skills/knowledge-management/blatt-hefte)"

STANDARD_TIMEOUTS = {"get": 8.0, "retry": 12.0, "head": 5.0}

MAANEDER = {
    "januar": 1, "februar": 2, "mars": 3, "april": 4, "mai": 5, "juni": 6,
    "juli": 7, "august": 8, "september": 9, "oktober": 10, "okt": 10,
    "november": 11, "desember": 12, "des": 12,
}


class NettFeil(Exception):
    """Kallet nådde aldri fram, eller svaret kunne ikke leses."""


# --- nettlag ---------------------------------------------------------------

class Nettklient:
    """Tynt lag over urllib, slik at testene kan sette inn en falsk klient."""

    def hent_side(self, url, timeout):
        req = urllib.request.Request(url, headers={"User-Agent": BRUKERAGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as svar:
                return {
                    "status": svar.status,
                    "content_type": svar.headers.get("Content-Type", ""),
                    "kropp": svar.read().decode("utf-8", "replace"),
                }
        except urllib.error.HTTPError as feil:
            return {"status": feil.code, "content_type": "", "kropp": ""}
        except Exception as feil:  # URLError, timeout, socket-feil
            raise NettFeil(str(feil)) from feil

    def prob(self, url, timeout):
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": BRUKERAGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as svar:
                lengde = svar.headers.get("Content-Length")
                return {
                    "status": svar.status,
                    "content_type": svar.headers.get("Content-Type", ""),
                    "content_length": int(lengde) if lengde and lengde.isdigit() else None,
                }
        except urllib.error.HTTPError as feil:
            return {"status": feil.code, "content_type": "", "content_length": None}
        except Exception as feil:
            raise NettFeil(str(feil)) from feil


# --- HTML ------------------------------------------------------------------

class LenkeSamler(HTMLParser):
    """Samler alle <a href=…pdf> med all tekst i elementet, også nøstet markup."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lenker = []
        self._dybde = 0
        self._href = None
        self._tekst = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        if self._dybde:
            self._dybde += 1
            return
        href = dict(attrs).get("href") or ""
        if ".pdf" in href.lower():
            self._dybde = 1
            self._href = href
            self._tekst = []

    def handle_endtag(self, tag):
        if tag != "a" or not self._dybde:
            return
        self._dybde -= 1
        if self._dybde:
            return
        tekst = re.sub(r"\s+", " ", "".join(self._tekst)).strip()
        self.lenker.append({"href": self._href, "tekst": tekst})
        self._href = None

    def handle_data(self, data):
        if self._dybde:
            self._tekst.append(data)


def samle_pdf_lenker(html, grunnurl=TEMASIDE):
    parser = LenkeSamler()
    parser.feed(html)
    lenker = []
    sett = set()
    for i, lenke in enumerate(parser.lenker):
        url = urllib.parse.urljoin(grunnurl, lenke["href"].strip())
        if url in sett:
            continue
        sett.add(url)
        lenker.append({"url": url, "tekst": lenke["tekst"], "posisjon": i})
    return lenker


# --- tolkning av lenker ----------------------------------------------------

def filnavn(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def finn_aar(tekst, url):
    """Årstall i lenketeksten først (høyeste når flere), så i filnavnet."""
    for kilde in (tekst, filnavn(url)):
        aar = [int(t) for t in re.findall(r"\b(20\d{2})\b", kilde or "")]
        if aar:
            return max(aar)
    return None


def finn_utgave(tekst, url):
    samlet = f"{tekst or ''} {filnavn(url)}".lower()
    if "vedtak" in samlet and "forslag" not in samlet:
        return "vedtak"
    if "forslag" in samlet:
        return "forslag"
    return "ukjent"


def finn_dato(tekst, url):
    """Nyeste dato i lenketekst eller filnavn, som ISO-streng. None når ingen finnes."""
    samlet = f"{tekst or ''} {filnavn(url)}".lower()
    datoer = []
    for aar, maaned, dag in re.findall(r"\b(20\d{2})[.\-/](\d{1,2})[.\-/](\d{1,2})\b", samlet):
        datoer.append((int(aar), int(maaned), int(dag)))
    for dag, navn, aar in re.findall(r"\b(\d{1,2})\.\s*-?\s*([a-zæøå]+)\.?\s*-?\s*(\d{2,4})\b", samlet):
        if navn in MAANEDER:
            a = int(aar)
            datoer.append((a + 2000 if a < 100 else a, MAANEDER[navn], int(dag)))
    for dag, maaned, aar in re.findall(r"\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b", samlet):
        a = int(aar)
        datoer.append((a + 2000 if a < 100 else a, int(maaned), int(dag)))
    if not datoer:
        return None
    a, m, d = max(datoer)
    return f"{a:04d}-{m:02d}-{d:02d}"


def tolk_lenker(lenker):
    tolket = []
    for lenke in lenker:
        tolket.append({
            "url": lenke["url"],
            "lenketekst": lenke["tekst"],
            "posisjon": lenke["posisjon"],
            "aar": finn_aar(lenke["tekst"], lenke["url"]),
            "utgave": finn_utgave(lenke["tekst"], lenke["url"]),
            "dato": finn_dato(lenke["tekst"], lenke["url"]),
        })
    return tolket


def velg_kandidat(kandidater):
    """Nyeste dato vinner; uten dato vinner den som står sist på den kronologiske siden."""
    med_dato = [k for k in kandidater if k["dato"]]
    if med_dato:
        return max(med_dato, key=lambda k: (k["dato"], k["posisjon"]))
    return max(kandidater, key=lambda k: k["posisjon"])


# --- veiene ----------------------------------------------------------------

def vei_a1(klient, timeouts, offline_html):
    """Les temasiden. Kaster NettFeil når begge forsøk feiler."""
    vei = {"navn": "temaside", "url": TEMASIDE, "forsok": [], "http_status": None,
           "antall_pdf_lenker": 0, "dom": ""}
    if offline_html is not None:
        vei["url"] = "offline"
        vei["dom"] = "lest fra --offline-html"
        vei["http_status"] = 200
        return vei, offline_html

    siste_feil = None
    for timeout in (timeouts["get"], timeouts["retry"]):
        start = time.perf_counter()
        try:
            svar = klient.hent_side(TEMASIDE, timeout)
        except NettFeil as feil:
            siste_feil = str(feil)
            vei["forsok"].append({"timeout_s": timeout, "status": None,
                                  "feil": siste_feil, "sekunder": round(time.perf_counter() - start, 3)})
            continue
        vei["forsok"].append({"timeout_s": timeout, "status": svar["status"], "feil": None,
                              "sekunder": round(time.perf_counter() - start, 3)})
        vei["http_status"] = svar["status"]
        if svar["status"] == 200:
            vei["dom"] = f"temasiden lest på forsøk {len(vei['forsok'])}"
            return vei, svar["kropp"]
        siste_feil = f"HTTP {svar['status']}"
    vei["dom"] = f"temasiden svarte ikke etter to forsøk: {siste_feil}"
    raise NettFeil(vei["dom"])


def filnavnvarianter(year, stage):
    if stage == "vedtak":
        return [
            f"{BASE}orientering-om-statsbudsjettet-{year}-for-universitet-og-hogskular.pdf",
            f"{BASE}orientering-om-statsbudsjettet-{year}-universitet-og-hogskular.pdf",
        ]
    return [
        f"{BASE}orientering-om-forslag-til-statsbudsjettet-{year}-universitet-og-hogskular.pdf",
        f"{BASE}orientering-om-forslag-til-statsbudsjettet-{year}-for-universitet-og-hogskular.pdf",
    ]


def vei_a2(klient, year, stage, timeouts):
    """To HEAD-prober parallelt. Publisert bare ved 200 og application/pdf."""
    urler = filnavnvarianter(year, stage)
    vei = {"navn": "filnavnprobe", "prober": [], "treff": [], "dom": ""}

    def prob(url):
        try:
            svar = klient.prob(url, timeouts["head"])
            svar["url"] = url
            svar["feil"] = None
        except NettFeil as feil:
            svar = {"url": url, "status": None, "content_type": "", "content_length": None,
                    "feil": str(feil)}
        return svar

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(urler)) as pool:
        vei["prober"] = list(pool.map(prob, urler))
    vei["treff"] = [p for p in vei["prober"]
                    if p["status"] == 200 and "application/pdf" in (p["content_type"] or "").lower()]
    vei["dom"] = (f"{len(vei['treff'])} av {len(urler)} filnavnvarianter svarte 200 med PDF"
                  if vei["treff"] else "ingen filnavnvariant svarte 200 med PDF")
    return vei


def vei_a3(tolket, kjente, year):
    """Diff mot kjente utgaver: hva er gjenfunnet, og hva er nytt."""
    kjente_url = {k["url"] for k in kjente}
    forventet = [k for k in kjente if k.get("lenketekst")]
    funn_url = {t["url"] for t in tolket}
    gjenfunnet = [k["url"] for k in forventet if k["url"] in funn_url]
    ukjente = [t for t in tolket if t["url"] not in kjente_url]
    maa_vurderes = [t for t in ukjente if t["aar"] is None or t["aar"] >= year]
    return {
        "navn": "diff mot kjente utgaver",
        "antall_kjente": len(kjente),
        "forventet_lenket": len(forventet),
        "gjenfunnet": len(gjenfunnet),
        "ukjente_lenker": ukjente,
        "maa_vurderes": maa_vurderes,
        "dom": f"{len(gjenfunnet)} av {len(forventet)} lenkede kjente utgaver gjenfunnet, "
               f"{len(ukjente)} ukjente lenker ({len(maa_vurderes)} må vurderes)",
    }


def soekestreng(year):
    return (f"site:regjeringen.no/contentassets orientering statsbudsjettet {year} "
            "universitet hogskular")


# --- hovedfunksjon ---------------------------------------------------------

def finn(year, stage, known, timeouts=None, offline_html=None, klient=None):
    """Finn utgaven av blått hefte for budsjettåret `year`.

    `stage` er "forslag", "vedtak" eller "alle". `known` er en liste med kjente
    utgaver (innholdet i kjente-utgaver.json) eller en sti til den filen.
    Returnerer rapporten som dict; feltet "returkode" er dommen.
    """
    start = time.perf_counter()
    timeouts = {**STANDARD_TIMEOUTS, **(timeouts or {})}
    kjente = les_kjente(known)
    klient = klient or Nettklient()

    rapport = {
        "skript": "finn_blaatt_hefte.py",
        "versjon": VERSJON,
        "tidsstempel_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "budsjettaar": year,
        "utgave": stage,
        "veier": {},
        "valgt": None,
        "kandidater": [],
        "merknad": None,
        "soekestreng": None,
        "returkode": None,
        "begrunnelse": "",
        "sekunder": None,
    }

    try:
        a1, html = vei_a1(klient, timeouts, offline_html)
    except NettFeil as feil:
        rapport["veier"]["A1"] = {"navn": "temaside", "url": TEMASIDE, "dom": str(feil)}
        return _avslutt(rapport, 4, "temasiden svarte ikke etter begge forsøk", start,
                        soek=soekestreng(year))

    tolket = tolk_lenker(samle_pdf_lenker(html))
    a1["antall_pdf_lenker"] = len(tolket)
    a1["lenker"] = tolket
    rapport["veier"]["A1"] = a1
    rapport["veier"]["A3"] = vei_a3(tolket, kjente, year)

    if rapport["veier"]["A3"]["forventet_lenket"] and not rapport["veier"]["A3"]["gjenfunnet"]:
        return _avslutt(rapport, 5, "temasiden svarte, men ingen kjente utgaver ble gjenfunnet",
                        start, soek=soekestreng(year))

    utgaver = ["forslag", "vedtak"] if stage == "alle" else [stage]
    delresultater = {}
    for utgave in utgaver:
        delresultater[utgave] = _doem_utgave(rapport, tolket, klient, year, utgave, timeouts)
    rapport["delresultater"] = delresultater

    if stage != "alle":
        del_ = delresultater[stage]
        rapport["valgt"] = del_["valgt"]
        rapport["kandidater"] = del_["kandidater"]
        rapport["merknad"] = del_["merknad"]
        return _avslutt(rapport, del_["returkode"], del_["begrunnelse"], start,
                        soek=soekestreng(year) if del_["returkode"] in (2, 4, 5) else None)

    feilende = [d for d in delresultater.values() if d["returkode"] != 0]
    rapport["valgt"] = {u: d["valgt"] for u, d in delresultater.items()}
    rapport["merknad"] = "; ".join(d["merknad"] for d in delresultater.values() if d["merknad"]) or None
    if feilende:
        verst = feilende[0]
        return _avslutt(rapport, verst["returkode"], verst["begrunnelse"], start,
                        soek=soekestreng(year) if verst["returkode"] in (2, 4, 5) else None)
    return _avslutt(rapport, 0, "begge utgaver funnet entydig", start)


def _doem_utgave(rapport, tolket, klient, year, utgave, timeouts):
    """Dom for én utgave: kandidater fra A1, ellers A2 og A3."""
    kandidater = [t for t in tolket if t["aar"] == year and t["utgave"] == utgave]
    del_ = {"utgave": utgave, "kandidater": kandidater, "valgt": None,
            "merknad": None, "returkode": None, "begrunnelse": ""}

    if kandidater:
        valgt = velg_kandidat(kandidater)
        del_["valgt"] = {"url": valgt["url"], "lenketekst": valgt["lenketekst"],
                         "aar": valgt["aar"], "utgave": valgt["utgave"]}
        del_["returkode"] = 0
        if len(kandidater) > 1:
            del_["merknad"] = (f"{len(kandidater)} kandidater for {year} {utgave}; valgte "
                               f"{filnavn(valgt['url'])} "
                               + ("nyeste dato " + valgt["dato"] if valgt["dato"]
                                  else "sist på den kronologiske siden"))
            del_["begrunnelse"] = del_["merknad"]
        else:
            del_["begrunnelse"] = f"én kandidat for {year} {utgave} på temasiden"
        return del_

    a2 = vei_a2(klient, year, utgave, timeouts)
    rapport["veier"].setdefault("A2", {})[utgave] = a2
    if a2["treff"]:
        treff = a2["treff"][0]
        del_["valgt"] = {"url": treff["url"], "lenketekst": None, "aar": year, "utgave": utgave}
        del_["returkode"] = 7
        del_["begrunnelse"] = (f"filnavnproben fant PDF for {year} {utgave} uten lenke på "
                               f"temasiden: {treff['url']}")
        return del_

    maa_vurderes = rapport["veier"]["A3"]["maa_vurderes"]
    if maa_vurderes:
        del_["returkode"] = 3
        del_["begrunnelse"] = (f"ingen kandidat for {year} {utgave}, men {len(maa_vurderes)} "
                               "ukjent(e) lenke(r) med år ≥ året eller ukjent år må vurderes")
        return del_

    del_["returkode"] = 2
    del_["begrunnelse"] = f"temasiden lest, ingen kandidat for {year} {utgave}, og filnavnproben ga 404"
    return del_


def _avslutt(rapport, returkode, begrunnelse, start, soek=None):
    rapport["returkode"] = returkode
    rapport["begrunnelse"] = begrunnelse
    rapport["sekunder"] = round(time.perf_counter() - start, 3)
    if soek:
        rapport["soekestreng"] = soek
    return rapport


def les_kjente(known):
    if known is None:
        return []
    if isinstance(known, (list, tuple)):
        return list(known)
    with open(known, encoding="utf-8") as fil:
        data = json.load(fil)
    return data["utgaver"] if isinstance(data, dict) else data


# --- kommandolinje ---------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="Finn blått hefte på regjeringen.no")
    ap.add_argument("--year", type=int, required=True, help="budsjettår, ikke publiseringsår")
    ap.add_argument("--stage", choices=["forslag", "vedtak", "alle"], default="forslag")
    ap.add_argument("--known", help="sti til kjente-utgaver.json")
    ap.add_argument("--output", help="sti til rapport-JSON")
    ap.add_argument("--offline-html", help="les temasiden fra fil i stedet for nett")
    ap.add_argument("--timeout-get", type=float, default=STANDARD_TIMEOUTS["get"])
    ap.add_argument("--timeout-retry", type=float, default=STANDARD_TIMEOUTS["retry"])
    ap.add_argument("--timeout-head", type=float, default=STANDARD_TIMEOUTS["head"])
    args = ap.parse_args(argv)

    html = None
    if args.offline_html:
        with open(args.offline_html, encoding="utf-8") as fil:
            html = fil.read()

    rapport = finn(
        args.year, args.stage, args.known,
        timeouts={"get": args.timeout_get, "retry": args.timeout_retry, "head": args.timeout_head},
        offline_html=html,
    )
    tekst = json.dumps(rapport, ensure_ascii=False, indent=2)
    if args.output:
        import os
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fil:
            fil.write(tekst + "\n")
    print(tekst)
    return rapport["returkode"]


if __name__ == "__main__":
    sys.exit(main())
