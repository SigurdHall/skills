from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "coding" / "repo-governance" / "SKILL.md"
CHILD_TEMPLATE = ROOT / "skills" / "coding" / "repo-governance" / "templates" / "child-readme.md"
HUB_TEMPLATE = ROOT / "skills" / "coding" / "repo-governance" / "templates" / "hub-entry.md"


class RepoGovernanceSkillTests(unittest.TestCase):
    def test_repo_governance_skill_exists_and_blocks_public_by_default(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("Default visibility is `private`", text)
        self.assertIn("Do not create a public repository without explicit user confirmation", text)
        self.assertIn("uit-private", text)
        self.assertIn("backlinks in both directions", text)

    def test_repo_governance_templates_include_origin_and_visibility(self):
        child = CHILD_TEMPLATE.read_text(encoding="utf-8")
        hub = HUB_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("Parent hub", child)
        self.assertIn("Original path", child)
        self.assertIn("private by default", child)
        self.assertIn("{{repo_name}}", hub)
        self.assertIn("{{target_url}}", hub)


if __name__ == "__main__":
    unittest.main()
