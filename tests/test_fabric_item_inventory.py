import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP_ROOT = REPO_ROOT / ".tmp-tests"
SCRIPT = (
    REPO_ROOT
    / "skills"
    / "fabric"
    / "fabric-item-authoring"
    / "scripts"
    / "inventory_fabric_skills.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("inventory_fabric_skills", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FabricItemInventoryTests(unittest.TestCase):
    def temp_dir(self) -> tempfile.TemporaryDirectory[str]:
        TEST_TEMP_ROOT.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT, ignore_cleanup_errors=True)

    def test_builds_versioned_inventory_and_categories(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            root = Path(tmpdir)
            (root / "package.json").write_text(
                json.dumps({"name": "@microsoft/skills-for-fabric", "version": "0.3.7"}),
                encoding="utf-8",
            )
            skills = root / "skills"
            fixtures = {
                "sqldb-authoring-cli": "Create SQL databases in Fabric.",
                "sqldb-consumption-cli": "Read SQL databases in Fabric.",
                "spark-operations-cli": "Diagnose Spark jobs.",
                "fabriciq": "Answer questions from Power BI.",
            }
            for name, description in fixtures.items():
                folder = skills / name
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text(
                    f"---\nname: {name}\ndescription: {description}\n---\n",
                    encoding="utf-8",
                )

            inventory = module.build_inventory(root, junction_roots=[])

            self.assertEqual(inventory["package_version"], "0.3.7")
            self.assertEqual(inventory["skill_count"], 4)
            self.assertEqual(
                inventory["category_counts"],
                {"authoring": 1, "consumption": 1, "operations": 1, "other": 1},
            )
            self.assertEqual(
                [skill["name"] for skill in inventory["skills"]],
                sorted(fixtures),
            )
            self.assertTrue(all("description" in skill for skill in inventory["skills"]))

    def test_rejects_missing_skills_directory(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                module.build_inventory(Path(tmpdir), junction_roots=[])

    def test_reports_duplicate_names_from_additional_skill_roots(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            root = Path(tmpdir) / "skills-for-fabric"
            primary = root / "skills" / "powerbi-report-authoring"
            additional_root = Path(tmpdir) / "plugin-cache" / "skills"
            duplicate = additional_root / "powerbi-report-authoring"
            primary.mkdir(parents=True)
            duplicate.mkdir(parents=True)
            (primary / "SKILL.md").write_text(
                "---\nname: powerbi-report-authoring\ndescription: Primary.\n---\n",
                encoding="utf-8",
            )
            (duplicate / "SKILL.md").write_text(
                "---\nname: powerbi-report-authoring\ndescription: Cached.\n---\n",
                encoding="utf-8",
            )

            inventory = module.build_inventory(
                root,
                junction_roots=[],
                additional_skill_roots=[additional_root],
            )

            self.assertEqual(inventory["duplicate_names"], ["powerbi-report-authoring"])
            self.assertEqual(len(inventory["skill_exposures"]), 2)
            self.assertIn("git", inventory)
            self.assertIsNone(inventory["git"]["commit"])


if __name__ == "__main__":
    unittest.main()
