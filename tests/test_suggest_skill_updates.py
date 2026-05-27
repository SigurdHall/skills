import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from suggest_skill_updates import (
    SuggestionType,
    build_skill_improvement_entry,
    build_stop_self_review_decision,
    discover_skill_catalog,
    generate_markdown_report,
    scan_text_for_suggestions,
)


class SkillSuggestionTests(unittest.TestCase):
    def test_scans_text_for_new_update_and_edge_case_suggestions(self) -> None:
        catalog = {
            "fabric-documentation": {
                "path": Path("skills/fabric/fabric-documentation/SKILL.md"),
                "description": "Use when documenting Fabric workspaces and architecture.",
            }
        }
        text = "\n".join(
            [
                "Next time, make this reusable as a checklist for Fabric review.",
                "The used skill fabric-documentation missed governance caveats.",
                "Edge case: except when the workspace has restricted data.",
            ]
        )

        suggestions = scan_text_for_suggestions(text, source=Path("notes/session.md"), catalog=catalog)

        self.assertEqual(
            [item.suggestion_type for item in suggestions],
            [
                SuggestionType.NEW_SKILL,
                SuggestionType.MODIFY_USED_SKILL,
                SuggestionType.ADD_EDGE_CASE_CONTEXT,
            ],
        )
        self.assertEqual(suggestions[1].matched_skill, "fabric-documentation")
        self.assertEqual(suggestions[2].matched_skill, "fabric-documentation")

    def test_discovers_skill_catalog_from_repo(self) -> None:
        catalog = discover_skill_catalog(REPO_ROOT)

        self.assertIn("fabric-documentation", catalog)
        self.assertEqual(
            catalog["fabric-documentation"]["path"],
            Path("skills/fabric/fabric-documentation/SKILL.md"),
        )

    def test_report_is_actionable_markdown(self) -> None:
        catalog = {
            "prompt-engineering": {
                "path": Path("skills/coding/prompt-engineering/SKILL.md"),
                "description": "Use when improving prompts.",
            }
        }
        suggestions = scan_text_for_suggestions(
            "Always add eval criteria when improving prompts.",
            source=Path("notes/session.md"),
            catalog=catalog,
        )

        report = generate_markdown_report(suggestions)

        self.assertIn("# Skill Suggestions", report)
        self.assertIn("new-skill", report)
        self.assertIn("notes/session.md", report)
        self.assertIn("prompt-engineering", report)

    def test_ignores_common_documentation_phrases(self) -> None:
        suggestions = scan_text_for_suggestions(
            "\n".join(
                [
                    "# Fabric Documentation Quality Checklist",
                    "Do not create a skill just to solve one isolated deck.",
                    "Is there an obvious appendix boundary?",
                ]
            ),
            source=Path("references/doc.md"),
            catalog={},
        )

        self.assertEqual(suggestions, [])

    def test_stop_hook_requests_self_review_after_skill_use(self) -> None:
        payload = {
            "hook_event_name": "Stop",
            "stop_hook_active": False,
            "last_assistant_message": "Using `skill-design` because this changes skill behavior.",
        }

        decision = build_stop_self_review_decision(payload)

        self.assertEqual(decision["decision"], "block")
        self.assertIn("Assess whether the task should become a new skill", decision["reason"])
        self.assertIn("Do not edit SKILL.md automatically", decision["reason"])

    def test_stop_hook_does_not_loop_or_trigger_without_signal(self) -> None:
        self.assertEqual(
            build_stop_self_review_decision(
                {
                    "hook_event_name": "Stop",
                    "stop_hook_active": True,
                    "last_assistant_message": "Using `skill-design`.",
                }
            ),
            {"continue": True, "suppressOutput": True},
        )
        self.assertEqual(
            build_stop_self_review_decision(
                {
                    "hook_event_name": "Stop",
                    "stop_hook_active": False,
                    "last_assistant_message": "I updated the file and ran the tests.",
                }
            ),
            {"continue": True, "suppressOutput": True},
        )

    def test_builds_skill_improvement_inbox_entry(self) -> None:
        entry = build_skill_improvement_entry(
            {
                "hook_event_name": "Stop",
                "last_assistant_message": "Using `skill-design` because this changes skill behavior.",
                "transcript_path": "C:/repos/.codex/sessions/example.jsonl",
            }
        )

        self.assertIn("## Skill self-review candidate", entry)
        self.assertIn("- Trigger: `Stop`", entry)
        self.assertIn("- Suggested action: Review whether to create a new skill", entry)
        self.assertIn("Using `skill-design`", entry)


if __name__ == "__main__":
    unittest.main()
