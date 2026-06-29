import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
TEST_TEMP_ROOT = REPO_ROOT / ".tmp-tests"

from sync_agent_files import extract_path_candidates, sync_agent_file  # noqa: E402


class SyncAgentFilesTests(unittest.TestCase):
    def temp_dir(self) -> tempfile.TemporaryDirectory[str]:
        TEST_TEMP_ROOT.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT)

    def test_syncs_claude_to_agents(self) -> None:
        with self.temp_dir() as tmpdir:
            folder = Path(tmpdir) / "skill"
            folder.mkdir()
            source = folder / "CLAUDE.md"
            source.write_text("# Shared instructions\n", encoding="utf-8")

            dest = sync_agent_file(source, workspace_root=Path(tmpdir))

            self.assertEqual(dest, folder / "AGENTS.md")
            self.assertEqual(dest.read_text(encoding="utf-8"), "# Shared instructions\n")

    def test_syncs_agents_to_claude(self) -> None:
        with self.temp_dir() as tmpdir:
            folder = Path(tmpdir) / "project"
            folder.mkdir()
            source = folder / "AGENTS.md"
            source.write_text("# Shared project instructions\n", encoding="utf-8")

            dest = sync_agent_file(source, workspace_root=Path(tmpdir))

            self.assertEqual(dest, folder / "CLAUDE.md")
            self.assertEqual(
                dest.read_text(encoding="utf-8"),
                "# Shared project instructions\n",
            )

    def test_skips_workspace_root(self) -> None:
        with self.temp_dir() as tmpdir:
            root = Path(tmpdir)
            source = root / "AGENTS.md"
            source.write_text("# Codex-specific root instructions\n", encoding="utf-8")

            dest = sync_agent_file(source, workspace_root=root)

            self.assertIsNone(dest)
            self.assertFalse((root / "CLAUDE.md").exists())

    def test_extracts_paths_from_claude_payload_and_patch_payload(self) -> None:
        payload = {
            "tool_input": {"file_path": r"C:\repos\skills\skills\demo\CLAUDE.md"},
            "input": {
                "patch": "\n".join(
                    [
                        "*** Begin Patch",
                        "*** Update File: C:/repos/demo/AGENTS.md",
                        "*** End Patch",
                    ]
                )
            },
        }

        paths = extract_path_candidates(payload)

        self.assertEqual(
            [path.name for path in paths],
            ["CLAUDE.md", "AGENTS.md"],
        )

    def test_hook_script_exits_zero_without_payload(self) -> None:
        script = REPO_ROOT / "scripts" / "sync_agent_files.py"

        result = subprocess.run(
            [sys.executable, str(script)],
            input="",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
