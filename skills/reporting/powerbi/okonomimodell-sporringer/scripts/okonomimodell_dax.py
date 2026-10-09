"""Kjør DAX-blokker mot okonomimodell_ppu (standard) eller den levende Okonomimodell på F8 (bare røyktest).

Blokkene i --fil starter med en linje "-- <KODE> <beskrivelse>". Mot F8 slippes bare spørringer som er kjørt på PPU
de siste 7 dagene med klasse S, og høyst F8_PER_DAG kall per dag, gjennom samme kø og pause som fabric-cu-glatting.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

if os.name == "nt":
    import msvcrt
else:
    import fcntl

SKILL = pathlib.Path(__file__).resolve().parent.parent
KONFIG = SKILL / "references" / "private" / "okonomimodell.json"
AZ = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" if os.name == "nt" else "az"

KO = pathlib.Path.home() / ".fabric_ko"
PPU_LOGG = KO / "okonomimodell_ppu_logg.jsonl"
F8_PER_DAG = 5
F8_PAUSE = 20.0
GYLDIG_PPU_DAGER = 7
S_SEKUNDER = 1.0
S_RADER = 500


def les_blokker(tekst: str) -> list[tuple[str, str]]:
    """Del filen i (kode, dax). Tekst før første "-- "-blokk ignoreres."""
    blokker = []
    for del_ in ("\n" + tekst).split("\n-- ")[1:]:
        hode, _, dax = del_.partition("\n")
        if dax.strip():
            blokker.append((hode.split()[0], dax.strip()))
    return blokker


def noekkel(dax: str) -> str:
    return hashlib.sha256(" ".join(dax.split()).encode("utf-8")).hexdigest()[:24]


def klasse(sekunder: float, rader: int | None, feil) -> str:
    if feil:
        return "X"
    if sekunder < S_SEKUNDER and rader is not None and rader <= S_RADER:
        return "S"
    if sekunder < 10:
        return "M"
    return "L"


def godkjent_for_f8(dax: str, logg: list[dict], naa: float) -> bool:
    """Spørringen må ha gått som klasse S på PPU de siste GYLDIG_PPU_DAGER dagene."""
    n = noekkel(dax)
    grense = naa - GYLDIG_PPU_DAGER * 86400
    return any(r["noekkel"] == n and r["klasse"] == "S" and r["tid"] >= grense for r in logg)


def les_logg() -> list[dict]:
    if not PPU_LOGG.exists():
        return []
    return [json.loads(linje) for linje in PPU_LOGG.read_text(encoding="utf-8").splitlines() if linje.strip()]


def f8_teller_sti() -> pathlib.Path:
    return KO / f"okonomimodell_f8_{time.strftime('%Y-%m-%d')}.json"


def hent_token() -> str:
    return subprocess.run(
        [AZ, "account", "get-access-token", "--resource", "https://analysis.windows.net/powerbi/api",
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, check=True).stdout.strip()


def kjor_dax(token: str, ws: str, ds: str, dax: str) -> dict:
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{ws}/datasets/{ds}/executeQueries"
    kropp = json.dumps({"queries": [{"query": dax}], "serializerSettings": {"includeNulls": True}}).encode()
    foresporsel = urllib.request.Request(url, data=kropp, method="POST", headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(foresporsel, timeout=900) as svar:
            data = json.load(svar)
        resultat = data["results"][0]
        rader = resultat["tables"][0]["rows"] if resultat.get("tables") else []
        feil = resultat.get("error")
    except urllib.error.HTTPError as e:
        rader, feil = None, e.read().decode("utf-8", "replace")[:800]
    sekunder = round(time.perf_counter() - start, 2)
    return {"sekunder": sekunder, "rader": None if rader is None else len(rader),
            "forste": (rader or [])[:3], "alle": rader, "feil": feil}


# Samme lås og pause som fabric_ko.py i fabric-cu-glatting, slik at F8-kall står i den felles køen.
OPPTATT = {errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK, getattr(errno, "EDEADLOCK", errno.EACCES)}


def _laas(fd, ta):
    if os.name == "nt":
        msvcrt.locking(fd, msvcrt.LK_NBLCK if ta else msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(fd, (fcntl.LOCK_EX | fcntl.LOCK_NB) if ta else fcntl.LOCK_UN)


def i_f8_ko(kall):
    KO.mkdir(exist_ok=True)
    siste = KO / "siste"
    fd = os.open(KO / "koe.laas", os.O_RDWR | os.O_CREAT)
    try:
        while True:
            os.lseek(fd, 0, os.SEEK_SET)
            try:
                _laas(fd, True)
                break
            except OSError as e:
                if e.errno not in OPPTATT:
                    raise
            time.sleep(2)
        try:
            forrige = siste.stat().st_mtime if siste.exists() else 0
            time.sleep(max(0, F8_PAUSE - (time.time() - forrige)))
            return kall()
        finally:
            siste.touch()
            os.lseek(fd, 0, os.SEEK_SET)
            _laas(fd, False)
    finally:
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fil", required=True, type=pathlib.Path)
    parser.add_argument("--mal", choices=["ppu", "f8"], default="ppu")
    parser.add_argument("--ut", type=pathlib.Path, default=pathlib.Path("ut") / "okonomimodell")
    parser.add_argument("koder", nargs="*")
    args = parser.parse_args()

    if not KONFIG.exists():
        print(f"Mangler {KONFIG}. Spør brukeren om arbeidsområde- og modell-id.", file=sys.stderr)
        return 2
    modell = json.loads(KONFIG.read_text(encoding="utf-8"))[args.mal]

    blokker = [(k, d) for k, d in les_blokker(args.fil.read_text(encoding="utf-8")) if not args.koder or k in args.koder]

    if args.mal == "f8":
        logg = les_logg()
        avvist = [k for k, d in blokker if not godkjent_for_f8(d, logg, time.time())]
        if avvist:
            print(f"Avvist mot F8, ikke kjørt som klasse S på PPU siste {GYLDIG_PPU_DAGER} dager: {avvist}", file=sys.stderr)
            return 3
        teller = f8_teller_sti()
        brukt = json.loads(teller.read_text())["kall"] if teller.exists() else 0
        if brukt + len(blokker) > F8_PER_DAG:
            print(f"F8-budsjett: {brukt} av {F8_PER_DAG} brukt i dag, {len(blokker)} ønsket.", file=sys.stderr)
            return 4

    token = hent_token()
    args.ut.mkdir(parents=True, exist_ok=True)
    for kode, dax in blokker:
        if args.mal == "f8":
            svar = i_f8_ko(lambda: kjor_dax(token, modell["workspace"], modell["dataset"], dax))
            KO.mkdir(exist_ok=True)
            teller = f8_teller_sti()
            brukt = json.loads(teller.read_text())["kall"] if teller.exists() else 0
            teller.write_text(json.dumps({"kall": brukt + 1}))
        else:
            svar = kjor_dax(token, modell["workspace"], modell["dataset"], dax)

        k = klasse(svar["sekunder"], svar["rader"], svar["feil"])
        if args.mal == "ppu":
            KO.mkdir(exist_ok=True)
            with PPU_LOGG.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"noekkel": noekkel(dax), "kode": kode, "klasse": k,
                                    "sekunder": svar["sekunder"], "tid": time.time()}) + "\n")
        hint = ""
        if svar["feil"] and "Resource Governance" in str(svar["feil"]):
            hint = "Minnetaket: del opp etter dim_periode[periode_aar], ellers SQL-endepunktet."
        stempel = time.strftime("%Y%m%d-%H%M%S")
        (args.ut / f"{stempel}-{args.mal}-{kode}.json").write_text(
            json.dumps({"kode": kode, "mal": args.mal, "dax": dax, **svar, "klasse": k}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        print(json.dumps({"kode": kode, "mal": args.mal, "klasse": k, "sekunder": svar["sekunder"],
                          "rader": svar["rader"], "forste": svar["forste"], "feil": svar["feil"], "hint": hint},
                         ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
