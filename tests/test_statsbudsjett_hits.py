import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills/knowledge-management/uit-statsbudsjett-analyse/scripts/extract_hits.py"
spec = importlib.util.spec_from_file_location("statsbudsjett_hits", SCRIPT)
hits = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hits)

DOC = """=== PDF-side 88 ===
Kap. 714 post 79 Andre tilskudd

Formålet med tilskuddet er å styrke kunnskapsgrunnlaget.

Det foreslås 7,3 mill. kroner til Tromsøundersøkelsen ved UiT Norges arktiske universitet.
Tilskuddet forvaltes av Helsedirektoratet.

Videre foreslås midler til andre formål uten tilknytning.
=== PDF-side 89 ===
Det er viktig med kontinuitet i arbeidet. NUIT er en annen enhet.
Linje to uten treff.
Linje tre uten treff.
Linje fire uten treff.
Linje fem uten treff.
Linje seks uten treff.
Linje sju nevner Universitetet i
Tromsø over linjeskift.
Linje ni uten treff.
Linje ti uten treff.
"""


def test_hits_have_context_and_short_keywords_need_word_boundaries():
    found = hits.find_hits(DOC, ["UiT", "Tromsøundersøkelsen", "Universitetet i Tromsø"], window=4)
    pages = [h["pdf_page"] for h in found]
    assert pages == [88, 89]
    first = found[0]
    assert first["keywords"] == ["UiT", "Tromsøundersøkelsen"]
    assert first["before"].startswith("Formålet") and first["after"].startswith("Videre")
    # side 89 har ingen avsnittsskille og deles i vinduer; «kontinuitet» og «NUIT» gir ikke UiT-treff
    second = found[1]
    assert "Universitetet i\nTromsø" in second["hit"] and "UiT" not in second["keywords"]
    assert all("kontinuitet" not in h["hit"] or "UiT" not in h["keywords"] for h in found)


def test_run_writes_per_part_files_and_reports_missing_sources(tmp_path):
    sources = tmp_path / "kilder"
    sources.mkdir()
    (sources / "hod-prop-2025.txt").write_text(DOC, encoding="utf-8")
    config = {"budget_year": 2025, "roles": [
        {"id": "helse_miljo", "parts": ["hod", "kld"], "keywords": ["Tromsøundersøkelsen", "Saminor"]},
    ]}
    cfg = tmp_path / "arbeidsdeling.json"
    cfg.write_text(json.dumps(config), encoding="utf-8")
    out = tmp_path / "treff"
    code = hits.main([str(cfg), "--sources-dir", str(sources), "--output", str(out)])
    assert code == 3  # kld-uttrekket mangler
    data = json.loads((out / "hod-treff.json").read_text(encoding="utf-8"))
    assert data["role"] == "helse_miljo" and "UiT" in data["keywords"] and "Saminor" in data["keywords"]
    assert len(data["files"]["hod-prop-2025.txt"]) == 2
    assert data["keyword_counts"] == {"UiT": 1, "Norges arktiske universitet": 1, "Tromsøundersøkelsen": 1, "Universitetet i Tromsø": 1}
    md = (out / "hod-treff.md").read_text(encoding="utf-8")
    assert "PDF-side 88" in md and "**Det foreslås 7,3 mill. kroner" in md
    assert "| Tromsøundersøkelsen | 1 |" in md
    assert (out / "kld-treff.json").exists()


def test_source_mapping_for_special_parts():
    assert hits.sources_for("ramme", 2027) == ["blaatt-hefte-forslag-2027.txt", "kd-prop-2027.txt"]
    assert hits.sources_for("fin", 2027) == ["fin-skatt-prop-2027.txt"]
    assert hits.sources_for("kud", 2027) == ["kud-prop-2027.txt"]
