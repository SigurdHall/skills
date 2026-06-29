"""Validate Power BI PBIR bookmark actions against page-local bookmarks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def literal_value(property_obj: dict) -> str | None:
    try:
        return property_obj["expr"]["Literal"]["Value"].strip("'")
    except KeyError:
        return None


def load_bookmarks(definition_dir: Path) -> dict[str, dict]:
    bookmarks = {}
    for path in sorted((definition_dir / "bookmarks").glob("*.bookmark.json")):
        bookmark = read_json(path)
        bookmarks[bookmark["name"]] = bookmark
    return bookmarks


def find_bookmark_action_issues(definition_dir: str | Path) -> list[str]:
    definition_dir = Path(definition_dir)
    pages_dir = definition_dir / "pages"
    bookmarks = load_bookmarks(definition_dir)
    issues = []

    for page_path in sorted(pages_dir.glob("*/page.json")):
        page_id = page_path.parent.name
        page = read_json(page_path)
        page_display = page.get("displayName", page_id)

        for visual_path in sorted(page_path.parent.glob("visuals/*/visual.json")):
            visual = read_json(visual_path)
            visual_name = visual.get("name", visual_path.parent.name)
            links = (
                visual.get("visual", {})
                .get("visualContainerObjects", {})
                .get("visualLink", [])
            )

            for link in links:
                properties = link.get("properties", {})
                if literal_value(properties.get("type", {})) != "Bookmark":
                    continue

                bookmark_name = literal_value(properties.get("bookmark", {}))
                if not bookmark_name:
                    continue

                bookmark = bookmarks.get(bookmark_name)
                if not bookmark:
                    issues.append(
                        f"{page_display}/{visual_name} points to missing bookmark {bookmark_name}"
                    )
                    continue

                active_section = bookmark.get("explorationState", {}).get("activeSection")
                if active_section and active_section != page_id:
                    issues.append(
                        f"{page_display}/{visual_name} points to "
                        f"{bookmark.get('displayName', bookmark_name)} activeSection={active_section}"
                    )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that PBIR bookmark actions stay on the button page."
    )
    parser.add_argument(
        "definition_dir",
        type=Path,
        help="Path to the report definition folder, for example My.Report/definition.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    issues = find_bookmark_action_issues(args.definition_dir)
    if args.json:
        print(json.dumps({"issues": issues}, ensure_ascii=False, indent=2))
    elif issues:
        print("Bookmark action issues:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("OK bookmark actions stay on their pages")

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
