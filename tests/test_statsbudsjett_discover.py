import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/knowledge-management/uit-statsbudsjett-analyse/scripts/discover_sources.py"
spec = importlib.util.spec_from_file_location("statsbudsjett_discover", SCRIPT)
discover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discover)

R = discover.REGJERINGEN
EL = discover.ELEMENTS


class FakeFetcher:
    """Svarer fra et oppslag: url -> (status, content_type, body)."""

    def __init__(self, pages, pdfs=()):
        self.pages = pages
        self.pdfs = set(pdfs)
        self.calls = []

    def get(self, url, headers=None):
        self.calls.append(("GET", url, headers or {}))
        if url in self.pages:
            body = self.pages[url]
            body = json.dumps(body).encode() if isinstance(body, (list, dict)) else body.encode("utf-8")
            return 200, "text/html", body
        return 404, "text/html", b""

    def head(self, url, headers=None):
        self.calls.append(("HEAD", url, headers or {}))
        if url in self.pdfs:
            return 200, "application/pdf", 1000
        return 404, "text/html", 0


def doc_page(department, code, year, kind="s"):
    return (
        f'<meta name="DC.Title" content="Prop. 1 {kind.upper()} ({year - 1}–{year}) - For budsjettåret {year} under {department}">'
        f'<meta name="DC.Creator" content="{department}">'
        f'<a href="/contentassets/abc{code}/nn-no/pdfs/prp{year - 1}{year}0001{code}dddpdfs.pdf">PDF</a>'
    )


def regjeringen_world(year=2025, departments=None, with_year_page=True):
    prev = year - 1
    departments = departments or [
        ("Kunnskapsdepartementet", "_kd", 1), ("Helse- og omsorgsdepartementet", "hod", 2), ("Klima- og miljødepartementet", "kld", 3),
        ("Nærings- og fiskeridepartementet", "nfd", 4), ("Arbeids- og inkluderingsdepartementet", "aid", 5), ("Kultur- og likestillingsdepartementet", "kud", 6),
        ("Kommunal- og distriktsdepartementet", "kdd", 7), ("Justis- og beredskapsdepartementet", "_jd", 8), ("Utenriksdepartementet", "_ud", 9),
        ("Energidepartementet", "_ed", 10), ("Barne- og familiedepartementet", "bfd", 11),
    ]
    pages = {}
    links = []
    for name, code, n in departments:
        url = f"{R}/no/dokumenter/prop.-1-s-{prev}{year}/id{n}/"
        pages[url] = doc_page(name, code, year)
        links.append(f'<a href="/no/dokumenter/prop.-1-s-{prev}{year}/id{n}/">{name} sitt budsjettforslag</a>')
    ls_url = f"{R}/no/dokumenter/prop.-1-ls-{prev}{year}/id99/"
    pages[ls_url] = doc_page("Finansdepartementet", "ls0", year, kind="ls")
    links.append(f'<a href="/no/dokumenter/prop.-1-ls-{prev}{year}/id99/">Skatter og avgifter {year}</a>')
    if with_year_page:
        pages[discover.STATSBUDSJETT_INDEX] = f'<a href="/no/statsbudsjett/{year}/id500/">Statsbudsjettet {year}</a>'
        pages[f"{R}/no/statsbudsjett/{year}/id500/"] = f'<a href="/no/statsbudsjett/{year}/dokumenter-og-pressemeldinger/id501/">Dokumenter</a>'
        pages[f"{R}/no/statsbudsjett/{year}/dokumenter-og-pressemeldinger/id501/"] = "\n".join(links)
    return pages


def elements_world(year=2025):
    prev = year - 1
    return {
        f"{EL}api/PredefinedQuery/DmbMeetings?year={prev}&dmbName=3": [
            {"MO_ID": 74, "MO_START": f"{prev}-05-23T12:00:00", "Database": "db1"},
            {"MO_ID": 75, "MO_START": f"{prev}-06-20T09:00:00", "Database": "db1"},
        ],
        f"{EL}api/DmbHandlings/GetByMeetingId/74": [{"Id": 190, "Title": "Årsrapport"}],
        f"{EL}api/DmbHandlings/GetByMeetingId/75": [
            {"Id": 206, "Title": "Orientering"},
            {"Id": 207, "Title": f"Foreløpig fordeling av budsjett for {year}"},
        ],
        f"{EL}api/DmbHandlings/207": {
            "Id": 207, "Title": f"Foreløpig fordeling av budsjett for {year}", "SequenceNumber": 18, "Year": prev, "Database": "db1",
            "Case": {"CaseNumber": f"{prev}/8285"},
            "RegistryEntry": {"Id": 2137, "Documents": [
                {"IsMainDocument": True, "DocumentDescription": {"Id": 4197, "DocumentTitle": "Foreløpig fordeling av budsjett for 2025", "IsPublished": True}},
                {"IsMainDocument": False, "DocumentDescription": {"Id": 5227, "DocumentTitle": "Vedlegg 1", "IsPublished": True}},
                {"IsMainDocument": False, "DocumentDescription": {"Id": 5228, "DocumentTitle": "Unntatt", "IsPublished": False}},
            ]},
        },
    }


