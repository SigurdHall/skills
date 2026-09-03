#!/usr/bin/env python3
"""Vendor a pinned microsoft/skills-for-fabric release into .claude/ for Claude Code.

Claude Code discovers project skills from `.claude/skills/<name>/SKILL.md`, and
cloud sessions load that folder from the cloned repo. The upstream skills link
to `../../common/...`, so the vendored layout mirrors the upstream root:

    .claude/skills/<name>/          one folder per upstream skill
    .claude/common/                 shared references the skills link to
    .claude/mcp-setup/              MCP registration notes linked from skills
    .claude/LICENSE-skills-for-fabric
    .claude/skills-for-fabric.vendor.json   tag, commit, version, skill list

Usage:
    python scripts/vendor_skills_for_fabric.py --tag v0.3.14
    python scripts/vendor_skills_for_fabric.py --tag v0.3.14 --source C:\\repos\\skills-for-fabric

Only skills listed in the previous manifest are removed before copying, so
skills you add to `.claude/skills/` yourself are left alone. A foreign folder
whose name collides with an upstream skill stops the run unless `--force`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

UPSTREAM_URL = "https://github.com/microsoft/skills-for-fabric"
MANIFEST_NAME = "skills-for-fabric.vendor.json"
SHARED_FOLDERS = ("common", "mcp-setup")


class VendorConflict(RuntimeError):
    """A folder under .claude/skills/ would be overwritten but is not ours."""


def read_manifest(dest: Path) -> dict:
    path = dest / MANIFEST_NAME
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def upstream_skill_names(checkout: Path) -> list[str]:
    skills_dir = checkout / "skills"
    if not skills_dir.is_dir():
        raise FileNotFoundError(f"No skills/ folder in {checkout}")
    return sorted(p.name for p in skills_dir.iterdir() if (p / "SKILL.md").is_file())


def git_output(checkout: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(checkout), *args],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def package_version(checkout: Path) -> str | None:
    package = checkout / "package.json"
    if not package.exists():
        return None
    return json.loads(package.read_text(encoding="utf-8")).get("version")


def vendor(checkout: Path, dest: Path, tag: str, force: bool = False) -> dict:
    """Copy the upstream skills, shared folders and license into dest; write the manifest."""

    previous = set(read_manifest(dest).get("skills", []))
    names = upstream_skill_names(checkout)
    skills_dest = dest / "skills"

    conflicts = [
        name for name in names
        if (skills_dest / name).exists() and name not in previous
    ]
    if conflicts and not force:
        raise VendorConflict(
            "These folders exist under .claude/skills/ but are not recorded as vendored: "
            + ", ".join(conflicts)
            + ". Rename them or pass --force to overwrite."
        )

    for name in sorted(previous | set(conflicts)):
        shutil.rmtree(skills_dest / name, ignore_errors=True)

    skills_dest.mkdir(parents=True, exist_ok=True)
    for name in names:
        shutil.copytree(checkout / "skills" / name, skills_dest / name)

    for folder in SHARED_FOLDERS:
        source = checkout / folder
        target = dest / folder
        shutil.rmtree(target, ignore_errors=True)
        if source.is_dir():
            shutil.copytree(source, target)

    license_file = checkout / "LICENSE"
    if license_file.exists():
        shutil.copyfile(license_file, dest / "LICENSE-skills-for-fabric")

    manifest = {
        "source": UPSTREAM_URL,
        "tag": tag,
        "commit": git_output(checkout, "rev-parse", "HEAD"),
        "package_version": package_version(checkout),
        "vendored_at": dt.date.today().isoformat(),
        "layout": {
            "skills": "skills/<name>",
            "shared": list(SHARED_FOLDERS),
            "license": "LICENSE-skills-for-fabric",
        },
        "skills": names,
    }
    (dest / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def obtain_checkout(source: str | None, tag: str, workdir: Path) -> Path:
    """Return a checkout at the tag: an existing path, or a fresh shallow clone."""

    if source and Path(source).is_dir():
        checkout = Path(source)
        described = git_output(checkout, "describe", "--tags", "--exact-match")
        if described and described != tag:
            raise SystemExit(f"{checkout} is at {described}, not {tag}. Check out the tag first.")
        return checkout

    url = source or UPSTREAM_URL
    clone = workdir / "skills-for-fabric"
    subprocess.run(
        ["git", "clone", "--quiet", "--depth", "1", "--branch", tag, url, str(clone)],
        check=True,
    )
    return clone


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tag", required=True, help="Upstream release tag, for example v0.3.14")
    parser.add_argument("--source", help="Existing checkout path or git URL (default: upstream GitHub)")
    parser.add_argument("--dest", default=".claude", help="Target .claude folder (default: ./.claude)")
    parser.add_argument("--force", action="store_true", help="Overwrite colliding non-vendored skill folders")
    args = parser.parse_args(argv)

    dest = Path(args.dest).resolve()
    with tempfile.TemporaryDirectory(prefix="skills-for-fabric-") as tmp:
        checkout = obtain_checkout(args.source, args.tag, Path(tmp))
        try:
            manifest = vendor(checkout, dest, tag=args.tag, force=args.force)
        except VendorConflict as error:
            print(f"error: {error}", file=sys.stderr)
            return 1

    print(
        f"Vendored {len(manifest['skills'])} skills from {manifest['source']} at {manifest['tag']} "
        f"(package {manifest['package_version']}, commit {manifest['commit']}) into {dest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
