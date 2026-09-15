import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills/knowledge-management/uit-statsbudsjett-analyse/scripts/check_clean_state.py"
spec = importlib.util.spec_from_file_location("statsbudsjett_clean_state", SCRIPT)
clean = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clean)


def make_project(tmp_path, year=2025, run_id="2025-claude-v1"):
    project = tmp_path / "prosjekt"
    (project / str(year)).mkdir(parents=True)  # fasitmappen: skal aldri røres
    (project / str(year) / "fasit.pdf").write_text("fasit", encoding="utf-8")
    (project / "arbeidsflyt").mkdir()
    (project / "arbeidsflyt" / f"arbeidsdeling-{year}.json").write_text("{}", encoding="utf-8")
    (project / "leveranser" / run_id / "oppdrag").mkdir(parents=True)
    (project / "leveranser" / run_id / "kildesjekk.json").write_text("{}", encoding="utf-8")
    (project / "leveranser" / "2024-v2").mkdir()
    (project / "leveranser" / f"{year}-claude-v0").mkdir()
    (project / "analyse" / "kilder" / str(year)).mkdir(parents=True)
    (project / "analyse" / "kilder" / str(year) / "kd.pdf").write_text("pdf", encoding="utf-8")
    (project / "analyse" / "kilder" / f"uit-forutsetninger-{year}").mkdir()
    (project / "analyse" / "kilder" / "2024").mkdir()
    (project / "analyse" / f"uit-forutsetninger-{year}.md").write_text("x", encoding="utf-8")
    (project / "analyse" / "uit-forutsetninger-2024.md").write_text("behold", encoding="utf-8")
    (project / "arbeidsminne" / "kd_ramme").mkdir(parents=True)
    (project / "arbeidsminne" / "kd_ramme" / "erfaringer-2018-2023.md").write_text("historikk", encoding="utf-8")
    (project / "arbeidsminne" / "kd_ramme" / f"erfaringer-{year}-proeve.md").write_text("rest", encoding="utf-8")
    return project


def test_leftovers_are_listed_but_fasit_config_and_history_are_not(tmp_path):
    project = make_project(tmp_path)
    found = {p.relative_to(project).as_posix() for p in clean.leftover_paths(project, 2025, "2025-claude-v1")}
    assert found == {
        "leveranser/2025-claude-v1", "analyse/kilder/2025", "analyse/kilder/uit-forutsetninger-2025",
        "analyse/uit-forutsetninger-2025.md", "arbeidsminne/kd_ramme/erfaringer-2025-proeve.md",
    }
    assert clean.other_runs_for_year(project, 2025, "2025-claude-v1") == ["2025-claude-v0"]


def test_check_without_archive_reports_and_exits_3(tmp_path, capsys):
    project = make_project(tmp_path)
    out = tmp_path / "rydd.json"
    assert clean.main(["--project", str(project), "--year", "2025", "--run-id", "2025-claude-v1", "--output", str(out)]) == 3
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["clean"] is False and report["archived_to"] is None and len(report["leftovers"]) == 5
    assert (project / "leveranser" / "2025-claude-v1").exists()


def test_archive_moves_leftovers_and_keeps_everything_else(tmp_path):
    project = make_project(tmp_path)
    assert clean.main(["--project", str(project), "--year", "2025", "--run-id", "2025-claude-v1", "--archive"]) == 0
    archived = list((project / "arkiv" / "avbrutt").iterdir())
    assert len(archived) == 1 and archived[0].name.endswith("-2025-claude-v1")
    moved = archived[0]
    assert (moved / "leveranser/2025-claude-v1/kildesjekk.json").exists()
    assert (moved / "analyse/kilder/2025/kd.pdf").exists()
    assert (moved / "arbeidsminne/kd_ramme/erfaringer-2025-proeve.md").read_text(encoding="utf-8") == "rest"
    assert not (project / "leveranser" / "2025-claude-v1").exists()
    assert not (project / "analyse" / "kilder" / "2025").exists()
    # untouched
    assert (project / "2025" / "fasit.pdf").read_text(encoding="utf-8") == "fasit"
    assert (project / "arbeidsflyt" / "arbeidsdeling-2025.json").exists()
    assert (project / "arbeidsminne" / "kd_ramme" / "erfaringer-2018-2023.md").read_text(encoding="utf-8") == "historikk"
    assert (project / "analyse" / "uit-forutsetninger-2024.md").exists() and (project / "analyse" / "kilder" / "2024").exists()
    assert (project / "leveranser" / "2024-v2").exists() and (project / "leveranser" / "2025-claude-v0").exists()
    assert clean.main(["--project", str(project), "--year", "2025", "--run-id", "2025-claude-v1"]) == 0
