#!/usr/bin/env python3
"""Build a deterministic, read-only inventory of a skills-for-fabric checkout."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<body>.*?)\n---", re.DOTALL)


def _frontmatter_value(body: str, key: str) -> str:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        match = re.match(rf"^{re.escape(key)}:\s*(.*)$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if value not in {">", ">-", "|", "|-"}:
            return value.strip("'\"")
        folded: list[str] = []
        for nested in lines[index + 1 :]:
            if nested and not nested[0].isspace():
                break
            if nested.strip():
                folded.append(nested.strip())
        return " ".join(folded)
    return ""


def read_skill_metadata(skill_file: Path) -> dict[str, str]:
    text = skill_file.read_text(encoding="utf-8-sig")
    match = FRONTMATTER_RE.search(text)
    if not match:
        raise ValueError(f"Missing YAML frontmatter: {skill_file}")
    body = match.group("body")
    name = _frontmatter_value(body, "name")
    if not name:
        raise ValueError(f"Missing skill name: {skill_file}")
    return {
        "name": name,
        "description": _frontmatter_value(body, "description"),
    }


def classify_skill(name: str) -> str:
    if "authoring" in name:
        return "authoring"
    if "consumption" in name:
        return "consumption"
    if "operations" in name:
        return "operations"
    if "migration" in name:
        return "migration"
    return "other"


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", lambda: False)
    return path.is_symlink() or bool(is_junction()) or os.path.islink(path)


def _junction_state(name: str, skill_path: Path, roots: list[Path]) -> list[dict[str, Any]]:
    states: list[dict[str, Any]] = []
    canonical = skill_path.resolve()
    for root in roots:
        candidate = root / name
        exists = candidate.exists()
        resolved = candidate.resolve() if exists else None
        states.append(
            {
                "root": str(root),
                "exists": exists,
                "is_link": _is_link(candidate) if exists else False,
                "target_matches": resolved == canonical if resolved else False,
            }
        )
    return states


def _git_state(root: Path) -> dict[str, Any]:
    if not (root / ".git").exists():
        return {"commit": None, "dirty": None}
    try:
        commit_result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if commit_result.returncode != 0:
            return {"commit": None, "dirty": None}
        status_result = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return {"commit": None, "dirty": None}
    return {
        "commit": commit_result.stdout.strip() or None,
        "dirty": bool(status_result.stdout.strip()) if status_result.returncode == 0 else None,
    }


def _scan_skill_root(root: Path, source: str) -> list[dict[str, str]]:
    if not root.is_dir():
        raise FileNotFoundError(f"Additional skills directory not found: {root}")
    exposures: list[dict[str, str]] = []
    for skill_file in sorted(root.glob("*/SKILL.md"), key=lambda item: item.parent.name):
        metadata = read_skill_metadata(skill_file)
        exposures.append(
            {
                "name": metadata["name"],
                "description": metadata["description"],
                "source": source,
                "path": str(skill_file.parent.resolve()),
            }
        )
    return exposures


def build_inventory(
    skills_repo: Path,
    junction_roots: list[Path],
    additional_skill_roots: list[Path] | None = None,
) -> dict[str, Any]:
    skills_repo = skills_repo.resolve()
    skills_dir = skills_repo / "skills"
    if not skills_dir.is_dir():
        raise FileNotFoundError(f"Skills directory not found: {skills_dir}")

    package_path = skills_repo / "package.json"
    package = json.loads(package_path.read_text(encoding="utf-8")) if package_path.exists() else {}

    additional_skill_roots = additional_skill_roots or []
    exposures = _scan_skill_root(skills_dir, "primary-checkout")
    for index, root in enumerate(additional_skill_roots, start=1):
        exposures.extend(_scan_skill_root(root.resolve(), f"additional-{index:02d}"))
    exposure_counts = Counter(exposure["name"] for exposure in exposures)

    skills: list[dict[str, Any]] = []
    for skill_file in sorted(skills_dir.glob("*/SKILL.md"), key=lambda item: item.parent.name):
        metadata = read_skill_metadata(skill_file)
        name = metadata["name"]
        skills.append(
            {
                "name": name,
                "category": classify_skill(name),
                "description": metadata["description"],
                "junctions": _junction_state(name, skill_file.parent, junction_roots),
            }
        )

    category_counts = Counter(skill["category"] for skill in skills)
    category_order = ["authoring", "consumption", "operations", "migration", "other"]
    return {
        "schema_version": "1.0",
        "package_name": package.get("name"),
        "package_version": package.get("version"),
        "git": _git_state(skills_repo),
        "skill_count": len(skills),
        "category_counts": {
            category: category_counts[category]
            for category in category_order
            if category_counts[category]
        },
        "skills": skills,
        "skill_exposures": exposures,
        "duplicate_names": sorted(
            name for name, count in exposure_counts.items() if count > 1
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills_repo", type=Path, help="Path to a skills-for-fabric checkout")
    parser.add_argument(
        "--junction-root",
        action="append",
        type=Path,
        default=[],
        help="Optional skill discovery root; repeat for multiple roots",
    )
    parser.add_argument(
        "--additional-skills-root",
        action="append",
        type=Path,
        default=[],
        help="Additional direct skill folder root (for example a plugin cache); repeat as needed",
    )
    parser.add_argument("--output", type=Path, help="Write JSON to this file instead of stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    inventory = build_inventory(
        args.skills_repo,
        args.junction_root,
        additional_skill_roots=args.additional_skills_root,
    )
    payload = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
