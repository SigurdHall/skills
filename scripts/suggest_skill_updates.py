from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Iterable


DEFAULT_SKILLS_REPO_ROOT = Path(__file__).resolve().parents[1]


class SuggestionType(StrEnum):
    NEW_SKILL = "new-skill"
    MODIFY_USED_SKILL = "modify-used-skill"
    ADD_EDGE_CASE_CONTEXT = "add-edge-case-context"


@dataclass(frozen=True)
class SkillSuggestion:
    suggestion_type: SuggestionType
    source: Path
    line_number: int
    evidence: str
    matched_skill: str | None = None
    matched_skill_path: Path | None = None


NEW_SKILL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\balways\b.*\b(do|use|add|check|include|run)\b",
        r"\bnext time\b",
        r"\bmake this reusable\b",
        r"\breusable workflow\b",
        r"(?<!do not )\bcreate (a )?skill\b",
        r"\bnew skill\b",
        r"\b(reusable|shared|repeatable)\b.*\bchecklist\b",
    ]
]

MODIFY_SKILL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bused skill\b",
        r"\bskill\b.*\b(missed|missing|wrong|should have|failed|lacked)\b",
        r"\bshould have loaded\b",
        r"\bwrong skill\b",
        r"\bupdate .*skill\b",
        r"\bmodify .*skill\b",
    ]
]

EDGE_CASE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bedge case\b",
        r"\bexcept when\b",
        r"\bfails when\b",
        r"\bspecial case\b",
        r"\bskill\b.*\bboundary\b",
        r"\bcorner case\b",
    ]
]

DEFAULT_SCAN_GLOBS = ["*.md", "*.txt"]
EXCLUDED_PARTS = {".git", "__pycache__", "reports", ".venv", "venv", "node_modules"}
NOOP_STOP_DECISION = {"continue": True, "suppressOutput": True}
SKILL_USE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\busing [`\"']?[\w:-]*skill",
        r"\bbruker [`\"']?[\w:-]*skill",
        r"\bskill[- ]?(design|creator|installer|evaluation|eval)",
        r"\bSKILL\.md\b",
        r"\bskills[/\\][\w/-]+[/\\]SKILL\.md\b",
    ]
]


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("\"'")
    return data


