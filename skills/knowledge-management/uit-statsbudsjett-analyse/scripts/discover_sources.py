"""Finn og kontroller årets offentlige kilder: blått hefte, fagproposisjoner og UiTs foreløpige fordeling.

check  : slå opp kildene på nett og skriv en statusrapport (JSON). Returkode 0 = alt funnet,
         2 = ikke publisert (blått hefte eller KD mangler), 3 = delvis.
write  : lag kilder-input.json for fetch_sources.py fra en statusrapport.

Bare standardbiblioteket brukes, slik at skriptet kjører med enhver Python 3.9+.
Nettkall går gjennom én funksjon (fetch) som testene bytter ut.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

REGJERINGEN = "https://www.regjeringen.no"
KD_BLAATT_HEFTE_PAGE = (
    REGJERINGEN
    + "/no/tema/utdanning/hoyere-utdanning/orientering-om-forslag-til-statsbudsjett-for-universiteter-og-hoyskoler/id619675/"
)
BLAATT_HEFTE_FOLDER = REGJERINGEN + "/contentassets/31af8e2c3a224ac2829e48cc91d89083/"
STATSBUDSJETT_INDEX = REGJERINGEN + "/no/statsbudsjett/id1437/"
STORTINGET_YEAR = "https://www.stortinget.no/no/Saker-og-publikasjoner/Statsbudsjettet/statsbudsjettet-{year}/"
SEARCH = (
    REGJERINGEN
    + "/no/dokumenter/id2000006/?documenttype=dokumenter/proposisjoner&term=%22Prop.+1+{kind}+({prev}%E2%80%93{year})%22&page={page}"
)
ELEMENTS = "https://prod02.elementscloud.no/publikum/"
ELEMENTS_TENANT = "970422528_PROD-970422528"
UIT_BOARD = 3
USER_AGENT = "uit-statsbudsjett-analyse/1.0 (kildeoppdagelse; kontakt via UiT)"

# Nøkkelord i DC.Creator -> del-id i arbeidsdelingen. Departementsnavn endres; utvid listen ved omorganisering.
DEPARTMENT_PARTS = [
    ("kunnskapsdepartementet", "kd"),
    ("helse- og omsorgsdepartementet", "hod"),
    ("klima- og miljødepartementet", "kld"),
    ("nærings- og fiskeridepartementet", "nfd"),
    ("arbeids- og inkluderingsdepartementet", "aid"),
    ("arbeids- og sosialdepartementet", "aid"),
    ("kultur- og likestillingsdepartementet", "kud"),
    ("kulturdepartementet", "kud"),
    ("kommunal- og distriktsdepartementet", "kdd"),
    ("kommunal- og moderniseringsdepartementet", "kdd"),
    ("justis- og beredskapsdepartementet", "jd"),
    ("utenriksdepartementet", "ud"),
    ("energidepartementet", "oed"),
    ("olje- og energidepartementet", "oed"),
]
REQUIRED_PARTS = ["kd", "hod", "kld", "nfd", "aid", "kud", "kdd", "jd", "ud", "oed", "fin"]


class Fetcher:
    """Tynt lag over urllib slik at testene kan bytte ut nettet."""

    def __init__(self, timeout: int = 40):
        self.timeout = timeout

    def get(self, url: str, headers: dict | None = None) -> tuple[int, str, bytes]:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, response.headers.get("Content-Type", ""), response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.headers.get("Content-Type", "") if error.headers else "", b""
        except (urllib.error.URLError, TimeoutError) as error:
            return 0, str(error), b""

    def head(self, url: str, headers: dict | None = None) -> tuple[int, str, int]:
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT, **(headers or {})})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                length = int(response.headers.get("Content-Length") or 0)
                return response.status, response.headers.get("Content-Type", ""), length
        except urllib.error.HTTPError as error:
            return error.code, "", 0
        except (urllib.error.URLError, TimeoutError):
            return 0, "", 0


def text_of(fetcher: Fetcher, url: str, headers: dict | None = None) -> str:
    status, _, body = fetcher.get(url, headers)
    return body.decode("utf-8", errors="replace") if status == 200 else ""


def is_pdf(status: int, content_type: str) -> bool:
    return status == 200 and "pdf" in content_type.lower()


# --- blått hefte -------------------------------------------------------------------

def find_blaatt_hefte(year: int, fetcher: Fetcher, stage: str = "forslag") -> dict:
    """Prøv det stabile filnavnet først, deretter KDs kronologiske side."""
    wanted = "forslag" if stage == "forslag" else "vedtak"
    candidates = []
    if wanted == "forslag":
        candidates = [
            BLAATT_HEFTE_FOLDER + f"orientering-om-forslag-til-statsbudsjettet-{year}-for-universitet-og-hogskular.pdf",
            BLAATT_HEFTE_FOLDER + f"orientering-om-forslag-til-statsbudsjettet-{year}-universitet-og-hogskular.pdf",
        ]
    for url in candidates:
        status, content_type, length = fetcher.head(url)
        if is_pdf(status, content_type):
            return {"status": "funnet", "url": url, "bytes": length, "via": "filnavnmønster"}
    page = text_of(fetcher, KD_BLAATT_HEFTE_PAGE)
    for href in re.findall(r'href="(/contentassets/[^"]*\.pdf)"', page):
        name = href.lower()
        if str(year) not in name:
            continue
        if wanted == "forslag" and "forslag" not in name:
            continue
        if wanted == "vedtak" and "vedtak" not in name:
            continue
        url = REGJERINGEN + href
        status, content_type, length = fetcher.head(url)
        if is_pdf(status, content_type):
            return {"status": "funnet", "url": url, "bytes": length, "via": "KDs kronologiske side"}
    return {"status": "ikke publisert", "url": None, "checked": candidates + [KD_BLAATT_HEFTE_PAGE]}


# --- fagproposisjoner --------------------------------------------------------------

def find_year_page(year: int, fetcher: Fetcher) -> str | None:
    pattern = re.compile(rf"/no/statsbudsjett/{year}/id\d+/")
    match = pattern.search(text_of(fetcher, STATSBUDSJETT_INDEX))
    if match:
        return REGJERINGEN + match.group(0)
    match = re.search(rf"regjeringen\.no(/no/statsbudsjett/{year}/id\d+/)", text_of(fetcher, STORTINGET_YEAR.format(year=year)))
    return REGJERINGEN + match.group(1) if match else None


def find_document_pages(year: int, fetcher: Fetcher) -> dict[str, str]:
    """Dokumentside-URL -> lenketekst, fra årets dokumentside og fra dokumentsøket."""
    prev = year - 1
    pages: dict[str, str] = {}
    year_page = find_year_page(year, fetcher)
    if year_page:
        page = text_of(fetcher, year_page)
        docs_link = re.search(rf"/no/statsbudsjett/{year}/dokumenter-og-pressemeldinger/id\d+/", page)
        if docs_link:
            docs = text_of(fetcher, REGJERINGEN + docs_link.group(0))
            for href, text in re.findall(rf'<a[^>]*href="(/no/dokumenter/prop\.-1-l?s-{prev}{year}/id\d+/)"[^>]*>([^<]*)</a>', docs):
                pages.setdefault(REGJERINGEN + href, unescape(text).strip())
    for kind in ("S", "LS"):
        for number in (1, 2):
            listing = text_of(fetcher, SEARCH.format(kind=kind, prev=prev, year=year, page=number))
            found = set(re.findall(rf'/no/dokumenter/prop\.-1-{kind.lower()}-{prev}{year}/id\d+/', listing))
            for href in found:
                pages.setdefault(REGJERINGEN + href, "")
            if not found:
                break
    return pages


def resolve_document(url: str, year: int, fetcher: Fetcher) -> dict:
    page = text_of(fetcher, url)
    creator = re.search(r'name="DC\.Creator" content="([^"]*)"', page)
    title = re.search(r'name="DC\.Title" content="([^"]*)"', page)
    pdfs = re.findall(rf'href="(/contentassets/[^"]*pdfs/prp{year - 1}{year}0001[^"]*\.pdf)"', page)
    pdf = REGJERINGEN + pdfs[0] if pdfs else None
    is_ls = "prop.-1-ls-" in url
    return {
        "doc_url": url,
        "department": unescape(creator.group(1)) if creator else "",
        "title": unescape(title.group(1)) if title else "",
        "pdf_url": pdf,
        "kind": "LS" if is_ls else "S",
        "status": "funnet" if pdf else "ikke identifisert",
    }


def part_for(department: str, kind: str) -> str | None:
    name = department.lower()
    if kind == "LS":
        return "fin" if "finans" in name else None
    for keyword, part in DEPARTMENT_PARTS:
        if keyword in name:
            return part
    return None


def find_departments(year: int, fetcher: Fetcher) -> list[dict]:
    documents = []
    for url in sorted(find_document_pages(year, fetcher)):
        document = resolve_document(url, year, fetcher)
        document["part"] = part_for(document["department"], document["kind"])
        documents.append(document)
    return documents


# --- UiTs foreløpige fordeling -----------------------------------------------------

def elements_json(fetcher: Fetcher, path: str):
    status, _, body = fetcher.get(ELEMENTS + "api/" + path, {"Tenant": ELEMENTS_TENANT, "Accept": "application/json"})
    if status != 200 or not body.strip().startswith((b"[", b"{")):
        return None
    return json.loads(body.decode("utf-8"))


def find_uit_allocation(year: int, fetcher: Fetcher, board: int = UIT_BOARD) -> dict:
    """Styresaken «Foreløpig fordeling av budsjett for <år>» ligger normalt i junimøtet året før."""
    meetings = elements_json(fetcher, f"PredefinedQuery/DmbMeetings?year={year - 1}&dmbName={board}") or []
    wanted = re.compile(rf"forel[øo]pig\s+fordeling.*{year}", re.IGNORECASE)
    for meeting in sorted(meetings, key=lambda m: m.get("MO_START", "")):
        handlings = elements_json(fetcher, f"DmbHandlings/GetByMeetingId/{meeting['MO_ID']}") or []
        for handling in handlings:
            if not wanted.search(handling.get("Title") or ""):
                continue
            detail = elements_json(fetcher, f"DmbHandlings/{handling['Id']}") or handling
            entry = detail.get("RegistryEntry") or {}
            database = detail.get("Database") or meeting.get("Database")
            documents = []
            for link in entry.get("Documents") or []:
                description = link.get("DocumentDescription") or {}
                if not description.get("IsPublished"):
                    continue
                documents.append({
                    "id": description["Id"],
                    "title": description.get("DocumentTitle", ""),
                    "main": bool(link.get("IsMainDocument")),
                    "url": f"{ELEMENTS}Documents/ShowDocument/{database}/{entry.get('Id')}/{description['Id']}",
                })
            case = detail.get("Case") or {}
            return {
                "status": "funnet" if documents else "ikke identifisert",
                "meeting_date": meeting.get("MO_START", "")[:10],
                "meeting_id": meeting.get("MO_ID"),
                "handling_id": detail.get("Id"),
                "case_title": detail.get("Title"),
                "board_case": f"S {detail.get('SequenceNumber')}/{str(detail.get('Year', ''))[-2:]}" if detail.get("SequenceNumber") else None,
                "archive_case": case.get("CaseNumber"),
                "documents": documents,
                "protocol_url": f"{ELEMENTS}Documents/ShowDmbHandlingDocument/{database}/{detail.get('Id')}/Protokoll",
                "portal": f"{ELEMENTS}{ELEMENTS_TENANT}/DmbBoard/{board}",
                "note": "API-kallene krever HTTP-headeren Tenant; selve PDF-nedlastingene gjør det ikke.",
            }
    return {"status": "ikke identifisert", "meetings_checked": [m.get("MO_START", "")[:10] for m in meetings], "portal": f"{ELEMENTS}{ELEMENTS_TENANT}/DmbBoard/{board}"}


# --- samlet kontroll ------------------------------------------------------------------

def check(year: int, stage: str, fetcher: Fetcher) -> dict:
    blaatt = find_blaatt_hefte(year, fetcher, stage)
    departments = find_departments(year, fetcher) if stage == "forslag" else []
    found_parts = {d["part"] for d in departments if d["part"] and d["status"] == "funnet"}
    missing = [p for p in REQUIRED_PARTS if p not in found_parts]
    uit = find_uit_allocation(year, fetcher)
    if blaatt["status"] != "funnet" or "kd" not in found_parts:
        verdict = "not_published"
    elif missing or uit["status"] != "funnet":
        verdict = "partial"
    else:
        verdict = "published"
    return {
        "year": year,
        "stage": stage,
        "checked_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "verdict": verdict,
        "blaatt_hefte": blaatt,
        "departments": departments,
        "missing_parts": missing,
        "unmapped_departments": [d["department"] for d in departments if not d["part"] and d["status"] == "funnet"],
        "uit_forelopig_fordeling": uit,
    }


def write_sources_input(report: dict, stage_text: str) -> tuple[list[dict], list[dict]]:
    """Returner (regjeringskilder, UiT-kilder), begge i fetch_sources.py-format. UiT-kildene hører til en egen mappe."""
    year = report["year"]
    sources = []
    if report["blaatt_hefte"].get("url"):
        sources.append({
            "id": f"blaatt-hefte-forslag-{year}",
            "url": report["blaatt_hefte"]["url"],
            "budget_year": year,
            "stage": stage_text,
            "title": f"Orientering om forslag til statsbudsjettet {year} for universitet og høgskular",
        })
    for document in report["departments"]:
        if not document.get("pdf_url") or not document.get("part"):
            continue
        prefix = "fin-skatt" if document["kind"] == "LS" else document["part"]
        label = "Prop. 1 LS" if document["kind"] == "LS" else "Prop. 1 S"
        sources.append({
            "id": f"{prefix}-prop-{year}",
            "url": document["pdf_url"],
            "budget_year": year,
            "stage": stage_text,
            "title": f"{document['department']} {label} ({year - 1}–{year})",
        })
    uit = report.get("uit_forelopig_fordeling") or {}
    uit_sources = [
        {
            "id": f"uit-forelopig-{year}-{'framlegg' if d['main'] else 'vedlegg-' + str(d['id'])}",
            "url": d["url"],
            "budget_year": year,
            "stage": "UiTs foreløpige fordeling",
            "title": d["title"],
        }
        for d in uit.get("documents", [])
    ]
    return sources, uit_sources


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check", help="slå opp kildene og skriv statusrapport")
    check_parser.add_argument("--year", type=int, required=True)
    check_parser.add_argument("--stage", default="forslag", choices=["forslag", "saldert"])
    check_parser.add_argument("--output", type=Path)
    write_parser = sub.add_parser("write", help="lag kilder-input.json fra statusrapport")
    write_parser.add_argument("--from", dest="report", type=Path, required=True)
    write_parser.add_argument("--output", type=Path, required=True)
    write_parser.add_argument("--uit-output", type=Path)
    write_parser.add_argument("--stage-text", default="regjeringens opprinnelige forslag")
    args = parser.parse_args(argv)

    if args.command == "check":
        report = check(args.year, args.stage, Fetcher())
        content = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + "\n", encoding="utf-8")
        print(content)
        return {"published": 0, "not_published": 2, "partial": 3}[report["verdict"]]

    report = json.loads(args.report.read_text(encoding="utf-8"))
    sources, uit_sources = write_sources_input(report, args.stage_text)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.uit_output:
        args.uit_output.parent.mkdir(parents=True, exist_ok=True)
        args.uit_output.write_text(json.dumps(uit_sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(sources)} regjeringskilder skrevet til {args.output}; {len(uit_sources)} UiT-kilder")
    return 0


if __name__ == "__main__":
    sys.exit(main())
