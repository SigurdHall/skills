"""
PostToolUse hook: when Claude Code edits a CLAUDE.md, copy it to AGENTS.md
in the same directory so Codex stays in sync.

Reads the tool call JSON from stdin (Claude Code hook protocol).
Exits 0 always — never block the tool call.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return

    tool_input = payload.get("tool_input") or payload.get("input") or {}
    file_path = tool_input.get("file_path", "")

    if not file_path:
        return

    src = Path(file_path)
    if src.name != "CLAUDE.md":
        return

    if not src.exists():
        return

    # Skip the workspace root — AGENTS.md there has different, Codex-specific content
    workspace_root = Path(r"C:\repos")
    if src.parent.resolve() == workspace_root.resolve():
        return

    dest = src.parent / "AGENTS.md"

    try:
        shutil.copy2(src, dest)
        print(f"[sync_agent_files] Copied {src.name} → {dest}", file=sys.stderr)
    except Exception as exc:
        print(f"[sync_agent_files] Could not copy to {dest}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