def discover_skill_catalog(repo_root: Path) -> dict[str, dict[str, Path | str]]:
    catalog: dict[str, dict[str, Path | str]] = {}
    for skill_file in sorted((repo_root / "skills").glob("*/*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        name = frontmatter.get("name") or skill_file.parent.name
        catalog[name] = {
            "path": skill_file.relative_to(repo_root),
            "description": frontmatter.get("description", ""),
        }
    return catalog


def iter_scan_files(repo_root: Path, input_path: Path | None) -> Iterable[Path]:
    if input_path is not None:
        yield input_path
        return

    for pattern in DEFAULT_SCAN_GLOBS:
        for path in sorted(repo_root.rglob(pattern)):
            if any(part in EXCLUDED_PARTS for part in path.relative_to(repo_root).parts):
                continue
            if path.name == "SKILL.md":
                continue
            yield path


def match_skill(line: str, catalog: dict[str, dict[str, Path | str]]) -> tuple[str | None, Path | None]:
    line_lower = line.lower()
    best_name: str | None = None
    best_path: Path | None = None
    best_score = 0

    for name, metadata in catalog.items():
        tokens = set(re.findall(r"[a-z0-9]+", name.lower()))
        description = str(metadata.get("description", ""))
        tokens.update(re.findall(r"[a-z0-9]+", description.lower()))
        score = sum(1 for token in tokens if len(token) > 3 and token in line_lower)
        if name.lower() in line_lower:
            score += 5
        if score > best_score:
            best_name = name
            best_path = Path(str(metadata["path"]))
            best_score = score

    return (best_name, best_path) if best_score > 0 else (None, None)


def classify_line(line: str) -> SuggestionType | None:
    if any(pattern.search(line) for pattern in EDGE_CASE_PATTERNS):
        return SuggestionType.ADD_EDGE_CASE_CONTEXT
    if any(pattern.search(line) for pattern in MODIFY_SKILL_PATTERNS):
        return SuggestionType.MODIFY_USED_SKILL
    if any(pattern.search(line) for pattern in NEW_SKILL_PATTERNS):
        return SuggestionType.NEW_SKILL
    return None


def scan_text_for_suggestions(
    text: str,
    source: Path,
    catalog: dict[str, dict[str, Path | str]],
) -> list[SkillSuggestion]:
    suggestions: list[SkillSuggestion] = []
    last_matched_skill: tuple[str | None, Path | None] = (None, None)

    for index, raw_line in enumerate(text.splitlines(), start=1):
        line = " ".join(raw_line.strip().split())
        if not line:
            continue
        suggestion_type = classify_line(line)
        if suggestion_type is None:
            continue

        matched_skill, matched_skill_path = match_skill(line, catalog)
        if matched_skill is not None:
            last_matched_skill = (matched_skill, matched_skill_path)
        elif suggestion_type == SuggestionType.ADD_EDGE_CASE_CONTEXT:
            matched_skill, matched_skill_path = last_matched_skill

        suggestions.append(
            SkillSuggestion(
                suggestion_type=suggestion_type,
                source=source,
                line_number=index,
                evidence=line,
                matched_skill=matched_skill,
                matched_skill_path=matched_skill_path,
            )
        )

    return suggestions


def scan_files(repo_root: Path, input_path: Path | None = None) -> list[SkillSuggestion]:
    catalog = discover_skill_catalog(repo_root)
    suggestions: list[SkillSuggestion] = []
    for path in iter_scan_files(repo_root, input_path):
        text = path.read_text(encoding="utf-8")
        source = path.relative_to(repo_root) if path.is_relative_to(repo_root) else path
        suggestions.extend(scan_text_for_suggestions(text, source=source, catalog=catalog))
    return suggestions


def generate_markdown_report(suggestions: list[SkillSuggestion]) -> str:
    lines = [
        "# Skill Suggestions",
        "",
        "Generated suggestions only. Review manually before creating or changing any skill.",
        "",
    ]
    if not suggestions:
        lines.extend(["No skill suggestions found.", ""])
        return "\n".join(lines)

    for item in suggestions:
        lines.append(f"## {item.suggestion_type.value}")
        lines.append("")
        lines.append(f"- Source: `{format_path(item.source)}:{item.line_number}`")
        if item.matched_skill:
            lines.append(f"- Candidate skill: `{item.matched_skill}`")
        if item.matched_skill_path:
            lines.append(f"- Skill path: `{format_path(item.matched_skill_path)}`")
        lines.append(f"- Evidence: {item.evidence}")
        lines.append("")
    return "\n".join(lines)


def format_path(path: Path) -> str:
    return path.as_posix()


def build_stop_self_review_decision(payload: dict) -> dict:
    return build_stop_self_review_decision_with_inbox(payload, inbox_path=None)


def build_stop_self_review_decision_with_inbox(payload: dict, inbox_path: Path | None) -> dict:
    if payload.get("hook_event_name") != "Stop":
        return NOOP_STOP_DECISION
    if payload.get("stop_hook_active"):
        return NOOP_STOP_DECISION

    last_message = str(payload.get("last_assistant_message") or "")
    if not has_skill_self_review_signal(last_message):
        return NOOP_STOP_DECISION

    if inbox_path is not None:
        append_skill_improvement_entry(payload, inbox_path)

    reason = (
        "Do a short skill self-review before ending. "
        "Assess whether the task should become a new skill. If a skill was used, assess whether it should be improved. "
        "Assess relevant edge cases and whether a change is actually necessary. "
        "Do not edit SKILL.md automatically; propose concrete changes or write suggestions to "
        "`C:\\repos\\skills\\reports\\skill-improvement-inbox.md` if useful. "
        "If no skill change is needed, say that briefly and finish."
    )
    return {"decision": "block", "reason": reason}


def has_skill_self_review_signal(text: str) -> bool:
    return any(pattern.search(text) for pattern in SKILL_USE_PATTERNS)


def build_skill_improvement_entry(payload: dict) -> str:
    event_name = str(payload.get("hook_event_name") or "unknown")
    transcript_path = str(payload.get("transcript_path") or "unknown")
    last_message = str(payload.get("last_assistant_message") or "").strip()
    excerpt = last_message[:600].replace("\r", " ").replace("\n", " ")

    lines = [
        "## Skill self-review candidate",
        "",
        f"- Trigger: `{event_name}`",
        f"- Transcript: `{transcript_path}`",
        "- Suggested action: Review whether to create a new skill, improve a used skill, or add edge-case context.",
        "- Necessity check: required / useful / not worth changing",
        "- Do not auto-edit: `SKILL.md` changes must be reviewed deliberately.",
        f"- Evidence: {excerpt}",
        "",
    ]
    return "\n".join(lines)


def append_skill_improvement_entry(payload: dict, inbox_path: Path) -> None:
    inbox_path.parent.mkdir(parents=True, exist_ok=True)
    header = "# Skill Improvement Inbox\n\n"
    existing = inbox_path.read_text(encoding="utf-8") if inbox_path.exists() else header
    if not existing.startswith("# Skill Improvement Inbox"):
        existing = header + existing
    inbox_path.write_text(existing.rstrip() + "\n\n" + build_skill_improvement_entry(payload), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Suggest skill creation or updates from notes and Markdown files.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root to scan.")
    parser.add_argument("--input", type=Path, default=None, help="Optional single context file to scan.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "skill-suggestions.md",
        help="Markdown report path, relative to repo root unless absolute.",
    )
    parser.add_argument("--fail-on-suggestions", action="store_true", help="Exit with code 2 when suggestions are found.")
    parser.add_argument("--codex-stop-hook", action="store_true", help="Read a Codex Stop hook payload from stdin.")
    parser.add_argument(
        "--inbox",
        type=Path,
        default=None,
        help="Optional skill improvement inbox path for Codex Stop hook logging.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.codex_stop_hook:
        payload = json.load(sys.stdin)
        inbox_path = args.inbox
        if inbox_path is None:
            inbox_path = DEFAULT_SKILLS_REPO_ROOT / "reports" / "skill-improvement-inbox.md"
        elif not inbox_path.is_absolute():
            inbox_path = DEFAULT_SKILLS_REPO_ROOT / inbox_path
        print(json.dumps(build_stop_self_review_decision_with_inbox(payload, inbox_path), ensure_ascii=False))
        return 0

    repo_root = args.repo_root.resolve()
    input_path = args.input.resolve() if args.input else None
    output_path = args.output if args.output.is_absolute() else repo_root / args.output

    suggestions = scan_files(repo_root=repo_root, input_path=input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_markdown_report(suggestions), encoding="utf-8")

    print(f"Wrote {len(suggestions)} suggestion(s) to {output_path}")
    if suggestions and args.fail_on_suggestions:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
