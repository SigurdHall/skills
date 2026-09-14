import hashlib
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT = Path(__file__).parents[1] / "skills/knowledge-management/uit-statsbudsjett-analyse/scripts/fetch_sources.py"


@pytest.fixture
def fetcher():
    spec = importlib.util.spec_from_file_location("statsbudsjett_fetch", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source():
    return {
        "id": "uit-2024-forutsetninger",
        "url": "https://uit.no/behandlingdok/123",
        "budget_year": 2024,
        "stage": "forelopig-fordeling",
        "title": "Foreløpig budsjettfordeling 2024",
    }


@pytest.fixture
def mock_curl(monkeypatch, fetcher):
    response = SimpleNamespace(
        data=b"%PDF-1.7\nTestdokument\n%%EOF\n",
        effective_url="https://uit.no/files/forutsetninger.pdf",
        calls=[],
    )

    def run(command, **kwargs):
        response.calls.append(command)
        assert command[0] == "curl"
        assert command[command.index("--proto") + 1] == "=https"
        assert command[command.index("--proto-redir") + 1] == "=https"
        assert "shell" not in kwargs
        Path(command[command.index("--output") + 1]).write_bytes(response.data)
        return SimpleNamespace(stdout=response.effective_url)

    monkeypatch.setattr(fetcher.subprocess, "run", run)
    return response


def test_download_records_bytes_redirect_time_and_unverified_classification(tmp_path, fetcher, mock_curl):
    records = fetcher.fetch_sources([source()], tmp_path)
    record = records[0]
    assert (tmp_path / record["file"]).read_bytes() == mock_curl.data
    assert record["file"] == "uit-2024-forutsetninger.pdf"
    assert record["sha256"] == hashlib.sha256(mock_curl.data).hexdigest()
    assert record["bytes"] == len(mock_curl.data)
    assert record["effective_url"] == mock_curl.effective_url
    assert datetime.fromisoformat(record["retrieved_at_utc"]).utcoffset().total_seconds() == 0
    assert record["classification_verified"] is False
    assert all(record[key] == value for key, value in source().items())
    assert json.loads((tmp_path / "sources.json").read_text()) == records


def test_identical_rerun_preserves_original_files_and_timestamp(tmp_path, fetcher, mock_curl):
    first = fetcher.fetch_sources([source()], tmp_path)
    before = {path.name: (path.read_bytes(), path.stat().st_mtime_ns) for path in tmp_path.iterdir()}
    second = fetcher.fetch_sources([source()], tmp_path)
    after = {path.name: (path.read_bytes(), path.stat().st_mtime_ns) for path in tmp_path.iterdir()}
    assert second == first
    assert after == before


def test_changed_remote_pdf_leaves_original_pdf_and_manifest_intact(tmp_path, fetcher, mock_curl):
    fetcher.fetch_sources([source()], tmp_path)
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    mock_curl.data = b"%PDF-1.7\nEndret dokument\n%%EOF\n"
    with pytest.raises(ValueError, match="avvikende"):
        fetcher.fetch_sources([source()], tmp_path)
    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == before


def test_changed_classification_cannot_relabel_archived_source(tmp_path, fetcher, mock_curl):
    fetcher.fetch_sources([source()], tmp_path)
    changed = source()
    changed["stage"] = "vedtatt-budsjett"
    with pytest.raises(ValueError, match="metadata"):
        fetcher.fetch_sources([changed], tmp_path)


def test_additional_source_preserves_existing_manifest_entry(tmp_path, fetcher, mock_curl):
    first = fetcher.fetch_sources([source()], tmp_path)
    extra = source()
    extra["id"] = "kd-2024-forslag"
    records = fetcher.fetch_sources([extra], tmp_path)
    assert records[0] == first[0]
    assert len(records) == 2


@pytest.mark.parametrize("source_id", ["../outside", "a/b", "a.b", "", "UPPER", "-leading"])
def test_unsafe_ids_are_rejected_before_network(tmp_path, fetcher, mock_curl, source_id):
    data = source()
    data["id"] = source_id
    with pytest.raises(ValueError, match="id"):
        fetcher.fetch_sources([data], tmp_path)
    assert not mock_curl.calls
    assert not list(tmp_path.iterdir())


def test_duplicate_ids_are_rejected_before_network(tmp_path, fetcher, mock_curl):
    with pytest.raises(ValueError, match="Duplikat"):
        fetcher.fetch_sources([source(), source()], tmp_path)
    assert not mock_curl.calls


@pytest.mark.parametrize("url", ["http://uit.no/a.pdf", "file:///tmp/a.pdf", "https://", "https://user:password@uit.no/a.pdf"])
def test_only_https_urls_without_credentials_are_accepted(tmp_path, fetcher, mock_curl, url):
    data = source()
    data["url"] = url
    with pytest.raises(ValueError, match="HTTPS"):
        fetcher.fetch_sources([data], tmp_path)
    assert not mock_curl.calls


def test_non_pdf_response_is_rejected_without_archiving(tmp_path, fetcher, mock_curl):
    mock_curl.data = b"<html>Access denied</html>"
    with pytest.raises(ValueError, match="PDF"):
        fetcher.fetch_sources([source()], tmp_path)
    assert not list(tmp_path.iterdir())


def test_batch_failure_does_not_publish_partial_downloads(tmp_path, fetcher, monkeypatch):
    extra = source()
    extra["id"] = "second"
    responses = iter([b"%PDF-1.7\nfirst", b"<html>Not found</html>"])

    def run(command, **kwargs):
        Path(command[command.index("--output") + 1]).write_bytes(next(responses))
        return SimpleNamespace(stdout=source()["url"])

    monkeypatch.setattr(fetcher.subprocess, "run", run)
    with pytest.raises(ValueError, match="PDF"):
        fetcher.fetch_sources([source(), extra], tmp_path)
    assert not list(tmp_path.iterdir())


def test_curl_failure_does_not_publish_files(tmp_path, fetcher, monkeypatch):
    def run(command, **kwargs):
        raise fetcher.subprocess.CalledProcessError(22, command, stderr="HTTP 404")

    monkeypatch.setattr(fetcher.subprocess, "run", run)
    with pytest.raises(ValueError, match="Henting feilet"):
        fetcher.fetch_sources([source()], tmp_path)
    assert not list(tmp_path.iterdir())