def blaatt_url(year, with_for=True):
    middle = "-for-universitet" if with_for else "-universitet"
    return discover.BLAATT_HEFTE_FOLDER + f"orientering-om-forslag-til-statsbudsjettet-{year}{middle}-og-hogskular.pdf"


def test_blaatt_hefte_pattern_then_page_fallback():
    fetcher = FakeFetcher({}, pdfs=[blaatt_url(2025)])
    assert discover.find_blaatt_hefte(2025, fetcher)["via"] == "filnavnmønster"

    odd = discover.BLAATT_HEFTE_FOLDER + "2026.09.30-forslag-til-orientering-2027-samlefil.pdf"
    vedtak = discover.BLAATT_HEFTE_FOLDER + "v3.-orientering-om-statsbudsjettet-2027-for-universitet-og-hogskular.pdf"
    page = (
        f'<a href="{odd.replace(R, "")}">Orientering om forslag til statsbudsjettet 2027 for universitet og høgskular</a>'
        f'<a href="{vedtak.replace(R, "")}">Orientering om statsbudsjettet 2027 for universitet og høgskular etter vedtak i Stortinget 17. desember 2026</a>'
    )
    fetcher = FakeFetcher({discover.KD_BLAATT_HEFTE_PAGE: page}, pdfs=[odd, vedtak])
    result = discover.find_blaatt_hefte(2027, fetcher)
    assert result["status"] == "funnet" and result["url"] == odd and result["via"] == "KDs kronologiske side"
    # etter vedtak: filnavnet mangler «vedtak», lenketeksten avgjør
    result = discover.find_blaatt_hefte(2027, fetcher, stage="saldert")
    assert result["status"] == "funnet" and result["url"] == vedtak and result["stage"] == "vedtak"

    assert discover.find_blaatt_hefte(2027, FakeFetcher({}))["status"] == "ikke publisert"


def test_check_saldert_stage_only_needs_vedtak_edition_and_next_year_uit_case():
    vedtak = discover.BLAATT_HEFTE_FOLDER + "orientering-om-statsbudsjettet-2024-for-universitet-og-hogskular.pdf"
    page = f'<a href="{vedtak.replace(R, "")}">Orientering om statsbudsjettet 2024 for universitet og høgskular etter vedtak i Stortinget 18. desember 2023</a>'
    fetcher = FakeFetcher({discover.KD_BLAATT_HEFTE_PAGE: page, **elements_world(2025)}, pdfs=[vedtak])
    report = discover.check(2024, "saldert", fetcher)
    assert report["verdict"] == "published" and report["departments"] == []
    assert report["uit_forelopig_fordeling_neste_aar"]["board_case"] == "S 18/24"
    sources, uit_sources = discover.write_sources_input(report, "x")
    assert sources[0]["id"] == "blaatt-hefte-vedtatt-2024" and "vedtak" in sources[0]["stage"]
    assert uit_sources[0]["id"] == "uit-forelopig-2025-framlegg" and uit_sources[0]["budget_year"] == 2025


def test_year_page_from_index_or_stortinget():
    fetcher = FakeFetcher({discover.STATSBUDSJETT_INDEX: '<a href="/no/statsbudsjett/2027/id777/">x</a>'})
    assert discover.find_year_page(2027, fetcher) == f"{R}/no/statsbudsjett/2027/id777/"
    fetcher = FakeFetcher({discover.STORTINGET_YEAR.format(year=2025): 'href="https://www.regjeringen.no/no/statsbudsjett/2025/id3052404/"'})
    assert discover.find_year_page(2025, fetcher) == f"{R}/no/statsbudsjett/2025/id3052404/"
    assert discover.find_year_page(2030, FakeFetcher({})) is None


