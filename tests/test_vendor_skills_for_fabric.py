import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP_ROOT = REPO_ROOT / ".tmp-tests"
SCRIPT = REPO_ROOT / "scripts" / "vendor_skills_for_fabric.py"


def load_module():
    spec = importlib.util.spec_from_file_location("vendor_skills_for_fabric", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_upstream(root: Path) -> None:
    write(root / "package.json", json.dumps({"name": "@microsoft/skills-for-fabric", "version": "9.9.9"}))
    write(root / "LICENSE", "MIT License\n")
    write(root / "skills" / "alpha" / "SKILL.md", "---\nname: alpha\ndescription: Alpha.\n---\n")
    write(root / "skills" / "alpha" / "references" / "detail.md", "see ../../../common/COMMON-CORE.md\n")
    write(root / "skills" / "not-a-skill" / "README.md", "no SKILL.md here\n")
    write(root / "common" / "COMMON-CORE.md", "core\n")
    write(root / "mcp-setup" / "README.md", "mcp\n")


class VendorSkillsForFabricTests(unittest.TestCase):
    def temp_dir(self) -> tempfile.TemporaryDirectory[str]:
        TEST_TEMP_ROOT.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT, ignore_cleanup_errors=True)

    def test_vendors_skills_common_license_and_manifest(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            upstream = Path(tmpdir) / "upstream"
            dest = Path(tmpdir) / ".claude"
            make_upstream(upstream)

            manifest = module.vendor(upstream, dest, tag="v9.9.9")

            self.assertTrue((dest / "skills" / "alpha" / "SKILL.md").exists())
            self.assertTrue((dest / "skills" / "alpha" / "references" / "detail.md").exists())
            self.assertFalse((dest / "skills" / "not-a-skill").exists())
            self.assertTrue((dest / "common" / "COMMON-CORE.md").exists())
            self.assertTrue((dest / "mcp-setup" / "README.md").exists())
            self.assertEqual((dest / "LICENSE-skills-for-fabric").read_text(encoding="utf-8"), "MIT License\n")

            written = json.loads((dest / module.MANIFEST_NAME).read_text(encoding="utf-8"))
            self.assertEqual(written, manifest)
            self.assertEqual(manifest["tag"], "v9.9.9")
            self.assertEqual(manifest["package_version"], "9.9.9")
            self.assertEqual(manifest["skills"], ["alpha"])
            self.assertEqual(manifest["source"], module.UPSTREAM_URL)

    def test_replaces_previously_vendored_skills_but_keeps_foreign_ones(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            upstream = Path(tmpdir) / "upstream"
            dest = Path(tmpdir) / ".claude"
            make_upstream(upstream)
            write(dest / "skills" / "old-vendored" / "SKILL.md", "---\nname: old-vendored\n---\n")
            write(dest / "skills" / "mine" / "SKILL.md", "---\nname: mine\n---\n")
            write(dest / "common" / "STALE.md", "stale\n")
            write(dest / module.MANIFEST_NAME, json.dumps({"skills": ["old-vendored"]}))

            module.vendor(upstream, dest, tag="v9.9.9")

            self.assertFalse((dest / "skills" / "old-vendored").exists())
            self.assertTrue((dest / "skills" / "mine" / "SKILL.md").exists())
            self.assertTrue((dest / "skills" / "alpha" / "SKILL.md").exists())
            self.assertFalse((dest / "common" / "STALE.md").exists())

    def test_refuses_to_overwrite_a_foreign_skill_with_the_same_name(self) -> None:
        module = load_module()
        with self.temp_dir() as tmpdir:
            upstream = Path(tmpdir) / "upstream"
            dest = Path(tmpdir) / ".claude"
            make_upstream(upstream)
            write(dest / "skills" / "alpha" / "SKILL.md", "---\nname: alpha\ndescription: Mine.\n---\n")

            with self.assertRaises(module.VendorConflict):
                module.vendor(upstream, dest, tag="v9.9.9")

            self.assertIn("Mine.", (dest / "skills" / "alpha" / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
