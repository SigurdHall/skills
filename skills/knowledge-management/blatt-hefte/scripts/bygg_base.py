"""Bygg budsjettbasen for UiT: forslag, vedtatt og RNB per budsjettår, kap. 260 post 50.

    bygg_base.py --kilder <mappe med <år>/blaatt-hefte-<år>-<utgave>.pdf> --output references/budsjettbase.json
                 [--rnb references/rnb-tillegg.json]

Forslag og vedtatt leses fra heftene med les_blaatt_hefte.les. RNB-endringene kan
ikke leses fra blått hefte; de kommer fra rnb-tillegg.json (per budsjettår: beløp i
1 000 kroner, komponenter og kilde), som vedlikeholdes fra RNB-proposisjonen og
KDs supplerende tildelingsbrev. Basen skrives på nytt hver gang og eier ingen tall
selv: alt spores til et dokument med sha256.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER))
import les_blaatt_hefte  # noqa: E402

REFERANSER = HER.parent / "references"
STANDARD_UT = REFERANSER / "budsjettbase.json"
STANDARD_RNB = REFERANSER / "rnb-tillegg.json"


def punkt_fra_hefte(pdf: Path, kilde: dict | None) -> dict:
    """Ett tidspunkt (forslag eller vedtatt) for UiT fra ett hefte."""
    dok = les_blaatt_hefte.les(pdf, kilde=kilde)
    h = dok["hovedtabell"]
    uit = next(r for r in h["rader"] if r["kortkode_norm"] == "UIT")
    p = dok["prisjustering"]
    return {
        "ramme": uit["verdier"][h["sum_indeks"]],
        "utgangspunkt": uit["verdier"][0],
        "utgangspunkt_etikett": h["kolonner"][0],
        "prisjustering": uit["verdier"][p["kolonne_indeks"]] if p["kolonne_indeks"] is not None else None,
        "sats_prosent": p["sats_prosent"],
        "ren_sats": p["ren_sats"],
        "kilde": {"filnavn": dok["kilde"]["filnavn"], "sha256": dok["kilde"]["sha256"], "url": dok["kilde"]["url"],
                  "pdf_side": h["pdf_side"], "tittel": dok["kilde"]["tittel"]},
    }


def les_kilder_json(mappe: Path) -> dict:
    fil = mappe / "kilder.json"
    return json.loads(fil.read_text(encoding="utf-8")) if fil.exists() else {}


def bygg(kilder: Path, rnb_fil: Path | None) -> dict:
    rnb = json.loads(rnb_fil.read_text(encoding="utf-8")) if rnb_fil and rnb_fil.exists() else {}
    base: dict[str, dict] = {}
    for pdf in sorted(kilder.glob("*/blaatt-hefte-*-*.pdf")):
        m = re.match(r"blaatt-hefte-(\d{4})-(forslag|vedtak)(-[a-z0-9]+)?\.pdf$", pdf.name)
        if not m or m.group(3):  # dubletter («-ulenket», «-v2») holdes utenfor basen
            continue
        aar, utgave = m.group(1), {"forslag": "forslag", "vedtak": "vedtatt"}[m.group(2)]
        kildeoppslag = les_kilder_json(pdf.parent).get(pdf.name)
        base.setdefault(aar, {"forslag": None, "vedtatt": None, "rnb": None})[utgave] = punkt_fra_hefte(pdf, kildeoppslag)
    for aar, post in rnb.get("aar", {}).items():
        base.setdefault(aar, {"forslag": None, "vedtatt": None, "rnb": None})["rnb"] = post
    for aar, post in base.items():
        v, r = post["vedtatt"], post["rnb"]
        post["vedtatt_etter_rnb"] = (v["ramme"] + r["endring"]) if v and r and r.get("endring") is not None else None
        brev = (r or {}).get("tildelingsbrev")
        if v and brev and brev.get("ramme") != v["ramme"]:
            raise SystemExit(f"{aar}: tildelingsbrevets ramme {brev['ramme']} avviker fra blått hefte etter vedtak {v['ramme']}")
    if not base:
        raise SystemExit(f"ingen hefter funnet under {kilder}; basen er ikke skrevet")
    return {
        "beskrivelse": "UiT, kap. 260 post 50, 1 000 kroner. forslag og vedtatt er lest fra blått hefte (utgave forslag / etter vedtak); rnb er endringen i revidert nasjonalbudsjett samme budsjettår, fra rnb-tillegg.json.",
        "bygget_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rnb_kilde": str(rnb_fil) if rnb_fil else None,
        "aar": dict(sorted(base.items())),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--kilder", type=Path, default=Path("/home/sihal7953/repos/uit-statsbudsjett/analyse/kilder/blaatt-hefte"))
    p.add_argument("--rnb", type=Path, default=STANDARD_RNB)
    p.add_argument("--output", type=Path, default=STANDARD_UT)
    a = p.parse_args(argv)
    base = bygg(a.kilder, a.rnb)
    if a.output.exists():
        gammel = json.loads(a.output.read_text(encoding="utf-8")).get("aar", {})
        tapt = [aar for aar, post in gammel.items()
                if aar not in base["aar"] or any(post.get(k) and not base["aar"][aar].get(k) for k in ("forslag", "vedtatt", "rnb"))]
        if tapt:
            raise SystemExit(f"basen ville mistet data for {tapt}; ikke skrevet")
    a.output.write_text(json.dumps(base, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for aar, post in base["aar"].items():
        f = post["forslag"]["ramme"] if post["forslag"] else "-"
        v = post["vedtatt"]["ramme"] if post["vedtatt"] else "-"
        r = post["rnb"]["endring"] if post["rnb"] else "-"
        print(f"{aar}: forslag {f}  vedtatt {v}  rnb {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