def test_departments_are_mapped_to_parts_and_unmapped_reported():
    documents = discover.find_departments(2025, FakeFetcher(regjeringen_world()))
    by_part = {d["part"]: d for d in documents if d["part"]}
    assert set(by_part) == set(discover.REQUIRED_PARTS)
    assert by_part["oed"]["department"] == "Energidepartementet"
    assert by_part["fin"]["kind"] == "LS"
    assert by_part["kd"]["pdf_url"].endswith("prp202420250001_kddddpdfs.pdf")
    unmapped = [d for d in documents if not d["part"]]
    assert [d["department"] for d in unmapped] == ["Barne- og familiedepartementet"]


def test_search_listing_is_used_when_year_page_is_missing():
    pages = regjeringen_world(with_year_page=False)
    listing = "".join(f'<a href="/no/dokumenter/prop.-1-s-20242025/id{n}/">x</a>' for n in range(1, 12))
    pages[discover.SEARCH.format(kind="S", prev=2024, year=2025, page=1)] = listing
    pages[discover.SEARCH.format(kind="LS", prev=2024, year=2025, page=1)] = '<a href="/no/dokumenter/prop.-1-ls-20242025/id99/">x</a>'
    documents = discover.find_departments(2025, FakeFetcher(pages))
    assert len(documents) == 12


def test_uit_allocation_from_elements_api_uses_tenant_header():
    fetcher = FakeFetcher(elements_world())
    result = discover.find_uit_allocation(2025, fetcher)
    assert result["status"] == "funnet"
    assert result["meeting_date"] == "2024-06-20" and result["board_case"] == "S 18/24" and result["archive_case"] == "2024/8285"
    assert [d["id"] for d in result["documents"]] == [4197, 5227]
    assert result["documents"][0]["url"] == f"{EL}Documents/ShowDocument/db1/2137/4197"
    assert all(call[2].get("Tenant") == discover.ELEMENTS_TENANT for call in fetcher.calls if "elementscloud" in call[1])


def test_uit_allocation_not_found_lists_meetings_checked():
    world = elements_world()
    world[f"{EL}api/DmbHandlings/GetByMeetingId/75"] = [{"Id": 1, "Title": "Annet"}]
    result = discover.find_uit_allocation(2025, FakeFetcher(world))
    assert result["status"] == "ikke identifisert" and result["meetings_checked"] == ["2024-05-23", "2024-06-20"]


def test_check_verdicts_and_exit_codes(tmp_path, capsys):
    pages = {**regjeringen_world(), **elements_world()}
    full = FakeFetcher(pages, pdfs=[blaatt_url(2025)])
    assert discover.check(2025, "forslag", full)["verdict"] == "published"

    without_uit = FakeFetcher(regjeringen_world(), pdfs=[blaatt_url(2025)])
    report = discover.check(2025, "forslag", without_uit)
    assert report["verdict"] == "partial" and report["missing_parts"] == []

    without_kd = {k: v for k, v in pages.items() if "/id1/" not in k}
    assert discover.check(2025, "forslag", FakeFetcher(without_kd, pdfs=[blaatt_url(2025)]))["verdict"] == "not_published"
    assert discover.check(2025, "forslag", FakeFetcher(pages))["verdict"] == "not_published"

    discover.Fetcher = lambda: full
    output = tmp_path / "kildesjekk.json"
    assert discover.main(["check", "--year", "2025", "--output", str(output)]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["verdict"] == "published"


def test_write_sources_input_separates_uit_documents(tmp_path):
    pages = {**regjeringen_world(), **elements_world()}
    report = discover.check(2025, "forslag", FakeFetcher(pages, pdfs=[blaatt_url(2025)]))
    report_path = tmp_path / "kildesjekk.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    out = tmp_path / "kilder-input.json"
    uit_out = tmp_path / "uit-kilder-input.json"
    assert discover.main(["write", "--from", str(report_path), "--output", str(out), "--uit-output", str(uit_out)]) == 0
    sources = json.loads(out.read_text(encoding="utf-8"))
    ids = [s["id"] for s in sources]
    assert ids[0] == "blaatt-hefte-forslag-2025" and "kd-prop-2025" in ids and "fin-skatt-prop-2025" in ids
    assert all(set(s) >= {"id", "url", "budget_year", "stage", "title"} for s in sources)
    assert "bfd" not in " ".join(ids)
    uit = json.loads(uit_out.read_text(encoding="utf-8"))
    assert [u["id"] for u in uit] == ["uit-forelopig-2025-framlegg", "uit-forelopig-2025-vedlegg-5227"]
    assert all(set(u) == {"id", "url", "budget_year", "stage", "title"} for u in uit)
