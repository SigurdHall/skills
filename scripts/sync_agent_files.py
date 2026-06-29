"""
PostToolUse hook: keep CLAUDE.md and AGENTS.md paired in the same directory.

When Claude edits CLAUDE.md, copy it to AGENTS.md. When Codex edits AGENTS.md,
copy it to CLAUDE.md. The workspace root is skipped because those files contain
different tool-specific guidance.

Reads hook JSON from stdin when available. Exits 0 always so it never blocks the
tool call.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


AGENT_FILE_NAMES = {"AGENTS.md", "CLAUDE.md"}
WORKSPACE_ROOT = Path(r"C:\repos")


def extract_path_candidates(payload: object) -> list[Path]:
    """Return likely edited file paths from Claude/Codex hook payload shapes."""

    candidates: list[Path] = []

    def add_path(value: object) -> None:
        if not isinstance(value, str) or not value.strip():
            return
        path = Path(value.strip().strip('"'))
        if path.name in AGENT_FILE_NAMES:
            candidates.append(path)

    def walk(value: object) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in {"file_path", "path"}:
                    add_path(nested)
                else:
                    walk(nested)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str):
            parse_patch_paths(value)

    def parse_patch_paths(text: str) -> None:
        for line in text.splitlines():
            for prefix in (
                "*** Add File: ",
                "*** Update File: ",
                "*** Delete File: ",
                "*** Move to: ",
            ):
                if line.startswith(prefix):
                    add_path(line.removeprefix(prefix))

    walk(payload)
    return candidates


def sync_agent_file(src: Path, workspace_root: Path = WORKSPACE_ROOT) -> Path | None:
    """Copy an edited agent instruction file to the paired agent file."""

    if src.name not in AGENT_FILE_NAMES:
        return None

    try:
        resolved_parent = src.parent.resolve()
    except OSError:
        return None

    if resolved_parent == workspace_root.resolve():
        return None

    if not src.exists():
        return None

    dest_name = "AGENTS.md" if src.name == "CLAUDE.md" else "CLAUDE.md"
    dest = src.parent / dest_name
    shutil.copy2(src, dest)
    return dest


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return

    for src in extract_path_candidates(payload):
        try:
            dest = sync_agent_file(src)
            if dest:
                print(f"[sync_agent_files] Copied {src.name} -> {dest}", file=sys.stderr)
        except Exception as exc:
            print(f"[sync_agent_files] Could not sync {src}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
