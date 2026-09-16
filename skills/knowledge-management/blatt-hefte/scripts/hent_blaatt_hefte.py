#!/usr/bin/env python3
"""Hent blått hefte til disk med hash og manifest.

Filen lastes til <dir>/<budsjettår>/blaatt-hefte-<år>-<utgave>.pdf via en .part-fil
som slettes ved avbrudd. En fil med annen hash overskrives aldri; da skrives -v2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

VERSJON = "1.0"
BRUKERAGENT = "uit-blatt-hefte/1.0 (+skills/knowledge-management/blatt-hefte)"


class HentFeil(Exception):
    """Nedlastingen kom ikke i mål, eller svaret var ikke en PDF."""


class Nedlaster:
    """Tynt lag over urllib, slik at testene kan sette inn en falsk klient."""

    def aapne(self, url, connect_timeout, read_timeout):
        req = urllib.request.Request(url, headers={"User-Agent": BRUKERAGENT})
        gammel = socket.getdefaulttimeout()
        socket.setdefaulttimeout(connect_timeout)
        try:
            svar = urllib.request.urlopen(req, timeout=read_timeout)
        except urllib.error.HTTPError as feil:
            raise HentFeil(f"HTTP {feil.code} for {url}") from feil
        except Exception as feil:
            raise HentFeil(f"nettfeil for {url}: {feil}") from feil
        finally:
            socket.setdefaulttimeout(gammel)
        return {
            "status": svar.status,
            "content_type": svar.headers.get("Content-Type", ""),
            "content_length": _heltall(svar.headers.get("Content-Length")),
            "filnavn_paa_serveren": url.rstrip("/").rsplit("/", 1)[-1],
            "strom": svar,
        }


def _heltall(verdi):
    return int(verdi) if verdi and str(verdi).isdigit() else None


def sha256_fil(sti, blokk=1 << 20):
    hasher = hashlib.sha256()
    with open(sti, "rb") as fil:
        for del_ in iter(lambda: fil.read(blokk), b""):
            hasher.update(del_)
    return hasher.hexdigest()


def maalsti(dir_, year, stage, suffiks=""):
    return os.path.join(str(dir_), str(year), f"blaatt-hefte-{year}-{stage}{suffiks}.pdf")


# --- henting ---------------------------------------------------------------

def hent(url, dir, year, stage, known=None, connect_timeout=5, read_timeout=15, klient=None):
    """Last ned én utgave. Returnerer dict med sti, sha256, hoppet_over og advarsler."""
    start = time.perf_counter()
    klient = klient or Nedlaster()
    mappe = os.path.join(str(dir), str(year))
    os.makedirs(mappe, exist_ok=True)
    sti = maalsti(dir, year, stage)
    forventet = _forventet_hash(known, year, stage, url)

    resultat = {"url": url, "budsjettaar": year, "utgave": stage, "sti": sti,
                "hoppet_over": False, "advarsler": [], "sekunder": None}

    if forventet and os.path.exists(sti) and sha256_fil(sti) == forventet:
        resultat.update(sha256=forventet, content_length=os.path.getsize(sti), hoppet_over=True)
        resultat["sekunder"] = round(time.perf_counter() - start, 3)
        return resultat

    del_sti = sti + ".part"
    svar = klient.aapne(url, connect_timeout, read_timeout)
    try:
        with open(del_sti, "wb") as ut:
            strom = svar["strom"]
            for blokk in iter(lambda: strom.read(1 << 16), b""):
                ut.write(blokk)
    except BaseException:
        _fjern(del_sti)
        raise
    finally:
        lukk = getattr(svar.get("strom"), "close", None)
        if lukk:
            lukk()

    with open(del_sti, "rb") as fil:
        if fil.read(5) != b"%PDF-":
            _fjern(del_sti)
            raise HentFeil(f"svaret fra {url} starter ikke med %PDF-")

    hash_ = sha256_fil(del_sti)
    endelig = sti
    if os.path.exists(sti) and sha256_fil(sti) != hash_:
        endelig = maalsti(dir, year, stage, "-v2")
        resultat["advarsler"].append(
            f"{os.path.basename(sti)} finnes med annen hash; skrev {os.path.basename(endelig)}")
    os.replace(del_sti, endelig)

    resultat.update(sti=endelig, sha256=hash_, content_length=os.path.getsize(endelig),
                    content_length_header=svar.get("content_length"),
                    filnavn_paa_serveren=svar.get("filnavn_paa_serveren"))
    if forventet and forventet != hash_:
        resultat["advarsler"].append(f"hash avviker fra kjente-utgaver.json (ventet {forventet})")
    skriv_kilder(mappe, resultat)
    resultat["sekunder"] = round(time.perf_counter() - start, 3)
    return resultat


def _fjern(sti):
    try:
        os.remove(sti)
    except OSError:
        pass


def _forventet_hash(known, year, stage, url):
    for utgave in _les_kjente(known):
        if utgave.get("url") == url:
            return utgave.get("sha256")
    for utgave in _les_kjente(known):
        if utgave.get("budsjettaar") == year and utgave.get("utgave") == stage \
                and utgave.get("gjeldende", True):
            return utgave.get("sha256")
    return None


def _les_kjente(known):
    if known is None:
        return []
    if isinstance(known, (list, tuple)):
        return list(known)
    with open(known, encoding="utf-8") as fil:
        data = json.load(fil)
    return data["utgaver"] if isinstance(data, dict) else data


def skriv_kilder(mappe, resultat):
    """Ett manifest per mappe, nøklet på filnavn."""
    sti = os.path.join(mappe, "kilder.json")
    data = {}
    if os.path.exists(sti):
        with open(sti, encoding="utf-8") as fil:
            data = json.load(fil)
    data[os.path.basename(resultat["sti"])] = {
        "url": resultat["url"],
        "sha256": resultat["sha256"],
        "content_length": resultat["content_length"],
        "hentet_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "filnavn_paa_serveren": resultat.get("filnavn_paa_serveren"),
    }
    _skriv_json(sti, dict(sorted(data.items())))


def _skriv_json(sti, data):
    os.makedirs(os.path.dirname(sti) or ".", exist_ok=True)
    with open(sti, "w", encoding="utf-8") as fil:
        json.dump(data, fil, ensure_ascii=False, indent=2)
        fil.write("\n")


# --- verifisering og inventar ----------------------------------------------

def verifiser(known, dir_):
    """Alle utgaver i kjente-utgaver.json skal finnes lokalt med riktig hash."""
    mangler = []
    for utgave in _les_kjente(known):
        navn = utgave.get("lokalt_filnavn") or os.path.basename(
            maalsti(dir_, utgave["budsjettaar"], utgave["utgave"]))
        sti = os.path.join(str(dir_), str(utgave["budsjettaar"]), navn)
        if not os.path.exists(sti):
            mangler.append({"sti": sti, "grunn": "finnes ikke"})
        elif sha256_fil(sti) != utgave["sha256"]:
            mangler.append({"sti": sti, "grunn": "feil sha256"})
    return mangler


def inventar(mapper):
    """Hash alle blått hefte-PDF-er i de oppgitte mappene."""
    funn = []
    for mappe in mapper:
        for navn in sorted(os.listdir(mappe)):
            if not navn.lower().endswith(".pdf") or "blaatt-hefte" not in navn:
                continue
            sti = os.path.join(mappe, navn)
            funn.append({"sti": sti, "filnavn": navn, "mappe": os.path.basename(mappe.rstrip("/")),
                         "sha256": sha256_fil(sti), "content_length": os.path.getsize(sti)})
    return funn


# --- kommandolinje ---------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="Hent blått hefte med hash og manifest")
    ap.add_argument("--url")
    ap.add_argument("--from", dest="fra", help="finn-rapport i JSON")
    ap.add_argument("--stage", choices=["forslag", "vedtak"], default="forslag")
    ap.add_argument("--year", type=int)
    ap.add_argument("--dir", default=".")
    ap.add_argument("--verify", help="kjente-utgaver.json; sjekker lokale filer og avslutter")
    ap.add_argument("--inventory", nargs="+", help="mapper som skal hashes")
    ap.add_argument("--output", help="sti til JSON-utdata (inventar eller hentresultat)")
    ap.add_argument("--known", help="kjente-utgaver.json for hash-sjekk ved henting")
    ap.add_argument("--connect-timeout", type=float, default=5.0)
    ap.add_argument("--read-timeout", type=float, default=15.0)
    args = ap.parse_args(argv)

    if args.inventory:
        funn = inventar(args.inventory)
        tekst = json.dumps(funn, ensure_ascii=False, indent=2)
        if args.output:
            _skriv_json(args.output, funn)
        print(tekst)
        return 0

    if args.verify:
        mangler = verifiser(args.verify, args.dir)
        print(json.dumps({"mangler": mangler, "antall": len(mangler)}, ensure_ascii=False, indent=2))
        return 1 if mangler else 0

    url, year, stage = args.url, args.year, args.stage
    if args.fra:
        with open(args.fra, encoding="utf-8") as fil:
            rapport = json.load(fil)
        valgt = rapport.get("valgt") or {}
        if args.stage in valgt:
            valgt = valgt[args.stage]
        if not valgt:
            print("finn-rapporten har ingen valgt kandidat", file=sys.stderr)
            return 2
        url, year, stage = valgt["url"], valgt["aar"], valgt["utgave"]
    if not url:
        print("mangler --url eller --from", file=sys.stderr)
        return 2

    resultat = hent(url, args.dir, year, stage, known=args.known,
                    connect_timeout=args.connect_timeout, read_timeout=args.read_timeout)
    print(json.dumps(resultat, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
